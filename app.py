"""
Krishi Market Advisor 🌾
Streamlit Web Dashboard — Phase 4
"""

import sys
from pathlib import Path
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from src.phase4.recommendation_adapter import (
    get_available_commodities,
    get_available_varieties,
    get_market_recommendation,
)
from src.phase4.explainer import generate_market_explanation
from main import run_pipeline as fetch_data_pipeline


# ── Page Configuration ────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Krishi Market Advisor 🌾",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom Styling ────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1b5e20;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.05rem;
        color: #4b6584;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background-color: #f1f8e9;
        border-left: 5px solid #2e7d32;
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 1rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .metric-value {
        font-size: 1.8rem;
        font-weight: 800;
        color: #1b5e20;
    }
    .metric-label {
        font-size: 0.9rem;
        color: #555555;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .metric-sub {
        font-size: 0.85rem;
        color: #2e7d32;
        font-weight: 600;
    }
    .advisor-box {
        background-color: #ffffff;
        border: 1px solid #c8e6c9;
        border-radius: 10px;
        padding: 1.5rem;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
    }
    .badge-ai {
        background-color: #e8f5e9;
        color: #1b5e20;
        padding: 4px 10px;
        border-radius: 12px;
        font-size: 0.8rem;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)


# ── Sidebar Setup ─────────────────────────────────────────────────────────────
st.sidebar.image("https://img.icons8.com/color/96/wheat.png", width=70)
st.sidebar.title("Krishi Advisor Settings")

data_folder = "data"
available_commodities = get_available_commodities(data_folder)
default_crop = "Arecanut(Betelnut/Supari)"
default_idx = available_commodities.index(default_crop) if default_crop in available_commodities else 0

selected_commodity = st.sidebar.selectbox(
    "🌾 Select Crop / Commodity",
    options=available_commodities,
    index=default_idx
)

available_varieties = get_available_varieties(data_folder, selected_commodity)
variety_options = ["Auto-Detect (Best Reliable Variety)"] + available_varieties
selected_variety_option = st.sidebar.selectbox(
    "🏷️ Select Variety",
    options=variety_options,
    index=0
)

selected_variety = None if selected_variety_option.startswith("Auto-Detect") else selected_variety_option

threshold = st.sidebar.slider(
    "📊 Reliability Threshold (%)",
    min_value=30,
    max_value=100,
    value=70,
    step=5,
    help="Markets reporting on at least this percentage of days are included in recommendations."
)

lang_choice = st.sidebar.radio(
    "🗣️ AI Explanation Language",
    options=["English", "ಕನ್ನಡ (Kannada)", "Dual (English + ಕನ್ನಡ)"],
    index=0
)

st.sidebar.markdown("---")
st.sidebar.subheader("🔄 Government API Data")
if st.sidebar.button("Fetch Today's Govt API Data"):
    with st.spinner("Fetching latest mandi price data from Government API..."):
        try:
            fetch_data_pipeline()
            st.sidebar.success("Data fetch pipeline completed!")
            st.rerun()
        except Exception as e:
            st.sidebar.error(f"Fetch failed: {e}")


# ── Main Header ───────────────────────────────────────────────────────────────
st.markdown('<div class="main-header">Krishi Market Advisor 🌾</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">AI-Powered Mandi Price Recommendations & Trend Analytics for Karnataka Farmers</div>', unsafe_allow_html=True)

# ── Load Recommendation Data ──────────────────────────────────────────────────
rec_result = get_market_recommendation(
    folder=data_folder,
    commodity=selected_commodity,
    variety=selected_variety,
    threshold_pct=float(threshold)
)

if rec_result.get("status") != "success":
    st.warning(f"⚠️ {rec_result.get('message', 'No market recommendation available for this selection.')}")
    st.info("Try lowering the reliability threshold slider in the sidebar or fetching fresh government data.")
    st.stop()

rec = rec_result["recommendation"]
markets_data = rec_result.get("markets", [])

