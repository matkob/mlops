resource "google_pubsub_schema" "order_book" {
  name       = "order-book-${var.random_suffix}"
  type       = "PROTOCOL_BUFFER"
  definition = file("${path.root}/schema/order_book.proto")

  depends_on = [google_project_service.pubsub]
}

resource "google_pubsub_topic" "mocked_data" {
  name = "order-book-${var.random_suffix}"

  # Minimum duration is 10 min
  message_retention_duration = "600s"

  schema_settings {
    schema   = google_pubsub_schema.order_book.id
    encoding = "JSON"
  }

  labels = {
    owner   = "matkob"
    purpose = "mlops-demo"
    type    = "mock"
  }
}

data "archive_file" "function_code" {
  type        = "zip"
  source_dir  = "${path.module}/python/"
  output_path = "${path.module}/target/mock_data.zip"
}

resource "google_storage_bucket_object" "data_mock_function_code" {
  name   = "code/mock_data.zip"
  bucket = google_storage_bucket.data_mock.name
  source = data.archive_file.function_code.output_path
}

resource "google_cloudfunctions_function" "data_mock" {
  name        = "data-mock-${var.random_suffix}"
  description = "Function producing mocked data"
  runtime     = "python310"

  available_memory_mb = 1024
  entry_point         = "produce"
  max_instances       = 1
  timeout             = 120

  source_archive_bucket = google_storage_bucket.data_mock.name
  source_archive_object = google_storage_bucket_object.data_mock_function_code.name

  labels = {
    owner   = "matkob"
    purpose = "mlops-demo"
    type    = "mock"
  }

  build_environment_variables = {
    GOOGLE_FUNCTION_SOURCE = "mock_data.py"
  }

  environment_variables = {
    TOPIC = google_pubsub_topic.mocked_data.id
    COUNT = "100"
  }

  event_trigger {
    event_type = "providers/cloud.pubsub/eventTypes/topic.publish"
    resource   = google_pubsub_topic.data_mock_trigger.id
  }

  # Coupling function's lifecycle with the code will trigger proper redeployment on code updates
  # This will not be the case otherwise
  lifecycle {
    replace_triggered_by = [
      google_storage_bucket_object.data_mock_function_code.md5hash
    ]
  }

  depends_on = [
    google_project_service.functions,
    google_project_service.build
  ]
}
