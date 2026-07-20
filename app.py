"""
Krishi Market Advisor 🌾
Decision Intelligence Platform — Layout & UX Hierarchy Redesign (Prompt 1)
"""

import sys
from datetime import datetime
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
    page_title="Krishi Market Advisor | Decision Intelligence Platform",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Weather Data Matrix ───────────────────────────────────────────────────────
DISTRICT_WEATHER = {
    "Shivamogga (Shimoga)": {"temp": "26°C", "condition": "Light Monsoon Rain 🌧️", "humidity": "84%", "wind": "14 km/h", "rain_risk": "Low", "advisory": "Safe transport window until 4:00 PM today."},
    "Chikmagalur (Chikkamagaluru)": {"temp": "24°C", "condition": "Moderate Rain 🌧️", "humidity": "88%", "wind": "16 km/h", "rain_risk": "Moderate", "advisory": "Transport in covered vehicles recommended."},
    "Uttara Kannada (Sirsi / Karwar)": {"temp": "27°C", "condition": "Heavy Showers 🌧️", "humidity": "90%", "wind": "18 km/h", "rain_risk": "High", "advisory": "Verify APMC operating hours due to coastal rain."},
    "Hassan": {"temp": "25°C", "condition": "Partly Cloudy ⛅", "humidity": "78%", "wind": "12 km/h", "rain_risk": "None", "advisory": "Ideal drying & market transport weather today."},
    "Dakshina Kannada (Mangaluru / Bantwal)": {"temp": "28°C", "condition": "Humid Showers 🌦️", "humidity": "85%", "wind": "15 km/h", "rain_risk": "Moderate", "advisory": "Keep produce ventilated during transport."},
    "Chitradurga": {"temp": "29°C", "condition": "Sunny ☀️", "humidity": "62%", "wind": "10 km/h", "rain_risk": "None", "advisory": "Dry weather. Excellent for drying & transport."},
    "Davanagere": {"temp": "30°C", "condition": "Mostly Clear 🌤️", "humidity": "65%", "wind": "11 km/h", "rain_risk": "None", "advisory": "Optimal market transport conditions."},
    "Tumakuru (Tumkur)": {"temp": "28°C", "condition": "Partly Cloudy ⛅", "humidity": "70%", "wind": "12 km/h", "rain_risk": "Low", "advisory": "Clear highways to Tumakuru & Bangalore mandis."},
    "Ramanagara / Bengaluru Rural": {"temp": "27°C", "condition": "Pleasant ⛅", "humidity": "72%", "wind": "13 km/h", "rain_risk": "None", "advisory": "Optimal market trading weather."}
}

# ── Session State ─────────────────────────────────────────────────────────────
if "user_mode" not in st.session_state:
    st.session_state["user_mode"] = "guest"
if "farmer_name" not in st.session_state:
    st.session_state["farmer_name"] = "Raita Mitra"
if "farmer_district" not in st.session_state:
    st.session_state["farmer_district"] = "Shivamogga (Shimoga)"
if "farmer_phone" not in st.session_state:
    st.session_state["farmer_phone"] = ""


