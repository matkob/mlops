import pandas as pd
import logging
import os
import google.cloud.storage as storage
import google.cloud.pubsub_v1 as pubsub
import google.cloud.logging as cloud_logging

from typing import Any, Dict


cloud_logging.Client().setup_logging()  # type: ignore


def read_static_data(bucket: str, object: str) -> pd.DataFrame:
    client = storage.Client()
    source_bucket = client.bucket(bucket)
    source_blob = source_bucket.blob(object)

    with source_blob.open("r") as f:
        return pd.read_csv(f)


def mock_data(reference: pd.DataFrame, count: int) -> pd.DataFrame:
    # TODO: implement smarter way to mock data
    return reference.head(count)


def publish_data(topic: str, data: pd.DataFrame) -> None:
    client = pubsub.PublisherClient()
    future = client.publish(topic, bytes(data.to_csv(index=False), encoding="utf-8"))
    future.result()


def produce(event: Dict[str, Any], _: Any) -> None:
    source_bucket_name = os.environ["SOURCE_BUCKET"]
    source_object_name = os.environ["SOURCE_OBJECT"]
    topic = os.environ["SINK"]

    count = int(event["attributes"]["count"])

    logging.info(
        "Triggered mock data production. "
        f"Reference data: {source_bucket_name}/{source_object_name}. "
        f"Count: {count}. "
        f"Sink: {topic}. "
    )

    reference_data = read_static_data(source_bucket_name, source_object_name)
    mocked_data = mock_data(reference_data, count)
    publish_data(topic, mocked_data)

    logging.info("Produced mock data successfully")
