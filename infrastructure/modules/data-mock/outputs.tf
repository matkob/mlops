output "bucket" {
  value = google_storage_bucket.data_mock.url
}

output "topic" {
  value = google_pubsub_topic.mocked_data.id
}
