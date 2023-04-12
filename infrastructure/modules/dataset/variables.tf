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
  description = "Region configured for the project"
}

variable "random_suffix" {
  type        = string
  description = "Element randomizing some components' names"
}

variable "order_book_updates_topic" {
  type        = string
  description = "ID of the topic containing live order book updates"
}
