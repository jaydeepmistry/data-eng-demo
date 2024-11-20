import os
from datetime import datetime, timedelta
from typing import Any

import pandas as pd
from airflow.operators.python_operator import (
    PythonOperator,  # pylint: disable=import-error; type: ignore[attr-defined]
)

from airflow import DAG  # type: ignore[attr-defined] # pylint: disable=import-error

default_args: dict[str, Any] = {
    "owner": "airflow",
    "start_date": datetime(2023, 1, 1),
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
    "max_active_runs": 1,  # Limit to one active run
}


def extract_data() -> None:
    # Ensure the directory exists
    os.makedirs("/opt/airflow/dags/data", exist_ok=True)

    # Simulate extracting advertising data from a source
    data: dict[str, list[Any]] = {
        "Date": ["2023-01-01", "2023-01-02", "2023-01-03"],
        "Clicks": [100, 150, 200],
        "Impressions": [1000, 1500, 2000],
    }
    df: pd.DataFrame = pd.DataFrame(data)
    df.to_csv("/opt/airflow/dags/data/advertising.csv", index=False)


def process_data() -> None:
    df: pd.DataFrame = pd.read_csv("/opt/airflow/dags/data/advertising.csv")
    df["CTR"] = df["Clicks"] / df["Impressions"] * 100
    df.to_csv("/opt/airflow/dags/data/processed_advertising.csv", index=False)


with DAG(
    "advertising_dag", default_args=default_args, schedule_interval="@daily", catchup=False
) as dag:
    extract_task: PythonOperator = PythonOperator(
        task_id="extract_data", python_callable=extract_data
    )

    process_task: PythonOperator = PythonOperator(
        task_id="process_data", python_callable=process_data
    )

    extract_task >> process_task
