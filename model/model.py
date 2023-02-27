import argparse

import polars as pl
import xgboost as xgb
import sklearn.metrics as metrics

from sklearn.model_selection import train_test_split

parser = argparse.ArgumentParser()
parser.add_argument("--data_dir", type=str)
parser.add_argument("--data_file", type=str)

parser.add_argument("--time_window", type=int, default=10)

parser.add_argument("--test_split", type=float, default=0.33)
parser.add_argument("--seed", type=int, default=7)
args = parser.parse_args()

df = pl.read_csv(f"{args.data_dir}/{args.data_file}", sep=",", infer_schema_length=0)
df = df.with_columns(df["timestamp"].cast(pl.Int64))

# Transform data
# using exchange timestamp
df = df.sort("timestamp")
# exchange, symbol is always binance, btcusdt
df = df.drop(columns=["timestamp", "local_timestamp", "exchange", "symbol"])
# making sure there are only asks and bids in the dataset
asks_n_bids = [c for c in df.columns if "asks" in c or "bids" in c]
df = df[asks_n_bids]
df = df.with_columns(pl.all().cast(pl.Float32))

# adding target - mid price
df = df.with_columns(((df["asks[0].price"] + df["bids[0].price"]) / 2).alias("mid.price"))

# shifting input data
for i in range(1, args.time_window + 1):
    cols = [f"{i}_tick_{c}" for c in asks_n_bids]
    shifted = df[asks_n_bids].shift(periods=i)
    shifted.columns = cols
    df = df.with_columns(shifted)

# removing data leakage
df = df.drop(columns=asks_n_bids)
# removing NaNs
df = df.drop_nulls()

# Split data
y = df[["mid.price"]]
X = df.drop(columns="mid.price")
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=args.test_split, random_state=args.seed)

# Train model
model = xgb.XGBRegressor()
model.fit(X_train, y_train)

# Test model
y_pred = model.predict(X_test)
predictions = [round(value) for value in y_pred]

# Show summary of the performance
max_error = metrics.max_error(y_test, predictions)
median_error = metrics.median_absolute_error(y_test, predictions)
mse_error = metrics.mean_squared_error(y_test, predictions)
explained_variance = metrics.explained_variance_score(y_test, predictions)

print("Max error: %.2f" % max_error)
print("Median error: %.2f" % median_error)
print("MSE: %.2f" % mse_error)
print("Explained variance: %.2f" % explained_variance)
