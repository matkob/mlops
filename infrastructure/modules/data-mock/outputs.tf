output "trigger_topic" {
  value = google_pubsub_topic.data_mock_trigger
}

output "payload_topic" {
  value = google_pubsub_topic.mocked_data
}
