"""
Krishi Market Advisor 🌾
Earth-Themed AI Agricultural Intelligence Dashboard for Karnataka Farmers
"""

import sys
from pathlib import Path
import streamlit as st
import pandas as pd
import plotly.express as px
import urllib.parse

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
from src.phase4.audio_service import generate_audio_speech
from src.phase4.transport_calculator import (
    calculate_net_transport_profit,
    DISTANCES_KM,
    VEHICLE_TYPES,
)
from main import run_pipeline as fetch_data_pipeline

# ── Page Configuration ────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Krishi Market Advisor 🌾 | ಕರ್ನಾಟಕ ಕೃಷಿ ಮಾರುಕಟ್ಟೆ ಸಲಹೆಗಾರ",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Earthy Agricultural Design System & Custom CSS ─────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&family=Noto+Sans+Kannada:wght@400;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', 'Noto Sans Kannada', system-ui, sans-serif;
    }

    /* Earthy Hero Header Container */
    .hero-banner {
        background: linear-gradient(135deg, #1b4332 0%, #2d6a4f 60%, #40916c 100%);
        border-radius: 18px;
        padding: 2.2rem 2rem;
        color: #ffffff;
        box-shadow: 0 10px 25px rgba(27, 67, 50, 0.15);
        margin-bottom: 1.8rem;
        position: relative;
        overflow: hidden;
    }
    .hero-banner::after {
        content: "🌾";
        position: absolute;
        right: 20px;
        bottom: -10px;
        font-size: 8rem;
        opacity: 0.12;
        pointer-events: none;
    }
    .hero-title {
        font-size: 2.4rem;
        font-weight: 800;
        color: #f4f1ea;
        margin-bottom: 0.3rem;
        letter-spacing: -0.5px;
    }
    .hero-subtitle {
        font-size: 1.1rem;
        color: #d8f3dc;
        font-weight: 500;
        max-width: 850px;
    }

    /* Live Ticker Bar */
    .ticker-bar {
        background-color: #fefae0;
        border: 1px solid #e9c46a;
        border-radius: 12px;
        padding: 0.65rem 1.2rem;
        margin-bottom: 1.5rem;
        color: #7f5539;
        font-weight: 700;
        font-size: 0.92rem;
        display: flex;
        align-items: center;
        gap: 15px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.03);
    }
    .ticker-tag {
        background: #dda15e;
        color: #ffffff;
        padding: 3px 10px;
        border-radius: 8px;
        font-size: 0.78rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    /* Earthy KPI Cards */
    .kpi-card {
        background: #ffffff;
        border-radius: 16px;
        padding: 1.3rem 1.4rem;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.05);
        border: 1.5px solid #e2e8f0;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
        height: 100%;
    }
    .kpi-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 24px rgba(45, 106, 79, 0.12);
        border-color: #95d5b2;
    }
    .kpi-icon {
        font-size: 1.6rem;
        margin-bottom: 0.4rem;
    }
    .kpi-label {
        font-size: 0.82rem;
        font-weight: 700;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .kpi-value {
        font-size: 1.85rem;
        font-weight: 800;
        color: #1b4332;
        margin: 0.2rem 0;
    }
    .kpi-sub {
        font-size: 0.88rem;
        color: #2d6a4f;
        font-weight: 600;
    }

    /* AI Badge Styling */
    .badge-gemini {
        background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%);
        color: #1b4332;
        border: 1px solid #81c784;
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 700;
        display: inline-block;
        margin-bottom: 1rem;
    }
    .badge-fallback {
        background-color: #fff3e0;
        color: #e65100;
        border: 1px solid #ffcc80;
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 700;
        display: inline-block;
        margin-bottom: 1rem;
    }

    /* Profit Card Styling */
    .profit-card-green {
        background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%);
        border: 2px solid #22c55e;
        border-radius: 16px;
        padding: 1.5rem;
        color: #14532d;
    }
    .profit-card-orange {
        background: linear-gradient(135deg, #fff7ed 0%, #ffedd5 100%);
        border: 2px solid #f97316;
        border-radius: 16px;
        padding: 1.5rem;
        color: #7c2d12;
    }

    /* Weather Widget */
    .weather-box {
        background: #fdfbf7;
        border: 1px solid #e6dfd5;
        border-radius: 14px;
        padding: 1rem 1.2rem;
        margin-top: 1rem;
        display: flex;
        align-items: center;
        gap: 15px;
    }

    /* Custom Button styling */
    .stButton>button {
        border-radius: 12px;
        font-weight: 700;
        background-color: #2d6a4f;
        color: white;
        border: none;
        padding: 0.5rem 1.2rem;
        transition: all 0.2s ease;
    }
    .stButton>button:hover {
        background-color: #1b4332;
        color: white;
        box-shadow: 0 4px 12px rgba(27, 67, 50, 0.25);
    }
</style>
""", unsafe_allow_html=True)


# ── Sidebar Configuration ─────────────────────────────────────────────────────
st.sidebar.markdown("### 🌾 Krishi Advisor Controls")

data_folder = "data"
available_commodities = get_available_commodities(data_folder)
default_crop = "Arecanut(Betelnut/Supari)"
default_idx = available_commodities.index(default_crop) if default_crop in available_commodities else 0

selected_commodity = st.sidebar.selectbox(
    "🌱 Select Crop / Commodity",
    options=available_commodities,
    index=default_idx
)

available_varieties = get_available_varieties(data_folder, selected_commodity)
variety_options = ["Auto-Detect (Best Reliable Variety)"] + available_varieties
selected_variety_option = st.sidebar.selectbox(
    "🏷️ Select Crop Variety",
    options=variety_options,
    index=0
)

selected_variety = None if selected_variety_option.startswith("Auto-Detect") else selected_variety_option

threshold = st.sidebar.slider(
    "📊 Mandi Reliability Threshold (%)",
    min_value=30,
    max_value=100,
    value=70,
    step=5,
    help="Filters out mandis that don't report data consistently."
)

lang_choice = st.sidebar.radio(
    "🗣️ Advisory Language",
    options=["English", "ಕನ್ನಡ (Kannada)", "Dual (English + ಕನ್ನಡ)"],
    index=0
)

st.sidebar.markdown("---")
st.sidebar.markdown("### 📡 Live Data Sync")
if st.sidebar.button("🔄 Fetch Government API Data"):
    with st.spinner("Connecting to Govt Agmarknet Portal..."):
        try:
            fetch_data_pipeline()
            st.sidebar.success("Daily mandi data updated!")
            st.rerun()
        except Exception as e:
            st.sidebar.error(f"Fetch failed: {e}")


# ── Hero Banner Section ───────────────────────────────────────────────────────
st.markdown("""
<div class="hero-banner">
    <div class="hero-title">Krishi Market Advisor 🌾</div>
    <div class="hero-subtitle">ಕರ್ನಾಟಕ ಕೃಷಿ ಮಾರುಕಟ್ಟೆ ಸಲಹೆಗಾರ · AI-Powered Mandi Selling Advice, Price Momentum Analytics & Transport Profit Engine</div>
</div>
""", unsafe_allow_html=True)

# ── Live Ticker Banner ────────────────────────────────────────────────────────
st.markdown("""
<div class="ticker-bar">
    <span class="ticker-tag">Live Market Ticker</span>
    <span>🌾 Arecanut: ₹52,600/Q (Rising ↑)</span>
    <span>•</span>
    <span>🥥 Copra: ₹32,100/Q (Stable →)</span>
    <span>•</span>
    <span>🌶️ Black Pepper: ₹66,900/Q</span>
    <span>•</span>
    <span>🍅 Tomato: ₹2,400/Q</span>
</div>
""", unsafe_allow_html=True)


# ── Load Recommendation Data ──────────────────────────────────────────────────
rec_result = get_market_recommendation(
    folder=data_folder,
    commodity=selected_commodity,
    variety=selected_variety,
    threshold_pct=float(threshold)
)

if rec_result.get("status") != "success":
    st.warning(f"⚠️ {rec_result.get('message', 'No market recommendation available for this crop.')}")
    st.info("Try adjusting the reliability threshold slider or fetching fresh government data.")
    st.stop()

rec = rec_result["recommendation"]
markets_data = rec_result.get("markets", [])


# ── Earthy KPI Cards ──────────────────────────────────────────────────────────
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-icon">🏛️</div>
        <div class="kpi-label">Recommended Mandi</div>
        <div class="kpi-value" style="font-size: 1.4rem;">{rec['recommended_market']}</div>
        <div class="kpi-sub">Reported on {rec['date']}</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-icon">💰</div>
        <div class="kpi-label">Highest Modal Price</div>
        <div class="kpi-value">₹{rec['highest_price']:,.0f}</div>
        <div class="kpi-sub">per quintal</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-icon">📈</div>
        <div class="kpi-label">Extra Earnings Advantage</div>
        <div class="kpi-value">+₹{rec['extra_earnings']:,.0f}</div>
        <div class="kpi-sub">+{rec['extra_earnings_pct']:.1f}% vs lowest mandi</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-icon">🛡️</div>
        <div class="kpi-label">Verified Mandis</div>
        <div class="kpi-value">{rec_result['reliable_markets_count']}</div>
        <div class="kpi-sub">Variety: {rec_result['variety']} ({rec_result['total_days']} days data)</div>
    </div>
    """, unsafe_allow_html=True)


