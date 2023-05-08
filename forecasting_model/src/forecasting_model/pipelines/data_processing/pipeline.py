from typing import Any, Dict
from kedro.pipeline import Pipeline, node, pipeline

from .nodes import (
    sort_by_time,
    calculate_mid_price,
    create_historical_features,
    merge_features,
)


def create_pipeline(**kwargs: Dict[str, Any]) -> Pipeline:
    return pipeline(
        [
            node(
                func=sort_by_time,
                inputs=["order_book"],
                outputs="sorted_order_book",
                name="sort_by_time",
            ),
            node(
                func=calculate_mid_price,
                inputs=["sorted_order_book"],
                outputs="mid_price",
                name="calculate_mid_price",
            ),
            node(
                func=create_historical_features,
                inputs=["sorted_order_book", "params:order_book_processing_options"],
                outputs="historical_features",
                name="create_historical_features",
            ),
            node(
                func=merge_features,
                inputs=["mid_price", "historical_features"],
                outputs="dataset",
                name="merge_features",
            ),
        ]
    )