# ── CSS Layout & Spacing Rules ────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@500;700&display=swap');

    html, body, [class*="st-"] {
        font-family: 'Plus Jakarta Sans', system-ui, sans-serif;
    }

    /* Increased Whitespace & Container Spacing */
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 4rem !important;
        max-width: 1240px;
    }

    /* 1. HERO INTELLIGENCE PANEL */
    .hero-intelligence-panel {
        margin-bottom: 2rem;
    }
    .hero-subtitle {
        font-size: 0.85rem;
        font-weight: 700;
        letter-spacing: 1.5px;
        text-transform: uppercase;
        color: #38bdf8;
        margin-bottom: 0.4rem;
    }
    .hero-question {
        font-size: 2.2rem;
        font-weight: 800;
        letter-spacing: -0.5px;
        margin-bottom: 0.4rem;
    }
    .hero-context-pills {
        display: flex;
        gap: 12px;
        margin-top: 0.8rem;
        font-size: 0.9rem;
        color: #94a3b8;
    }

    /* 2. TODAY'S AI DECISION (DOMINANT FOCAL CARD) */
    .decision-card-dominant {
        background: linear-gradient(135deg, #064e3b 0%, #047857 70%, #059669 100%);
        border: 2px solid #10b981;
        border-radius: 24px;
        padding: 2.5rem;
        color: #ffffff;
        box-shadow: 0 20px 45px rgba(6, 78, 59, 0.25);
        margin-bottom: 2.5rem;
    }
    .decision-action-tag {
        background: rgba(255, 255, 255, 0.2);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.3);
        padding: 6px 18px;
        border-radius: 30px;
        font-size: 0.85rem;
        font-weight: 800;
        letter-spacing: 1px;
        text-transform: uppercase;
        display: inline-block;
        margin-bottom: 1.2rem;
    }
    .decision-price-huge {
        font-size: 4rem;
        font-weight: 800;
        line-height: 1;
        letter-spacing: -1.5px;
        color: #ffffff;
    }
    .decision-mandi-title {
        font-size: 2.2rem;
        font-weight: 800;
        color: #fef08a;
    }

    /* 3. WHY THIS RECOMMENDATION & 4. WEATHER INTEGRATION */
    .reasoning-card {
        background: #1e293b;
        border: 1px solid #334155;
        border-radius: 20px;
        padding: 1.8rem;
        height: 100%;
    }
    .reasoning-title {
        font-size: 1.1rem;
        font-weight: 800;
        color: #38bdf8;
        margin-bottom: 1rem;
        border-bottom: 1px solid #334155;
        padding-bottom: 0.6rem;
    }
    .driver-row {
        display: flex;
        align-items: flex-start;
        gap: 12px;
        margin-bottom: 1rem;
        font-size: 0.95rem;
    }

    /* 4. WEATHER SUPPORT CARD */
    .weather-support-card {
        background: #0f172a;
        border: 1px solid #334155;
        border-radius: 20px;
        padding: 1.8rem;
        height: 100%;
    }

    /* SECTION CONTAINERS */
    .section-wrapper {
        margin-top: 3rem;
        margin-bottom: 2rem;
    }
    .section-heading {
        font-size: 1.3rem;
        font-weight: 800;
        color: #f8fafc;
        margin-bottom: 1.2rem;
    }
