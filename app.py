import streamlit as st

from config.settings import APP_NAME, APP_ICON, LAYOUT, DEFAULT_TICKER
from data import get_stock_data, get_price_history, get_financial_statements, get_key_metrics, get_comparison_data, calculate_score, generate_score_explanation, calculate_comps_valuation, calculate_dcf, generate_dcf_excel, generate_investment_thesis, assemble_pitch_data, generate_pitch_docx, get_company_news, calculate_dcf_sensitivity, run_screener
from components import display_company_overview, display_price_chart, display_financial_statements, display_key_metrics, display_comparison_table, display_score, display_comps_valuation, display_dcf_valuation, display_investment_thesis, display_full_pitch, display_news, display_dcf_sensitivity, display_screener_results
st.set_page_config(
    page_title=APP_NAME,
    page_icon=APP_ICON,
    layout=LAYOUT
)

st.title(f"{APP_ICON} {APP_NAME}")
st.caption("AI-powered equity research, from ticker to investment pitch.")

# --- Screener ---
with st.expander("🔍 Screener — Scan Multiple Companies", expanded=False):
    screener_input = st.text_input(
        "Enter tickers to scan, separated by commas",
        placeholder="e.g. AAPL, MSFT, GOOGL, AMZN, NVDA",
        key="screener_input"
    )
    if st.button("Run Screener", key="run_screener_button"):
        if screener_input:
            screener_tickers = [t.strip().upper() for t in screener_input.split(",") if t.strip()]
            with st.spinner(f"Scanning {len(screener_tickers)} companies..."):
                screener_results = run_screener(screener_tickers)
            display_screener_results(screener_results)
        else:
            st.info("Enter at least one ticker to scan.")

st.divider()

# --- Ticker Search ---
ticker_input = st.text_input(
    "Enter a stock ticker",
    value=DEFAULT_TICKER,
    placeholder="e.g. AAPL, MSFT, TSLA",
    key="main_ticker_input"
).upper().strip()

