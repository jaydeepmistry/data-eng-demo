import os
from datetime import datetime, timedelta
from typing import Any, Dict

import pandas as pd
from airflow.operators.python_operator import PythonOperator  # type: ignore[attr-defined]

from airflow import DAG  # type: ignore[attr-defined]

default_args: Dict[str, Any] = {
    "owner": "airflow",
    "start_date": datetime(2023, 1, 1),
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
    "max_active_runs": 1,  # Limit to one active run
}


def extract_data(**kwargs: Dict[str, Any]) -> None:
    # Log the execution date
    execution_date = kwargs["execution_date"]
    print(f"Running for execution date: {execution_date}")

    # Ensure the directory exists
    os.makedirs("/opt/airflow/dags/data", exist_ok=True)

    # Simulate extracting advertising data from a source
    data: Dict[str, list[Any]] = {
        "Date": ["2023-01-01", "2023-01-02", "2023-01-03"],
        "Clicks": [100, 150, 200],
        "Impressions": [1000, 1500, 2000],
    }
    df: pd.DataFrame = pd.DataFrame(data)
    df.to_csv("/opt/airflow/dags/data/advertising.csv", index=False)


def process_data(**kwargs: Dict[str, Any]) -> None:
    # Log the execution date
    execution_date = kwargs["execution_date"]
    print(f"Running for execution date: {execution_date}")

    df: pd.DataFrame = pd.read_csv("/opt/airflow/dags/data/advertising.csv")
    df["CTR"] = df["Clicks"] / df["Impressions"] * 100
    df.to_csv("/opt/airflow/dags/data/processed_advertising.csv", index=False)


with DAG(
    "advertising_dag", default_args=default_args, schedule_interval="@daily", catchup=False
) as dag:
    extract_task: PythonOperator = PythonOperator(
        task_id="extract_data", python_callable=extract_data, provide_context=True
    )

    process_task: PythonOperator = PythonOperator(
        task_id="process_data", python_callable=process_data, provide_context=True
    )

    extract_task >> process_task