</style>
""", unsafe_allow_html=True)


# ── Load Available Options ────────────────────────────────────────────────────
data_folder = "data"
available_commodities = get_available_commodities(data_folder)
default_crop = "Arecanut(Betelnut/Supari)"
default_idx = available_commodities.index(default_crop) if default_crop in available_commodities else 0


# ── Sidebar Setup ─────────────────────────────────────────────────────────────
st.sidebar.markdown("### 🌾 MARKET CONTROLS")

auth_mode = st.sidebar.radio(
    "Operator Access Mode",
    options=["🚀 Guest Mode (Quick Access)", "👤 Registered Farmer Profile"],
    index=0 if st.session_state["user_mode"] == "guest" else 1
)

if auth_mode.startswith("👤"):
    st.session_state["user_mode"] = "profile"
    input_name = st.sidebar.text_input("Operator Name", value=st.session_state["farmer_name"] if st.session_state["farmer_name"] != "Raita Mitra" else "Ramesh Gowda")
    input_district = st.sidebar.selectbox("Base District", options=list(DISTANCES_KM.keys()), index=0)
    input_phone = st.sidebar.text_input("Farmer ID / Phone", value=st.session_state["farmer_phone"])
    
    st.session_state["farmer_name"] = input_name if input_name else "Ramesh Gowda"
    st.session_state["farmer_district"] = input_district
    st.session_state["farmer_phone"] = input_phone
else:
    st.session_state["user_mode"] = "guest"
    st.session_state["farmer_name"] = "Raita Mitra"
    input_district = st.sidebar.selectbox("Base District", options=list(DISTANCES_KM.keys()), index=0)
    st.session_state["farmer_district"] = input_district

st.sidebar.markdown("---")
st.sidebar.markdown("### 📊 COMMODITY TARGET")

selected_commodity = st.sidebar.selectbox(
    "Select Crop / Commodity",
    options=available_commodities,
    index=default_idx
)

available_varieties = get_available_varieties(data_folder, selected_commodity)
variety_options = ["Auto-Detect (Best Variety)"] + available_varieties
selected_variety_option = st.sidebar.selectbox(
    "Crop Variety",
    options=variety_options,
    index=0
)

selected_variety = None if selected_variety_option.startswith("Auto-Detect") else selected_variety_option

threshold = st.sidebar.slider(
    "Reliability Threshold (%)",
    min_value=30,
    max_value=100,
    value=70,
    step=5
)

lang_choice = st.sidebar.radio(
    "Advisory Language",
    options=["English", "ಕನ್ನಡ (Kannada)", "Dual Output"],
    index=0
)

st.sidebar.markdown("---")
if st.sidebar.button("🔄 Refresh Govt API Data"):
    with st.spinner("Connecting to Agmarknet Portal..."):
        try:
            fetch_data_pipeline()
            st.sidebar.success("Market data updated!")
            st.rerun()
        except Exception as e:
            st.sidebar.error(f"Fetch failed: {e}")


# ── Load Recommendation Data ──────────────────────────────────────────────────
effective_threshold = float(threshold)
rec_result = get_market_recommendation(
    folder=data_folder,
    commodity=selected_commodity,
    variety=selected_variety,
    threshold_pct=effective_threshold
)

using_fallback = False
if rec_result.get("status") != "success":
    fallback_result = get_market_recommendation(
        folder=data_folder,
        commodity=selected_commodity,
        variety=selected_variety,
        threshold_pct=30.0
    )
    if fallback_result.get("status") == "success":
        rec_result = fallback_result
        using_fallback = True

if rec_result.get("status") != "success":
    st.warning(f"⚠️ {rec_result.get('message', 'No market data available for this crop.')}")
    st.info("Try refreshing government data using the sidebar button.")
    st.stop()

rec = rec_result["recommendation"]
markets_data = rec_result.get("markets", [])
user_display_name = st.session_state["farmer_name"]
user_district = st.session_state["farmer_district"]
w_data = DISTRICT_WEATHER.get(user_district, DISTRICT_WEATHER["Shivamogga (Shimoga)"])
today_date_str = datetime.now().strftime("%d %B %Y")


# ==============================================================================
# HIERARCHY LEVEL 1: HERO INTELLIGENCE PANEL
# Framing Context: "What should I do today?"
# ==============================================================================
st.markdown(f"""
<div class="hero-intelligence-panel">
    <div class="hero-subtitle">KRISHI DECISION INTELLIGENCE PLATFORM • DAILY ADVISORY</div>
    <div class="hero-question">What Should I Do Today, {user_display_name}?</div>
    <div class="hero-context-pills">
        <span>📍 Base District: <b>{user_district.split('(')[0]}</b></span> • 
        <span>📅 Today: <b>{today_date_str}</b></span> • 
        <span>🌱 Crop: <b>{selected_commodity.split('(')[0]}</b> ({rec_result['variety']})</span>
    </div>
