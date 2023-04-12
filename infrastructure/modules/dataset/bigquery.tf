resource "google_bigquery_dataset" "order_book" {
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
  dataset_id  = google_bigquery_dataset.order_book.dataset_id

  external_data_configuration {
    autodetect    = true
    schema        = file("${path.root}/schema/order_book.bigquery.json")
    source_format = "CSV"
    compression   = "NONE"

    source_uris = [
      "${google_storage_bucket.training_data.url}/${google_storage_bucket_object.initial.name}"
    ]
  }

  # Set for convenient development, shouldn't be used in production environment.
  deletion_protection = false

  labels = {
    owner   = "matkob"
    purpose = "mlops-demo"
  }
}

resource "google_bigquery_table" "live" {
  table_id    = "live"
  description = "This table contains live production data. It's dynamic and constantly updated."
  dataset_id  = google_bigquery_dataset.order_book.dataset_id

  schema = file("${path.root}/schema/order_book.bigquery.json")

  time_partitioning {
    # 2 Days
    expiration_ms = 172800000
    type          = "HOUR"
  }

  # Set for convenient development, shouldn't be used in production environment.
  deletion_protection = false

  labels = {
    owner   = "matkob"
    purpose = "mlops-demo"
  }
}

resource "google_project_iam_member" "viewer" {
  project = var.project_id
  role    = "roles/bigquery.metadataViewer"
  member  = "serviceAccount:service-${var.project_number}@gcp-sa-pubsub.iam.gserviceaccount.com"
}

resource "google_project_iam_member" "editor" {
  project = var.project_id
  role    = "roles/bigquery.dataEditor"
  member  = "serviceAccount:service-${var.project_number}@gcp-sa-pubsub.iam.gserviceaccount.com"
}

resource "google_pubsub_subscription" "live_order_book_sink" {
  name  = "live-data-subscription-${var.random_suffix}"
  topic = var.order_book_updates_topic

  bigquery_config {
    table            = "${var.project_id}.${google_bigquery_dataset.order_book.dataset_id}.${google_bigquery_table.live.table_id}"
    use_topic_schema = true
  }

  labels = {
    owner   = "matkob"
    purpose = "mlops-demo"
  }

  depends_on = [google_project_iam_member.viewer, google_project_iam_member.editor]
}
