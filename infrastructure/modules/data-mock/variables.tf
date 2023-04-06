variable "project_id" {
  type        = string
  default     = "abc123"
  description = "ID of the project"
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
  default     = "568de2a"
  description = "Element randomizing some components' names"
}

variable "trigger_schedule" {
  type        = string
  default     = "*/10 * * * *"
  description = "Cron-like specification for how often mocked data will be published"
}