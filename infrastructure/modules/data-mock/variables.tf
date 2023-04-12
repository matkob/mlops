variable "region" {
  type        = string
  description = "Region configured for the project"
}

variable "random_suffix" {
  type        = string
  description = "Element randomizing some components' names"
}

variable "trigger_schedule" {
  type        = string
  default     = "*/10 * * * *"
  description = "Cron-like specification for how often mocked data will be published"
}
