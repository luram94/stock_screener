import logging
import os
import json
import pandas as pd
from finvizfinance.screener.overview import Overview
import gspread
from gspread_dataframe import set_with_dataframe
from oauth2client.service_account import ServiceAccountCredentials

# ------------------- Logging Setup -------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
log = logging.getLogger()

log.info("Starting daily stock screener script...")

# ------------------- Data Collection -------------------
log.info("Applying filters and collecting data from Finviz")

base_filters = {'Sales growthqtr over qtr': 'Over 20%'}
highlow_options = ['0-10% below High', 'New High']

all_data = []

for option in highlow_options:
    log.info(f"Filtering for 52-Week High/Low: {option}")
    filters_dict = base_filters.copy()
    filters_dict['52-Week High/Low'] = option

    try:
        foverview = Overview()
        foverview.set_filter(filters_dict=filters_dict)
        df = foverview.screener_view()
        df = df[df['Market Cap'] >= 1e9]
        all_data.append(df)
        log.info(f"Retrieved {len(df)} records for: {option}")
    except Exception as e:
        log.error(f"Failed for filter option '{option}': {e}")

# ------------------- Data Cleaning -------------------
log.info("Merging and cleaning data")
df = pd.concat(all_data)
df = df.drop_duplicates(subset='Ticker').reset_index(drop=True)
df = df.sort_values(by="Market Cap", ascending=False)

# Format columns
df['Market Cap'] = df['Market Cap'] / 1e9
df['Market Cap'] = df['Market Cap'].round(2).astype(str) + 'B'
df['Change'] = (df['Change'] * 100).round(2).astype(str) + '%'

log.info(f"Final dataset contains {len(df)} unique tickers")

# ------------------- Google Sheets Export -------------------
try:
    creds_dict = json.loads(os.environ["GOOGLE_CREDENTIALS_JSON"])
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)

    spreadsheet = client.open("My Stock Screener")
    worksheet = spreadsheet.worksheet("Sheet1")

    worksheet.clear()
    set_with_dataframe(worksheet, df)

    log.info("✅ Data successfully exported to Google Sheets")

except gspread.exceptions.APIError as e:
    log.error(f"Google Sheets API error: {e.response.text}")
except Exception as e:
    log.error("❌ Unexpected error occurred during export")
    log.exception(e)

