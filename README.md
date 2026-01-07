# 🚀 Investor Alpha: Institutional 13F Tracker

![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-App-ff4b4b)
![Pandas](https://img.shields.io/badge/Pandas-Data%20Analysis-150458)
![Status](https://img.shields.io/badge/Status-MVP%20Complete-success)

**Investor Alpha** is a data engineering pipeline and interactive dashboard designed to democratize access to institutional-grade financial data. It tracks, parses, and analyzes SEC 13F filings from the world's top hedge funds to identify high-conviction "Smart Money" signals.

---

## 📊 Key Features

* **Automated ETL Pipeline:** Scrapes raw XML data directly from the SEC EDGAR database.
* **Smart Parsing:** Converts messy government filings into clean, structured CSV datasets.
* **Consensus Engine:** Identifies "Cluster Buys"—stocks that multiple top funds are buying simultaneously.
* **Interactive Dashboard:** A Streamlit-based frontend to visualize portfolios, asset allocation, and conviction bets.

---

## 🧠 The "Smart Money" Universe

We currently track the following high-performing funds:
* **The Titans:** Berkshire Hathaway, Appaloosa LP, Altimeter Capital Management LP, Pershing Square.
* **The Mavericks:** Third Point, Tiger Global, Baupost Group.
* **The Hunters:** Mohnish Pabrai, SRS Investment Management, Duquesne Family Office, KENSICO CAPITAL MANAGEMENT CORP, RATAN CAPITAL MANAGEMENT LP.

---

## 🛠️ Project Structure

```text
investor-alpha/
│
├── data/                   # Data Vault
│   ├── raw/                # (Optional) Raw XML downloads
│   ├── processed/          # Cleaned Portfolio CSVs
│   └── analysis/           # Generated Consensus Reports
│
├── src/                    # Source Code
│   ├── app.py              # Streamlit Dashboard Frontend
│   ├── analysis.py         # Consensus Engine logic
│   ├── config.py           # Fund Universe & Settings
│   ├── parser.py           # XML Parsing Logic
│   └── sec_client.py       # SEC API Connection
│
├── main.py                 # ETL Pipeline Orchestrator
├── requirements.txt        # Python Dependencies
└── README.md               # Documentation