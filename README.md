# British Film Institute - Weekend Box Office Top 15

<p align="center">
  <img src="images\British_Film_Institute_logo.svg">
</p>


This repository is the final project for the Data Engineering Zoomcamp, cohort 2025. 


---
## Index
- [Data Description](#data-description)
- [Problem Description](#problem-description)
- [Project Objective](#project-objective)
- [Technologies](#technologies)
- [Project Details and Implementation](#project-details-and-implementation)
- [Project Replication](#project-replication)
  - [Google Cloud Platform](#google-cloud-platform)
    - [Create a GCP account](#create-a-gcp-account)
    - [Create a GCP project](#create-a-gcp-project)
    - [Create a service account, assign roles, download associated credentials](#create-a-service-account-assign-roles-download-associated-credentials)
    - [GCP APIs](#gcp-apis)
    - [Set up Google Cloud SDK](#set-up-google-cloud-sdk)
  - [Create a VM instance](#create-a-vm-instance)
  - [Set up SSH access to the VM instance](#set-up-ssh-access-to-the-vm-instance)
  - [SSH into the VM](#ssh-into-the-vm)
  - [Install Terraform on the VM](#install-terraform-on-the-vm)
  - [Load the credentials to the VM](#load-the-credentials-to-the-vm)
    - [Google credentials](#google-credentials)
    - [Github private key](#github-private-key)
  - [Clone the repo in the VM](#clone-the-repo-in-the-vm)
  - [Set up Cloud infrastructure](#set-up-cloud-infrastructure)
  - [Cloud Composer](#cloud-composer)
    - [Load the historical data](#load-the-historical-data)
    - [Load the weekly DAG](#load-the-weekly-dag)
    - [Run the weekly DAG](#run-the-weekly-dag)
  - [Set up dbt Cloud](#set-up-dbt-cloud)
  - [Deploy models in dbt Cloud with a Production environment](#deploy-models-in-dbt-cloud-with-a-production-environment)
  - [Create the dashboard](#create-the-dashboard)


## Data Description
The data comes from the British Film Institute (BFI) [Weekend Box Office](https://www.bfi.org.uk/industry-data-insights/weekend-box-office-figures).
Each week the BFI publishes box office figures for the top 15 films released in the UK, all other British releases and newly-released films.<br>
The figures cover box offices grosses in pounds sterling, Friday to Sunday, and show the performance of each film compared to the previous week and its total UK box office gross since release.


## Problem Description
This is a simple project which takes data from the the website provided above and transforms it in order to visualize the performance of movie distributors from 2017 onwards. The dashboards displays the total weekend earnings by week, the distribution of total earnings, the number of weekly top rank category and maximum weekly number of movies.


## Project Objective
The aim of the project is to handle the ingestion, processing and data analysis, including a dashboard for data visualizations, in order to answer several questions about the top distributors of movies released in the UK since 2017.


## Technologies
The project uses the following tools: 
- Cloud: [**Google Cloud Platform**](https://cloud.google.com)
- Infrastructure as code (IaC): [**Terraform**](https://www.terraform.io)
- Data processing - [**Python**](https://www.python.org)
- Workflow orchestration: [**Google Cloud Composer**](https://cloud.google.com/composer?hl=en)
- Data Lake - [**Google Cloud Storage**](https://cloud.google.com/storage)
- Data Warehouse - [**BigQuery**](https://cloud.google.com/bigquery)
- Data transformation: [**Data Build Tool (dbt)**](https://www.getdbt.com)
- Data visualization - [**Looker Studio**](https://lookerstudio.google.com/overview)


## Project Details and Implementation
This project uses Google Cloud Platform, particularly BigQuery and Cloud Composer which comes with its own Cloud Storage.

The Cloud infrastructure is mostly managed with Terraform, except for the VM instance which is created manually and the dbt instances.

Weekly data ingestion is done via an Airflow DAG inside Cloud Composer. The DAG downloads the new report weekly into Cloud Composer default bucket which acts as the Data Lake for the project. 
The data format is relatively complicated: an excel file from which we only select the top 15 rows, clean it and format it to csv file. The DAG creates or appends the data to a BigQuery table partitioned by sunday date (report_date) and clustered on distributor, rank and film.

dbt is used to transform the data for visualization. A view is created in a staging phase with deduplicated data from the the raw BigQuery table where we loaded the csv files and a final table containing the aggregations by distributor alone is materialized in the deployment phase.

The dashboard is a simple Google Looker Studio report with 5 widgets.


## Project Replication
In order to replicate this project you need to follow the steps below.

### Google Cloud Platform
#### Create a GCP account 
If you don't already have one, create a [GCP account](https://console.cloud.google.com/freetrial) with $300 free credit that can be used up to 90 days.

#### Create a GCP project
Once you have the account set up, you will need to create a project.
In the Google Cloud console, go to **Menu ≡ > IAM & Admin > Create a Project**. Name the project `weekend-box-office` then select this project to work on.

#### Create a service account, assign roles, download associated credentials
You will need to create a service account (similar to a user account but for apps and workloads) and download the authentication keys to your computer. 
Go to **IAM & Admin > Service Accounts > Create service account**.
Name the service account `weekend-box-office-user` and leave all the other fields with the default values.

You will be using the same service account for all the steps in the project.

Assign the following roles to the service account:
* `Viewer`: to view most Google Cloud resources.
* `Storage Admin`: to create and manage buckets.
* `Storage Object Admin`: to create and manage objects in the buckets.
* `BigQuery Admin`: to manage BigQuery resources and data.
* `Composer Administrator`: to create, configure, and manage Cloud Composer environments.
* `Composer Worker`: to allow execution of DAGs and tasks within a Cloud Composer environment.
* `Environment and Storage Object Administrator`: to manage both Cloud Composer environments and the storage objects (like DAGs and plugins) used by them.
* `Logs Writer`: to write logs to Cloud Logging from supported services.
* `Service Account User`: to allow principals to act as or use a service account in API calls or other operations.

Now you need to generate the service account credential file. On the `weekend-box-office-user`, click the 3 dots below **Actions**, **Manage keys > Add key > Create new key**, select JSON and create. The file gets automatically downloaded to your computer. Rename it to `google_credentials.json` and store it in `$HOME/.google/credentials/`.

#### GCP APIs
For Terraform to interact with GCP, enable the following APIs for your project:
- [Identity and Access Management (IAM) API](https://console.cloud.google.com/apis/library/iam.googleapis.com)
- [IAM service account credentials API](https://console.cloud.google.com/apis/library/iamcredentials.googleapis.com)
- [Compute Engine API](https://console.developers.google.com/apis/api/compute.googleapis.com) for using VM instances.
- [Cloud Composer API](https://console.cloud.google.com/apis/library/composer.googleapis.com) to be able to create Composer environment.


#### Set up Google Cloud SDK
You need Google Cloud SDK (Software Development Kit) to interact with GCP services and resources.
Download [Google Cloud SDK](https://cloud.google.com/sdk/docs/quickstart) for local setup. Follow the instructions in the link to install the version for your OS and connect to your account and project.

Set the environment variable to point to the auth keys.
   ```bash
   export GOOGLE_APPLICATION_CREDENTIALS="$HOME/.google/credentials/google_credentials.json"

   # Refresh token/session and verify authentication
   gcloud auth application-default login
   ```

Initialise GCP SDK by running `gcloud init` from a terminal. Follow the instructions to select your account and project.
Run `gcloud config list` to check the configurations and ensure you're using the right account and project.


### Create a VM instance
 In the Google Cloud console, go to **Menu ≡ > Compute Engine > VM instances > Create instance**. Follow these steps to generate the instance.
1. Choose any name for your instance.
1. Select the best region and zone that work for you. Make sure you use the same location across all the Google Cloud components.<br>
The other components will be generated with Terraform and you should modify the variables `region` and `location` inside the `variables.tf` file to be the same as the VM region.
1. Select a _E2 series_ instance. A _e2-standard-4_ instance is recommended (4 vCPUs, 16GB RAM)
1. In OS and Storage, change the OS to _Ubuntu_ and leave the default version _Ubuntu 20.04 LTS_. Select at least 30GB of storage.
1. Leave everythig else as default and click on _Create_.


### Set up SSH access to the VM instance
Once created, the instance starts automatically. You can stop and start it again and eventually delete it from the 3 dots menu to the right of the instance name in Google Cloud _VM instances_ dashboard.

1. In a local terminal, check to see that gcloud SDK is configured for the correct account and project. Run `gcloud config list` to list your current config's details.

1. (Optional) If you need to change the account, run
   ```bash
   #  List the available accounts
   gcloud auth list

   # Switch account
   gcloud config set account <your_account_email>
   ```

1. (Optional) If you need to change the project, run
   ```bash
   #  List the available projects
   gcloud projects list

   # Switch project
   gcloud config set project <your_project_id>
   ```

1. (Optional) Check again to see you have the desired configuration `gcloud config list`.

In order to SSH to the VM you need to create a public-private key pair and load or propagate the public key to the VM. 

You can use the course method by running
   ```bash
    ssh-keygen -t rsa -f ~/.ssh/gcp -C <vm_username> -b 2048
   ```
to create the ssh keys called _gcp_ and _gcp.pub_ in the `~/.ssh` folder locally. 
In GCP Console, you need to go into **Compute Engine > Settings > Metadata > SSH Keys > Edit > Add item** and copy paste the contents of the public key.

In VSCode, with the Remote SSH extension, if you run the [command palette](https://code.visualstudio.com/docs/getstarted/userinterface#_command-palette) and look for _Remote-SSH: Connect to Host_, the instance should appear in the list. Select it to connect to it and work remotely.


### SSH into the VM
Navigate to the `~/.ssh` folder and edit the `config` file with `nano config`.
Copy paste the below and edit to match your settings
```
Host <vm_name>
    Hostname <public_ip_address>
    User <vm_username>
    IdentityFile ~/.ssh/gcp
```
Then you can run `ssh <vm_name>` to connect. 
Copy paste `<public_ip_address>` from the VM Console and make sure you change `<public_ip_address>` every time you stop and restart the VM.


### Install Terraform on the VM
The project uses Terraform to create GCP infrastructure, namely a BigQuery dataset and a Composer environment which creates its own Storage Bucket.
Run this code
   ```bash
   # Download and add HashiCorp’s GPG key to verify package authenticity
    curl -fsSL https://apt.releases.hashicorp.com/gpg | sudo apt-key add -

    # Add the official HashiCorp APT repository to your system's sources list
    sudo apt-add-repository "deb [arch=amd64] https://apt.releases.hashicorp.com $(lsb_release -cs) main"

    # Update the package list and install Terraform
    sudo apt-get update && sudo apt-get install terraform
   ```


### Load the credentials to the VM
You will need to upload the `google_credentials.json`, used by the service account to access the GCP resources, and the private key to for your github account to be able to clone the repository on the VM.

#### Google credentials
You need to upload `google_credentials.json` to `~/.google/credentials/` folder on your VM.

On the remote terminal create the folder path `~/.google/credentials/`.
   ```bash
   mkdir .google
   cd .google
   mkdir credentials
   ```
In a local terminal upload the credentials to the VM.
   ```bash
   scp $HOME/.google/credentials/google_credentials.json <vm_name>:~/.google/credentials/google_credentials.json
   ```
where `<vm_name>` is the same one as in the `~/.ssh/config` file.

#### Github private key
You need to upload the private key from the `~/.ssh/` folder called `id_ed25519`. The folder `~/.ssh` is created by default on the VM. From the local terminal run the command
   ```bash
   scp $HOME/.ssh/id_ed25519 <vm_name>:~/.ssh/id_ed25519
   ```
If you happen to have a github private key with a different name, then make sure you upload that one.


### Clone the repo in the VM
In on VM terminal run this code from the `HOME` folder:
```bash
  git clone git@github.com:buzdugan/weekend_box_office.git
```
>***IMPORTANT:*** I recommend that you fork the project and clone your copy to be able to change some variables in the code. If you skip this step, you will need to open the code in VS Code SSH Remote-Host, make the changes there then save them just on the instance without being able to push them to the original repository.


### Set up Cloud infrastructure
The configuration files are in the `terraform` folder:
- `main.tf`: the settings for launching the infrastructure in the cloud
- `variables.tf`: the variables to make the configuration dynamic.
Make sure you use the region and location closest to you, the same ones you used when creating the VM.

Terraform with generate 2 resources: a BigQuery dataset and a Cloud Composer 3 environment.<br>
Cloud Composer will be used to orchestrate the workflow. It is a fully managed workflow orchestration service built on Apache Airflow, designed to automate and manage data pipelines. It integrates seamlessly with GCP suite of data analytics services. Because it’s fully managed, it reduces operational overhead by automating Airflow infrastructure management.

>***IMPORTANT:***: Creating a Composer 3 environment can take 20 minutes or more, so make sure the settings are correct before launching it.

In the `variables.tf` file, you will need to change several variables to customize it to your project: `project`, `region` and `location`.

Use the steps below to generate resources inside the GCP:
1. Navigate to the `terraform` folder.
2. Run `terraform init` to initialize the configuration.
3. Run `terraform plan` to check local changes against the remote state before creating the infrastructure.
4. Run `terraform apply` to apply changes to the infrastructure in the cloud.

Once the resources you've created in the cloud are no longer needed, use `terraform destroy` to remove everything.
 

### Cloud Composer

#### Check packages
Composer 3 images come with [predefined list of installed python packages](https://cloud.google.com/composer/docs/composer-versions#images). So you only need to add whatever is not already installed.

Terraform seems to provide conflicting documentation [here](https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/composer_environment) regarding `pypi_packages`. For Composer 3, it should sit under `sofware_config`, which is where it is in the `main.tf` file. However, when testing the code, the packages failed to get installed, so you once the Composer environment gets created, in the Composer Environments dashboard click on its name and go to _Pypi packages_ in the menu bar.

Check if the packages listed in the `main.tf` file got installed. If any of them is missing, you will need to click _ADD PACKAGE_. Get the package name from the terraform file (no quotes) and the version in _Extras and version 1_ tab (no quotes).

When you click _Save_, the packages will be installed and the environment will be recreated, which unfortunately will take another 20+ minutes.
Check again for packages when the environment is recreated.


#### Load the historical data
The reports on the [Weekend Box Office website](https://www.bfi.org.uk/industry-data-insights/weekend-box-office-figures) don't create a direct connection between the dates and the download links, as the latter are of the structure `https://core-cms.bfi.org.uk/media/<some_random_number>/download`.

Therefore the dates need to be extracted from the text in the website and mapped to the download links. This makes the historical data load more involved.

The dag `data_ingestion_current_year.py` should download the reports from 2025 in task groups in parallel. However, it takes a long time to run, therefore it is infinitely faster and strongly recommended to run the code from the `python_scripts` folder to download the data on the VM, then load it from there to BigQuery. 

Make sure you follow the instructions [here](./python_scripts/README.md) to create a virtual environment, activate it and install the required packages.

Once your virtual environment is set up, from the repo home folder on the VM terminal run
   ```bash
    python3 python_scripts/historic_data_download.py
   ```

The script `historic_data_download.py` should only take a couple of minutes to run and it will generate a csv file with all the data called `../wbo_reports/historical_data.csv`.
You can either check in VS Code or using the code below to see if the data was generated.
   ```bash
    # Navigate to the newly created folder
    cd wbo_reports
    # Check the historical_data.csv was created
    ls
   ```

To load the data to a BigQuery table, you need Google Cloud SDK. Since it's already installed on the local machine, it's best to download the file to the local machine first. Make sure `<some_path_to_local_folder>` already exists before running the code below in the local terminal.
   ```bash
    scp <instance_name>:~/weekend_box_office/wbo_reports/historical_data.csv <some_path_to_local_folder>/historical_data.csv
   ```

Navigate to `<some_path_to_local_folder>` and load the historical data to the BigQuery table via the command line.
   ```bash
  bq load \
  --source_format=CSV \
  --skip_leading_rows=1 \
  --field_delimiter="," \
  --time_partitioning_field=report_date \
  --clustering_fields=distributor,rank,film \
  weekend-box-office:uk_movies.weekend_top_15_movies \
  <some_path_to_local_folder>/historical_data.csv \
  report_date:DATE,rank:INTEGER,film:STRING,country_of_origin:STRING,weekend_gross:INTEGER,distributor:STRING,percent_change_on_last_week:FLOAT,weeks_on_release:INTEGER,number_of_cinemas:INTEGER,site_average:INTEGER,total_gross_to_date:INTEGER
   ```
The code creates the partitioned and clustered table with a predefined schema. Make sure you change the path to match yours.


#### Load the weekly DAG
Composer creates its own bucket where it stores objects such as dags, data, plugins and logs in their respective folders.
In the terraform file, you can specify the bucket yourself, and then link it to the composer environment, but in this case it creates its own bucket. 
Once the environment is created, in the GCP Console, navigate to Composer Environments, and click on your environment.
Here you will open 2 pages by clicking in the top part on:
- `OPEN AIRFLOW UI`
- `OPEN DAGS FOLDER`

The second page shows the bucket contents. You can copy the name of the bucket from here and replace it in the dag `composer\data_ingestion_last_weekend.py` where it says `BUCKET = "europe-west1-composer-3-d1522633-bucket"`.
Save the file and then load it into the dags folder via the GCP Console by going to ***Upload > Upload files***.

#### Run the weekly DAG
Then go to the Airflow UI page and keep refreshing until the dag appears in the list. This can take anywhere between 30 seconds to 2 minutes.

`data_ingestion_last_sunday` is automatically triggered on load, but otherwise it is scheduled to run every Thursday	at 10 am to allow for the report with the data for the previous weekend to be uploaded to the website.
If run from Thursday to Saturday, it should upload in the `data/` folder the data from the previous weekend as excel and csv files, append the csv file to the BigQuery table `weekend-box-office.uk_movies.weekend_top_15_movies` and delete the two files downloaded.
If the dag is run on any other day, it should not upload the data and should log that the report is not yet available.


### Set up dbt Cloud

1. Create a [dbt Cloud account](https://www.getdbt.com/).
1. Create a new project.
   * Name the project `weekend-box-office` and under _Advanced settings_, set `dbt` as the _Project subdirectory_.
   * Select _BigQuery_ as a database connection.
   * Select the settings:
      * Upload a Service Account JSON file > choose the `google_credentials.json` that was created previously.
      * Under _Optional Settings_, make sure that you put your Google Cloud location under _Location_, otherwise it will default to US and dbt won't be able to create tables in the target dataset.
   * Under _Development credentials_, choose `uk_movies_dev` as Dataset. This is where dbt will write your models during development.
      * Test the connection and click on _Continue_ once the connection is tested successfully.

   * In _Setup a repository_, select Github and choose your fork from your user account or you can provide a URL and clone the repo.
1. Once the project has been created, you should be able to click on **Develop > Cloud IDE**.

First you need to install the packages by running `dbt deps` in the bottom prompt.
Then run `dbt run` which will generate 3 datasets in BigQuery:
* `uk_movies_dev.stg_movies`, view of the deduplicated source data from `uk_movies.weekend_top_15_movies`
* `uk_movies_dev.int_movie_performance`, view with more derived columns
* `uk_movies_dev.mart_distributor_performance`, table with data for the dashboard, partitioned by `report_date` and clustered by `distributor` and `top_rank_category` which are used as filters in the dashboard.


### Deploy models in dbt Cloud with a Production environment

1. Click on **Deploy > Environments** on the top left.
1. Click on the _Create environment_ button on the top right.
1. Name the environment `Production` of type _Deployment_. 
1. Choose _BigQuery_ Connection
1. In _Deployment credentials_, choose `production` for _Dataset_ field. This is where dbt will write your models during deployment.
1. Create a new job with these settings:
   * _Deploy_ job
   * Job name `weekly run`
   * Commands `dbt build`
   * Environment `Production`.
   * Click _Generate docs on run_ checkbox to create documentation.
   * Choose _Run on schedule_ checkbox, select _custom cron schedule_ and input  `0 11 * * 4` to run every Thursday at 11 am to allow the weekly DAG run to be successful.
1. Save the job.

You can now trigger the job manually or you may wait until the scheduled trigger to run it. The first time you run it, 3 new datasets will be added to BigQuery in the `production` dataset with the same pattern as in the Development environment.


### Create the dashboard

<p align="center">
  <img src="images\Dashboard.png">
</p>


The dashboard was created with [Google Looker Studio](https://lookerstudio.google.com/overview).
Dashboards in Looker are called _reports_. Reports get data from _data sources_, so you will need to generate a data source first then the report.

1. Generate the data source.
   * Click on the _Create_ button and choose _Data Source_.
   * Click on the _BigQuery_ connector.
   * Choose the Google Cloud project > `production` dataset > `mart_distributor_performance` table > Use report_date as date range dimension. Click on the _Connect_ button at the top.
   * You can choose _None_ for all default aggregations or leave it as such.

1. Generate the report.
   * From table page, click on the _Create Report_ button.

   * Click on _Add control > Date range control_. It defaults to `report_date`. Choose the interval 1 January 2017 to current date to view all the data.
   * Click on _Add control > Drop-down list_
      * Control field `top_rank_category`

   * To create the chart _Number of unique distributors_, click on _Add a chart > Scorecard_. 
      * Primery field Metric CTD `distributor`

   * To create the chart _Total weekend gross across all distributors_, click on _Add a chart > Time series chart_. 
      * Dimension `report_date` 
      * Metric SUM `total_weekend_gross`

   * To create the chart _Distribution of total earnings to date by movie distributor_, click on _Add a chart > Pie chart_.
      * Dimension `distributor` 
      * Metric SUM `total_gross_to_date`

   * To create the chart _Number of weekly top rank category by distributor_, click on _Add a chart > Pivot table_.
      * Row dimension `distributor` 
      * Column dimension `top_rank_category` 
      * Metric AUT `Record Count`

   * To create the chart _Maximum weekly number of movies in top 15 by distributor_, click on _Add a chart > Horizontal bar chart_.
      * Dimension `distributor` 
      * Metric Max `number_of_films`

You should now have a functioning dashboard.


_[Back to the top](https://github.com/buzdugan/weekend_box_office)_
