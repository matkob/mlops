module "data_mock" {
  source = "./modules/data-mock"

  project_id    = var.project_id
  region        = var.region
  zone          = var.zone
  random_suffix = var.random_suffix
}
