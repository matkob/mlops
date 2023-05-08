from typing import Any, Dict
import pandas as pd


def sort_by_time(order_book: pd.DataFrame) -> pd.DataFrame:
    """
    Sorts the order book with timestamp value and removes all the temporal columns afterwards.
    """  # noqa: E501
    return (
        order_book.sort_values(by="timestamp")
        # After sorting timestamp is no longer needed
        .drop(columns=["timestamp", "local_timestamp", "exchange", "symbol"])
    )


def calculate_mid_price(order_book: pd.DataFrame) -> pd.DataFrame:
    """
    Calculates mid price by getting an average between smallest ask and biggest bid.
    """  # noqa: E501

    asks_n_bids = [c for c in order_book.columns if "asks" in c or "bids" in c]
    typed = order_book[asks_n_bids].astype("float32")

    df = pd.DataFrame(index=order_book.index)
    df["mid_price"] = (typed["asks_0_price"] + typed["bids_0_price"]) / 2

    return df


def create_historical_features(
    order_book: pd.DataFrame, parameters: Dict[str, Any]
) -> pd.DataFrame:
    """
    Creates historical features such as ask/bid values from the past. Can be parametrized with:
    - time_window: Number of ticks to look back

    Will result in a
    """  # noqa: E501
    time_window = parameters["time_window"]
    asks_n_bids = [c for c in order_book.columns if "asks" in c or "bids" in c]

    df = pd.DataFrame(index=order_book.index)

    for i in range(1, time_window + 1):
        cols = [f"{i}_tick_{c}" for c in asks_n_bids]
        df[cols] = order_book[asks_n_bids].shift(periods=i)

    return df


def merge_features(mid_price: pd.DataFrame, historical: pd.DataFrame) -> pd.DataFrame:
    """Merges features into a signle DataFrame using index."""
    return pd.concat([mid_price, historical], axis="columns", join="inner")
