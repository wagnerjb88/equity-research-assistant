import yfinance as yf
import pandas as pd

def get_stock_data(ticker):
    """
    Fetches a yfinance Ticker object and its info dictionary for a given ticker symbol.
    Returns (stock, info) or (None, None) if the ticker is invalid.
    """
    stock = yf.Ticker(ticker)
    info = stock.info

    # Some tickers populate longName, others only populate shortName.
    # Fall back through a few fields before concluding the ticker is invalid.
    name = info.get("longName") or info.get("shortName") or info.get("symbol")

    if not info or name is None:
        return None, None

    return stock, info
def get_price_history(stock, period="1y"):
    """
    Fetches historical price data for a given stock (yfinance Ticker object).
    period options: '1mo', '6mo', '1y', '5y', 'max', etc.
    """
    history = stock.history(period=period)
    return history
def get_financial_statements(stock, period="annual"):
    """
    Fetches income statement, balance sheet, and cash flow statement.
    period: 'annual' or 'quarterly'
    Returns a dict with three DataFrames.
    """
    if period == "annual":
        income_stmt = stock.financials
        balance_sheet = stock.balance_sheet
        cash_flow = stock.cashflow
    else:
        income_stmt = stock.quarterly_financials
        balance_sheet = stock.quarterly_balance_sheet
        cash_flow = stock.quarterly_cashflow

    return {
        "income_statement": income_stmt,
        "balance_sheet": balance_sheet,
        "cash_flow": cash_flow
    }
def get_key_metrics(info, stock):
    """
    Extracts and calculates key financial ratios/metrics from the info dict
    and cash flow statement.
    Returns a dict of grouped metrics.
    """
    # --- Free Cash Flow (calculated from cash flow statement) ---
    fcf = None
    fcf_margin = None
    try:
        cash_flow = stock.cashflow
        if not cash_flow.empty and "Free Cash Flow" in cash_flow.index:
            fcf = cash_flow.loc["Free Cash Flow"].iloc[0]
        elif not cash_flow.empty:
            # Fallback: Operating Cash Flow - CapEx
            op_cf = cash_flow.loc["Operating Cash Flow"].iloc[0] if "Operating Cash Flow" in cash_flow.index else None
            capex = cash_flow.loc["Capital Expenditure"].iloc[0] if "Capital Expenditure" in cash_flow.index else None
            if op_cf is not None and capex is not None:
                fcf = op_cf + capex  # capex is usually negative already

        total_revenue = info.get("totalRevenue")
        if fcf is not None and total_revenue:
            fcf_margin = fcf / total_revenue
    except Exception:
        fcf = None
        fcf_margin = None

    return {
        "valuation": {
            "P/E (TTM)": info.get("trailingPE"),
            "Forward P/E": info.get("forwardPE"),
            "P/B": info.get("priceToBook"),
            "P/S": info.get("priceToSalesTrailing12Months"),
            "EV/EBITDA": info.get("enterpriseToEbitda"),
        },
        "profitability": {
            "Gross Margin": info.get("grossMargins"),
            "Operating Margin": info.get("operatingMargins"),
            "Net Margin": info.get("profitMargins"),
            "ROE": info.get("returnOnEquity"),
            "ROA": info.get("returnOnAssets"),
        },
        "growth": {
            "Revenue Growth (YoY)": info.get("revenueGrowth"),
            "Earnings Growth (YoY)": info.get("earningsGrowth"),
        },
        "financial_health": {
            "Debt/Equity": info.get("debtToEquity"),
            "Current Ratio": info.get("currentRatio"),
            "Quick Ratio": info.get("quickRatio"),
        },
        "cash_generation": {
            "Free Cash Flow": fcf,
            "FCF Margin": fcf_margin,
        }
    }

