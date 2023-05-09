terraform {

  required_providers {

    google = {
      source  = "hashicorp/google"
      version = "4.63.1"
    }

    archive = {
      source  = "hashicorp/archive"
      version = "2.3.0"
    }
  }

  backend "gcs" {
    bucket = "terraform-state-568de2"
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
  zone    = var.zone
}
