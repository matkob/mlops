resource "google_pubsub_topic" "dataset_update_topic" {
  name = "dataset-update-${var.random_suffix}"

  # Minimum duration is 10 min
  message_retention_duration = "610s"

  labels = {
    owner   = "matkob"
    purpose = "mlops-demo"
    type    = "mock"
  }
}

resource "google_cloud_scheduler_job" "dataset_update_job" {
  name        = "trigger-dataset-update-${var.random_suffix}"
  description = "Produces an event triggering dataset update."
  schedule    = "*/10 * * * *"

  pubsub_target {
    # Topic name is exprected to be in the full format, so equal to the id
    topic_name = google_pubsub_topic.dataset_update_topic.id
    attributes = {
      source_bucket = google_storage_bucket.datalake.name
      source_object = google_storage_bucket_object.timeseries_data.name
      target_bucket = google_storage_bucket.dataset.name
    }
  }

  depends_on = [google_project_service.cloud_scheduler]
}

resource "google_storage_bucket" "data_update_func" {
  name          = "data-update-func-${var.random_suffix}"
  location      = var.region
  force_destroy = true

  storage_class = "STANDARD"

  labels = {
    owner   = "matkob"
    purpose = "mlops-demo"
    type    = "mock"
  }

  uniform_bucket_level_access = true
}

data "archive_file" "data_update_func_code" {
  type        = "zip"
  source_dir  = "functions/"
  excludes    = ["data_update.zip"]
  output_path = "functions/data_update.zip"
}

resource "google_storage_bucket_object" "data_update_func" {
  name   = "data_update.zip"
  bucket = google_storage_bucket.data_update_func.name
  source = "functions/data_update.zip"
}

resource "google_cloudfunctions_function" "data_update_func" {
  name        = "data-update-func-${var.random_suffix}"
  description = "Function posting a new version of the timeseries dataset"
  runtime     = "python310"

  available_memory_mb = 1024
  entry_point         = "update_dataset"
  max_instances       = 1
  timeout             = 60

  source_archive_bucket = google_storage_bucket.data_update_func.name
  source_archive_object = google_storage_bucket_object.data_update_func.name

  labels = {
    owner   = "matkob"
    purpose = "mlops-demo"
    type    = "mock"
  }

  build_environment_variables = {
    GOOGLE_FUNCTION_SOURCE = "data_update.py"
  }

  event_trigger {
    event_type = "providers/cloud.pubsub/eventTypes/topic.publish"
    resource   = google_pubsub_topic.dataset_update_topic.id
  }

  # Coupling function's lifecycle with the code will trigger proper redeployment on code updates
  # This will not be the case otherwise
  lifecycle {
    replace_triggered_by = [
      google_storage_bucket_object.data_update_func.md5hash
    ]
  }

  depends_on = [google_project_service.cloud_functions]
}
