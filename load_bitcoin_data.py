# import libraries
import requests 
import pandas as pd
import os
import pandas_gbq

print("Starting Bitcoin data load pipeline...")

# --- 1. CONFIG & SECURITY ---
API_KEY = os.environ.get('GECKO_API_KEY')
if not API_KEY:
    raise ValueError("Error: GECKO_API_KEY environment variable not set.")

GCP_PROJECT_ID = "silken-apex-477018-d4"
COIN_ID = "bitcoin"
DAYS_OF_DATA = "91"
destination_table = "dbt_bootcamp.raw_coingecko_bitcoin"

# --- 2. EXTRACT (Get data from API) ---
url = f"https://api.coingecko.com/api/v3/coins/{COIN_ID}/market_chart"
params = {
    'vs_currency': 'usd',
    'days': DAYS_OF_DATA,
    'interval': 'daily', 
    'x_cg_demo_api_key': API_KEY
}

print(f"Requesting data from CoinGecko for '{COIN_ID}'...")
response = requests.get(url, params=params)

# --- 3. TRANSFORM & LOAD ---
if response.status_code == 200:
    print("Success! Data received from API.")
    data = response.json()

    # T: selecting just price and date data
    price_data = data['prices']

    # T: changing column name
    df = pd.DataFrame(price_data, columns=['timestamp', 'price'])

    # T: converting date, from milisecond to day_time format
    df['date'] = pd.to_datetime(df['timestamp'], unit='ms')
    final_df = df[['date', 'price']].copy() 
    
    print(f"Loaded {len(final_df)} rows of data.") 
    
    # --- 4. LOAD (Send data to BigQuery) ---
    print(f"Loading data into BigQuery table: {destination_table}...")
    pandas_gbq.to_gbq(
        final_df,
        destination_table=destination_table,
        project_id=GCP_PROJECT_ID,
        if_exists='replace'
    )
    print("✅ Pipeline finished successfully. Data is in BigQuery.")

else:
    # If API call fails, print the error
    print(f"Error: API request failed with status code {response.status_code}")
    print(f"Response: {response.text}")