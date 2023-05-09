resource "google_artifact_registry_repository" "model_image" {
  location      = var.region
  repository_id = "model"
  format        = "DOCKER"

  description = "Docker repository for images used for training the model"

  docker_config {
    # For the sake of simplicity, in production tags should be immutable
    immutable_tags = false
  }
}

resource "google_artifact_registry_repository_iam_member" "member" {
  project    = google_artifact_registry_repository.model_image.project
  location   = google_artifact_registry_repository.model_image.location
  repository = google_artifact_registry_repository.model_image.name
  role       = "roles/artifactregistry.reader"
  member     = "serviceAccount:service-${var.project_number}@gcp-sa-aiplatform-cc.iam.gserviceaccount.com"
}
