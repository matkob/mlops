import pandas as pd
import random

import google.cloud.functions.context as gfunc
import google.cloud.storage as gs

from typing import Any, Dict


def gen_next_timestamps(timestamps: pd.Series) -> pd.Series:
    first_entry = timestamps.min()
    last_entry = timestamps.max()

    time_diff = timestamps - first_entry
    return last_entry + time_diff


def update_dataset(event: Dict[str, Any], context: gfunc.Context) -> None:
    source_bucket_name = event["attributes"]["source_bucket"]
    source_object_name = event["attributes"]["source_object"]

    target_bucket_name = event["attributes"]["target_bucket"]
    target_object_name = f"orderbook_{context.timestamp}.csv"

    client = gs.Client()

    source_bucket = client.bucket(source_bucket_name)
    source_blob = source_bucket.blob(source_object_name)

    with source_blob.open("r") as f:
        static_data = pd.read_csv(f)

    print(f"Source dataset read from {source_bucket_name}/{source_object_name}")

    # Here's where the whole data mocking logic is

    # Mocking price randomly
    asks = static_data.filter(regex="asks.*price")
    bids = static_data.filter(regex="bids.*price")

    ask = random.uniform(0.1, 1000)
    bid = ask - random.uniform(0.01, ask * 0.95)
    asks.values[:] = ask
    bids.values[:] = bid

    static_data.update(asks)
    static_data.update(bids)

    # Mocking timestamp
    static_data["timestamp"] = gen_next_timestamps(static_data["timestamp"])
    static_data["local_timestamp"] = gen_next_timestamps(static_data["local_timestamp"])

    target_bucket = client.bucket(target_bucket_name)
    target_blob = target_bucket.blob(target_object_name)

    with target_blob.open("w") as f:
        static_data.to_csv(f, index=False)

    print(f"Target dataset created in {target_bucket_name}/{target_object_name}")
