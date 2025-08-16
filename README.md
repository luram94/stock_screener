# 📈 Automated Stock Screener to Google Sheets

This project is a daily stock screener that filters financial data from [Finviz](https://finviz.com/) using Python, and automatically exports the results to a **Google Sheet** every day using **GitHub Actions** — all for free.

---

## 🚀 What It Does
- Filters stocks using:
  - Sales Growth (Quarter over Quarter) over 20%
  - 52-Week High/Low: Near new highs or recently hit new highs
  - Market Cap ≥ 1 Billion
- Removes duplicates and formats:
  - Market Cap in billions (e.g. `10.5B`)
  - Daily change in percentage
- Pushes the results to a Google Sheet of your choice

---

## 🔧 Tech Stack
- Python (`finvizfinance`, `pandas`)
- Google Sheets API (`gspread`)
- GitHub Actions (for daily cloud automation)

---

## 📋 Setup Instructions

### Prerequisites
- GitHub account
- Google account
- Basic familiarity with Python and Git

### Step 1: Clone This Repository
```bash
git clone https://github.com/luram94/stock-screener.git
cd stock-screener
```

### Step 2: Set Up Google Sheets API
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable the Google Sheets API and Google Drive API
4. Create a **Service Account** with Google Sheets & Drive access
5. Download the JSON key file

### Step 3: Create Your Google Sheet
1. Create a new Google Sheet
2. Name it exactly as referenced in your code (e.g., "My Stock Screener")
3. Share it with the email address from your service account (found in the JSON file)
4. Make sure the first worksheet is named "Sheet1"

### Step 4: Add GitHub Secret
1. In your GitHub repository, go to Settings > Secrets and variables > Actions
2. Create a new repository secret named `GOOGLE_CREDENTIALS_JSON`
3. Copy the entire content of your Google service account JSON file
4. Paste it as the value of the secret

### Step 5: Configure GitHub Actions
1. Create a directory structure: `.github/workflows/`
2. Add a file named `screener.yml` with the workflow configuration
3. The workflow will run daily and on manual trigger

## 📁 Project Structure
```
stock-screener/
├── .github/
│   └── workflows/
│       └── screener.yml      # GitHub Actions workflow
├── screener.py               # Main script
├── requirements.txt          # Python dependencies 
└── README.md                 # Documentation
```

## 📄 Configuration

### requirements.txt
```
finvizfinance
pandas
gspread
gspread-dataframe
oauth2client
```

### screener.yml
```yaml
name: Daily Stock Screener to Google Sheets

on:
  schedule:
    - cron: '0 8 * * *'  # Every day at 8:00 UTC
  workflow_dispatch:      # Also allow manual trigger

jobs:
  run:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Run script
        env:
          GOOGLE_CREDENTIALS_JSON: ${{ secrets.GOOGLE_CREDENTIALS_JSON }}
        run: |
          echo "$GOOGLE_CREDENTIALS_JSON" > creds.json
          python screener.py
```

## 🛠️ Customization
You can easily customize the stock filters in `screener.py`:

```python
base_filters = {'Sales growthqtr over qtr': 'Over 20%'}
highlow_options = ['0-10% below High', 'New High']
```

For more filter options, check the [Finviz Screener](https://finviz.com/screener.ashx) or the [finvizfinance documentation](https://github.com/lit26/finvizfinance).

## ⚠️ Troubleshooting
- **Spreadsheet not found error**: Ensure the spreadsheet name matches exactly and is shared with the service account email
- **Authentication errors**: Check that your credentials JSON is correctly formatted and has the right permissions
- **Workflow not running**: Verify the GitHub Actions workflow file is correctly configured

## 🔄 Using Different Filters
Finviz offers many filters for stock screening. To see all available options:

```python
from finvizfinance.screener.overview import Overview
foverview = Overview()
filter_options = foverview.get_filter_options()
print(filter_options)
```

## 📊 Example Output
The script outputs data to your Google Sheet with these columns:
- Ticker
- Company
- Sector
- Industry
- Country
- Market Cap
- P/E
- Price
- Change
- Volume

## 📝 License
This project is open source and available under the [MIT License](LICENSE).

## 👏 Acknowledgments
- [Finviz](https://finviz.com/) for providing financial data
- [lit26/finvizfinance](https://github.com/lit26/finvizfinance) for the Python wrapper
