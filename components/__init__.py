import streamlit as st
import plotly.graph_objects as go
import pandas as pd

def display_company_overview(info):
    """
    Displays the company overview section: business description, key stats, leadership.
    """
    st.subheader(info.get("longName") or info.get("shortName") or info.get("symbol", "N/A"))
    # --- Top row: quick stats ---
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Market Cap", format_large_number(info.get("marketCap")))

    with col2:
        st.metric("Current Price", f"${info.get('currentPrice', 'N/A')}")

    with col3:
        st.metric("52W Range", f"${info.get('fiftyTwoWeekLow', 'N/A')} - ${info.get('fiftyTwoWeekHigh', 'N/A')}")

    with col4:
        st.metric("Beta", info.get("beta", "N/A"))

    st.divider()

    # --- Company details ---
    col1, col2 = st.columns(2)

    with col1:
        st.write(f"**Sector:** {info.get('sector', 'N/A')}")
        st.write(f"**Industry:** {info.get('industry', 'N/A')}")
        st.write(f"**Employees:** {format_large_number(info.get('fullTimeEmployees'))}")
        st.write(f"**CEO:** {get_ceo_name(info)}")

    with col2:
        st.write(f"**Exchange:** {info.get('exchange', 'N/A')}")
        st.write(f"**Website:** {info.get('website', 'N/A')}")
        st.write(f"**Avg Volume:** {format_large_number(info.get('averageVolume'))}")
        st.write(f"**Shares Outstanding:** {format_large_number(info.get('sharesOutstanding'))}")

    st.divider()

    # --- Business summary ---
    st.write("**Business Summary**")
    st.write(info.get("longBusinessSummary", "No description available."))


def format_large_number(num):
    """
    Formats large numbers into readable strings (e.g. 2500000000 -> '2.50B').
    """
    if num is None:
        return "N/A"

    if num >= 1_000_000_000:
        return f"{num / 1_000_000_000:.2f}B"
    elif num >= 1_000_000:
        return f"{num / 1_000_000:.2f}M"
    elif num >= 1_000:
        return f"{num / 1_000:.2f}K"
    else:
        return str(num)


def get_ceo_name(info):
    """
    Extracts the CEO's name from the company officers list, if available.
    """
    officers = info.get("companyOfficers", [])
    for officer in officers:
        title = officer.get("title", "")
        if "CEO" in title or "Chief Executive" in title:
            return officer.get("name", "N/A")
    return "N/A"
import plotly.graph_objects as go


def display_price_chart(history, ticker):
    """
    Displays an interactive candlestick price chart using Plotly.
    """
    if history.empty:
        st.warning("No price history available.")
        return

    fig = go.Figure(data=[
        go.Candlestick(
            x=history.index,
            open=history["Open"],
            high=history["High"],
            low=history["Low"],
            close=history["Close"],
            name=ticker
        )
    ])

    fig.update_layout(
        title=f"{ticker} Price History",
        xaxis_title="Date",
        yaxis_title="Price ($)",
        xaxis_rangeslider_visible=False,
        template="plotly_dark",
        height=500
    )

    st.plotly_chart(fig, use_container_width=True)


def format_financial_dataframe(df):
    """
    Formats a raw financial statement DataFrame for display:
    - Converts column headers (dates) to readable strings
    - Formats large numbers in millions
    """
    if df is None or df.empty:
        return df

    formatted = df.copy()

    # Convert date columns to readable strings (e.g. "2024-09-30" -> "2024")
    formatted.columns = [col.strftime("%Y-%m-%d") if hasattr(col, "strftime") else str(col) for col in formatted.columns]

    # Convert all values to millions for readability
    formatted = formatted / 1_000_000

    return formatted


