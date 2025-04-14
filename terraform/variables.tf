variable "credentials" {
  description = "Service Account Credentials"
  default     = "~/.google/credentials/google_credentials.json"
}

# Project specific
variable "project" {
  description = "Your GCP Project ID"
  # Update the below to your project ID
  default = "weekend-box-office"
}

variable "region" {
  description = "Region for GCP resources"
  # Update the below to your desired region https://cloud.google.com/compute/docs/regions-zones
  default     = "europe-west1"
}

variable "location" {
  description = "Project Location "
  # Update the below to your desired location https://cloud.google.com/about/locations
  default     = "europe-west1"
}

variable "bq_dataset_name" {
  description = "BigQuery Dataset Name"
  default     = "uk_movies_test" # FOR TESTING ONLY, update later with final version
}

variable "composer_env_name" {
  description = "Composer Environment Name"
  default     = "composer-3-test" # FOR TESTING ONLY, update later with final version
}

variable "service_account" {
  description = "Service account name and email"
  default     = "weekend-box-office-user@weekend-box-office.iam.gserviceaccount.com"
}
