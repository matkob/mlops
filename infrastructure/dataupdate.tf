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
  source_file = "functions/data_update.py"
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
  runtime     = "python311"

  available_memory_mb = 1024
  trigger_http        = true
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

  depends_on = [google_project_service.cloud_functions]
}

output "data_update_func" {
  value = google_cloudfunctions_function.data_update_func.https_trigger_url
}
