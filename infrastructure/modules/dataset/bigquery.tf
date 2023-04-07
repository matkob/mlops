resource "google_bigquery_dataset" "dataset" {
  dataset_id    = "order_book_${var.random_suffix}"
  friendly_name = "order-book"
  description   = "This dataset contains order book data - both offline snapshot and live updates."
  location      = var.region

  delete_contents_on_destroy = true

  labels = {
    owner   = "matkob"
    purpose = "mlops-demo"
  }

  depends_on = [google_project_service.bigquery]
}

resource "google_bigquery_table" "initial" {
  table_id    = "initial"
  description = "This table contains initial training data. It's offline and static."
  dataset_id  = google_bigquery_dataset.dataset.dataset_id

  external_data_configuration {
    autodetect    = true
    source_format = "CSV"
    compression   = "NONE"

    source_uris = [
      "${google_storage_bucket.training_data.url}/${google_storage_bucket_object.initial.name}"
    ]
  }

  labels = {
    owner   = "matkob"
    purpose = "mlops-demo"
  }
}

resource "google_bigquery_table" "live" {
  table_id    = "live"
  description = "This table contains live production data. It's dynamic and constantly updated."
  dataset_id  = google_bigquery_dataset.dataset.dataset_id

  # BigQuery table must have a schema before it accepts any incoming data.
  # The schema can be empty so it is inferred by incoming live data.
  schema = "[]"

  time_partitioning {
    # 2 Days
    expiration_ms = 172800000
    type          = "HOUR"
  }

  # Set for convenient development, shouldn't be used in production environment.
  deletion_protection = false

  # We do not really care about the schema, it's just a sink for incoming live data.
  lifecycle {
    ignore_changes = [schema]
  }

  labels = {
    owner   = "matkob"
    purpose = "mlops-demo"
  }
}
