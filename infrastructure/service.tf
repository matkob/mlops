resource "google_project_service" "cloud_functions" {
  service            = "cloudfunctions.googleapis.com"
  disable_on_destroy = false
}

resource "google_project_service" "vertex_ai" {
  service            = "aiplatform.googleapis.com"
  disable_on_destroy = false
}

resource "google_project_service" "cloud_scheduler" {
  service = "cloudscheduler.googleapis.com"
  disable_on_destroy = false
}
