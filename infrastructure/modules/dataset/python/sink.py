import pandas as pd
import logging
import os
import io
import base64
import google.cloud.logging as cloud_logging

from google.cloud import bigquery
from typing import Any, Dict


cloud_logging.Client().setup_logging()  # type: ignore


def consume(event: Dict[str, Any], _: Any) -> None:
    dataset_id = os.environ["DATASET_ID"]
    table_id = os.environ["TABLE_ID"]

    data = event["data"]
    df = (
        pd.read_csv(io.BytesIO(base64.b64decode(data)), encoding="utf-8")
        # BigQuery does not support `[`, `]` and `.` characters
        .rename(
            columns=lambda c: c.replace("[", "_").replace("]", "_").replace(".", "_")
        )
    )

    logging.info(
        "Triggered consumer function. "
        f"Dataset: {dataset_id}. "
        f"Table: {table_id}. "
        f"Payload size: {len(df)}. "
    )

    client = bigquery.Client()
    job = client.load_table_from_dataframe(
        df, f"{dataset_id}.{table_id}", job_config=bigquery.LoadJobConfig()
    )
    job.result()
    logging.info("Loaded data successfully.")
