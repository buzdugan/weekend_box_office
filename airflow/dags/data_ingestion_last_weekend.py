import logging
import os
import re
from datetime import datetime, timedelta

import pandas as pd
import requests
from bs4 import BeautifulSoup

from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from airflow.providers.google.cloud.operators.bigquery import BigQueryCreateExternalTableOperator, BigQueryInsertJobOperator

from google.cloud import storage


PROJECT_ID = os.environ.get("GCP_PROJECT_ID")
BUCKET = os.environ.get("GCP_GCS_BUCKET")
# URL of the BFI Weekend Box Office Figures page with all the years and the current year reports
URL = 'https://www.bfi.org.uk/industry-data-insights/weekend-box-office-figures'
HOME_FOLDER = os.environ.get("AIRFLOW_HOME", "/opt/airflow/")
BIGQUERY_DATASET = os.environ.get("BIGQUERY_DATASET", 'movies_data')


def get_last_sunday_date():
    # Get current date and look for report for last Sunday
    today = datetime.now().date()
    idx = (today.weekday() + 1) % 7
    last_sunday = today - timedelta(idx)
    return last_sunday


def get_sunday_date_from_report_title(report_text):
    """Extracts the last date from the report text and formats it as YYYY_MM_DD."""
    # Replace " to " with " – "
    report_text = report_text.replace(" to ", " – ")
    # Pattern 1: "28 February – 2 March 2025 or 28 February to 2 March 2025"
    pattern1 = re.search(r"(\d{1,2})\s*(\w+)\s*–\s*(\d{1,2})\s*(\w+)\s*(\d{4})", report_text)
    # Pattern 2: "7-9 March 2025 or 7 to 9 March 2025"
    pattern2 = re.search(r"(\d{1,2})\s*–\s*(\d{1,2})\s*(\w+)\s*(\d{4})", report_text)

    if pattern1:
        end_day, end_month, year = pattern1.group(3), pattern1.group(4), pattern1.group(5)
    elif pattern2:
        end_day, end_month, year = pattern2.group(2), pattern2.group(3), pattern2.group(4)
    else:
        return None
    
    year = int(year)
    end_day = int(end_day)
    end_month = datetime.strptime(end_month, "%B").month
    
    # Construct the Sunday date
    sunday_date = datetime(year, end_month, end_day).strftime("%Y_%m_%d")
    return sunday_date


def download_last_sunday_report(url, download_folder, last_sunday):
    # Download the reports for last Sunday if it's available in original Excel format
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    links = soup.find_all("a", href=True)
    links = [link for link in links if "Weekend box office report" in link.text]
    # Get the title of the latest weekend box office report
    report_title = links[0].text.strip()
    # Extract the date from the report title
    sunday_date = get_sunday_date_from_report_title(report_title)

    if sunday_date:
        print(f"Last Sunday report date: {sunday_date}")
        # If the date is the same last_sunday, then download the report
        if sunday_date == last_sunday.strftime("%Y_%m_%d"):
            report_url = links[0]["href"]
            filename = f"{download_folder}/{sunday_date}.xlsx"
            
            # Download the report in original Excel format
            report_response = requests.get(report_url)
            with open(filename, "wb") as file:
                file.write(report_response.content)
                print(f"Downloaded last Sunday report: {filename}")
        else:
            print(f"Last Sunday report is not available yet.")
            return
    else:
        print("The latest report date could not be extracted.")
        return 


def format_to_parquet(download_folder, last_sunday):
    # If last Sunday's report has been downloaded, convert it to parquet 
    filename = f"{download_folder}/{last_sunday}.xlsx"

    # Check if the file exists as Excel file in the home folder
    if filename:
        # Load the data and keep only the first 15 rows
        df = pd.read_excel(filename, header=1).head(15)
        # Remove empty columns
        df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
        # Add a column with the report date
        df.insert(0, "report_date", last_sunday, True)

       # Write the data to a parquet file
        df.to_parquet(filename.replace(".xlsx", ".parquet").replace(".xls", ".parquet"))
        print(f"Converted: {filename} to parquet") 
    else:
        logging.error("Last Sunday report file not found.")


def upload_to_gcs(download_folder, bucket, last_sunday):
    source_file = f"{download_folder}/{last_sunday}.parquet"
    target_file = f"raw/{last_sunday}.parquet"

    # If the file exists as parquet file in the home folder, upload it to GCS
    if os.path.exists(source_file):
        client = storage.Client()
        bucket = client.bucket(bucket)

        blob = bucket.blob(target_file)
        blob.upload_from_filename(source_file)
    else:
        logging.error("Last Sunday report parquet file not found in home folder.")


default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "retries": 1,
}

with DAG(
    dag_id="data_ingestion_last_sunday",
    schedule_interval="0 10 * * 4", # every Thursday at 10:00 to allow time for the report to be available
    start_date=datetime(2025, 4, 1),
    default_args=default_args,
    catchup=False,
    max_active_runs=1,
    tags=['dtc-de'],
) as dag:

    last_sunday = get_last_sunday_date()

    download_report_task = PythonOperator(
        task_id="download_report_task",
        python_callable=download_last_sunday_report,
        op_kwargs={
            "url": URL,
            "download_folder": HOME_FOLDER,
            "last_sunday": last_sunday,
        },
    )

    format_to_parquet_task = PythonOperator(
        task_id = "format_to_parquet_task",
        python_callable=format_to_parquet,
        op_kwargs={
            "download_folder": HOME_FOLDER,
            "last_sunday": last_sunday,
        },
    )

    local_to_gcs_task = PythonOperator(
        task_id="local_to_gcs_task",
        python_callable=upload_to_gcs,
        op_kwargs={
            "download_folder": HOME_FOLDER,
            "bucket": BUCKET,
            "last_sunday": last_sunday,
        },
    )

    gcs_2_bq_ext_task = BigQueryCreateExternalTableOperator(
        task_id=f"bq_external_table_task",
        table_resource={
            "tableReference": {
                "projectId": PROJECT_ID,
                "datasetId": BIGQUERY_DATASET,
                "tableId": "external_table_{LAST_SUNDAY}",
            },
            "externalDataConfiguration": {
                "sourceFormat": "PARQUET",
                "sourceUris": [f"gs://{BUCKET}/raw/{last_sunday}.parquet"],
            },
        },
    )

    remove_files_task = BashOperator(
        task_id="remove_files_task",
        bash_command=f"rm {HOME_FOLDER}/{last_sunday}.xlsx {HOME_FOLDER}/{last_sunday}.parquet"
    )

    download_report_task >> format_to_parquet_task >> local_to_gcs_task >> gcs_2_bq_ext_task  >> remove_files_task