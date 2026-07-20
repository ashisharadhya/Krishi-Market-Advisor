"""
Krishi Market Advisor 🌾
Farmer-First Personalised Dashboard with Farmer Profile, Guest Mode & Agricultural Weather
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
    page_title="Krishi Market Advisor 🌾 | ಕರ್ನಾಟಕ ಕೃಷಿ ಮಾರುಕಟ್ಟೆ ಸಲಹೆಗಾರ",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Weather Data Matrix for Karnataka Districts ──────────────────────────────
DISTRICT_WEATHER = {
    "Shivamogga (Shimoga)": {"temp": "26°C", "condition": "Light Monsoon Rain 🌧️", "humidity": "84%", "wind": "14 km/h", "advisory": "Favorable road transport weather. Secure crop tarpaulins."},
    "Chikmagalur (Chikkamagaluru)": {"temp": "24°C", "condition": "Moderate Rain 🌧️", "humidity": "88%", "wind": "16 km/h", "advisory": "Precipitation expected. Transport in covered vehicles."},
    "Uttara Kannada (Sirsi / Karwar)": {"temp": "27°C", "condition": "Heavy Showers 🌧️", "humidity": "90%", "wind": "18 km/h", "advisory": "Coastal rain heavy. Check APMC operating hours."},
    "Hassan": {"temp": "25°C", "condition": "Partly Cloudy ⛅", "humidity": "78%", "wind": "12 km/h", "advisory": "Good drying & transport conditions today."},
    "Dakshina Kannada (Mangaluru / Bantwal)": {"temp": "28°C", "condition": "Humid Showers 🌦️", "humidity": "85%", "wind": "15 km/h", "advisory": "Humid weather. Keep produce ventilated."},
    "Chitradurga": {"temp": "29°C", "condition": "Sunny ☀️", "humidity": "62%", "wind": "10 km/h", "advisory": "Dry weather. Excellent for drying & market transport."},
    "Davanagere": {"temp": "30°C", "condition": "Mostly Clear 🌤️", "humidity": "65%", "wind": "11 km/h", "advisory": "Optimal market transport conditions."},
    "Tumakuru (Tumkur)": {"temp": "28°C", "condition": "Partly Cloudy ⛅", "humidity": "70%", "wind": "12 km/h", "advisory": "Clear roads to Tumakuru & Bangalore mandis."},
    "Ramanagara / Bengaluru Rural": {"temp": "27°C", "condition": "Pleasant ⛅", "humidity": "72%", "wind": "13 km/h", "advisory": "Ideal market trading weather."}
}


# ── Session State Management (Profile & Guest Mode) ─────────────────────────
if "user_mode" not in st.session_state:
    st.session_state["user_mode"] = "guest"  # default guest mode
if "farmer_name" not in st.session_state:
    st.session_state["farmer_name"] = "ರೈತ ಮಿತ್ರ (Farmer Friend)"
if "farmer_district" not in st.session_state:
    st.session_state["farmer_district"] = "Shivamogga (Shimoga)"
if "farmer_phone" not in st.session_state:
    st.session_state["farmer_phone"] = ""


# ── Custom CSS Styling ────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&family=Noto+Sans+Kannada:wght@400;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', 'Noto Sans Kannada', system-ui, sans-serif;
    }

    /* Welcome Header Banner */
    .welcome-card {
        background: linear-gradient(135deg, #1b4332 0%, #2d6a4f 70%, #40916c 100%);
        border-radius: 20px;
        padding: 1.8rem 2.2rem;
        color: #ffffff;
        box-shadow: 0 10px 30px rgba(27, 67, 50, 0.18);
        margin-bottom: 1.5rem;
    }
    .welcome-greeting {
        font-size: 2.2rem;
        font-weight: 800;
        color: #f4f1ea;
        margin-bottom: 0.3rem;
    }
    .meta-pills-row {
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
        margin-top: 0.8rem;
    }
    .meta-pill {
        background: rgba(255, 255, 255, 0.15);
        backdrop-filter: blur(8px);
        border: 1px solid rgba(255, 255, 255, 0.25);
        padding: 6px 14px;
        border-radius: 30px;
        font-size: 0.88rem;
        font-weight: 600;
        color: #e8f5e9;
    }

    /* Agricultural Weather Card */
    .weather-card {
        background: linear-gradient(135deg, #fefae0 0%, #faedcd 100%);
        border: 1.5px solid #e9c46a;
        border-radius: 18px;
        padding: 1.3rem 1.5rem;
        color: #7f5539;
        box-shadow: 0 4px 14px rgba(0,0,0,0.04);
        margin-bottom: 1.5rem;
    }
    .weather-title {
        font-size: 1.1rem;
        font-weight: 800;
        color: #7f5539;
        margin-bottom: 0.5rem;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .weather-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(130px, 1fr));
        gap: 12px;
        margin-top: 0.6rem;
    }
    .weather-item {
        background: #ffffff;
        padding: 0.6rem 0.9rem;
        border-radius: 12px;
        border: 1px solid #ccd5ae;
    }
    .weather-val {
        font-size: 1.2rem;
        font-weight: 800;
        color: #1b4332;
    }

    /* Spotlight Card */
    .spotlight-card {
        background: #ffffff;
        border-radius: 20px;
        padding: 1.8rem;
        border: 2px solid #2d6a4f;
        box-shadow: 0 8px 24px rgba(45, 106, 79, 0.12);
        margin-bottom: 2rem;
    }
    .spotlight-header {
        font-size: 1.3rem;
        font-weight: 800;
        color: #1b4332;
        border-bottom: 2px solid #e8f5e9;
        padding-bottom: 0.6rem;
        margin-bottom: 1.2rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .spotlight-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1.2rem;
    }
    .spotlight-item {
        background: #f8faf6;
        border-radius: 12px;
        padding: 1rem 1.1rem;
        border: 1px solid #e2e8f0;
    }
    .spotlight-label {
        font-size: 0.8rem;
        font-weight: 700;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .spotlight-value {
        font-size: 1.6rem;
        font-weight: 800;
        color: #1b4332;
        margin-top: 0.2rem;
    }
    .spotlight-sub {
        font-size: 0.85rem;
        font-weight: 700;
        color: #2d6a4f;
    }

    /* Badges */
    .badge-gemini {
        background: #e8f5e9;
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

    /* Profit Card */
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

    .stButton>button {
        border-radius: 12px;
        font-weight: 700;
        background-color: #2d6a4f;
        color: white;
        border: none;
        padding: 0.5rem 1.2rem;
    }
    .stButton>button:hover {
        background-color: #1b4332;
        color: white;
    }
</style>
""", unsafe_allow_html=True)