def display_financial_statements(statements):
    """
    Displays income statement, balance sheet, and cash flow in tabs.
    statements: dict with keys 'income_statement', 'balance_sheet', 'cash_flow'
    """
    tab1, tab2, tab3 = st.tabs(["Income Statement", "Balance Sheet", "Cash Flow"])

    with tab1:
        df = format_financial_dataframe(statements["income_statement"])
        if df is not None and not df.empty:
            st.caption("All figures in $ millions")
            st.dataframe(df, use_container_width=True)
        else:
            st.warning("No income statement data available.")

    with tab2:
        df = format_financial_dataframe(statements["balance_sheet"])
        if df is not None and not df.empty:
            st.caption("All figures in $ millions")
            st.dataframe(df, use_container_width=True)
        else:
            st.warning("No balance sheet data available.")

    with tab3:
        df = format_financial_dataframe(statements["cash_flow"])
        if df is not None and not df.empty:
            st.caption("All figures in $ millions")
            st.dataframe(df, use_container_width=True)
        else:
            st.warning("No cash flow data available.")


def display_key_metrics(metrics):
    """
    Displays key financial ratios/metrics grouped into sections.
    metrics: dict of dicts, as returned by get_key_metrics()
    """
    st.write("**Valuation**")
    display_metric_row(metrics["valuation"])

    st.write("**Profitability**")
    display_metric_row(metrics["profitability"], is_percent=True)

    st.write("**Growth**")
    display_metric_row(metrics["growth"], is_percent=True)

    st.write("**Financial Health**")
    display_metric_row(metrics["financial_health"])

    st.write("**Cash Generation**")
    display_cash_metrics(metrics["cash_generation"])


def display_metric_row(metric_dict, is_percent=False):
    """
    Displays a dictionary of metrics as a row of columns.
    """
    cols = st.columns(len(metric_dict))

    for col, (label, value) in zip(cols, metric_dict.items()):
        with col:
            if value is None:
                display_value = "N/A"
            elif is_percent:
                display_value = f"{value * 100:.2f}%"
            else:
                display_value = f"{value:.2f}"
            st.metric(label, display_value)


def display_cash_metrics(cash_dict):
    """
    Displays FCF and FCF margin (special formatting: FCF in $ millions, margin as %).
    """
    col1, col2 = st.columns(2)

    with col1:
        fcf = cash_dict.get("Free Cash Flow")
        display_value = format_large_number(fcf) if fcf is not None else "N/A"
        st.metric("Free Cash Flow", f"${display_value}" if fcf is not None else display_value)

    with col2:
        margin = cash_dict.get("FCF Margin")
        display_value = f"{margin * 100:.2f}%" if margin is not None else "N/A"
        st.metric("FCF Margin", display_value)
        import pandas as pd


def display_comparison_table(comparison_data, base_ticker):
    """
    Displays a side-by-side comparison table of companies.
    comparison_data: list of dicts, as returned by get_comparison_data()
    base_ticker: the main ticker being researched, highlighted in the table
    """
    if not comparison_data:
        st.warning("No comparison data available. Check that the peer tickers are valid.")
        return

    df = pd.DataFrame(comparison_data)
    df = df.set_index("Ticker")

    # Format percentage columns
    percent_cols = ["Gross Margin", "Operating Margin", "Net Margin", "ROE", "Revenue Growth"]
    for col in percent_cols:
        if col in df.columns:
            df[col] = df[col].apply(lambda x: f"{x * 100:.2f}%" if pd.notna(x) else "N/A")

    # Format market cap
    if "Market Cap" in df.columns:
        df["Market Cap"] = df["Market Cap"].apply(lambda x: format_large_number(x) if pd.notna(x) else "N/A")

    # Format remaining numeric columns to 2 decimals
    numeric_cols = ["P/E (TTM)", "Forward P/E", "P/B", "EV/EBITDA", "Debt/Equity"]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = df[col].apply(lambda x: f"{x:.2f}" if pd.notna(x) else "N/A")

    st.dataframe(df, use_container_width=True)

    st.caption(f"**{base_ticker}** is your primary company being researched, compared against selected peers.")
