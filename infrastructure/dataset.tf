resource "google_storage_bucket" "dataset" {
  name          = "dataset-${var.random_suffix}"
  location      = var.region
  force_destroy = true

  storage_class = "STANDARD"

  # This bucket's size will increase over time, lifecycle prevents it from swelling too much
  lifecycle_rule {
    condition {
      age = 1
    }
    action {
      type = "Delete"
    }
  }

  labels = {
    owner   = "matkob"
    purpose = "mlops-demo"
  }

  uniform_bucket_level_access = true
}

resource "google_vertex_ai_dataset" "dataset" {
  display_name        = "Dummy Timeseries Dataset"
  metadata_schema_uri = "gs://google-cloud-aiplatform/schema/dataset/metadata/tabular_1.0.0.yaml"

  labels = {
    owner   = "matkob"
    purpose = "mlops-demo"
  }

  depends_on = [google_project_service.vertex_ai]
}
