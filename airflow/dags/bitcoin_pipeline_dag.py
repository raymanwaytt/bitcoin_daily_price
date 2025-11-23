from __future__ import annotations

import pendulum
from airflow.models.dag import DAG
from airflow.providers.standard.operators.bash import BashOperator

DBT_PROJECT_DIR = "/opt/airflow/projects/dbt"
PYTHON_SCRIPT_PATH = "/opt/airflow/projects/scripts/append_daily_bitcoin_data.py"

with DAG(
    dag_id="bitcoin_daily_pipeline",
    schedule="0 5 * * *",
    start_date=pendulum.datetime(2025, 11, 1, tz="UTC"),
    catchup=False,
    tags=["fintech", "production"],
) as dag:

    # Task 1: Run Python script
    extract_and_load = BashOperator(
        task_id="run_python_script",
        bash_command=f"python {PYTHON_SCRIPT_PATH}",
        env={
            "GECKO_API_KEY": "{{ var.value.GECKO_API_KEY }}",
            "GCP_PROJECT_ID": "{{ var.value.GCP_PROJECT_ID }}",
        },
    )

    # Task 2: dbt run
    dbt_run_models = BashOperator(
        task_id="dbt_run_models",
        bash_command=f"dbt run --project-dir {DBT_PROJECT_DIR}",
    )

    # Task 3: dbt test
    dbt_test_models = BashOperator(
        task_id="dbt_test_models",
        bash_command=f"dbt test --project-dir {DBT_PROJECT_DIR}",
    )

    extract_and_load >> dbt_run_models >> dbt_test_models