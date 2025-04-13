variable "credentials" {
  description = "Service Account Credentials"
  default     = "~/.google/credentials/google_credentials.json"
}

variable "project" {
  description = "Your GCP Project ID"
  # Update the below to your project ID
  # default = "weekend-box-office"
  default = "ziritrion-456409"
}

variable "region" {
  description = "Region for GCP resources"
  # Update the below to your desired region https://cloud.google.com/compute/docs/regions-zones
  default     = "europe-west1"
}

variable "location" {
  description = "Project Location "
  # Update the below to your desired location https://cloud.google.com/about/locations
  default     = "EUROPE-WEST1"
}

variable "bq_dataset_name" {
  description = "BigQuery Dataset Name"
  default     = "movies_db"
}

variable "gcs_bucket_name" {
  description = "Storage Bucket Name"
  # Update the below to a unique bucket name
  default     = "weekend-box-office-bucket"
}

variable "gcs_storage_class" {
  description = "Bucket Storage Class"
  default     = "STANDARD"
}

variable "composer_env_name" {
  description = "Composer Environment Name"
  default     = "composer-3"
}