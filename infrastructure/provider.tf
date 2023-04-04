terraform {

  required_providers {

    google = {
      source  = "hashicorp/google"
      version = "4.56.0"
    }

    archive = {
      source  = "hashicorp/archive"
      version = "2.3.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
  zone    = var.zone
}
