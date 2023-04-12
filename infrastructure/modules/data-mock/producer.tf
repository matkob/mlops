resource "google_pubsub_schema" "order_book" {
  name       = "order-book-${var.random_suffix}"
  type       = "PROTOCOL_BUFFER"
  definition = file("${path.root}/schema/order_book.proto")

  depends_on = [google_project_service.pubsub]
}

resource "google_pubsub_topic" "mocked_data" {
  name = "order-book-${var.random_suffix}"

  # Minimum duration is 10 min
  message_retention_duration = "600s"

  schema_settings {
    schema   = google_pubsub_schema.order_book.id
    encoding = "JSON"
  }

  labels = {
    owner   = "matkob"
    purpose = "mlops-demo"
    type    = "mock"
  }
}
