import os
from datetime import datetime, timedelta
from typing import Any, Dict

import pandas as pd
import requests
from airflow.operators.python_operator import PythonOperator  # type: ignore[attr-defined]

from airflow import DAG  # type: ignore[attr-defined]

default_args: Dict[str, Any] = {
    "owner": "airflow",
    "start_date": datetime(2023, 1, 1),
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
    "max_active_runs": 1,  # Limit to one active run
}


def download_csv_from_url(**kwargs: Dict[str, Any]) -> None:
    url = "https://github.com/WittmannF/imdb-tv-ratings/raw/refs/heads/master/data/top-250-movie-ratings.csv"
    response = requests.get(url)
    if response.status_code == 200:
        os.makedirs("/opt/airflow/dags/data", exist_ok=True)
        file_path = "/opt/airflow/dags/data/top-250-movie-ratings.csv"
        with open(file_path, "wb") as f:
            f.write(response.content)
        print(f"Downloaded file to {file_path}")
    else:
        raise Exception(f"Failed to download file from {url}, status code: {response.status_code}")


def extract_data(**kwargs: Dict[str, Any]) -> None:
    # Log the execution date
    execution_date = kwargs["execution_date"]
    print(f"Running for execution date: {execution_date}")

    # Read the downloaded CSV file
    file_path = "/opt/airflow/dags/data/top-250-movie-ratings.csv"
    df: pd.DataFrame = pd.read_csv(file_path)

    # Add the 'Code' column header to the first column
    df.rename(columns={df.columns[0]: "Code"}, inplace=True)

    # Remove commas from 'Rating Count' column
    df["Rating Count"] = df["Rating Count"].str.replace(",", "").astype(int)

    # Save the cleaned CSV file
    cleaned_file_path = "/opt/airflow/dags/data/top-250-movie-ratings-cleaned.csv"
    df.to_csv(cleaned_file_path, index=False)
    print(f"Cleaned data saved to {cleaned_file_path}")


def process_data(**kwargs: Dict[str, Any]) -> None:
    # Log the execution date
    execution_date = kwargs["execution_date"]
    print(f"Running for execution date: {execution_date}")

    # Read the cleaned CSV file
    cleaned_file_path = "/opt/airflow/dags/data/top-250-movie-ratings-cleaned.csv"
    df: pd.DataFrame = pd.read_csv(cleaned_file_path)

    # Calculate statistics
    avg_rating = df["Rating"].mean()
    avg_rating_count = df["Rating Count"].mean()

    # Save statistics to CSV
    stats_df = pd.DataFrame(
        {
            "Metric": ["Average Rating", "Average Rating Count"],
            "Value": [avg_rating, avg_rating_count],
        }
    )
    stats_file_path = "/opt/airflow/dags/data/statistics.csv"
    stats_df.to_csv(stats_file_path, index=False)
    print(f"Statistics saved to {stats_file_path}")


def process_data_per_year(**kwargs: Dict[str, Any]) -> None:
    # Log the execution date
    execution_date = kwargs["execution_date"]
    print(f"Running for execution date: {execution_date}")

    # Read the cleaned CSV file
    cleaned_file_path = "/opt/airflow/dags/data/top-250-movie-ratings-cleaned.csv"
    df: pd.DataFrame = pd.read_csv(cleaned_file_path)

    # Calculate statistics per year
    stats_per_year = (
        df.groupby("Year").agg({"Rating": "mean", "Rating Count": "mean"}).reset_index()
    )

    # Save statistics to CSV
    stats_per_year_file_path = "/opt/airflow/dags/data/statistics_per_year.csv"
    stats_per_year.to_csv(stats_per_year_file_path, index=False)
    print(f"Statistics per year saved to {stats_per_year_file_path}")


with DAG(
    "advertising_dag", default_args=default_args, schedule_interval="@daily", catchup=False
) as dag:
    download_csv_task: PythonOperator = PythonOperator(
        task_id="download_csv", python_callable=download_csv_from_url, provide_context=True
    )

    extract_task: PythonOperator = PythonOperator(
        task_id="extract_data", python_callable=extract_data, provide_context=True
    )

    process_task: PythonOperator = PythonOperator(
        task_id="process_data", python_callable=process_data, provide_context=True
    )

    process_task_per_year: PythonOperator = PythonOperator(
        task_id="process_data_per_year", python_callable=process_data_per_year, provide_context=True
    )

    download_csv_task >> extract_task
    extract_task >> [process_task, process_task_per_year]  # Run both tasks in parallel
