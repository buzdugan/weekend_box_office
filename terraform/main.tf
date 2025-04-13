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


# Data Lake Bucket
resource "google_storage_bucket" "gcs_bucket" {
  name          = var.gcs_bucket_name
  location      = var.location
  force_destroy = true


  lifecycle_rule {
    condition {
      age = 1
    }
    action {
      type = "AbortIncompleteMultipartUpload"
    }
  }
}


# Data Warehouse Dataset
resource "google_bigquery_dataset" "bigquery_dataset" {
  dataset_id = var.bq_dataset_name
  location   = var.location
}


# # Composer 3 Environment 
# resource "google_composer_environment" "composer3_env" {
#   name   = var.composer_env_name
#   region = var.region

#   config {
#     software_config {
#       image_version = "composer-3-airflow-2.10.2-build.12"
#       pypi_packages = {
#         beautifulsoup4  = "==4.9.3"
#         requests        = "==2.32.3"
#         openpyxl        = "==3.1.5"
#         xlrd            = "==2.0.1"
#         pandas          = "==2.2.3"
#       }
#     }

#     node_config {
#       service_account  = var.service_account
#     }

#     # Small Composer resources
#     workloads_config {
#       scheduler {
#         cpu = 0.5
#         memory_gb = 2
#         storage_gb = 1
#       }
#     }
#   }
# }