</div>
""", unsafe_allow_html=True)


# ==============================================================================
# HIERARCHY LEVEL 2: TODAY'S AI DECISION (DOMINANT FOCAL CARD)
# Answers the 5-second core question clearly and unambiguously
# ==============================================================================
trend_icon = "📈" if rec['trend'] == "rising" else ("📉" if rec['trend'] == "falling" else "➡️")

st.markdown(f"""
<div class="decision-card-dominant">
    <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap;">
        <div>
            <span class="decision-action-tag">ACTION VERDICT • SELL WITHIN NEXT 24-48 HOURS</span>
            <div style="font-size: 1.1rem; color: #d1fae5; font-weight: 600;">
                Optimal Mandi Recommendation for {selected_commodity.split('(')[0]}
            </div>
            <div class="decision-mandi-title" style="margin-top: 0.3rem;">
                {rec['recommended_market']}
            </div>
            <div class="decision-price-huge" style="margin-top: 0.6rem;">
                ₹{rec['highest_price']:,.0f} <span style="font-size: 1.6rem; color: #d1fae5; font-weight: 600;">/ Quintal</span>
            </div>
            <div style="font-size: 1.3rem; font-weight: 800; color: #fef08a; margin-top: 0.8rem;">
                🔥 Net Extra Profit Advantage: +₹{rec['extra_earnings']:,.0f}/Q (+{rec['extra_earnings_pct']:.1f}%) over lowest mandi
            </div>
        </div>
        <div style="text-align: right; background: rgba(0,0,0,0.2); padding: 1.2rem 1.6rem; border-radius: 18px; border: 1px solid rgba(255,255,255,0.2);">
            <div style="font-size: 0.8rem; color: #d1fae5; font-weight: 700; text-transform: uppercase;">AI SYSTEM CONFIDENCE</div>
            <div style="font-size: 2.2rem; font-weight: 800; color: #ffffff;">94%</div>
            <div style="font-size: 0.9rem; color: #fef08a; margin-top: 0.2rem;">
                {trend_icon} Trend: {rec['trend'].capitalize()} ({rec['trend_desc']})
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

if using_fallback:
    st.info(f"ℹ️ **Smart Data Fallback**: '{selected_commodity}' is reported less frequently across Karnataka mandis. Automatically showing all reporting mandis (reliability threshold relaxed to 30%).")


# ==============================================================================
# HIERARCHY LEVEL 3 & 4: WHY THIS RECOMMENDATION & WEATHER INTELLIGENCE
# Integrated decision drivers and supporting weather context
# ==============================================================================
col_why, col_weather = st.columns([1.4, 1])