def get_comparison_data(tickers):
    """
    Fetches key comparison metrics for a list of ticker symbols.
    Returns a list of dicts, one per company, skipping any that fail.
    """
    comparison_data = []

    for ticker in tickers:
        try:
            stock, info = get_stock_data(ticker)
            if stock is None:
                continue

            comparison_data.append({
                "Ticker": ticker,
                "Company": info.get("longName", ticker),
                "Market Cap": info.get("marketCap"),
                "P/E (TTM)": info.get("trailingPE"),
                "Forward P/E": info.get("forwardPE"),
                "P/B": info.get("priceToBook"),
                "EV/EBITDA": info.get("enterpriseToEbitda"),
                "Gross Margin": info.get("grossMargins"),
                "Operating Margin": info.get("operatingMargins"),
                "Net Margin": info.get("profitMargins"),
                "ROE": info.get("returnOnEquity"),
                "Revenue Growth": info.get("revenueGrowth"),
                "Debt/Equity": info.get("debtToEquity"),
            })
        except Exception:
            continue

    return comparison_data

SECTOR_THRESHOLDS = {
    "Technology": {
        "pe": {"good": 25, "bad": 60},
        "ev_ebitda": {"good": 15, "bad": 35},
        "net_margin": {"good": 0.20, "bad": 0.05},
        "revenue_growth": {"good": 0.15, "bad": 0.0},
    },
    "Financial Services": {
        "pe": {"good": 10, "bad": 20},
        "ev_ebitda": {"good": 8, "bad": 16},
        "net_margin": {"good": 0.25, "bad": 0.10},
        "revenue_growth": {"good": 0.08, "bad": 0.0},
    },
    "Healthcare": {
        "pe": {"good": 18, "bad": 40},
        "ev_ebitda": {"good": 12, "bad": 25},
        "net_margin": {"good": 0.15, "bad": 0.03},
        "revenue_growth": {"good": 0.10, "bad": 0.0},
    },
    "Consumer Cyclical": {
        "pe": {"good": 15, "bad": 30},
        "ev_ebitda": {"good": 10, "bad": 20},
        "net_margin": {"good": 0.08, "bad": 0.02},
        "revenue_growth": {"good": 0.08, "bad": 0.0},
    },
    "Consumer Defensive": {
        "pe": {"good": 15, "bad": 28},
        "ev_ebitda": {"good": 10, "bad": 18},
        "net_margin": {"good": 0.08, "bad": 0.02},
        "revenue_growth": {"good": 0.05, "bad": 0.0},
    },
    "Energy": {
        "pe": {"good": 10, "bad": 20},
        "ev_ebitda": {"good": 5, "bad": 12},
        "net_margin": {"good": 0.10, "bad": 0.02},
        "revenue_growth": {"good": 0.05, "bad": -0.05},
    },
    "Industrials": {
        "pe": {"good": 15, "bad": 28},
        "ev_ebitda": {"good": 10, "bad": 18},
        "net_margin": {"good": 0.10, "bad": 0.03},
        "revenue_growth": {"good": 0.06, "bad": 0.0},
    },
    "Utilities": {
        "pe": {"good": 16, "bad": 25},
        "ev_ebitda": {"good": 9, "bad": 14},
        "net_margin": {"good": 0.12, "bad": 0.05},
        "revenue_growth": {"good": 0.04, "bad": -0.02},
    },
    # Fallback for any sector not listed above
    "Default": {
        "pe": {"good": 15, "bad": 40},
        "ev_ebitda": {"good": 10, "bad": 25},
        "net_margin": {"good": 0.15, "bad": 0.02},
        "revenue_growth": {"good": 0.10, "bad": 0.0},
    },
}


def get_sector_thresholds(sector):
    """
    Returns the threshold dict for a given sector, falling back to Default
    if the sector isn't explicitly covered.
    """
    return SECTOR_THRESHOLDS.get(sector, SECTOR_THRESHOLDS["Default"])
