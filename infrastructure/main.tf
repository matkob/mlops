module "data_mock" {
  source = "./modules/data-mock"

  region        = var.region
  random_suffix = var.random_suffix

  trigger_schedule         = "*/10 * * * *"
}

module "dataset" {
  source = "./modules/dataset"

  project_id    = var.project_id
  region        = var.region
  random_suffix = var.random_suffix

  order_book_updates_topic = module.data_mock.topic.id

  depends_on = [module.data_mock]
}
