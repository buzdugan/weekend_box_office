import logging
import os
import re
from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator


PROJECT_ID = os.environ.get("GCP_PROJECT_ID")
BUCKET = os.environ.get("GCP_GCS_BUCKET")
# URL of the BFI Weekend Box Office Figures page with all the years and the current year reports
URL = 'https://www.bfi.org.uk/industry-data-insights/weekend-box-office-figures'
HOME_FOLDER = os.environ.get("AIRFLOW_HOME", "/opt/airflow/")
BIGQUERY_DATASET = os.environ.get("BIGQUERY_DATASET", 'movies_data')

logging.info("This is a log message")
logging.info("PROJECT_ID:", PROJECT_ID)


def get_last_sunday_date():
    # Get current date and look for report for last Sunday
    today = datetime.now().date()
    idx = (today.weekday() + 1) % 7
    last_sunday = today - timedelta(idx)
    return last_sunday


def test_function(url, download_folder):
    last_sunday = get_last_sunday_date()

    print(url)
    print(download_folder)
    print(last_sunday)


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

    test_function_task = PythonOperator(
        task_id="test_function_task",
        python_callable=test_function,
        op_kwargs={
            "url": URL,
            "download_folder": HOME_FOLDER,
        },
    )


    test_function_task