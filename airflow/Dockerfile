FROM apache/airflow:3.1.2

USER airflow

RUN pip install --no-cache-dir \
    dbt-bigquery \
    requests \
    pandas \
    pandas-gbq \
    python-dotenv
ac
WORKDIR /opt/airflow