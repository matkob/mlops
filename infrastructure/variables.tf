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

variable "timeseries_data_url" {
  type        = string
  default     = "https://datasets.tardis.dev/v1/binance/book_snapshot_5/2023/03/01/BTCUSDT.csv.gz"
  description = "URL of timeseries data used as source of data in this example project"
}
