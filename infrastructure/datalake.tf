resource "google_storage_bucket" "datalake" {
  name          = "datalake-${var.random_suffix}"
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
  name   = "order_book.csv"
  source = "data/order_book.csv"
  bucket = google_storage_bucket.datalake.name
}

output "timeseries_data_object_url" {
  value = google_storage_bucket_object.timeseries_data.media_link
}
