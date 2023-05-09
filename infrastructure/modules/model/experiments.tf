resource "google_storage_bucket" "experiments" {
  name          = "experimentation-data-${var.random_suffix}"
  location      = var.region
  force_destroy = true

  storage_class = "STANDARD"

  labels = {
    owner   = "matkob"
    purpose = "mlops-demo"
  }

  uniform_bucket_level_access = true

  # Delete anything older than 5 days to minimize the costs
  lifecycle_rule {
    condition {
      age = 5
    }
    action {
      type = "Delete"
    }
  }

  depends_on = [google_project_service.storage]
}