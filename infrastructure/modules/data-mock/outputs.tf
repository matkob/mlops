output "trigger_topic" {
  value = google_pubsub_topic.trigger
}

output "payload_topic" {
  value = google_pubsub_topic.payload
}
