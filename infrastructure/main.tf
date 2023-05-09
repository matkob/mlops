module "data_mock" {
  source = "./modules/data-mock"

  region        = var.region
  random_suffix = var.random_suffix

  trigger_schedule = "*/10 * * * *"
}

module "dataset" {
  source = "./modules/dataset"

  project_id     = var.project_id
  project_number = var.project_number
  region         = var.region
  random_suffix  = var.random_suffix

  order_book_updates_topic = module.data_mock.payload_topic.id

  depends_on = [module.data_mock]
}

module "model" {
  source = "./modules/model"

  project_id     = var.project_id
  project_number = var.project_number
  region         = var.region
  random_suffix  = var.random_suffix

  depends_on = [module.dataset]
}

output "trigger_topic" {
  value = module.data_mock.trigger_topic.id
}

output "payload_topic" {
  value = module.data_mock.payload_topic.id
}
