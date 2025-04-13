import logging
import re
from datetime import datetime, timedelta

import requests
from bs4 import BeautifulSoup

from airflow import DAG
from airflow.operators.empty import EmptyOperator
from airflow.operators.python import PythonOperator


# URL of the BFI Weekend Box Office Figures page with all the years and the current year reports
URL = 'https://www.bfi.org.uk/industry-data-insights/weekend-box-office-figures'
PROJECT_ID = "weekend-box-office"
BUCKET = "weekend-box-office-bucket"
BIGQUERY_DATASET = "movies_data"
DATA_FOLDER = "/home/airflow/gcs/data" # Default storage location created by Composer in the Cloud Storage bucket associated with the environment


def get_last_sunday_date():
    # Get current date and look for report for last Sunday
    today = datetime.now().date()
    idx = (today.weekday() + 1) % 7
    last_sunday = today - timedelta(idx)
    last_sunday = last_sunday.strftime("%Y_%m_%d")

    last_sunday = "2025_04_06"  # For testing purposes, set a fixed date

    return last_sunday


def get_sunday_date_from_report_title(report_text):
    "Extracts the last date from the report text and formats it as YYYY_MM_DD."
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


def download_last_sunday_report():
    # Download the reports for last Sunday if it's available in original Excel format
    response = requests.get(URL)
    soup = BeautifulSoup(response.text, "html.parser")
    links = soup.find_all("a", href=True)
    links = [link for link in links if "Weekend box office report" in link.text]
    
    # Get the title of the latest weekend box office report
    report_title = links[0].text.strip()
    print(f"Latest report title: {report_title}")

    # Extract the date from the report title
    sunday_date = get_sunday_date_from_report_title(report_title)
    print(f"Extracted Sunday date: {sunday_date}")
    last_sunday = get_last_sunday_date()
    if sunday_date:
        print(f"Last Sunday report date: {sunday_date}")
        # If the date is the same last_sunday, then download the report
        if sunday_date == last_sunday:
            report_url = links[0]["href"]
            filename = f"{DATA_FOLDER}/{sunday_date}.xlsx"
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
    tags=['dez-project'],
) as dag:
    
    start_task = EmptyOperator(task_id="start_task")
    end_task = EmptyOperator(task_id="end_task")

    download_last_sunday_report_task = PythonOperator(
        task_id="download_last_sunday_report_task",
        python_callable=download_last_sunday_report,
    )


    # start_task >> test_logging_task >> download_last_sunday_report_task >> end_task
    start_task >> download_last_sunday_report_task >> end_task








