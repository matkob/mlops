resource "google_storage_bucket" "training_data" {
  name          = "training-data-${var.random_suffix}"
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

resource "google_storage_bucket_object" "initial" {
  name   = "order_book.csv"
  source = "${path.root}/data/order_book.csv"
  bucket = google_storage_bucket.training_data.name
}
