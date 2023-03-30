from typing import Any, Dict
import pandas as pd


def enrich_order_book(
    order_book: pd.DataFrame, parameters: Dict[str, Any]
) -> pd.DataFrame:
    """Preprocesses the data for order book.
    Note this is overly simplified problem with simple timeseries processing
    just for the purpose of the demo.
    """

    time_window = parameters["time_window"]

    asks_n_bids = [c for c in order_book.columns if "asks" in c or "bids" in c]

    df = (
        order_book.sort_values(by="timestamp")
        # After sorting timestamp is no longer needed
        .drop(columns=["timestamp", "local_timestamp", "exchange", "symbol"])
        # There should only be asks and bids in the dataset
        [asks_n_bids].astype("float32")
    )
    df["mid.price"] = (df["asks[0].price"] + df["bids[0].price"]) / 2

    # shifting input data
    for i in range(1, time_window + 1):
        cols = [f"{i}_tick_{c}" for c in asks_n_bids]
        df[cols] = df[asks_n_bids].shift(periods=i)

    return df.drop(columns=asks_n_bids).dropna()


def process_feature_names(order_book: pd.DataFrame) -> pd.DataFrame:
    """Removes any unsupported characters from a dataset."""

    return order_book.rename(
        mapper=lambda c: c.replace("[", "").replace("]", ""), axis=1
    )