def calculate_score(metrics, comparison_data=None, base_ticker=None, sector=None):
    """
    Calculates a 0-100 score for each category (Valuation, Profitability, Growth,
    Financial Health) plus an overall weighted score.
    Uses peer comparison if available, otherwise falls back to absolute thresholds.
    """
    use_peers = comparison_data is not None and len(comparison_data) > 1

    if use_peers:
        peer_df = pd.DataFrame(comparison_data).set_index("Ticker")

    def score_relative(metric_label, raw_value, lower_is_better=False):
        """Scores a metric 0-100 based on percentile rank among peers."""
        if raw_value is None or peer_df[metric_label].dropna().empty:
            return None
        values = peer_df[metric_label].dropna()
        if base_ticker not in values.index:
            return None
        rank = values.rank(pct=True, ascending=not lower_is_better)
        return round(rank.get(base_ticker, 0.5) * 100)

    def score_absolute(raw_value, good, bad, lower_is_better=False):
        """Scores a metric 0-100 based on fixed thresholds. 'good' and 'bad' define the scale."""
        if raw_value is None:
            return None
        if lower_is_better:
            if raw_value <= good:
                return 100
            if raw_value >= bad:
                return 0
            return round(100 * (bad - raw_value) / (bad - good))
        else:
            if raw_value >= good:
                return 100
            if raw_value <= bad:
                return 0
            return round(100 * (raw_value - bad) / (good - bad))

    def get_category_score(metric_scores):
        """Averages non-None scores in a category. Returns None if no data available."""
        valid_scores = [s for s in metric_scores if s is not None]
        if not valid_scores:
            return None
        return round(sum(valid_scores) / len(valid_scores))

    val = metrics["valuation"]
    prof = metrics["profitability"]
    growth = metrics["growth"]
    health = metrics["financial_health"]

    thresholds = get_sector_thresholds(sector)

    # --- Valuation (lower is generally "cheaper" = better) ---
    if use_peers:
        valuation_scores = [
            score_relative("P/E (TTM)", val["P/E (TTM)"], lower_is_better=True),
            score_relative("P/B", val["P/B"], lower_is_better=True),
            score_relative("EV/EBITDA", val["EV/EBITDA"], lower_is_better=True),
        ]
    else:
        valuation_scores = [
            score_absolute(val["P/E (TTM)"], good=thresholds["pe"]["good"], bad=thresholds["pe"]["bad"], lower_is_better=True),
            score_absolute(val["P/B"], good=2, bad=8, lower_is_better=True),
            score_absolute(val["EV/EBITDA"], good=thresholds["ev_ebitda"]["good"], bad=thresholds["ev_ebitda"]["bad"], lower_is_better=True),
        ]
    # --- Profitability (higher is better) ---
    if use_peers:
        profitability_scores = [
            score_relative("Gross Margin", prof["Gross Margin"]),
            score_relative("Operating Margin", prof["Operating Margin"]),
            score_relative("Net Margin", prof["Net Margin"]),
            score_relative("ROE", prof["ROE"]),
        ]
    else:
        profitability_scores = [
            score_absolute(prof["Gross Margin"], good=0.5, bad=0.15),
            score_absolute(prof["Operating Margin"], good=0.25, bad=0.05),
            score_absolute(prof["Net Margin"], good=thresholds["net_margin"]["good"], bad=thresholds["net_margin"]["bad"]),
            score_absolute(prof["ROE"], good=0.20, bad=0.05),
        ]

    # --- Growth (higher is better) ---
    if use_peers:
        growth_scores = [
            score_relative("Revenue Growth", growth["Revenue Growth (YoY)"]),
        ]
    else:
        growth_scores = [
            score_absolute(growth["Revenue Growth (YoY)"], good=thresholds["revenue_growth"]["good"], bad=thresholds["revenue_growth"]["bad"]),
            score_absolute(growth["Earnings Growth (YoY)"], good=0.15, bad=0.0),
        ]

    # --- Financial Health (lower debt / higher liquidity is better) ---
    if use_peers:
        health_scores = [
            score_relative("Debt/Equity", health["Debt/Equity"], lower_is_better=True),
        ]
    else:
        health_scores = [
            score_absolute(health["Debt/Equity"], good=50, bad=200, lower_is_better=True),
            score_absolute(health["Current Ratio"], good=2, bad=0.8),
            score_absolute(health["Quick Ratio"], good=1.5, bad=0.5),
        ]

    category_scores = {
        "Valuation": get_category_score(valuation_scores),
        "Profitability": get_category_score(profitability_scores),
        "Growth": get_category_score(growth_scores),
        "Financial Health": get_category_score(health_scores),
    }

    weights = {
        "Valuation": 0.20,
        "Profitability": 0.30,
        "Growth": 0.25,
        "Financial Health": 0.25,
    }

    weighted_total = 0
    weight_used = 0
    for category, score in category_scores.items():
        if score is not None:
            weighted_total += score * weights[category]
            weight_used += weights[category]

    overall_score = round(weighted_total / weight_used) if weight_used > 0 else None

    return {
        "categories": category_scores,
        "overall": overall_score,
        "method": "peer-relative" if use_peers else "absolute thresholds"
    }

