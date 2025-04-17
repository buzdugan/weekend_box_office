import logging
import os
import re
from datetime import datetime, timedelta

import pandas as pd
import requests
from bs4 import BeautifulSoup

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.google.cloud.operators.bigquery import BigQueryInsertJobOperator


# URL of the BFI Weekend Box Office Figures page with all the years and the current year reports
URL = 'https://www.bfi.org.uk/industry-data-insights/weekend-box-office-figures'
DATA_FOLDER = "/home/airflow/gcs/data" # Mapped default storage location created by Composer in the Cloud Storage bucket associated with the environment
# Change the below to your own settings
PROJECT_ID = "weekend-box-office"
BUCKET = "europe-west1-composer-3-d1522633-bucket" # Default storage location created by Composer in the Cloud Storage bucket associated with the environment
BIGQUERY_DATASET = "uk_movies"
BIGQUERY_TABLE = "weekend_top_15_movies"


# schema definition
SCHEMA = [
    {"name": "report_date", "type": "DATE"},
    {"name": "rank", "type": "INTEGER"},
    {"name": "film", "type": "STRING"},
    {"name": "country_of_origin", "type": "STRING"},
    {"name": "weekend_gross", "type": "INTEGER"},
    {"name": "distributor", "type": "STRING"},
    {"name": "percent_change_on_last_week", "type": "FLOAT"},
    {"name": "weeks_on_release", "type": "INTEGER"},
    {"name": "number_of_cinemas", "type": "INTEGER"},
    {"name": "site_average", "type": "INTEGER"},
    {"name": "total_gross_to_date", "type": "INTEGER"},
]


def get_last_sunday_date():
    # Get current date and look for report for last Sunday
    today = datetime.now().date()
    idx = (today.weekday() + 1) % 7
    last_sunday = today - timedelta(idx)
    last_sunday = last_sunday.strftime("%Y_%m_%d")

    return last_sunday


def get_sunday_date_from_report_title(report_text):
    """Extracts the last date from the report text and formats it as YYYY_MM_DD."""
    # Standardize separators
    report_text = report_text.replace(" to ", " - ")
    
    # Pattern 1: "28 February - 2 March 2025" (different months)
    pattern1 = re.search(r"(\d{1,2})\s*(\w+)\s*-\s*(\d{1,2})\s*(\w+)\s*(\d{4})", report_text)

    # Pattern 2: "7-9 March 2025" or "7 - 9 March 2025" (same month)
    pattern2 = re.search(r"(\d{1,2})\s*-\s*(\d{1,2})\s*(\w+)\s*(\d{4})", report_text)
    
    # Pattern 3: "24-26 January 2025" (no spaces around hyphen)
    pattern3 = re.search(r"(\d{1,2})-(\d{1,2})\s*(\w+)\s*(\d{4})", report_text)
    
    # Pattern 4: "24 December 2024 - 26 January 2025" (different months with years)
    pattern4 = re.search(r"(\d{1,2})\s*(\w+)\s*(\d{4})\s*-\s*(\d{1,2})\s*(\w+)\s*(\d{4})", report_text)
    
    if pattern1:
        end_day, end_month, year = pattern1.group(3), pattern1.group(4), pattern1.group(5)
    elif pattern2:
        end_day, end_month, year = pattern2.group(2), pattern2.group(3), pattern2.group(4)
    elif pattern3:
        end_day, end_month, year = pattern3.group(2), pattern3.group(3), pattern3.group(4)
    elif pattern4:
        end_day, end_month, year = pattern4.group(4), pattern4.group(5), pattern4.group(6)
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


def clean_columns(df, last_sunday):
    # Remove empty columns
    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
    # Add a column with the report date with - instead of _
    df.insert(0, "report_date", last_sunday.replace("_", "-"), True)

    # Convert to lowercase
    columns = [col.lower().replace(" ", "_") for col in df.columns]
    # Change the column with % to percent
    columns = [col.replace("%", "percent") for col in columns]

    # Rename columns
    df.columns = columns

    # Remove empty value substitute - from percent_change_on_last_week
    df['percent_change_on_last_week'] = df['percent_change_on_last_week'].replace("-", None).replace(" - ", None)

    # Change data types
    df['report_date'] = pd.to_datetime(df['report_date'], format='%Y-%m-%d')
    df['rank'] = df['rank'].astype('int')
    df['weekend_gross'] = df['weekend_gross'].astype('int')
    df['percent_change_on_last_week'] = df['percent_change_on_last_week'].astype('float')
    df['weeks_on_release'] = df['weeks_on_release'].astype('int')
    df['number_of_cinemas'] = df['number_of_cinemas'].astype('int')
    df['site_average'] = df['site_average'].astype('int')
    df['total_gross_to_date'] = df['total_gross_to_date'].astype('int')

    return df


def format_to_csv():
    last_sunday = get_last_sunday_date()
    # If last Sunday's report has been downloaded, convert it to parquet
    excel_filename = f"{DATA_FOLDER}/{last_sunday}.xlsx"
    csv_filename = f"{DATA_FOLDER}/{last_sunday}.csv"

    # Check if the file exists as Excel file in the home folder
    if excel_filename:
        # Load the data and keep only the first 15 rows
        df = pd.read_excel(excel_filename, header=1).head(15)
        # Clean the columns
        df = clean_columns(df, last_sunday)
        # Write the data to a csv file
        df.to_csv(csv_filename, index=False)
        print(f"Converted: {excel_filename} to csv")
    else:
        logging.error("Last Sunday report file not found.")


def delete_reports():
    # Delete the reports from the home folder
    last_sunday = get_last_sunday_date()
    excel_filename = f"{DATA_FOLDER}/{last_sunday}.xlsx"
    csv_filename = f"{DATA_FOLDER}/{last_sunday}.csv"

    if os.path.exists(excel_filename):
        os.remove(excel_filename)
        print(f"Deleted: {excel_filename}")
    else:
        logging.error("Excel file not found.")

    if os.path.exists(csv_filename):
        os.remove(csv_filename)
        print(f"Deleted: {csv_filename}")
    else:
        logging.error("CSV file not found.")



last_sunday = get_last_sunday_date()

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
    

    download_last_sunday_report_task = PythonOperator(
        task_id="download_last_sunday_report_task",
        python_callable=download_last_sunday_report,
    )


    format_to_csv_task = PythonOperator(
        task_id = "format_to_csv_task",
        python_callable=format_to_csv,
    )


    gcs_to_bq_task = BigQueryInsertJobOperator(
        task_id="gcs_to_bq_task",
        configuration={
            "load": {
                "sourceUris": [f"gs://{BUCKET}/data/{last_sunday}.csv"],
                "destinationTable": {
                    "projectId": PROJECT_ID,
                    "datasetId": BIGQUERY_DATASET,
                    "tableId": BIGQUERY_TABLE,
                },
                "schema": {"fields": SCHEMA},
                "skipLeadingRows": 1,
                "sourceFormat": "CSV",
                "writeDisposition": "WRITE_APPEND",
                "timePartitioning": {"type": "DAY", "field": "report_date"},
                "clustering": {"fields": ["distributor", "rank", "film"]},
            }
        },
    )

    delete_reports_task = PythonOperator(
        task_id = "delete_reports_task",
        python_callable=delete_reports,
    )


    download_last_sunday_report_task >> format_to_csv_task >> gcs_to_bq_task >> delete_reports_task
