resource "google_pubsub_topic" "data_mock_trigger" {
  name = "data-mock-trigger-${var.random_suffix}"

  # Minimum duration is 10 min
  message_retention_duration = "610s"

  labels = {
    owner   = "matkob"
    purpose = "mlops-demo"
    type    = "mock"
  }

  depends_on = [google_project_service.pubsub]
}

resource "google_cloud_scheduler_job" "data_mock_trigger_job" {
  name        = "publish-to-${google_pubsub_topic.data_mock_trigger.name}"
  description = "Produces an event triggering dataset update."
  schedule    = var.trigger_schedule

  pubsub_target {
    # Topic name is exprected to be in the full format, so equal to the id
    topic_name = google_pubsub_topic.data_mock_trigger.id
    attributes = {
      source_bucket = google_storage_bucket.data_mock.name
      source_object = google_storage_bucket_object.timeseries_data.name
      period        = "10m"
      sink          = google_pubsub_topic.mocked_data.id
    }
  }

  depends_on = [google_project_service.scheduler, google_project_service.pubsub]
}