def generate_score_explanation(metrics, score_result):
    """
    Generates plain-English bullet points explaining why each category scored as it did.
    Returns a dict: category -> list of explanation strings.
    """
    explanations = {}

    val = metrics["valuation"]
    prof = metrics["profitability"]
    growth = metrics["growth"]
    health = metrics["financial_health"]

    # --- Valuation ---
    notes = []
    pe = val["P/E (TTM)"]
    if pe is not None:
        if pe < 15:
            notes.append(f"P/E of {pe:.1f} is low, suggesting the stock may be undervalued.")
        elif pe > 35:
            notes.append(f"P/E of {pe:.1f} is elevated, suggesting the market is pricing in high expectations.")
        else:
            notes.append(f"P/E of {pe:.1f} is in a moderate range.")
    ev_ebitda = val["EV/EBITDA"]
    if ev_ebitda is not None:
        if ev_ebitda > 20:
            notes.append(f"EV/EBITDA of {ev_ebitda:.1f} is on the higher side relative to typical benchmarks.")
        elif ev_ebitda < 10:
            notes.append(f"EV/EBITDA of {ev_ebitda:.1f} looks attractive relative to typical benchmarks.")
    explanations["Valuation"] = notes

    # --- Profitability ---
    notes = []
    net_margin = prof["Net Margin"]
    if net_margin is not None:
        if net_margin > 0.20:
            notes.append(f"Net margin of {net_margin*100:.1f}% is strong, indicating efficient conversion of revenue to profit.")
        elif net_margin < 0.05:
            notes.append(f"Net margin of {net_margin*100:.1f}% is thin, indicating limited profit conversion.")
    roe = prof["ROE"]
    if roe is not None:
        if roe > 0.20:
            notes.append(f"ROE of {roe*100:.1f}% shows strong returns generated on shareholder equity.")
        elif roe < 0.08:
            notes.append(f"ROE of {roe*100:.1f}% is relatively weak.")
    explanations["Profitability"] = notes

    # --- Growth ---
    notes = []
    rev_growth = growth["Revenue Growth (YoY)"]
    if rev_growth is not None:
        if rev_growth > 0.15:
            notes.append(f"Revenue growth of {rev_growth*100:.1f}% YoY reflects strong top-line momentum.")
        elif rev_growth < 0:
            notes.append(f"Revenue declined {abs(rev_growth)*100:.1f}% YoY, a red flag worth investigating.")
        else:
            notes.append(f"Revenue growth of {rev_growth*100:.1f}% YoY is modest.")
    explanations["Growth"] = notes

    # --- Financial Health ---
    notes = []
    debt_equity = health["Debt/Equity"]
    if debt_equity is not None:
        if debt_equity > 150:
            notes.append(f"Debt/Equity of {debt_equity:.0f} is elevated, indicating meaningful leverage risk.")
        elif debt_equity < 50:
            notes.append(f"Debt/Equity of {debt_equity:.0f} is conservative, indicating low leverage risk.")
    current_ratio = health["Current Ratio"]
    if current_ratio is not None:
        if current_ratio < 1:
            notes.append(f"Current ratio of {current_ratio:.2f} is below 1, meaning short-term liabilities exceed short-term assets.")
        elif current_ratio > 2:
            notes.append(f"Current ratio of {current_ratio:.2f} indicates strong short-term liquidity.")
    explanations["Financial Health"] = notes

    return explanations