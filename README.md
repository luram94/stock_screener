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
