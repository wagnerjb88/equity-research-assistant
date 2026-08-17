#  AI-Powered Equity Research Assistant

A full-stack equity research and valuation platform built to mirror how a hedge fund or private equity analyst evaluates a company — from raw financials to a downloadable investment memo.

Enter a ticker, and the app pulls live market data to generate a complete research package: financial statements, valuation models (DCF and comparable companies), a sector-aware scoring engine, AI-generated qualitative analysis, and an auto-generated investment memo — all exportable as Excel and Word documents.


---

## Features

**Company Dashboard**
- Live ticker search with company overview, key stats, and business description
- Interactive candlestick price charts with adjustable timeframes
- Multi-year financial statements (income statement, balance sheet, cash flow), toggleable between annual and quarterly

**Valuation**
- **DCF model** with CAPM-derived discount rate defaults, user-adjustable growth/discount/terminal growth assumptions, and a 5×5 sensitivity table

- **Comparable company analysis** using peer-median P/E, EV/EBITDA, P/S, and P/B multiples, visualized as a football field chart
- Downloadable Excel DCF model with live formulas — adjust assumptions directly in Excel and watch it recalculate

**Analysis & Scoring**
- Sector-aware composite scoring across Valuation, Profitability, Growth, and Financial Health
- Peer-relative percentile ranking when peer companies are provided, with industry-specific fallback thresholds otherwise
- Plain-language explanations for every score

**AI Research**
- Claude API integration generating qualitative competitive advantage, risk, and news-impact analysis alongside the quantitative models

**Screener**
- Scan and rank a user-defined list of tickers by composite score in one view

**Investment Memo**
- Auto-generated investment thesis with a buy/hold/avoid recommendation, synthesized from scoring and valuation signals
- Auto-flagged risks and catalysts based on company-specific data
- Full memo viewable in-app or downloadable as a formatted Word document

---

## Tech Stack

- **Frontend/App:** Streamlit
- **Data:** yfinance
- **Analysis:** Pandas, NumPy
- **Visualization:** Plotly
- **AI:** Anthropic Claude API
- **Document Generation:** OpenPyXL (Excel), python-docx (Word)

---

## Screenshots
<img width="2696" height="1438" alt="Screenshot 2026-08-17 143725" src="https://github.com/user-attachments/assets/07b9ed77-84bc-44cd-89a6-f83b0d467e16" />
<img width="2671" height="1382" alt="Screenshot 2026-08-17 143746" src="https://github.com/user-attachments/assets/d8603fa8-7b4e-4a65-a69e-4803a05c7167" />
<img width="2668" height="1090" alt="Screenshot 2026-08-17 143814" src="https://github.com/user-attachments/assets/e90fee1b-58bc-480c-aa2f-88bc1ac87aa9" />
<img width="2609" height="1309" alt="Screenshot 2026-08-17 143941" src="https://github.com/user-attachments/assets/bc81770a-3cb2-46f9-9bf2-ec9639d6bb15" />





---

## Running Locally

```bash
# Clone the repo
git clone https://github.com/wagnerjb88/equity-research-assistant.git
cd equity-research-assistant

# Set up a virtual environment
python -m venv venv
venv\Scripts\Activate.ps1   # Windows
# source venv/bin/activate  # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Add your Anthropic API key (optional — required only for AI analysis feature)
# Create a .env file in the project root:
# ANTHROPIC_API_KEY=your-key-here

# Run the app
streamlit run app.py
```

---

## Project Structure

```
equity-research-assistant/
├── app.py                 # Main Streamlit app / page logic
├── data/                  # Data fetching, calculations, valuation models
├── components/            # Reusable UI display functions
├── config/                 # App-wide settings
└── requirements.txt
```

Built with a separation-of-concerns architecture: data-fetching and calculation logic lives in `data/`, UI rendering lives in `components/`, keeping `app.py` focused on page flow.

## About

Built by Wagner Jeffreys-Berns, a Finance & Data Analytics student at the University of Minnesota's Carlson School of Management, as a portfolio project demonstrating equity research and financial modeling skills for hedge fund and investment banking recruiting.

[LinkedIn](https://linkedin.com/in/wagner-jeffreys-berns-07983a260)
