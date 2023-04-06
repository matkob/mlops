resource "google_pubsub_topic" "mocked_data" {
  name = "mocked-data-${var.random_suffix}"

  # Minimum duration is 10 min
  message_retention_duration = "610s"

  labels = {
    owner   = "matkob"
    purpose = "mlops-demo"
    type    = "mock"
  }

  depends_on = [google_project_service.pubsub]
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

resource "google_cloudfunctions_function" "data_mock_function" {
  name        = "data-mock-${var.random_suffix}"
  description = "Function producing mocked data"
  runtime     = "python310"

  available_memory_mb = 1024
  entry_point         = "produce"
  max_instances       = 1
  timeout             = 60

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

  depends_on = [google_project_service.functions]
}