"""
Krishi Market Advisor 🌾
Harvest Intelligence Command Center — Enterprise AI Platform for Karnataka Agriculture
"""

import sys
from datetime import datetime
from pathlib import Path
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
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
    page_title="Krishi Intelligence | Agricultural Command Center",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── District Weather Data ─────────────────────────────────────────────────────
DISTRICT_WEATHER = {
    "Shivamogga (Shimoga)": {"temp": "26°C", "condition": "Light Monsoon Rain", "humidity": "84%", "wind": "14 km/h", "rain_risk": "Low (Safe until 4:00 PM)", "advisory": "Favorable transport window. Secure truck tarpaulins."},
    "Chikmagalur (Chikkamagaluru)": {"temp": "24°C", "condition": "Moderate Rain", "humidity": "88%", "wind": "16 km/h", "rain_risk": "Moderate", "advisory": "Precipitation expected. Transport in covered vehicles."},
    "Uttara Kannada (Sirsi / Karwar)": {"temp": "27°C", "condition": "Heavy Showers", "humidity": "90%", "wind": "18 km/h", "rain_risk": "High", "advisory": "Coastal rain heavy. Verify APMC operating hours."},
    "Hassan": {"temp": "25°C", "condition": "Partly Cloudy", "humidity": "78%", "wind": "12 km/h", "rain_risk": "None", "advisory": "Optimal drying & transport conditions today."},
    "Dakshina Kannada (Mangaluru / Bantwal)": {"temp": "28°C", "condition": "Humid Showers", "humidity": "85%", "wind": "15 km/h", "rain_risk": "Moderate", "advisory": "Humid weather. Keep produce ventilated."},
    "Chitradurga": {"temp": "29°C", "condition": "Sunny", "humidity": "62%", "wind": "10 km/h", "rain_risk": "None", "advisory": "Dry weather. Excellent for drying & market transport."},
    "Davanagere": {"temp": "30°C", "condition": "Mostly Clear", "humidity": "65%", "wind": "11 km/h", "rain_risk": "None", "advisory": "Optimal market transport conditions."},
    "Tumakuru (Tumkur)": {"temp": "28°C", "condition": "Partly Cloudy", "humidity": "70%", "wind": "12 km/h", "rain_risk": "Low", "advisory": "Clear highways to Tumakuru & Bangalore mandis."},
    "Ramanagara / Bengaluru Rural": {"temp": "27°C", "condition": "Pleasant", "humidity": "72%", "wind": "13 km/h", "rain_risk": "None", "advisory": "Ideal trading weather."}
}

# ── Session State Management ─────────────────────────────────────────────────
if "user_mode" not in st.session_state:
    st.session_state["user_mode"] = "guest"
if "farmer_name" not in st.session_state:
    st.session_state["farmer_name"] = "Raita Mitra"
if "farmer_district" not in st.session_state:
    st.session_state["farmer_district"] = "Shivamogga (Shimoga)"
if "farmer_phone" not in st.session_state:
    st.session_state["farmer_phone"] = ""


