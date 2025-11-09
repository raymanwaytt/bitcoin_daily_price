# Bitcoin Daily Price Analysis Pipeline

This is an end-to-end data pipeline. The project automatically extracts daily Bitcoin price data, loads it into a data warehouse, transforms it for analysis, and visualizes the trend on a live dashboard.

## 🛠️ Modern Data Stack Used

* **Data Warehouse:** Google BigQuery
* **Extraction (EL):** Python (`requests`, `pandas`, `pandas-gbq`)
* **Transformation (T):** dbt Core
* **BI & Visualization:** Looker Studio
* **Version Control:** Git / GitHub

---

## 🚀 The Pipeline Explained

This project follows a modern **ELT (Extract, Load, Transform)** architecture:

### 1. Extract & Load (EL)

A Python script (`coingecko_pipeline.py`) is run to:
* Hit the **CoinGecko API** with a secure API key.
* Fetch the last 90+ days of Bitcoin (BTC) price history.
* Clean and format the JSON response into a `pandas` DataFrame.
* Load this raw data into a BigQuery table named `raw_coingecko_bitcoin` using the `pandas-gbq` library.

### 2. Transform (T)

**dbt (Data Build Tool)** takes over inside the warehouse:
* **`sources.yml`**: The raw `raw_coingecko_bitcoin` table is defined as a `dbt source`.
* **Staging Model (`stg_coingecko_bitcoin.sql`):** This model reads from the source, casts data types (like `price_date`), renames columns, and prepares the data for its final use.

### 3. Business Intelligence (BI)

* **Looker Studio** connects directly to the final, clean `stg_coingecko_bitcoin` table in BigQuery.
* This provides a live, interactive **Time series chart** that visualizes the 90-day price trend of Bitcoin.
**[View the Live Dashboard Here](https://lookerstudio.google.com/reporting/31a8ba69-c53a-4211-90b2-2daa7085b06f)**

## 🔮 Future Improvements

* **Orchestration:** Integrate the pipeline with an orchestrator (like **dbt Cloud** or **Apache Airflow**) to run the entire ELT process automatically every 24 hours.