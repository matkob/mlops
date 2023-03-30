import logging
import mlflow
from typing import Any, Dict, Tuple

import pandas as pd
import xgboost as xgb
import sklearn.metrics as metrics
from sklearn.model_selection import train_test_split


def split_data(
    data: pd.DataFrame, parameters: Dict[str, Any]
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Splits data into features and targets training and test sets.

    Args:
        data: Data containing features and target.
        parameters: Parameters defined in parameters/data_science.yml.
    Returns:
        Split data.
    """
    X = data.drop(columns="mid.price")
    y = data["mid.price"]
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=parameters["test_size"],
        random_state=parameters["random_state"],
        shuffle=False,
    )
    return X_train, X_test, y_train, y_test


def train_model(X_train: pd.DataFrame, y_train: pd.Series) -> xgb.XGBRegressor:
    """Trains the linear regression model.

    Args:
        X_train: Training data of independent features.
        y_train: Training data for price.

    Returns:
        Trained model.
    """
    regressor = xgb.XGBRegressor()
    regressor.fit(X_train, y_train)
    return regressor


def evaluate_model(
    regressor: xgb.XGBRegressor, stage: str, X: pd.DataFrame, y: pd.Series
) -> None:
    """Calculates and logs the coefficient of determination.

    Args:
        regressor: Trained model.
        X_test: Testing data of independent features.
        y_test: Testing data for price.
    """
    y_pred = regressor.predict(X)

    max_error = metrics.max_error(y, y_pred)
    median_error = metrics.median_absolute_error(y, y_pred)
    mse_error = metrics.mean_squared_error(y, y_pred)
    explained_variance = metrics.explained_variance_score(y, y_pred)

    logger = logging.getLogger(__name__)
    logger.info("Model has a max error of %.3f on %s data.", max_error, stage)
    logger.info("Model has a median error of %.3f on %s data.", median_error, stage)
    logger.info("Model has a mse error of %.3f on %s data.", mse_error, stage)
    logger.info(
        "Model has an explained variance score of %.3f on %s data.",
        explained_variance,
        stage,
    )

    mlflow.log_metric(f"{stage}_max_error", max_error)
    mlflow.log_metric(f"{stage}_median_error", median_error)
    mlflow.log_metric(f"{stage}_mse_error", mse_error)
    mlflow.log_metric(f"{stage}_explained_variance", explained_variance)