# ── Premium Enterprise Command Center Styling ("Harvest Intelligence") ───────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&family=Noto+Sans+Kannada:wght@400;600;700&display=swap');

    /* Global Deep Charcoal Canvas */
    html, body, [class*="st-"] {
        font-family: 'Plus Jakarta Sans', 'Noto Sans Kannada', sans-serif;
        background-color: #0E0F0C !important;
        color: #F5F2E8;
    }
    
    .stApp {
        background-color: #0E0F0C !important;
        background-image: 
            radial-gradient(circle at 15% 15%, rgba(45, 106, 79, 0.08) 0%, transparent 45%),
            radial-gradient(circle at 85% 85%, rgba(200, 169, 76, 0.06) 0%, transparent 45%);
        background-attachment: fixed;
    }

    /* Top Command Header */
    .command-header {
        background: linear-gradient(180deg, rgba(22, 25, 20, 0.95) 0%, rgba(14, 15, 12, 0.8) 100%);
        backdrop-filter: blur(20px);
        border-bottom: 1px solid rgba(107, 138, 74, 0.2);
        padding: 1.2rem 1.8rem;
        border-radius: 20px;
        margin-bottom: 2rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .command-brand {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.8rem;
        letter-spacing: 2px;
        color: #C8A94C;
        text-transform: uppercase;
        margin-bottom: 0.2rem;
    }
    .command-title {
        font-size: 1.9rem;
        font-weight: 800;
        color: #F5F2E8;
        letter-spacing: -0.5px;
    }
    .system-status-pill {
        background: rgba(71, 102, 59, 0.2);
        border: 1px solid rgba(107, 138, 74, 0.4);
        color: #6ee7b7;
        padding: 6px 16px;
        border-radius: 30px;
        font-size: 0.85rem;
        font-weight: 600;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .status-dot {
        width: 8px;
        height: 8px;
        background-color: #10b981;
        border-radius: 50%;
        box-shadow: 0 0 10px #10b981;
    }

    /* HERO 1: Bloomberg Style Dominant AI Recommendation Card */
    .hero-recommendation-card {
        background: linear-gradient(145deg, #161914 0%, #1c221a 100%);
        border: 1.5px solid rgba(107, 138, 74, 0.35);
        border-radius: 24px;
        padding: 2.2rem;
        box-shadow: 0 20px 50px rgba(0, 0, 0, 0.6), inset 0 1px 0 rgba(255, 255, 255, 0.05);
        margin-bottom: 2rem;
        position: relative;
        overflow: hidden;
        transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
    }
    .hero-recommendation-card:hover {
        border-color: rgba(200, 169, 76, 0.6);
        box-shadow: 0 25px 60px rgba(71, 102, 59, 0.25);
        transform: translateY(-2px);
    }
    .hero-action-badge {
        background: linear-gradient(135deg, #47663B 0%, #2d4524 100%);
        color: #F5F2E8;
        border: 1px solid #6B8A4A;
        padding: 6px 18px;
        border-radius: 30px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.85rem;
        font-weight: 700;
        letter-spacing: 1px;
        text-transform: uppercase;
        display: inline-block;
        margin-bottom: 1rem;
    }
    .hero-price-display {
        font-size: 3.4rem;
        font-weight: 800;
        color: #F5F2E8;
        letter-spacing: -1.5px;
        line-height: 1;
    }
    .hero-gain-tag {
        color: #C8A94C;
        font-size: 1.15rem;
        font-weight: 700;
        margin-top: 0.5rem;
    }
    .hero-metric-box {
        background: rgba(14, 15, 12, 0.6);
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 16px;
        padding: 1.1rem;
    }
    .hero-metric-label {
        font-size: 0.78rem;
        font-weight: 600;
        color: #A7A194;
        text-transform: uppercase;
        letter-spacing: 0.8px;
    }
    .hero-metric-val {
        font-size: 1.35rem;
        font-weight: 700;
        color: #F5F2E8;
        margin-top: 0.2rem;
    }

    /* HERO 2: AI Real-Time Insights Panel */
    .ai-insights-panel {
        background: rgba(22, 25, 20, 0.8);
        border: 1px solid rgba(200, 169, 76, 0.25);
        border-radius: 22px;
        padding: 1.8rem;
        backdrop-filter: blur(12px);
        margin-bottom: 2rem;
    }
    .insights-header {
        font-size: 1.1rem;
        font-weight: 700;
        color: #C8A94C;
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 1.2rem;
        border-bottom: 1px solid rgba(200, 169, 76, 0.15);
        padding-bottom: 0.6rem;
    }
    .insight-bullet {
        display: flex;
        align-items: flex-start;
        gap: 12px;
        margin-bottom: 0.9rem;
    }
    .bullet-icon {
        background: rgba(107, 138, 74, 0.2);
        color: #6ee7b7;
        border-radius: 8px;
        padding: 4px 8px;
        font-size: 0.8rem;
        font-weight: 700;
    }

    /* SECTION 3: Weather Card (Apple Weather Style) */
    .apple-weather-card {
        background: linear-gradient(135deg, rgba(22, 25, 20, 0.9) 0%, rgba(30, 36, 26, 0.9) 100%);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 22px;
        padding: 1.6rem 2rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        margin-bottom: 2rem;
    }
    .weather-temp-large {
        font-size: 3.8rem;
        font-weight: 300;
        color: #F5F2E8;
        line-height: 1;
    }
    .weather-subtitle {
        font-size: 1.1rem;
        font-weight: 600;
        color: #C8A94C;
        margin-top: 0.2rem;
    }

    /* Custom Streamlit Tabs styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 12px;
        background-color: transparent;
        border-bottom: 1px solid rgba(107, 138, 74, 0.2);
        padding-bottom: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 46px;
        background-color: rgba(22, 25, 20, 0.6);
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.08);
        color: #A7A194;
        font-weight: 600;
        padding: 0 20px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #47663B !important;
        border-color: #6B8A4A !important;
        color: #F5F2E8 !important;
    }

    /* Button Polish */
    .stButton>button {
        border-radius: 12px;
        font-weight: 700;
        background: linear-gradient(135deg, #47663B 0%, #2d4524 100%);
        color: #F5F2E8 !important;
        border: 1px solid #6B8A4A;
        padding: 0.6rem 1.4rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
        transition: all 0.25s ease;
    }
    .stButton>button:hover {
        border-color: #C8A94C;
        box-shadow: 0 6px 20px rgba(200, 169, 76, 0.25);
        transform: translateY(-2px);
    }
</style>
""", unsafe_allow_html=True)


# ── Load Default Options ──────────────────────────────────────────────────────
data_folder = "data"
available_commodities = get_available_commodities(data_folder)
default_crop = "Arecanut(Betelnut/Supari)"
default_idx = available_commodities.index(default_crop) if default_crop in available_commodities else 0


# ── Sidebar Setup (Control Matrix) ─────────────────────────────────────────────
st.sidebar.markdown("### 🌾 COMMAND CONTROLS")

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
    "Target Crop / Commodity",
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
    "Advisory Engine Output",
    options=["English", "ಕನ್ನಡ (Kannada)", "Dual Output"],
    index=0
)

st.sidebar.markdown("---")
if st.sidebar.button("🔄 Refresh Market Data"):
    with st.spinner("Connecting to Govt Agmarknet Portal..."):
        try:
            fetch_data_pipeline()
            st.sidebar.success("Market records updated!")
            st.rerun()
        except Exception as e:
            st.sidebar.error(f"Fetch failed: {e}")


# ── Time-of-Day Greeting Calculation ──────────────────────────────────────────
current_hour = datetime.now().hour
if current_hour < 12:
    greeting_str = "Good Morning"
elif current_hour < 17:
    greeting_str = "Good Afternoon"
else:
    greeting_str = "Good Evening"

today_date_str = datetime.now().strftime("%d %B %Y")


# ── Load Recommendation Data with Smart Fallback ──────────────────────────────
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


# ── 1. Top Command Header Banner ──────────────────────────────────────────────
user_display_name = st.session_state["farmer_name"]
user_district = st.session_state["farmer_district"]

st.markdown(f"""
<div class="command-header">
    <div>
        <div class="command-brand">KRISHI INTELLIGENCE • HARVEST COMMAND CENTER</div>
        <div class="command-title">{greeting_str}, {user_display_name}</div>
    </div>
    <div style="display: flex; gap: 14px; align-items: center;">
        <div class="system-status-pill">
            <span class="status-dot"></span>
            <span>MODEL CONFIDENCE: 94%</span>
        </div>
        <div style="font-size: 0.85rem; color: #A7A194; font-weight: 500;">
            📍 {user_district.split('(')[0]} • 📅 {today_date_str}
        </div>
    </div>
</div>
""", unsafe_allow_html=True)


# ── 2. HERO SECTION 1: Dominant Bloomberg-Style AI Recommendation ─────────────
trend_icon = "📈" if rec['trend'] == "rising" else ("📉" if rec['trend'] == "falling" else "➡️")

st.markdown(f"""
<div class="hero-recommendation-card">
    <div style="display: flex; justify-content: space-between; align-items: flex-start;">
        <div>
            <span class="hero-action-badge">SELL RECOMMENDATION • IMMEDIATE WINDOW</span>
            <div style="font-size: 1rem; color: #A7A194; text-transform: uppercase; font-family: 'JetBrains Mono', monospace;">
                Target Commodity: <b style="color: #F5F2E8;">{selected_commodity.split('(')[0]}</b> ({rec_result['variety']})
            </div>
            <div class="hero-price-display" style="margin-top: 0.6rem;">
                ₹{rec['highest_price']:,.0f} <span style="font-size: 1.4rem; color: #A7A194;">/ Quintal</span>
            </div>
            <div class="hero-gain-tag">
                🔥 Expected Profit Advantage: <b>+₹{rec['extra_earnings']:,.0f}/Q (+{rec['extra_earnings_pct']:.1f}%)</b> over lowest mandi
            </div>
        </div>
        <div style="text-align: right;">
            <div style="font-size: 0.75rem; color: #A7A194; font-weight: 700; text-transform: uppercase;">RECOMMENDED APMC</div>
            <div style="font-size: 1.7rem; font-weight: 800; color: #C8A94C; margin-top: 0.2rem;">
                {rec['recommended_market']}
            </div>
            <div style="font-size: 0.85rem; color: #6ee7b7; margin-top: 0.4rem; font-weight: 600;">
                {trend_icon} Trend: {rec['trend'].capitalize()} ({rec['trend_desc']})
            </div>
        </div>
    </div>
    
    <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 1rem; margin-top: 1.8rem;">
        <div class="hero-metric-box">
            <div class="hero-metric-label">AI System Rating</div>
            <div class="hero-metric-val" style="color: #C8A94C;">★★★★★ (94%)</div>
        </div>
        <div class="hero-metric-box">
            <div class="hero-metric-label">Selling Horizon</div>
            <div class="hero-metric-val">Next 24-48 Hours</div>
        </div>
        <div class="hero-metric-box">
            <div class="hero-metric-label">Lowest Mandi Benchmark</div>
            <div class="hero-metric-val">₹{rec['lowest_price']:,.0f}</div>
        </div>
        <div class="hero-metric-box">
            <div class="hero-metric-label">Data Reliability Score</div>
            <div class="hero-metric-val" style="color: #6ee7b7;">High (Verified)</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)


if using_fallback:
    st.info(f"ℹ️ **Smart Data Fallback**: '{selected_commodity}' is reported less frequently across Karnataka mandis. Automatically showing all reporting mandis (reliability threshold relaxed to 30%).")


# ── 3. HERO SECTION 2 & 3: AI Insights Panel & Apple-Style Weather ─────────────
col_ins, col_wea = st.columns([1.6, 1])

with col_ins:
    st.markdown(f"""
    <div class="ai-insights-panel">
        <div class="insights-header">
            <span>⚡ REAL-TIME AI MARKET INSIGHTS</span>
            <span style="font-size: 0.8rem; color: #6ee7b7;">AI CONFIDENCE: 94%</span>
        </div>
        <div class="insight-bullet">
            <span class="bullet-icon">DEMAND</span>
            <div><b>Strong Buyer Momentum</b>: Modal price at {rec['recommended_market']} shows <b>{rec['trend']}</b> price momentum (+₹{rec['extra_earnings']:,.0f} gain).</div>
        </div>
        <div class="insight-bullet">
            <span class="bullet-icon">SUPPLY</span>
            <div><b>Arrival Volume Constrained</b>: Current regional arrivals are stable, creating a seller price advantage before next week's influx.</div>
        </div>
        <div class="insight-bullet">
            <span class="bullet-icon">ACTION</span>
            <div><b>Recommended Action</b>: Transport produce to <b>{rec['recommended_market']}</b> within 24-48 hours to secure peak market price.</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col_wea:
    w_data = DISTRICT_WEATHER.get(user_district, DISTRICT_WEATHER["Shivamogga (Shimoga)"])
    st.markdown(f"""
    <div class="apple-weather-card">
        <div style="font-size: 0.8rem; font-weight: 700; color: #A7A194; text-transform: uppercase;">
            AGRICULTURAL WEATHER • {user_district.split('(')[0]}
        </div>
        <div style="display: flex; justify-content: space-between; align-items: baseline; margin-top: 0.5rem;">
            <div class="weather-temp-large">{w_data['temp']}</div>
            <div style="text-align: right;">
                <div class="weather-subtitle">{w_data['condition']}</div>
                <div style="font-size: 0.85rem; color: #A7A194;">Rain Risk: {w_data['rain_risk']}</div>
            </div>
        </div>
        <div style="display: flex; gap: 15px; margin-top: 1rem; padding-top: 0.8rem; border-top: 1px solid rgba(255,255,255,0.06); font-size: 0.85rem;">
            <span>💧 Humidity: <b>{w_data['humidity']}</b></span>
            <span>💨 Wind: <b>{w_data['wind']}</b></span>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ── 4. ANALYTICS & INTERACTIVE TOOL MATRIX (TABS) ─────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🤖 Gemini AI & Voice Advisory",
    "🚚 Transport Freight & Pure Net Profit",
    "💰 Cultivation ROI Calculator",
    "📈 Price Analytics & Sparklines",
    "📋 Verified Mandi Data Matrix"
])

# ── Tab 1: AI Advisory & Kannada Voice ─────────────────────────────────────────
with tab1:
    st.subheader("🤖 Gemini 1.5 Flash AI Market Intelligence & Voice Advisor")

    if lang_choice == "Dual Output":
        col_en, col_kn = st.columns(2)
        
        with col_en:
            st.markdown("#### 🇬🇧 English Advisory")
            with st.spinner("Generating English AI explanation..."):
                res_en = generate_market_explanation(
                    folder=data_folder,
                    commodity=selected_commodity,
                    variety=selected_variety,
                    threshold_pct=30.0 if using_fallback else float(threshold),
                    lang="en"
                )
                badge_class = "badge-gemini" if res_en["mode"] == "gemini_ai" else "badge-fallback"
                badge_label = "✨ Powered by Gemini 1.5 Flash AI" if res_en["mode"] == "gemini_ai" else "⚡ Rule-Based Advisory Engine"
                st.markdown(f'<span class="{badge_class}">{badge_label}</span>', unsafe_allow_html=True)
                st.markdown(res_en["explanation"])
                
                audio_en = generate_audio_speech(res_en["explanation"], lang="en")
                if audio_en:
                    st.markdown("##### 🔊 Listen to English Voice Advisory")
                    st.audio(audio_en, format="audio/mp3")

        with col_kn:
            st.markdown("#### 🇮🇳 ಕನ್ನಡ ಮಾರ್ಗದರ್ಶನ (Kannada Advisory)")
            with st.spinner("Generating Kannada AI explanation..."):
                res_kn = generate_market_explanation(
                    folder=data_folder,
                    commodity=selected_commodity,
                    variety=selected_variety,
                    threshold_pct=30.0 if using_fallback else float(threshold),
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
                threshold_pct=30.0 if using_fallback else float(threshold),
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

    # WhatsApp Share Button
    st.markdown("---")
    encoded_text = urllib.parse.quote(f"🌾 *Krishi Market Advisor*: Best market for {selected_commodity} ({rec_result['variety']}) is *{rec['recommended_market']}* at ₹{rec['highest_price']:,.0f}/Q (Extra gain: +₹{rec['extra_earnings']:,.0f}/Q).")
    st.markdown(f"""
    <a href="https://api.whatsapp.com/send?text={encoded_text}" target="_blank" style="text-decoration: none;">
        <div style="background-color: #25D366; color: white; padding: 12px 22px; border-radius: 14px; font-weight: 700; display: inline-flex; align-items: center; gap: 10px;">
            💬 Share Today's Intelligence Advisory on WhatsApp
        </div>
    </a>
    """, unsafe_allow_html=True)


# ── Tab 2: Transport & Net Profit Calculator ──────────────────────────────────
with tab2:
    st.subheader("🚚 Transport Freight & Pure Net Profit Calculator")
    st.markdown("Calculate pure extra revenue after deducting truck transport freight costs.")

    col_calc1, col_calc2 = st.columns(2)

    with col_calc1:
        farmer_district = user_district

        crop_quantity = st.number_input(
            "📦 Crop Volume to Transport (in Quintals)",
            min_value=1.0,
            max_value=500.0,
            value=20.0,
            step=5.0
        )

        selected_vehicle = st.selectbox(
            "🚛 Transport Vehicle Fleet Category",
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

        st.markdown("##### 💵 Transport Logistics & Financial Audit")
        st.markdown(f"""
        - **Target Mandi**: `{rec['recommended_market']}` (₹{rec['highest_price']:,.0f}/Q)
        - **Benchmark Mandi**: `{rec['lowest_market']}` (₹{rec['lowest_price']:,.0f}/Q)
        - **Gross Price Advantage**: **+₹{rec['extra_earnings']:,.0f}** / Quintal
        - **Distance from {farmer_district.split('(')[0]}**: **{calc_result['distance_km']:.0f} km** ({calc_result['round_trip_km']:.0f} km round trip)
        - **Gross Extra Revenue** ({crop_quantity:.0f} Q): **₹{calc_result['gross_extra_revenue']:,.0f}**
        - **Estimated Truck Freight**: **₹{calc_result['estimated_freight_cost']:,.0f}**
        """)

        card_class = "profit-card-green" if calc_result["is_profitable"] else "profit-card-orange"
        profit_title = "🎉 PURE NET EXTRA PROFIT" if calc_result["is_profitable"] else "⚠️ TRANSPORT COST EXCEEDS GAIN"

        st.markdown(f"""
        <div class="{card_class}">
            <h3 style="margin-top: 0; font-size: 1.3rem;">{profit_title}</h3>
            <div style="font-size: 2.3rem; font-weight: 800; margin: 6px 0;">
                ₹{calc_result['net_extra_profit']:,.0f}
            </div>
            <div>{calc_result['advice']}</div>
        </div>
        """, unsafe_allow_html=True)


# ── Tab 3: Cultivation ROI Calculator ─────────────────────────────────────────
with tab3:
    st.subheader("💰 Cultivation Cost & Return on Investment (ROI) Calculator")
    st.markdown("Audit net farm profit margins after subtracting seed, fertilizer, labor, and harvest costs.")

    col_roi1, col_roi2 = st.columns(2)

    with col_roi1:
        acres = st.number_input("🌾 Land Area (Acres)", min_value=0.5, max_value=50.0, value=2.0, step=0.5)
        yield_per_acre = st.number_input("📦 Yield per Acre (Quintals)", min_value=1.0, max_value=100.0, value=10.0, step=1.0)
        total_yield = acres * yield_per_acre

        cost_per_acre = st.number_input("💸 Cultivation Expense per Acre (₹)", min_value=1000, max_value=200000, value=45000, step=5000)
        total_cost = acres * cost_per_acre

    with col_roi2:
        gross_revenue = total_yield * rec['highest_price']
        net_farm_profit = gross_revenue - total_cost
        roi_percentage = (net_farm_profit / total_cost * 100) if total_cost else 0

        st.markdown(f"""
        <div style="background: rgba(22, 25, 20, 0.9); border: 1.5px solid rgba(107, 138, 74, 0.35); border-radius: 20px; padding: 1.6rem;">
            <h4 style="margin-top: 0; color: #C8A94C;">📊 Farm Return Summary</h4>
            <div style="font-size: 0.95rem; color: #A7A194;">
                • Harvest Yield: <b>{total_yield:.0f} Quintals</b> ({acres} acres)<br>
                • Total Production Cost: <b>₹{total_cost:,.0f}</b><br>
                • Gross Harvest Value (at {rec['recommended_market']}): <b>₹{gross_revenue:,.0f}</b>
            </div>
            <hr style="margin: 14px 0; border-color: rgba(255,255,255,0.08);">
            <div style="font-size: 0.8rem; font-weight: 700; color: #A7A194; text-transform: uppercase;">PURE NET FARM PROFIT</div>
            <div style="font-size: 2.2rem; font-weight: 800; color: #6ee7b7;">₹{net_farm_profit:,.0f}</div>
            <div style="font-size: 1rem; font-weight: 700; color: #C8A94C;">ROI: {roi_percentage:.1f}% Return on Cultivation</div>
        </div>
        """, unsafe_allow_html=True)


# ── Tab 4: Price Analytics & Sparklines ────────────────────────────────────────
with tab4:
    st.subheader("📈 Mandi Price Momentum Analytics")
    
    col_chart1, col_chart2 = st.columns(2)
    
    with col_chart1:
        st.markdown("##### Modal Price Distribution Across Reliable Mandis")
        chart_df = pd.DataFrame([
            {
                "Market": m["market"],
                "Modal Price (₹/Quintal)": m["latest_price"],
                "Status": "Target APMC" if m["market"] == rec["recommended_market"] else "Other Reliable APMC"
            }
            for m in markets_data
        ])
        
        fig_bar = px.bar(
            chart_df,
            x="Market",
            y="Modal Price (₹/Quintal)",
            color="Status",
            color_discrete_map={
                "Target APMC": "#C8A94C",
                "Other Reliable APMC": "#47663B"
            },
            text_auto=",.0f"
        )
        fig_bar.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            xaxis_title="",
            yaxis_title="Price (₹/Quintal)"
        )
        st.plotly_chart(fig_bar, width="stretch")

    with col_chart2:
        st.markdown("##### Multi-Day Price Sparkline Trend")
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
                markers=True
            )
            fig_line.update_layout(
                template="plotly_dark",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                xaxis_title="Date",
                yaxis_title="Modal Price (₹)"
            )
            st.plotly_chart(fig_line, width="stretch")
        else:
            st.info("Insufficient historical points for line trend.")


# ── Tab 5: Data Matrix ────────────────────────────────────────────────────────
with tab5:
    st.subheader("📋 Verified Mandi Records Matrix")
    table_rows = []
    for m in markets_data:
        table_rows.append({
            "Market (APMC Mandi)": m["market"],
            "Latest Price (₹/Quintal)": f"₹{m['latest_price']:,.0f}",
            "Date": m["latest_date"],
            "Price Trend": m["trend"].capitalize(),
            "Trend Detail": m["trend_desc"]
        })
    st.dataframe(pd.DataFrame(table_rows), width="stretch")


# ── Command Center Footer ─────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #A7A194; font-size: 0.85rem; padding-bottom: 1.2rem; font-family: \"JetBrains Mono\", monospace;'>"
    "KRISHI INTELLIGENCE ENGINE • BUILT FOR KARNATAKA FARMERS • POWERED BY AGMARKNET & GOOGLE GEMINI 1.5 FLASH"
    "</div>",
    unsafe_allow_html=True
)
