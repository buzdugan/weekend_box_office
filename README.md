# British Film Institute - Weekend Box Office Top 15

<p align="center">
  <img src="images\British_Film_Institute_logo.svg">
</p>


This repository is the final project for the Data Engineering Zoomcamp, cohort 2025.


## Data Description

The data comes from the British Film Institute (BFI) [Weekend Box Office](https://www.bfi.org.uk/).
Each week the BFI publishes box office figures for the top 15 films released in the UK, all other British releases and newly-released films.<br>
The figures cover box offices grosses in pounds sterling, Friday to Sunday, and show the performance of each film compared to the previous week and its total UK box office gross since release.

## Problem Description



## Project Objective

The aim of the project is to develop a <code>DATA ARCHITECTURE</code> to handle the ingestion, processing and data analysis, including a dashboard for data visualizations, in order to answer several questions about the top films released in the UK since 2017.



## Technologies

The project uses the following tools: 
- Cloud: [**Google Cloud Platform**](https://cloud.google.com)
- Infrastructure as code (IaC): [**Terraform**](https://www.terraform.io)
- Containerization - [**Docker**](https://www.docker.com), [**Docker Compose**](https://docs.docker.com/compose/)
- Data processing - [**Python**](https://www.python.org)
- Workflow orchestration: [**Airflow**](https://airflow.apache.org)
- Data Lake - [**Google Cloud Storage**](https://cloud.google.com/storage)
- Data Warehouse - [**BigQuery**](https://cloud.google.com/bigquery)
- Data transformation: [**Data Build Tool (dbt)**](https://www.getdbt.com)
- Data visualization - [**Data Studio**](https://datastudio.google.com/overview)


## Project architecture
Image with the flow


## Project Replication

In order to replicate this project you need to follow the steps below.

### Create a GCP account 
If you don't already have one, create a [GCP account](https://console.cloud.google.com/freetrial) with $300 free credit that can be used up to 90 days.

### Create a GCP project
Once you have the account set up, you will need to create a project.
In the Google Cloud console, go to **Menu ≡ > IAM & Admin > Create a Project**. Name the project `weekend-box-office` then select this project to work on.

### Create a service account, assign roles, download associated credentials
You will need to create a service account (similar to a user account but for apps and workloads) and download the authentication keys to your computer. 
Go to **IAM & Admin > Service Accounts > Create service account**.
Name the service account `weekend-box-office-user` and leave all the other fields with the default values.

Assign the following roles to the service account:
* `Viewer`: to view most Google Cloud resources.
* `Storage Admin`: to create and manage buckets.
* `Storage Object Admin`: to create and manage objects in the buckets.
* `BigQuery Admin`: to manage BigQuery resources and data.

Now you need to generate the service account credential file. On the `weekend-box-office-user`, click the 3 dots below **Actions**, **Manage keys > Add key > Create new key**, select JSON and create. The file gets automatically downloaded to your computer. Rename it to `google_credentials.json` and store it in `$HOME/.google/credentials/`.


Enable these APIs for your project:
- [Identity and Access Management (IAM) API](https://console.cloud.google.com/apis/library/iam.googleapis.com)
- [IAM service account credentials API](https://console.cloud.google.com/apis/library/iamcredentials.googleapis.com)
- [Compute Engine API](https://console.developers.google.com/apis/api/compute.googleapis.com) for using VM instances



### Setup Google Cloud SDK
You need Google Cloud SDK (Software Development Kit) to interact with GCP services and resources.
Download [Google Cloud SDK](https://cloud.google.com/sdk/docs/quickstart) for local setup. Follow the instructions in the link to install the version for your OS and connect to your account and project.

Set the environment variable to point to the auth keys.
   ```shell
   export GOOGLE_APPLICATION_CREDENTIALS="$HOME/.google/credentials/google_credentials.json"

   # Refresh token/session and verify authentication
   gcloud auth application-default login
```

Initialise GCP SDK by running `gcloud init` from a terminal. Follow the instructions to select your account and project.
Run `gcloud config list` to check the configurations and ensure you're using the right account and project.


### Terraform
The project uses Terraform to create GCP Infrastructure.
Follow the instructions [here](https://www.terraform.io/downloads) to install Terraform client.


The configuration files are in the `terraform` folder:
- `main.tf`: the settings for launching the infrastructure in the cloud
- `variables.tf`: the variables to make the configuration dynamic.
Make sure you use the region and 

Use the steps below to generate resources inside the GCP:
1. Navigate to the `terraform` folder.
2. Run `terraform init` to initialize the configuration.
3. Run `terraform plan` to check local changes against the remote state before creating the infrastructure.
4. Run `terraform apply` to apply changes to the infrastructure in the cloud.

Once the resources you've created in the cloud are no longer needed, use `terraform destroy` to remove everything.
