# General setup for the project
terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "5.6.0"
    }
  }
}


provider "google" {
  project     = var.project
  region      = var.region
  credentials = file(var.credentials)
}


# Data Warehouse Dataset
resource "google_bigquery_dataset" "bigquery_dataset" {
  dataset_id = var.bq_dataset_name
  location   = var.location
}


# Composer 3 Environment 
resource "google_composer_environment" "composer3_env" {
  name   = var.composer_env_name
  region = var.region

  config {
    software_config {
      image_version = "composer-3-airflow-2.10.2-build.12"
      pypi_packages = {
        beautifulsoup4  = "==4.9.3"
        openpyxl        = "==3.1.5"
        xlrd            = "==2.0.1"
      }

    }

    node_config {
      service_account  = var.service_account
    }

    environment_size = "ENVIRONMENT_SIZE_SMALL"
  }
}