def display_score(score_result, explanations):
    """
    Displays the overall score and category breakdown with explanations.
    """
    overall = score_result["overall"]
    categories = score_result["categories"]
    method = score_result["method"]

    st.write(f"**Overall Score: {overall if overall is not None else 'N/A'} / 100**")
    st.caption(f"Scoring method: {method}")

    st.divider()

    cols = st.columns(4)
    category_names = ["Valuation", "Profitability", "Growth", "Financial Health"]

    for col, category in zip(cols, category_names):
        with col:
            score = categories.get(category)
            st.metric(category, f"{score}/100" if score is not None else "N/A")

            notes = explanations.get(category, [])
            for note in notes:
                st.caption(f"• {note}")

def display_comps_valuation(comps_result):
    """
    Displays comps-based valuation: implied price range, per-method breakdown,
    and per-peer multiple detail.
    """
    if comps_result is None:
        st.info("Enter at least one peer ticker above to run a comps valuation.")
        return

    current_price = comps_result["current_price"]
    avg_price = comps_result["average_implied_price"]
    avg_upside = comps_result["average_upside_pct"]
    low = comps_result["low"]
    high = comps_result["high"]

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Current Price", f"${current_price:.2f}" if current_price else "N/A")
    with col2:
        st.metric("Implied Range", f"${low:.2f} - ${high:.2f}")
    with col3:
        st.metric("Avg. Implied Price", f"${avg_price:.2f}")
    with col4:
        if avg_upside is not None:
            st.metric("Avg. Upside/Downside", f"{avg_upside:+.1f}%")

    st.divider()

    # --- Football field chart ---
    display_football_field(comps_result, current_price)

    st.divider()

    # --- Per-method breakdown with peer detail ---
    st.write("**By Method**")
    for method_name, method_data in comps_result["methods"].items():
        implied = method_data["implied_price"]
        upside = round((implied - current_price) / current_price * 100, 1) if current_price else None
        upside_str = f" ({upside:+.1f}%)" if upside is not None else ""

        st.write(f"**{method_name}** — Peer median: {method_data['peer_median_multiple']}x → Implied price: ${implied:.2f}{upside_str}")

        peer_multiples = method_data["peer_multiples"]
        multiples_str = "  |  ".join([f"{ticker}: {mult}x" for ticker, mult in peer_multiples.items()])
        st.caption(multiples_str)


def display_football_field(comps_result, current_price):
    """
    Displays a horizontal 'football field' style bar chart showing the implied
    price range from each valuation method, plus the current price as a reference line.
    """
    methods = list(comps_result["methods"].keys())
    prices = [comps_result["methods"][m]["implied_price"] for m in methods]

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=prices,
        y=methods,
        orientation="h",
        marker=dict(color="#3b82f6"),
        text=[f"${p:.2f}" for p in prices],
        textposition="outside",
    ))

    if current_price:
        fig.add_vline(
            x=current_price,
            line_dash="dash",
            line_color="red",
            annotation_text=f"Current: ${current_price:.2f}",
            annotation_position="top",
        )

    fig.update_layout(
        title="Implied Price by Valuation Method",
        xaxis_title="Implied Price ($)",
        template="plotly_dark",
        height=300,
        showlegend=False,
        margin=dict(l=10, r=10, t=40, b=10),
    )

    st.plotly_chart(fig, use_container_width=True)