if ticker_input:
    try:
        stock, info = get_stock_data(ticker_input)

        if stock is None:
            st.error(f"Couldn't find data for '{ticker_input}'. Check the ticker and try again.")
        else:
            display_company_overview(info)

            st.divider()

            # --- Recent News ---
            st.subheader("Recent News")
            news_articles = get_company_news(stock)
            display_news(news_articles)

            st.divider()

            # --- Timeframe selector for price chart ---
            timeframe_map = {
                "1M": "1mo",
                "6M": "6mo",
                "YTD": "ytd",
                "1Y": "1y",
                "5Y": "5y",
                "Max": "max"
            }
            selected_label = st.radio(
                "Select timeframe",
                options=list(timeframe_map.keys()),
                index=3,
                horizontal=True
            )
            selected_period = timeframe_map[selected_label]

            history = get_price_history(stock, period=selected_period)
            display_price_chart(history, ticker_input)

            st.divider()

            # --- Key metrics/ratios ---
            st.subheader("Key Metrics")
            metrics = get_key_metrics(info, stock)
            display_key_metrics(metrics)

            st.divider()

            # --- Financial statements ---
            st.subheader("Financial Statements")

            statement_period = st.radio(
                "Statement period",
                options=["Annual", "Quarterly"],
                horizontal=True
            )
            period_value = "annual" if statement_period == "Annual" else "quarterly"

            statements = get_financial_statements(stock, period=period_value)
            display_financial_statements(statements)

            st.divider()

            # --- Competitor comparison ---
            st.subheader("Competitor Comparison")

            peer_input = st.text_input(
                "Enter peer tickers, separated by commas",
                placeholder="e.g. MSFT, GOOGL, AMZN",
                key="peer_ticker_input"
            )

            if peer_input:
                peer_tickers = [t.strip().upper() for t in peer_input.split(",") if t.strip()]
                all_tickers = [ticker_input] + peer_tickers

                comparison_data = get_comparison_data(all_tickers)
                display_comparison_table(comparison_data, ticker_input)
            else:
                comparison_data = None
                st.info("Enter peer tickers above to compare against.")

            st.divider()

            # --- Comps Valuation ---
            st.subheader("Comparable Company Valuation")
            comps_result = calculate_comps_valuation(info, comparison_data)
            display_comps_valuation(comps_result)

            st.divider()

            # --- DCF Valuation ---
            st.subheader("DCF Valuation")

            default_dcf = calculate_dcf(info, stock)

            if default_dcf is None:
                st.warning("Unable to calculate DCF — missing free cash flow or share data for this company.")
            else:
                default_assumptions = default_dcf["assumptions"]

                st.write("**Adjust Assumptions** (defaults are auto-calculated from company data)")
                col1, col2, col3 = st.columns(3)
                with col1:
                    growth_rate_input = st.slider(
                        "Revenue/FCF Growth Rate (%)",
                        min_value=-10.0, max_value=30.0,
                        value=float(default_assumptions["growth_rate"]),
                        step=0.5,
                        key="dcf_growth_slider"
                    )
                with col2:
                    discount_rate_input = st.slider(
                        "Discount Rate (%)",
                        min_value=4.0, max_value=20.0,
                        value=float(default_assumptions["discount_rate"]),
                        step=0.25,
                        key="dcf_discount_slider"
                    )
                with col3:
                    terminal_growth_input = st.slider(
                        "Terminal Growth Rate (%)",
                        min_value=0.0, max_value=5.0,
                        value=float(default_assumptions["terminal_growth"]),
                        step=0.25,
                        key="dcf_terminal_slider"
                    )

                dcf_result = calculate_dcf(
                    info, stock,
                    growth_rate=growth_rate_input / 100,
                    discount_rate=discount_rate_input / 100,
                    terminal_growth=terminal_growth_input / 100,
                )

                st.divider()
                display_dcf_valuation(dcf_result)

                if dcf_result is not None:
                    excel_buffer = generate_dcf_excel(info, dcf_result, ticker_input)
                    st.download_button(
                        label="📥 Download DCF Model (Excel)",
                        data=excel_buffer,
                        file_name=f"{ticker_input}_DCF_Model.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        key="dcf_excel_download"
                    )

                st.divider()

                # --- DCF Sensitivity Table ---
                st.write("**Sensitivity Analysis**")
                sensitivity_result = calculate_dcf_sensitivity(
                    info, stock,
                    growth_rate=growth_rate_input / 100,
                    discount_rate_center=discount_rate_input / 100,
                    terminal_growth_center=terminal_growth_input / 100,
                )
                display_dcf_sensitivity(sensitivity_result)

           # --- Company Score ---
            st.subheader("Company Score")
            company_sector = info.get("sector")
            score_result = calculate_score(metrics, comparison_data=comparison_data, base_ticker=ticker_input, sector=company_sector)
            explanations = generate_score_explanation(metrics, score_result)
            display_score(score_result, explanations)

            st.divider()

           # --- Investment Thesis ---
            st.subheader("Investment Thesis")
            thesis_result = generate_investment_thesis(info, score_result, dcf_result, comps_result, metrics, ticker_input)
            display_investment_thesis(thesis_result)

            st.divider()

            # --- Full Investment Memo ---
            st.subheader("📄 Full Investment Memo")
            with st.expander("View Full Memo", expanded=False):
                pitch_data = assemble_pitch_data(info, metrics, score_result, dcf_result, comps_result, thesis_result, news_articles, ticker_input)
                display_full_pitch(pitch_data)

                st.divider()

                docx_buffer = generate_pitch_docx(pitch_data)
                st.download_button(
                    label="📥 Download Investment Memo (Word)",
                    data=docx_buffer,
                    file_name=f"{ticker_input}_Investment_Memo.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    key="pitch_docx_download"
                )
    except Exception as e:
        st.error(f"Error fetching data: {e}")
else:
    st.info("Enter a ticker above to begin.")