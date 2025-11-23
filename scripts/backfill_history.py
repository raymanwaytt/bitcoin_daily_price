#this script extracts Bitcoin price data from the CoinGecko API for the past 91 days,
#transforms it into a clean DataFrame, and loads it into a BigQuery table.

# import libraries
import requests 
import pandas as pd
import os
from dotenv import load_dotenv
import pandas_gbq

# load environment variables from .env file
load_dotenv()
API_KEY = os.getenv("GECKO_API_KEY") 

# validate environment variables
if not API_KEY:
    raise ValueError("Error: GECKO_API_KEY environment variable not set.")

# set parameters for API request
COIN_ID = "bitcoin"
VS_CURRENCY = "usd"
DAYS = 91  
url = f"https://api.coingecko.com/api/v3/coins/{COIN_ID}/market_chart"
params = {
    "vs_currency": VS_CURRENCY,
    "days": DAYS
}
headers = {"x-cg-api-key": API_KEY}

# make API request
try:
    print("Fetching Bitcoin price data from CoinGecko API...")
    response = requests.get(url, params=params, headers=headers)    

    print("Data fetched successfully.")
except requests.exceptions.RequestException as e:
    print(f"Error fetching data from CoinGecko API: {e}")
    exit(1)

# parse JSON response
data = response.json()


# ----------------- Data Transformation -----------------

# convert price data to DataFrame
prices = pd.DataFrame(data['prices'], columns=['timestamp', 'price'])

# convert timestamp to datetime
prices['date'] = pd.to_datetime(prices['timestamp'], unit='ms') 

# select relevant columns
prices_df = prices[['date', 'price']]

# keep the first 90 rows, which are all clean, closed prices.
prices_df = prices_df.iloc[:-1]

# final columns
prices_df = prices_df[['date', 'price']]

# ----------------- Loading Data to BigQuery -----------------

# setting up parameters to load data to GBQ
GCP_PROJECT_ID = os.getenv("GCP_PROJECT_ID")
destination_table = "btc.raw_coingecko_bitcoin"

# load data to BigQuery
try:
    print("Loading data to BigQuery...")
    pandas_gbq.to_gbq(
        prices_df,
        destination_table=destination_table,
        project_id=GCP_PROJECT_ID,
        if_exists='replace'
    )

    print(f"✅ Data successfully loaded to {destination_table} in project {GCP_PROJECT_ID}.")
except Exception as e:
    print(f"Error loading data to BigQuery: {e}")