resource "random_id" "suffix" {
  keepers = {
    project_id = var.project_id
  }

  byte_length = 8
}

resource "google_storage_bucket" "datalake" {
  name          = "datalake-${random_id.suffix.hex}"
  location      = var.region
  force_destroy = true

  storage_class = "STANDARD"

  labels = {
    owner   = "matkob"
    purpose = "mlops-demo"
  }

  uniform_bucket_level_access = true
}

resource "null_resource" "timeseries_data_object" {
  triggers = {
    url    = var.timeseries_data_url
    bucket = google_storage_bucket.datalake.url
  }

  provisioner "local-exec" {
    command = join(" | ", [
      "curl ${var.timeseries_data_url}",
      "gunzip -c",
      "gsutil -h \"Content-Type: text/plain; charset=utf-8\" cp - ${google_storage_bucket.datalake.url}/timeseries_data.csv"
    ])
  }
}

output "timeseries_data_object_url" {
  value = "${google_storage_bucket.datalake.url}/timeseries_data.csv"
}