# ── KPI Cards Row ─────────────────────────────────────────────────────────────
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Recommended Mandi</div>
        <div class="metric-value" style="font-size: 1.4rem;">{rec['recommended_market']}</div>
        <div class="metric-sub">As of {rec['date']}</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Highest Modal Price</div>
        <div class="metric-value">₹{rec['highest_price']:,.0f}</div>
        <div class="metric-sub">per quintal</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Extra Earnings Potential</div>
        <div class="metric-value">+₹{rec['extra_earnings']:,.0f}</div>
        <div class="metric-sub">+{rec['extra_earnings_pct']:.1f}% vs lowest market</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Reliable Markets</div>
        <div class="metric-value">{rec_result['reliable_markets_count']}</div>
        <div class="metric-sub">Variety: {rec_result['variety']} ({rec_result['total_days']} days data)</div>
    </div>
    """, unsafe_allow_html=True)


# ── Tabs Navigation ───────────────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["🤖 AI Farmer Advisory", "📈 Mandi Price Analytics", "📋 Detailed Data Table"])

# ── Tab 1: AI Farmer Advisory ─────────────────────────────────────────────────
with tab1:
    st.subheader("🤖 Gemini AI Market Explanation & Advisory")
    
    if lang_choice == "Dual (English + ಕನ್ನಡ)":
        col_en, col_kn = st.columns(2)
        
        with col_en:
            st.markdown("**English Advisory**")
            with st.spinner("Generating English AI explanation..."):
                res_en = generate_market_explanation(
                    folder=data_folder,
                    commodity=selected_commodity,
                    variety=selected_variety,
                    threshold_pct=float(threshold),
                    lang="en"
                )
                mode_badge = "✨ Powered by Gemini 1.5 Flash AI" if res_en["mode"] == "gemini_ai" else "⚡ Rule-Based Advisory Engine"
                st.markdown(f'<span class="badge-ai">{mode_badge}</span>', unsafe_allow_html=True)
                st.markdown(res_en["explanation"])
                
        with col_kn:
            st.markdown("**ಕನ್ನಡ ಮಾಹಿತಿ (Kannada Advisory)**")
            with st.spinner("Generating Kannada AI explanation..."):
                res_kn = generate_market_explanation(
                    folder=data_folder,
                    commodity=selected_commodity,
                    variety=selected_variety,
                    threshold_pct=float(threshold),
                    lang="kn"
                )
                mode_badge = "✨ Powered by Gemini 1.5 Flash AI" if res_kn["mode"] == "gemini_ai" else "⚡ Rule-Based Advisory Engine"
                st.markdown(f'<span class="badge-ai">{mode_badge}</span>', unsafe_allow_html=True)
                st.markdown(res_kn["explanation"])
    else:
        target_lang = "kn" if "ಕನ್ನಡ" in lang_choice else "en"
        with st.spinner("Generating AI explanation..."):
            res = generate_market_explanation(
                folder=data_folder,
                commodity=selected_commodity,
                variety=selected_variety,
                threshold_pct=float(threshold),
                lang=target_lang
            )
            mode_badge = "✨ Powered by Gemini 1.5 Flash AI" if res["mode"] == "gemini_ai" else "⚡ Rule-Based Advisory Engine"
            st.markdown(f'<span class="badge-ai">{mode_badge}</span>', unsafe_allow_html=True)
            st.markdown(res["explanation"])

    st.warning(f"🚨 **Transport & Distance Notice**: {rec_result['transport_warning']}")


# ── Tab 2: Mandi Price Analytics ──────────────────────────────────────────────
with tab2:
    st.subheader("📈 Mandi Price Comparisons & Trends")
    
    col_chart1, col_chart2 = st.columns(2)
    
    # Chart 1: Price Comparison Bar Chart
    with col_chart1:
        st.markdown("##### Modal Price Comparison across Reliable Mandis")
        chart_df = pd.DataFrame([
            {
                "Market": m["market"],
                "Modal Price (₹/Quintal)": m["latest_price"],
                "Is Recommended": "Recommended Mandi" if m["market"] == rec["recommended_market"] else "Other Reliable Mandi"
            }
            for m in markets_data
        ])
        
        fig_bar = px.bar(
            chart_df,
            x="Market",
            y="Modal Price (₹/Quintal)",
            color="Is Recommended",
            color_discrete_map={
                "Recommended Mandi": "#2e7d32",
                "Other Reliable Mandi": "#90caf9"
            },
            text_auto=",.0f",
            title=f"Latest Prices for {selected_commodity} ({rec_result['variety']})"
        )
        fig_bar.update_layout(xaxis_title="", yaxis_title="Price (₹/Quintal)", showlegend=True)
        st.plotly_chart(fig_bar, width="stretch")

    # Chart 2: Historical Price Trend Line Chart
    with col_chart2:
        st.markdown("##### Historical Price Trend over Time")
        history_rows = []
        for m in markets_data:
            for date_str, price in m["history"]:
                history_rows.append({
                    "Date": date_str,
                    "Market": m["market"],
                    "Modal Price (₹)": price
                })
        
        if history_rows:
            hist_df = pd.DataFrame(history_rows)
            fig_line = px.line(
                hist_df,
                x="Date",
                y="Modal Price (₹)",
                color="Market",
                markers=True,
                title="Multi-Day Price Movement"
            )
            fig_line.update_layout(xaxis_title="Date", yaxis_title="Modal Price (₹/Quintal)")
            st.plotly_chart(fig_line, width="stretch")
        else:
            st.info("Insufficient multi-day data points for line chart.")


# ── Tab 3: Detailed Data Table ────────────────────────────────────────────────
with tab3:
    st.subheader("📋 Verified Mandi Price Records")
    table_rows = []
    for m in markets_data:
        table_rows.append({
            "Market (Mandi)": m["market"],
            "Latest Modal Price (₹/Quintal)": f"₹{m['latest_price']:,.0f}",
            "Record Date": m["latest_date"],
            "Price Trend": m["trend"].capitalize(),
            "Trend Detail": m["trend_desc"]
        })
    st.dataframe(pd.DataFrame(table_rows), width="stretch")


# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #777; font-size: 0.85rem;'>"
    "Krishi Market Advisor 🌾 — Production AI Agricultural Advisory Engine for Karnataka Farmers"
    "</div>",
    unsafe_allow_html=True
)
