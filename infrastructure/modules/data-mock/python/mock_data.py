import json
import pandas as pd
import numpy as np
import logging
import os
import time
import datetime
import google.cloud.pubsub_v1 as pubsub
import google.cloud.logging as cloud_logging

from typing import Any, Dict


cloud_logging.Client().setup_logging()  # type: ignore


def mock_data(count: int) -> pd.DataFrame:
    df = pd.DataFrame(index=range(count))
    now = round(time.time_ns() / 1000)
    hour = datetime.datetime.fromtimestamp(now / 1_000_000).hour

    # Constants
    df["exchange"] = "binance"
    df["symbol"] = "BTCUSDT"
    logging.info("Added constants")

    # Timestamp
    time_range = 1_000_000 * 60 * 12  # 12 minutes in microseconds
    df["timestamp"] = now + np.random.randint(0, time_range, size=(count,))
    df["local_timestamp"] = df["timestamp"] + np.random.randint(0, 1000, size=(count,))
    logging.info("Added time columns")

    # Levels
    for i in range(5):
        df[f"asks_{i}_price"] = hour + i + np.random.rand()
        df[f"asks_{i}_amount"] = np.random.rand() * 10
        df[f"bids_{i}_price"] = hour - i - np.random.rand()
        df[f"bids_{i}_amount"] = np.random.rand() * 10
        logging.info(f"Added asks and bids at level {i}")

    return df


def publish_data(topic: str, data: pd.DataFrame) -> None:
    batch_settings = pubsub.types.BatchSettings(
        max_messages=len(data),
        max_bytes=2048,
        max_latency=1,
    )
    client = pubsub.PublisherClient(batch_settings)

    logging.info(f"Publishing {len(data)} entries to pubsub")
    for _, row in data.iterrows():
        json_msg = json.dumps(row.to_dict())
        message = json_msg.encode("utf-8")
        _ = client.publish(topic, data=message)
    logging.info(f"{len(data)} entries published successfully")


def produce(event: Dict[str, Any], _: Any) -> None:
    topic = os.environ["TOPIC"]
    count = int(os.environ["COUNT"])

    logging.info(
        "Triggered mock data production. " f"Count: {count}. " f"Sink: {topic}. "
    )

    mocked_data = mock_data(count)
    publish_data(topic, mocked_data)
