from typing import Any, Dict
from kedro.pipeline import Pipeline, node, pipeline

from .nodes import enrich_order_book, process_feature_names


def create_pipeline(**kwargs: Dict[str, Any]) -> Pipeline:
    return pipeline(
        [
            node(
                func=enrich_order_book,
                inputs=["order_book", "params:order_book_processing_options"],
                outputs="enriched_order_book",
                name="enrich_order_book",
            ),
            node(
                func=process_feature_names,
                inputs="enriched_order_book",
                outputs="processed_order_book",
                name="preprocess_feature_names",
            ),
        ]
    )