def display_dcf_valuation(dcf_result):
    """
    Displays DCF valuation results: key outputs, assumptions used, and year-by-year projection.
    """
    if dcf_result is None:
        st.warning("Unable to calculate DCF — missing free cash flow or share data for this company.")
        return

    current_price = dcf_result["current_price"]
    implied_price = dcf_result["implied_price"]
    upside = dcf_result["upside_pct"]

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Current Price", f"${current_price:.2f}" if current_price else "N/A")
    with col2:
        st.metric("DCF Implied Price", f"${implied_price:.2f}")
    with col3:
        if upside is not None:
            st.metric("Upside/Downside", f"{upside:+.1f}%")

    st.divider()

    st.write("**Assumptions Used**")
    a = dcf_result["assumptions"]
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.write(f"Growth Rate: **{a['growth_rate']}%**")
    with col2:
        st.write(f"Discount Rate: **{a['discount_rate']}%**")
    with col3:
        st.write(f"Terminal Growth: **{a['terminal_growth']}%**")
    with col4:
        st.write(f"Projection Years: **{a['projection_years']}**")

    st.divider()

    st.write("**Projected Free Cash Flow**")
    years = [f"Year {i+1}" for i in range(len(dcf_result["projected_fcf"]))]
    projection_df = pd.DataFrame({
        "Projected FCF": dcf_result["projected_fcf"],
        "Discounted FCF (PV)": dcf_result["discounted_fcf"],
    }, index=years)
    projection_df = projection_df.map(lambda x: f"${x:,.0f}")
    st.dataframe(projection_df, use_container_width=True)

    st.write("**Valuation Bridge**")
    st.write(f"- Sum of Discounted FCF: **${sum(dcf_result['discounted_fcf']):,.0f}**")
    st.write(f"- Discounted Terminal Value: **${dcf_result['discounted_terminal_value']:,.0f}**")
    st.write(f"- Enterprise Value: **${dcf_result['enterprise_value']:,.0f}**")
    st.write(f"- Equity Value: **${dcf_result['equity_value']:,.0f}**")
def display_investment_thesis(thesis_result):
    """
    Displays the auto-generated investment thesis and recommendation.
    """
    recommendation = thesis_result["recommendation"]

    rec_colors = {
        "Attractive": "🟢",
        "Neutral / Hold": "🟡",
        "Unattractive": "🔴",
        "Insufficient Data": "⚪",
    }
    icon = rec_colors.get(recommendation, "⚪")

    st.write(f"### {icon} Recommendation: {recommendation}")
    st.write(thesis_result["thesis_paragraph"])

def display_full_pitch(pitch_data):
    """
    Displays the complete investment memo in-app: header, thesis, valuation summary,
    score breakdown, and key metrics — pulling entirely from the assembled pitch_data dict.
    """
    st.write(f"## {pitch_data['company_name']} ({pitch_data['ticker']})")
    st.caption(f"{pitch_data['sector']} | {pitch_data['industry']}")

    if pitch_data["thesis"]:
        rec_colors = {"Attractive": "🟢", "Neutral / Hold": "🟡", "Unattractive": "🔴", "Insufficient Data": "⚪"}
        icon = rec_colors.get(pitch_data["thesis"]["recommendation"], "⚪")
        st.write(f"### {icon} {pitch_data['thesis']['recommendation']}")

    st.divider()

    st.write("### Investment Thesis")
    if pitch_data["thesis"]:
        st.write(pitch_data["thesis"]["thesis_paragraph"])

    st.divider()

    st.write("### Valuation Summary")
    col1, col2, col3 = st.columns(3)
    with col1:
        cp = pitch_data["current_price"]
        st.metric("Current Price", f"${cp:.2f}" if cp else "N/A")
    with col2:
        if pitch_data["dcf"]:
            st.metric("DCF Implied Price", f"${pitch_data['dcf']['implied_price']:.2f}")
        else:
            st.metric("DCF Implied Price", "N/A")
    with col3:
        if pitch_data["comps"]:
            st.metric("Comps Implied Price", f"${pitch_data['comps']['average_implied_price']:.2f}")
        else:
            st.metric("Comps Implied Price", "N/A")

    st.divider()

    st.write("### Company Score")
    if pitch_data["score"]:
        display_score(pitch_data["score"], {})

    st.divider()

    st.write("### Risks")
    for risk in pitch_data["risks"]:
        st.write(f"- {risk}")

    st.divider()

    st.write("### Catalysts")
    for catalyst in pitch_data["catalysts"]:
        st.write(f"- {catalyst}")

    st.divider()

    if pitch_data["comps"]:
        st.write("### Comparable Company Analysis")
        for method_name, method_data in pitch_data["comps"]["methods"].items():
            st.write(f"- **{method_name}**: Peer median {method_data['peer_median_multiple']}x → Implied price ${method_data['implied_price']:.2f}")
        st.divider()

    st.write("### Business Summary")
    st.write(pitch_data["business_summary"])