resource "google_storage_bucket" "dataset_functions" {
  name          = "dataset-functions-${var.random_suffix}"
  location      = var.region
  force_destroy = true

  storage_class = "STANDARD"

  labels = {
    owner   = "matkob"
    purpose = "mlops-demo"
  }

  uniform_bucket_level_access = true

  depends_on = [google_project_service.storage]
}

data "archive_file" "function_code" {
  type        = "zip"
  source_dir  = "${path.module}/python/"
  output_path = "${path.module}/target/sink.zip"
}

resource "google_storage_bucket_object" "sink_function_code" {
  name   = "sink.zip"
  bucket = google_storage_bucket.dataset_functions.name
  source = data.archive_file.function_code.output_path
}

data "google_pubsub_topic" "order_book_topic" {
  name = var.order_book_updates_topic
}

# TODO: replace with BigQuery subscription
resource "google_cloudfunctions_function" "sink" {
  name        = "sink-${var.random_suffix}"
  description = "Function consuming online order book data and storing it in BigQuery."
  runtime     = "python310"

  available_memory_mb = 1024
  entry_point         = "consume"
  max_instances       = 1
  timeout             = 60

  source_archive_bucket = google_storage_bucket.dataset_functions.name
  source_archive_object = google_storage_bucket_object.sink_function_code.name

  labels = {
    owner   = "matkob"
    purpose = "mlops-demo"
  }

  build_environment_variables = {
    GOOGLE_FUNCTION_SOURCE = "sink.py"
  }

  environment_variables = {
    DATASET_ID = google_bigquery_dataset.dataset.dataset_id
    TABLE_ID   = google_bigquery_table.live.table_id
  }

  event_trigger {
    event_type = "providers/cloud.pubsub/eventTypes/topic.publish"
    resource   = data.google_pubsub_topic.order_book_topic.id
  }

  # Coupling function's lifecycle with the code will trigger proper redeployment on code updates
  # This will not be the case otherwise
  lifecycle {
    replace_triggered_by = [
      google_storage_bucket_object.sink_function_code.md5hash
    ]
  }

  depends_on = [
    google_project_service.functions,
    google_project_service.build
  ]
}