# ── Load Default Options ──────────────────────────────────────────────────────
data_folder = "data"
available_commodities = get_available_commodities(data_folder)
default_crop = "Arecanut(Betelnut/Supari)"
default_idx = available_commodities.index(default_crop) if default_crop in available_commodities else 0


# ── Sidebar Setup (Farmer Profile & Controls) ─────────────────────────────────
st.sidebar.image("https://img.icons8.com/color/96/wheat.png", width=70)
st.sidebar.title("👤 Farmer Profile & Settings")

# Guest Mode vs Profile Login Toggle
auth_mode = st.sidebar.radio(
    "Access Mode",
    options=["🚀 Guest Mode (Quick Access)", "👤 Farmer Profile Sign-In"],
    index=0 if st.session_state["user_mode"] == "guest" else 1
)

if auth_mode.startswith("👤"):
    st.session_state["user_mode"] = "profile"
    input_name = st.sidebar.text_input("Your Full Name", value=st.session_state["farmer_name"] if st.session_state["farmer_name"] != "ರೈತ ಮಿತ್ರ (Farmer Friend)" else "Ramesh Gowda")
    input_district = st.sidebar.selectbox("Home District / Region", options=list(DISTANCES_KM.keys()), index=0)
    input_phone = st.sidebar.text_input("Mobile / Farmer ID (Optional)", value=st.session_state["farmer_phone"])
    
    st.session_state["farmer_name"] = input_name if input_name else "Ramesh Gowda"
    st.session_state["farmer_district"] = input_district
    st.session_state["farmer_phone"] = input_phone
else:
    st.session_state["user_mode"] = "guest"
    st.session_state["farmer_name"] = "ರೈತ ಮಿತ್ರ (Valued Farmer)"
    input_district = st.sidebar.selectbox("Home District / Region", options=list(DISTANCES_KM.keys()), index=0)
    st.session_state["farmer_district"] = input_district

st.sidebar.markdown("---")
st.sidebar.markdown("### 🌾 Crop & Mandi Settings")

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
    step=5
)

lang_choice = st.sidebar.radio(
    "🗣️ Advisory Language",
    options=["English", "ಕನ್ನಡ (Kannada)", "Dual (English + ಕನ್ನಡ)"],
    index=0
)

st.sidebar.markdown("---")
if st.sidebar.button("🔄 Fetch Today's Govt API Data"):
    with st.spinner("Connecting to Govt Agmarknet Portal..."):
        try:
            fetch_data_pipeline()
            st.sidebar.success("Daily mandi data updated!")
            st.rerun()
        except Exception as e:
            st.sidebar.error(f"Fetch failed: {e}")


# ── Dynamic Time-of-Day Greeting Calculation ──────────────────────────────────
current_hour = datetime.now().hour
if current_hour < 12:
    greeting_str = "Good Morning"
elif current_hour < 17:
    greeting_str = "Good Afternoon"
else:
    greeting_str = "Good Evening"

today_date_str = datetime.now().strftime("%d %B %Y")


# ── Load Recommendation Data ──────────────────────────────────────────────────
rec_result = get_market_recommendation(
    folder=data_folder,
    commodity=selected_commodity,
    variety=selected_variety,
    threshold_pct=float(threshold)
)

if rec_result.get("status") != "success":
    st.warning(f"⚠️ {rec_result.get('message', 'No market recommendation available.')}")
    st.stop()

rec = rec_result["recommendation"]
markets_data = rec_result.get("markets", [])


