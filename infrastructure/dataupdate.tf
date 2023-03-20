resource "google_project_service" "cloud_functions" {
  service            = "cloudfunctions.googleapis.com"
  disable_on_destroy = false
}

resource "google_storage_bucket" "data_update_func" {
  name          = "data-update-func-${random_id.suffix.hex}"
  location      = var.region
  force_destroy = true

  storage_class = "STANDARD"

  labels = {
    owner   = "matkob"
    purpose = "mlops-demo"
  }

  uniform_bucket_level_access = true
}

resource "google_storage_bucket_object" "data_update_func" {
  name   = "archive.zip"
  bucket = google_storage_bucket.data_update_func.name
  source = "../dataset/archive.zip"
}

resource "google_cloudfunctions_function" "data_update_func" {
  name        = "data-update-func-${random_id.suffix.hex}"
  description = "Function posting a new version of the timeseries dataset"
  runtime     = "python311"

  available_memory_mb = 1024
  trigger_http        = true
  entry_point         = "update_dataset"
  max_instances       = 1
  timeout             = 60

  source_archive_bucket = google_storage_bucket.data_update_func.name
  source_archive_object = google_storage_bucket_object.data_update_func.name

  depends_on = [
    google_project_service.cloud_functions
  ]
}

output "data_update_func" {
  value = google_cloudfunctions_function.data_update_func.https_trigger_url
}
