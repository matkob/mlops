resource "google_pubsub_schema" "order_book" {
  name       = "order-book-${var.random_suffix}"
  type       = "PROTOCOL_BUFFER"
  definition = file("${path.root}/schema/order_book.proto")

  depends_on = [google_project_service.pubsub]
}

resource "google_pubsub_topic" "trigger" {
  name = "data-mock-trigger-${var.random_suffix}"

  # Minimum duration is 10 min
  message_retention_duration = "600s"

  labels = {
    owner   = "matkob"
    purpose = "mlops-demo"
    type    = "mock"
  }

  depends_on = [google_project_service.pubsub]
}

resource "google_pubsub_topic" "payload" {
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

resource "google_cloud_scheduler_job" "trigger" {
  name        = "publish-data-mock-trigger"
  description = "Produces an event triggering dataset update."
  schedule    = var.trigger_schedule

  pubsub_target {
    # Topic name is exprected to be in the full format, so equal to the id
    topic_name = google_pubsub_topic.trigger.id
    attributes = {
      schedule = var.trigger_schedule
    }
  }

  depends_on = [google_project_service.scheduler]
}