# ── 1. Personalized Welcome Header ────────────────────────────────────────────
user_display_name = st.session_state["farmer_name"]
user_district = st.session_state["farmer_district"]

st.markdown(f"""
<div class="welcome-card">
    <div class="welcome-greeting">🌾 {greeting_str}, {user_display_name} 👋</div>
    <div style="font-size: 1.05rem; color: #d8f3dc;">Krishi Market Advisor — Karnataka's AI Mandi Intelligence & Price Advisory Platform</div>
    <div class="meta-pills-row">
        <span class="meta-pill">📍 Home District: {user_district}</span>
        <span class="meta-pill">📅 Date: {today_date_str}</span>
        <span class="meta-pill">🔓 Mode: {'Guest Mode' if st.session_state['user_mode']=='guest' else 'Registered Profile'}</span>
    </div>
</div>
""", unsafe_allow_html=True)


# ── 2. Live Agricultural Weather Card ──────────────────────────────────────────
w_data = DISTRICT_WEATHER.get(user_district, DISTRICT_WEATHER["Shivamogga (Shimoga)"])

st.markdown(f"""
<div class="weather-card">
    <div class="weather-title">
        <span>🌦 Live Agricultural Weather — {user_district.split('(')[0].strip()}</span>
    </div>
    <div class="weather-grid">
        <div class="weather-item">
            <div style="font-size:0.75rem; font-weight:700; color:#7f5539;">TEMPERATURE</div>
            <div class="weather-val">{w_data['temp']}</div>
        </div>
        <div class="weather-item">
            <div style="font-size:0.75rem; font-weight:700; color:#7f5539;">CONDITION</div>
            <div class="weather-val" style="font-size:1.05rem;">{w_data['condition']}</div>
        </div>
        <div class="weather-item">
            <div style="font-size:0.75rem; font-weight:700; color:#7f5539;">HUMIDITY</div>
            <div class="weather-val">{w_data['humidity']}</div>
        </div>
        <div class="weather-item">
            <div style="font-size:0.75rem; font-weight:700; color:#7f5539;">WIND SPEED</div>
            <div class="weather-val">{w_data['wind']}</div>
        </div>
    </div>
    <div style="margin-top: 0.8rem; font-size: 0.9rem; font-weight: 700; color: #2d6a4f;">
        💡 <b>Farmer Weather Advisory</b>: {w_data['advisory']}
    </div>
</div>
""", unsafe_allow_html=True)


# ── 3. Today's Recommendation Spotlight Card ──────────────────────────────────
trend_icon = "📈" if rec['trend'] == "rising" else ("📉" if rec['trend'] == "falling" else "➡️")
trend_label = f"{trend_icon} {rec['trend'].capitalize()} ({rec['trend_desc']})"

st.markdown(f"""
<div class="spotlight-card">
    <div class="spotlight-header">
        <span>🌟 Today's Best Market Recommendation</span>
        <span style="font-size: 0.9rem; font-weight: 600; color: #2d6a4f;">Variety: {rec_result['variety']}</span>
    </div>
    <div class="spotlight-grid">
        <div class="spotlight-item">
            <div class="spotlight-label">Crop / Commodity</div>
            <div class="spotlight-value" style="font-size: 1.4rem;">{selected_commodity.split('(')[0]}</div>
            <div class="spotlight-sub">Karnataka Mandis</div>
        </div>
        <div class="spotlight-item">
            <div class="spotlight-label">Best Market</div>
            <div class="spotlight-value" style="font-size: 1.4rem;">{rec['recommended_market']}</div>
            <div class="spotlight-sub">Highest Price Mandi</div>
        </div>
        <div class="spotlight-item">
            <div class="spotlight-label">Today's Price</div>
            <div class="spotlight-value">₹{rec['highest_price']:,.0f}</div>
            <div class="spotlight-sub">per quintal ({rec['date']})</div>
        </div>
        <div class="spotlight-item">
            <div class="spotlight-label">Market Trend</div>
            <div class="spotlight-value" style="font-size: 1.25rem;">{trend_label}</div>
            <div class="spotlight-sub">+₹{rec['extra_earnings']:,.0f}/Q (+{rec['extra_earnings_pct']:.1f}%) Extra</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)


# ── 4. Tabs Navigation ────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "🤖 AI Advisory & Voice",
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
            Selling within the next 2 days captures current peak prices before arrival increases.
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

    # WhatsApp Share Button
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
        farmer_district = user_district  # Uses selected home district

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
        - **Estimated Distance from {farmer_district}**: **{calc_result['distance_km']:.0f} km** ({calc_result['round_trip_km']:.0f} km round trip)
        - **Gross Extra Revenue** ({crop_quantity:.0f} quintals): **₹{calc_result['gross_extra_revenue']:,.0f}**
        - **Estimated Freight Cost**: **₹{calc_result['estimated_freight_cost']:,.0f}**
        """)

        card_class = "profit-card-green" if calc_result["is_profitable"] else "profit-card-orange"
        profit_title = "🎉 PURE NET EXTRA PROFIT" if calc_result["is_profitable"] else "⚠️ TRANSPORT COST EXCEEDS GAIN"

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
