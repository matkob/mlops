variable "project_id" {
  type        = string
  description = "ID of the project"
}

variable "project_number" {
  # This can be fetched by running 
  # `gcloud projects describe mlops-383318 --format json | jq -r '.projectNumber'`
  # Kept as variable to prevent unnecessary IAM roles replacement on each terraform run
  type        = string
  description = "Number of the project, one of the project's metadata"
}

variable "region" {
  type        = string
  default     = "europe-west1"
  description = "Region configured for the project"
}

variable "zone" {
  type        = string
  default     = "europe-west1-b"
  description = "Zone configured for the project"
}

variable "random_suffix" {
  type        = string
  default     = "568de2"
  description = "Element randomizing some components' names"
}