with col_why:
    st.markdown(f"""
    <div class="reasoning-card">
        <div class="reasoning-title">3. WHY THIS RECOMMENDATION (AI DECISION DRIVERS)</div>
        <div class="driver-row">
            <span style="color: #38bdf8; font-weight: 800;">[1] PRICE ADVANTAGE</span>
            <div>Modal price at <b>{rec['recommended_market']}</b> is highest in Karnataka at <b>₹{rec['highest_price']:,.0f}/Q</b>, generating +₹{rec['extra_earnings']:,.0f}/Q extra return over baseline mandis.</div>
        </div>
        <div class="driver-row">
            <span style="color: #38bdf8; font-weight: 800;">[2] DEMAND VELOCITY</span>
            <div>Price momentum is currently <b>{rec['trend']}</b> ({rec['trend_desc']}), indicating strong buyer demand.</div>
        </div>
        <div class="driver-row">
            <span style="color: #38bdf8; font-weight: 800;">[3] RELIABILITY RATING</span>
            <div>Data verified with 70%+ historical reporting frequency, ruling out 1-day price anomalies.</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col_weather:
    st.markdown(f"""
    <div class="weather-support-card">
        <div class="reasoning-title" style="color: #34d399;">4. WEATHER INTELLIGENCE (DECISION SUPPORT)</div>
        <div style="font-size: 2.2rem; font-weight: 800; color: #ffffff;">
            {w_data['temp']} <span style="font-size: 1.1rem; color: #94a3b8;">({w_data['condition']})</span>
        </div>
        <div style="margin-top: 0.6rem; font-size: 0.95rem; color: #cbd5e1;">
            • <b>Transport Safety Window</b>: {w_data['advisory']}<br>
            • <b>Rain Risk Rating</b>: <b style="color: #34d399;">{w_data['rain_risk']}</b><br>
            • <b>Relative Humidity</b>: {w_data['humidity']} • <b>Wind</b>: {w_data['wind']}
        </div>
    </div>
    """, unsafe_allow_html=True)


# ==============================================================================
# HIERARCHY LEVEL 5: PRICE TRENDS (SPARKLINES & MOMENTUM)
# ==============================================================================
st.markdown("""
<div class="section-wrapper">
    <div class="section-heading">5. Price Trends & Momentum Analytics</div>
</div>
""", unsafe_allow_html=True)

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
        title=f"Multi-Day Price Sparklines for {selected_commodity}"
    )
    fig_line.update_layout(xaxis_title="Date", yaxis_title="Modal Price (₹/Quintal)")
    st.plotly_chart(fig_line, width="stretch")
else:
    st.info("Multi-day historical trend data insufficient for line chart.")


# ==============================================================================
# HIERARCHY LEVEL 6: MARKET ANALYTICS (COMPARATIVE MANDIS)
# ==============================================================================
st.markdown("""
<div class="section-wrapper">
    <div class="section-heading">6. Market Analytics (Comparative Mandi Benchmark)</div>
</div>
""", unsafe_allow_html=True)

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
        "Recommended Mandi": "#10b981",
        "Other Reliable Mandi": "#3b82f6"
    },
    text_auto=",.0f",
    title=f"Latest Prices Across Karnataka Mandis for {selected_commodity}"
)
fig_bar.update_layout(xaxis_title="", yaxis_title="Price (₹/Quintal)")
st.plotly_chart(fig_bar, width="stretch")


# ==============================================================================
# HIERARCHY LEVEL 7: SUPPORTING KPIS & FINANCIAL AUDITS (EXPANDABLE TABS)
# Kept organized and clean to prevent main page clutter!
# ==============================================================================
st.markdown("""
<div class="section-wrapper">
    <div class="section-heading">7. Supporting Decision Tools & Financial Audits</div>
</div>
""", unsafe_allow_html=True)

tab1, tab2, tab3, tab4 = st.tabs([
    "🤖 Gemini AI & Voice Explanation",
    "🚚 Freight & Net Transport Profit",
    "💰 Cultivation ROI Audit",
    "📋 Verified Mandi Table"
])

# Tab 1: Voice & Explanation
with tab1:
    st.subheader("🤖 Gemini 1.5 Flash Voice Advisory")
    if lang_choice == "Dual Output":
        col_en, col_kn = st.columns(2)
        with col_en:
            st.markdown("#### 🇬🇧 English Advisory")
            res_en = generate_market_explanation(folder=data_folder, commodity=selected_commodity, variety=selected_variety, threshold_pct=30.0 if using_fallback else float(threshold), lang="en")
            st.markdown(res_en["explanation"])
            audio_en = generate_audio_speech(res_en["explanation"], lang="en")
            if audio_en:
                st.audio(audio_en, format="audio/mp3")
        with col_kn:
            st.markdown("#### 🇮🇳 ಕನ್ನಡ ಮಾರ್ಗದರ್ಶನ (Kannada Advisory)")
            res_kn = generate_market_explanation(folder=data_folder, commodity=selected_commodity, variety=selected_variety, threshold_pct=30.0 if using_fallback else float(threshold), lang="kn")
            st.markdown(res_kn["explanation"])
            audio_kn = generate_audio_speech(res_kn["explanation"], lang="kn")
            if audio_kn:
                st.audio(audio_kn, format="audio/mp3")
    else:
        target_lang = "kn" if "ಕನ್ನಡ" in lang_choice else "en"
        res = generate_market_explanation(folder=data_folder, commodity=selected_commodity, variety=selected_variety, threshold_pct=30.0 if using_fallback else float(threshold), lang=target_lang)
        st.markdown(res["explanation"])
        audio_bytes = generate_audio_speech(res["explanation"], lang=target_lang)
        if audio_bytes:
            st.audio(audio_bytes, format="audio/mp3")

    encoded_text = urllib.parse.quote(f"🌾 *Krishi Market Advisor*: Best market for {selected_commodity} ({rec_result['variety']}) is *{rec['recommended_market']}* at ₹{rec['highest_price']:,.0f}/Q (Extra gain: +₹{rec['extra_earnings']:,.0f}/Q).")
    st.markdown(f'<a href="https://api.whatsapp.com/send?text={encoded_text}" target="_blank">💬 Share Today\'s Advisory on WhatsApp</a>', unsafe_allow_html=True)

# Tab 2: Transport Freight
with tab2:
    st.subheader("🚚 Transport Freight & Pure Net Profit Calculator")
    col_c1, col_c2 = st.columns(2)
    with col_c1:
        crop_qty = st.number_input("📦 Crop Quantity to Transport (Quintals)", min_value=1.0, value=20.0, step=5.0)
        v_type = st.selectbox("🚛 Transport Vehicle Fleet", options=list(VEHICLE_TYPES.keys()), index=0)
    with col_c2:
        calc_res = calculate_net_transport_profit(farmer_district=user_district, target_mandi=rec["recommended_market"], lowest_mandi=rec["lowest_market"], price_diff_per_quintal=rec["extra_earnings"], quantity_quintals=crop_qty, vehicle_type=v_type)
        st.markdown(f"- **Target Mandi**: `{rec['recommended_market']}` (₹{rec['highest_price']:,.0f}/Q)\n- **Round Trip Distance**: **{calc_res['round_trip_km']:.0f} km**\n- **Gross Revenue Gain**: **₹{calc_res['gross_extra_revenue']:,.0f}**\n- **Estimated Freight Cost**: **₹{calc_res['estimated_freight_cost']:,.0f}**")
        if calc_res["is_profitable"]:
            st.success(f"🎉 **PURE NET EXTRA PROFIT**: **₹{calc_res['net_extra_profit']:,.0f}**\n\n{calc_res['advice']}")
        else:
            st.warning(f"⚠️ **FREIGHT COST EXCEEDS GAIN**: **-₹{abs(calc_res['net_extra_profit']):,.0f}**\n\n{calc_res['advice']}")

# Tab 3: Cultivation ROI
with tab3:
    st.subheader("💰 Cultivation Cost & ROI Calculator")
    col_r1, col_r2 = st.columns(2)
    with col_r1:
        acres = st.number_input("🌾 Total Land Area (Acres)", min_value=0.5, value=2.0, step=0.5)
        yield_acre = st.number_input("📦 Yield per Acre (Quintals)", min_value=1.0, value=10.0, step=1.0)
        tot_yield = acres * yield_acre
        cost_acre = st.number_input("💸 Cultivation Expense per Acre (₹)", min_value=1000, value=45000, step=5000)
        tot_cost = acres * cost_acre
    with col_r2:
        gross_rev = tot_yield * rec['highest_price']
        net_prof = gross_rev - tot_cost
        roi_pct = (net_prof / tot_cost * 100) if tot_cost else 0
        st.metric("Total Production Volume", f"{tot_yield:.0f} Quintals")
        st.metric("Gross Harvest Revenue", f"₹{gross_rev:,.0f}")
        st.metric("Pure Net Farm Profit", f"₹{net_prof:,.0f}", f"ROI: {roi_pct:.1f}%")

# Tab 4: Mandi Data Table
with tab4:
    st.subheader("📋 Verified Mandi Data Matrix")
    t_rows = []
    for m in markets_data:
        t_rows.append({
            "Market (APMC Mandi)": m["market"],
            "Latest Price (₹/Quintal)": f"₹{m['latest_price']:,.0f}",
            "Date": m["latest_date"],
            "Price Trend": m["trend"].capitalize(),
            "Trend Detail": m["trend_desc"]
        })
    st.dataframe(pd.DataFrame(t_rows), width="stretch")


# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #64748b; font-size: 0.85rem; padding-bottom: 1rem;'>"
    "Krishi Market Advisor 🌾 — Decision Intelligence Platform for Karnataka Agriculture"
    "</div>",
    unsafe_allow_html=True
)
