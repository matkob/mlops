import kfp
import kfp.v2.dsl as dsl


@dsl.component(base_image="python:3.10")
def create_dataset(output_csv: dsl.Output[dsl.Dataset]):
    """
    Fetches dataset from tardis.dev. Must be of type: order book snapshot.
    """
    import requests

    url = "https://datasets.tardis.dev/v1/deribit/book_snapshot_25/2020/04/01/BTC-PERPETUAL.csv.gz"
    with open(output_csv.path, "wb") as output_file:
        output_file.write(requests.get(url).content)


@dsl.component(packages_to_install=["polars~=0.16.9"], base_image="python:3.10")
def transform_dataset(input_csv: dsl.Input[dsl.Dataset], time_window: int, output_csv: dsl.Output[dsl.Dataset]):
    import polars as pl

    # TODO: increase memory resource limits and remove nrows limit
    df = pl.read_csv(input_csv.path, n_rows=500, sep=",", infer_schema_length=0)
    df = df.with_columns(df["timestamp"].cast(pl.Int64))
    # using exchange timestamp
    df = df.sort("timestamp")
    # exchange, symbol is always binance, btcusdt
    df = df.drop(columns=["timestamp", "local_timestamp", "exchange", "symbol"])
    # making sure there are only asks and bids in the dataset
    asks_n_bids = [c for c in df.columns if "asks" in c or "bids" in c]
    df = df[asks_n_bids].with_columns(pl.all().cast(pl.Float32))
    # adding target - mid price
    df = df.with_columns(((df["asks[0].price"] + df["bids[0].price"]) / 2).alias("mid.price"))
    # shifting input data
    for i in range(1, time_window + 1):
        cols = [f"{i}_tick_{c}" for c in asks_n_bids]
        shifted = df[asks_n_bids].shift(periods=i)
        shifted.columns = cols
        df = df.with_columns(shifted)
    # removing data leakage
    df = df.drop(columns=asks_n_bids)
    # removing NaNs
    df = df.drop_nulls()

    df.write_csv(output_csv.path)


@dsl.component(packages_to_install=["polars~=0.16.9", "scikit-learn~=1.0.2"], base_image="python:3.10")
def split_dataset(input_csv: dsl.Input[dsl.Dataset], test_split: float, seed: int, x_train_csv: dsl.Output[dsl.Dataset],
                  y_train_csv: dsl.Output[dsl.Dataset], x_test_csv: dsl.Output[dsl.Dataset],
                  y_test_csv: dsl.Output[dsl.Dataset]):
    import polars as pl
    import numpy as np
    from sklearn.model_selection import train_test_split

    df = pl.read_csv(input_csv.path, sep=",")
    y = df["mid.price"].to_numpy()
    X = df.drop(columns="mid.price").to_numpy()
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_split, random_state=seed)

    np.savetxt(x_train_csv.path, X_train, delimiter=",")
    np.savetxt(y_train_csv.path, y_train, delimiter=",")
    np.savetxt(x_test_csv.path, X_test, delimiter=",")
    np.savetxt(y_test_csv.path, y_test, delimiter=",")


@dsl.component(packages_to_install=["xgboost~=1.6.2", "scikit-learn~=1.0.2"], base_image="python:3.10")
def train_and_test_model(x_train_csv: dsl.Input[dsl.Dataset], y_train_csv: dsl.Input[dsl.Dataset],
                         x_test_csv: dsl.Input[dsl.Dataset], y_test_csv: dsl.Input[dsl.Dataset],
                         model_file: dsl.Output[dsl.Model]):
    import numpy as np
    import xgboost as xgb
    import sklearn.metrics as metrics

    X_train = np.genfromtxt(x_train_csv.path, delimiter=",")
    y_train = np.genfromtxt(y_train_csv.path, delimiter=",")
    X_test = np.genfromtxt(x_test_csv.path, delimiter=",")
    y_test = np.genfromtxt(y_test_csv.path, delimiter=",")

    model = xgb.XGBRegressor()
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    predictions = [round(value) for value in y_pred]

    max_error = metrics.max_error(y_test, predictions)
    median_error = metrics.median_absolute_error(y_test, predictions)
    mse_error = metrics.mean_squared_error(y_test, predictions)
    explained_variance = metrics.explained_variance_score(y_test, predictions)

    model.save_model(model_file.path)
    model_file.metadata["Max error"] = max_error
    model_file.metadata["Median error"] = median_error
    model_file.metadata["MSE"] = mse_error
    model_file.metadata["Explained variance"] = explained_variance


@dsl.pipeline(name="dummy-regression-model",
              description="An example pipeline that trains a crypto price regression model.",
              pipeline_root="gs://test-vertex-ai-datasets/kubeflow")
def add_pipeline(time_window: int = 2, test_split: float = 0.33, seed: int = 2):
    create_task = create_dataset()
    transform_task = transform_dataset(create_task.outputs["output_csv"], time_window)
    split_task = split_dataset(transform_task.outputs["output_csv"], test_split, seed)
    train_and_test_model(split_task.outputs["x_train_csv"], split_task.outputs["y_train_csv"],
                         split_task.outputs["x_test_csv"], split_task.outputs["y_test_csv"])


kfp.v2.compiler.Compiler().compile(pipeline_func=add_pipeline, package_path="pipeline.json")