st.markdown("<br>", unsafe_allow_html=True)


# ── Tabs Navigation ───────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "🤖 AI Market Advisory & Voice",
    "🚚 Transport & Pure Net Profit Calculator",
    "📈 Price Momentum Analytics",
    "📋 Verified Mandi Table"
])

# ── Tab 1: AI Advisory & Kannada Voice ─────────────────────────────────────────
with tab1:
    st.subheader("🤖 Gemini AI Market Explanation & Voice Advisor")

    # Smart Selling Timing Recommendation Card
    st.markdown(f"""
    <div style="background-color: #f4f6f0; border-left: 5px solid #2d6a4f; padding: 1.1rem; border-radius: 12px; margin-bottom: 1.2rem;">
        <h5 style="margin:0; color: #1b4332;">⏳ Smart Timing Advisor: <b>BEST TIME TO SELL: NEXT 24-48 HOURS</b></h5>
        <p style="margin: 4px 0 0 0; color: #4a5568; font-size: 0.95rem;">
            Modal prices at <b>{rec['recommended_market']}</b> are currently <b>{rec['trend']}</b> ({rec['trend_desc']}). 
            Market arrivals are expected to peak later this week. Selling within the next 2 days captures current peak prices.
        </p>
    </div>
    """, unsafe_allow_html=True)

    if lang_choice == "Dual (English + ಕನ್ನಡ)":
        col_en, col_kn = st.columns(2)
        
        with col_en:
            st.markdown("#### 🇬🇧 English Advisory")
            with st.spinner("Generating English AI explanation..."):
                res_en = generate_market_explanation(
                    folder=data_folder,
                    commodity=selected_commodity,
                    variety=selected_variety,
                    threshold_pct=float(threshold),
                    lang="en"
                )
                badge_class = "badge-gemini" if res_en["mode"] == "gemini_ai" else "badge-fallback"
                badge_label = "✨ Powered by Gemini 1.5 Flash AI" if res_en["mode"] == "gemini_ai" else "⚡ Rule-Based Advisory Engine"
                st.markdown(f'<span class="{badge_class}">{badge_label}</span>', unsafe_allow_html=True)
                st.markdown(res_en["explanation"])
                
                audio_en = generate_audio_speech(res_en["explanation"], lang="en")
                if audio_en:
                    st.markdown("##### 🔊 Listen to English Advisory")
                    st.audio(audio_en, format="audio/mp3")

        with col_kn:
            st.markdown("#### 🇮🇳 ಕನ್ನಡ ಮಾರ್ಗದರ್ಶನ (Kannada Advisory)")
            with st.spinner("Generating Kannada AI explanation..."):
                res_kn = generate_market_explanation(
                    folder=data_folder,
                    commodity=selected_commodity,
                    variety=selected_variety,
                    threshold_pct=float(threshold),
                    lang="kn"
                )
                badge_class = "badge-gemini" if res_kn["mode"] == "gemini_ai" else "badge-fallback"
                badge_label = "✨ Powered by Gemini 1.5 Flash AI" if res_kn["mode"] == "gemini_ai" else "⚡ Rule-Based Advisory Engine"
                st.markdown(f'<span class="{badge_class}">{badge_label}</span>', unsafe_allow_html=True)
                st.markdown(res_kn["explanation"])
                
                audio_kn = generate_audio_speech(res_kn["explanation"], lang="kn")
                if audio_kn:
                    st.markdown("##### 🔊 ಕನ್ನಡದಲ್ಲಿ ಆಡಿಯೋ ಕೇಳಿ (Listen in Kannada)")
                    st.audio(audio_kn, format="audio/mp3")
    else:
        target_lang = "kn" if "ಕನ್ನಡ" in lang_choice else "en"
        with st.spinner(f"Generating {'Kannada' if target_lang=='kn' else 'English'} AI explanation..."):
            res = generate_market_explanation(
                folder=data_folder,
                commodity=selected_commodity,
                variety=selected_variety,
                threshold_pct=float(threshold),
                lang=target_lang
            )
            badge_class = "badge-gemini" if res["mode"] == "gemini_ai" else "badge-fallback"
            badge_label = "✨ Powered by Gemini 1.5 Flash AI" if res["mode"] == "gemini_ai" else "⚡ Rule-Based Advisory Engine"
            st.markdown(f'<span class="{badge_class}">{badge_label}</span>', unsafe_allow_html=True)
            st.markdown(res["explanation"])

            audio_bytes = generate_audio_speech(res["explanation"], lang=target_lang)
            if audio_bytes:
                st.markdown(f"##### 🔊 Listen in {'Kannada (ಕನ್ನಡ)' if target_lang=='kn' else 'English'}")
                st.audio(audio_bytes, format="audio/mp3")

    # WhatsApp Share Helper
    st.markdown("---")
    encoded_text = urllib.parse.quote(f"🌾 *Krishi Market Advisor*: Best market for {selected_commodity} ({rec_result['variety']}) is *{rec['recommended_market']}* at ₹{rec['highest_price']:,.0f}/Q (Extra gain: +₹{rec['extra_earnings']:,.0f}/Q).")
    st.markdown(f"""
    <a href="https://api.whatsapp.com/send?text={encoded_text}" target="_blank" style="text-decoration: none;">
        <div style="background-color: #25D366; color: white; padding: 10px 18px; border-radius: 12px; font-weight: 700; display: inline-flex; align-items: center; gap: 8px;">
            💬 Share Today's Advisory on WhatsApp
        </div>
    </a>
    """, unsafe_allow_html=True)


