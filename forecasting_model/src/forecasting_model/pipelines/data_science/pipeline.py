from typing import Any, Dict
from kedro.pipeline import Pipeline, node, pipeline

from .nodes import evaluate_model, split_data, train_model


def create_pipeline(**kwargs: Dict[str, Any]) -> Pipeline:
    return pipeline(
        [
            node(
                func=split_data,
                inputs=["processed_order_book", "params:model_options"],
                outputs=["X_train", "X_test", "y_train", "y_test"],
                name="split_data",
            ),
            node(
                func=train_model,
                inputs=["X_train", "y_train"],
                outputs="regressor",
                name="train_model",
            ),
            node(
                func=lambda model, X, y: evaluate_model(model, "train", X, y),
                inputs=["regressor", "X_train", "y_train"],
                outputs=None,
                name="evaluate_model_on_train_data",
            ),
            node(
                func=lambda model, X, y: evaluate_model(model, "test", X, y),
                inputs=["regressor", "X_test", "y_test"],
                outputs=None,
                name="evaluate_model_on_test_data",
            ),
        ]
    )
