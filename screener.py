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
log.info("Starting Google Sheets export process")

try:
    # Verifica que el archivo existe
    log.info("Checking if credentials file exists")
    if not os.path.exists('creds.json'):
        log.error("❌ Credentials file 'creds.json' not found")
        raise FileNotFoundError("Credentials file not found")
    
    # Lee las credenciales del archivo
    log.info("Reading credentials file")
    with open('creds.json', 'r') as f:
        creds_json = f.read()
        log.info(f"Credentials file length: {len(creds_json)} characters")
        creds_dict = json.loads(creds_json)
    
    # Define el alcance y crea las credenciales
    log.info("Setting up Google API scope and credentials")
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    
    # Autoriza con las credenciales
    log.info("Authorizing with Google using credentials")
    client = gspread.authorize(creds)
    
    # Intenta abrir la hoja de cálculo
    log.info("Attempting to open spreadsheet 'My Stock Screener'")
    spreadsheet = client.open("My Stock Screener")
    
    # Intenta acceder a la hoja específica
    log.info("Accessing worksheet 'Sheet1'")
    worksheet = spreadsheet.worksheet("Sheet1")
    
    # Limpia la hoja y exporta los datos
    log.info("Clearing previous data from worksheet")
    worksheet.clear()
    
    log.info(f"Exporting dataframe with {len(df)} rows to Google Sheets")
    set_with_dataframe(worksheet, df)
    
    log.info("✅ Data successfully exported to Google Sheets")

except FileNotFoundError as e:
    log.error(f"❌ File error: {e}")
except json.JSONDecodeError as e:
    log.error(f"❌ JSON parsing error: {e}")
    log.error("Please check that your credentials JSON is properly formatted")
except gspread.exceptions.SpreadsheetNotFound as e:
    log.error(f"❌ Spreadsheet 'My Stock Screener' not found: {e}")
    log.error("Make sure the spreadsheet exists and is shared with the service account email")
except gspread.exceptions.WorksheetNotFound as e:
    log.error(f"❌ Worksheet 'Sheet1' not found: {e}")
    log.error("Make sure the worksheet 'Sheet1' exists in your spreadsheet")
except gspread.exceptions.APIError as e:
    log.error(f"❌ Google API error: {e}")
    if hasattr(e, 'response') and e.response:
        log.error(f"Response details: {e.response.text}")
except Exception as e:
    log.error(f"❌ Unexpected error during export: {str(e)}")
    log.exception(e)

log.info("Script execution completed")