# ── Tab 2: Transport & Net Profit Calculator ──────────────────────────────────
with tab2:
    st.subheader("🚚 Transport Freight & Pure Net Profit Calculator")
    st.markdown("Calculate whether travelling to the recommended market yields **pure extra profit** after paying truck transport fees.")

    col_calc1, col_calc2 = st.columns(2)

    with col_calc1:
        district_options = list(DISTANCES_KM.keys())
        farmer_district = st.selectbox(
            "📍 Select Your Home District / Region",
            options=district_options,
            index=0
        )

        crop_quantity = st.number_input(
            "📦 Crop Quantity to Sell (in Quintals)",
            min_value=1.0,
            max_value=500.0,
            value=20.0,
            step=5.0
        )

        selected_vehicle = st.selectbox(
            "🚛 Transport Vehicle Type",
            options=list(VEHICLE_TYPES.keys()),
            index=0
        )

    with col_calc2:
        calc_result = calculate_net_transport_profit(
            farmer_district=farmer_district,
            target_mandi=rec["recommended_market"],
            lowest_mandi=rec["lowest_market"],
            price_diff_per_quintal=rec["extra_earnings"],
            quantity_quintals=crop_quantity,
            vehicle_type=selected_vehicle
        )

        st.markdown("##### 💵 Financial Calculation Breakdown")
        st.markdown(f"""
        - **Target Mandi**: `{rec['recommended_market']}` (₹{rec['highest_price']:,.0f}/quintal)
        - **Closest/Lowest Mandi**: `{rec['lowest_market']}` (₹{rec['lowest_price']:,.0f}/quintal)
        - **Gross Price Advantage**: **+₹{rec['extra_earnings']:,.0f}** per quintal
        - **Estimated One-Way Distance**: **{calc_result['distance_km']:.0f} km** ({calc_result['round_trip_km']:.0f} km round trip)
        - **Total Gross Extra Revenue** ({crop_quantity:.0f} quintals): **₹{calc_result['gross_extra_revenue']:,.0f}**
        - **Estimated Truck Freight Cost**: **₹{calc_result['estimated_freight_cost']:,.0f}**
        """)

        card_class = "profit-card-green" if calc_result["is_profitable"] else "profit-card-orange"
        profit_title = "🎉 PURE NET EXTRA PROFIT" if calc_result["is_profitable"] else "⚠️ TRANSPORT COST EXCEEDS PRICE GAIN"

        st.markdown(f"""
        <div class="{card_class}">
            <h3 style="margin-top: 0; font-size: 1.35rem;">{profit_title}</h3>
            <div style="font-size: 2.2rem; font-weight: 800; margin: 6px 0;">
                ₹{calc_result['net_extra_profit']:,.0f}
            </div>
            <div>{calc_result['advice']}</div>
        </div>
        """, unsafe_allow_html=True)


