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
  # credentials = file(var.credentials)
  project     = var.project
  region      = var.region
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
