variable "project_id" {
  type        = string
  description = "ID of the project"
}

variable "project_number" {
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
