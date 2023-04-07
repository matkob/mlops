module "data_mock" {
  source = "./modules/data-mock"

  region        = var.region
  random_suffix = var.random_suffix

  trigger_schedule         = "*/10 * * * *"
  order_book_updates_topic = "order-book-${var.random_suffix}"
}

module "dataset" {
  source = "./modules/dataset"

  project_id    = var.project_id
  region        = var.region
  random_suffix = var.random_suffix

  order_book_updates_topic = "order-book-${var.random_suffix}"
}
