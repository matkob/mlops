resource "google_storage_bucket" "data_mock" {
  name          = "data-mock-${var.random_suffix}"
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

resource "google_storage_bucket_object" "timeseries_data" {
  name   = "static/order_book.csv"
  source = "${path.root}/data/order_book.csv"
  bucket = google_storage_bucket.data_mock.name
}
