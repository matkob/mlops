terraform {

  required_providers {
    random = {
      source  = "hashicorp/random"
      version = "3.4.3"
    }

    google = {
      source  = "hashicorp/google"
      version = "4.56.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
  zone    = var.zone
}
