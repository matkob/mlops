import pandas as pd
import datetime
import logging
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


def mock_data(reference: pd.DataFrame, period: datetime.timedelta) -> pd.DataFrame:
    # TODO: take data from reference that corresponds to given period
    return reference.head(100)


def publish_data(topic: str, data: pd.DataFrame) -> None:
    client = pubsub.PublisherClient()
    future = client.publish(topic, bytes(data.to_csv(index=False), encoding="utf-8"))
    future.result()


def produce(event: Dict[str, Any], _: Any) -> None:
    source_bucket_name = event["attributes"]["source_bucket"]
    source_object_name = event["attributes"]["source_object"]

    raw_period = event["attributes"]["period"]
    topic = event["attributes"]["sink"]

    logging.info(
        "Triggered mock data production. "
        f"Reference data: {source_bucket_name}/{source_object_name}. "
        f"Period: {raw_period}. "
        f"Sink: {topic}. "
    )

    period = datetime.timedelta(
        minutes=datetime.datetime.strptime(raw_period, "%Mm").minute
    )
    reference_data = read_static_data(source_bucket_name, source_object_name)
    mocked_data = mock_data(reference_data, period)
    publish_data(topic, mocked_data)

    logging.info("Produced mock data successfully")