# ── Tab 3: Mandi Price Analytics ──────────────────────────────────────────────
with tab3:
    st.subheader("📈 Mandi Price Comparisons & Trends")
    
    col_chart1, col_chart2 = st.columns(2)
    
    with col_chart1:
        st.markdown("##### Modal Price Comparison across Reliable Mandis")
        chart_df = pd.DataFrame([
            {
                "Market": m["market"],
                "Modal Price (₹/Quintal)": m["latest_price"],
                "Status": "Recommended Mandi" if m["market"] == rec["recommended_market"] else "Other Reliable Mandi"
            }
            for m in markets_data
        ])
        
        fig_bar = px.bar(
            chart_df,
            x="Market",
            y="Modal Price (₹/Quintal)",
            color="Status",
            color_discrete_map={
                "Recommended Mandi": "#2d6a4f",
                "Other Reliable Mandi": "#b7e4c7"
            },
            text_auto=",.0f",
            title=f"Latest Prices for {selected_commodity} ({rec_result['variety']})"
        )
        fig_bar.update_layout(xaxis_title="", yaxis_title="Price (₹/Quintal)", showlegend=True)
        st.plotly_chart(fig_bar, width="stretch")

    with col_chart2:
        st.markdown("##### Historical Price Movement over Time")
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
                title="Multi-Day Price Movement Trend"
            )
            fig_line.update_layout(xaxis_title="Date", yaxis_title="Modal Price (₹/Quintal)")
            st.plotly_chart(fig_line, width="stretch")
        else:
            st.info("Insufficient multi-day data points for line chart.")


# ── Tab 4: Detailed Data Table ────────────────────────────────────────────────
with tab4:
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
    "<div style='text-align: center; color: #64748b; font-size: 0.88rem; padding-bottom: 1rem;'>"
    "Krishi Market Advisor 🌾 — Built for Karnataka Farmers · Powered by Agmarknet & Google Gemini AI"
    "</div>",
    unsafe_allow_html=True
)
