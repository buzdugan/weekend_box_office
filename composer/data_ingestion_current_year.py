import re
from datetime import datetime

import pandas as pd
import requests
from bs4 import BeautifulSoup

from airflow.decorators import task
from airflow.models.dag import DAG
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


def extract_file_links_and_names():
    response = requests.get(URL)
    soup = BeautifulSoup(response.text, "html.parser")
    links = soup.find_all("a", href=True)
    links = [link for link in links if "Weekend box office report" in link.text]

    files_to_process = []
    for link in links:
        report_title = link.text.strip()
        report_url = link["href"]
        sunday_date = get_sunday_date_from_report_title(report_title)
        if sunday_date:
            files_to_process.append({
                "url": report_url,
                "filename": sunday_date
            })
            print(f"Added to list Date: {sunday_date}, URL: {report_url}")

    return files_to_process


def download_file(file_info):
    # Download the report in the original Excel format
    url = file_info["url"]
    filename = f"{DATA_FOLDER}/{file_info['filename']}.xlsx"
    response = requests.get(url)
    with open(filename, "wb") as f:
        f.write(response.content)
    return file_info['filename']


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
    df['percent_change_on_last_week'] = df['percent_change_on_last_week'].replace("-", None)

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


def convert_xlsx_to_csv(filename):
    excel_filename = f"{DATA_FOLDER}/{filename}.xlsx"
    csv_filename = f"{DATA_FOLDER}/{filename}.csv"

    df = pd.read_excel(excel_filename, header=1).head(15)
    df = clean_columns(df, filename)
    df.to_csv(csv_filename, index=False)
    return filename  # pass it to BQ


def generate_bq_config(filename):
    return {
        "load": {
            "sourceUris": [f"gs://{BUCKET}/data/{filename}.csv"],
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
            "clustering": {"fields": ["rank", "distributor", "film"]},
        }
    }



default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "retries": 1,
}

with DAG(
    dag_id="parallel_report_processing",
    schedule_interval=None,
    catchup=False,
    max_active_runs=1,
    tags=['dez-project'],
) as dag:

    @task
    def get_files():
        return extract_file_links_and_names()

    @task
    def download(file_info):
        return download_file(file_info)

    @task
    def to_csv(filename):
        return convert_xlsx_to_csv(filename)

    @task
    def bq_config(filename):
        return generate_bq_config(filename)

    files = get_files()
    downloaded = download.expand(file_info=files)
    csv_files = to_csv.expand(filename=downloaded)
    bq_configs = bq_config.expand(filename=csv_files)

    bq_uploads = BigQueryInsertJobOperator.partial(
        task_id="upload_to_bq",
    ).expand(configuration=bq_configs)

    files >> downloaded >> csv_files >> bq_configs >> bq_uploads


