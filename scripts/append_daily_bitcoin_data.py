# --- BTC Daily Price Data Extraction, Load to BigQuery ---


# --- IMPORT LIBRARIES ---
import requests 
import pandas as pd
import os
import pandas_gbq
from dotenv import load_dotenv
from datetime import date, datetime, time, timedelta

print("Starting INCREMENTAL Bitcoin data load pipeline...")

# --- LOAD SECRETS & CONFIG ---
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/opt/airflow/keys/bq_service_account.json" # Path to GCP service account key file - airflow

load_dotenv()
API_KEY = os.getenv("GECKO_API_KEY")
GCP_PROJECT_ID = os.getenv("GCP_PROJECT_ID")
destination_table = "btc.raw_coingecko_bitcoin"
COIN_ID = "bitcoin"

url = f"https://api.coingecko.com/api/v3/coins/{COIN_ID}/market_chart"

# Validate secrets
if not API_KEY or not GCP_PROJECT_ID:
    raise ValueError("Error: GECKO_API_KEY or GCP_PROJECT_ID not set.")
print("✅ Secrets loaded successfully.")

# --- GET TODAY'S OPENING DATA ---

#Get today's date as a string (e.g., "2025-11-18")
today_midnight = datetime.combine(date.today(), time.min)
today_str = today_midnight.strftime("%Y-%m-%d") 
print(f"Checking data for date: {today_str}")

# -- we can set a fixed date here: --
# target_date = date(2025, 11, 21)
# today_midnight = datetime.combine(target_date, time.min)
# today_str = target_date.strftime("%Y-%m-%d")
# print(f"Checking data for date: {today_str}")

# This endpoint is designed to get historical data for a specific date.
url = f"https://api.coingecko.com/api/v3/coins/{COIN_ID}/history"

# Set parameters for the API request - for today's opening price
params = {
    "date": today_str, 
    "localization": "false",
    "x_cg_demo_api_key": API_KEY
}

# --- EXTRACT (Get data from API) ---
try:
    print(f"Fetching final price for date: {today_midnight}...")
    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()
    print("Data fetched successfully.")
except requests.exceptions.RequestException as e:
    print(f"Error fetching data from CoinGecko API: {e}")
    exit(1) # Quit the script if we can't get data

# --- TRANSFORM (Parse the new JSON response) ---

# We parse it to get the single, final price.
try:
    price = data['market_data']['current_price']['usd']
except KeyError:
    print(f"Error: Could not find price in API response. JSON was: {data}")
    exit(1)

# Convert to DataFrame
df_to_load = pd.DataFrame({
    'date': [today_midnight],
    'price': [price]
})

print(f"Successfully parsed 1 row: {today_midnight}, ${price}")

# --- LOAD (Append data to BigQuery) ---

# load data to BigQuery
try:
    print(f"Appending 1 row to BigQuery table: {destination_table}...")
    pandas_gbq.to_gbq(
        df_to_load,
        destination_table=destination_table,
        project_id=GCP_PROJECT_ID,
        if_exists='append' 
    )
    print("✅ Pipeline finished successfully. 1 row appended to BigQuery.")
except Exception as e:
    print(f"Error loading data to BigQuery: {e}")
    exit(1)