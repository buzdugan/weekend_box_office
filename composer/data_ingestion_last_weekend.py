import logging
from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.empty import EmptyOperator
from airflow.operators.python import PythonOperator


# URL of the BFI Weekend Box Office Figures page with all the years and the current year reports
URL = 'https://www.bfi.org.uk/industry-data-insights/weekend-box-office-figures'
PROJECT_ID = "weekend-box-office"
BUCKET = "weekend-box-office-bucket"
BIGQUERY_DATASET = "movies_data"


def get_last_sunday_date():
    # Get current date and look for report for last Sunday
    today = datetime.now().date()
    idx = (today.weekday() + 1) % 7
    last_sunday = today - timedelta(idx)
    last_sunday = last_sunday.strftime('%Y-%m-%d')
    return last_sunday


def test_function():
    last_sunday = get_last_sunday_date()
    
    print("Printing: This is a print message")
    logging.info("Logging: This is a log message")
    print("Printing last_sunday:", last_sunday)
    formatted_message = f"Logging last_sunday: {last_sunday}"
    logging.info(formatted_message)


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

    test_function_task = PythonOperator(
        task_id="test_function_task",
        python_callable=test_function,
    )


    start_task >> test_function_task >> end_task