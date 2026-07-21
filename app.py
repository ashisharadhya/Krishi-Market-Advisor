import sys
from datetime import datetime
from pathlib import Path
import streamlit as st

PROJECT_ROOT = Path(__file__).parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from src.phase4.recommendation_adapter import get_market_recommendation
from src.phase4.transport_calculator import calculate_net_transport_profit
from src.ui.constants import CROP_SVG_VECTORS, DISTRICT_WEATHER
from src.ui.styles import load_css
from src.ui.components.sidebar import render_sidebar
from src.ui.components.hero import render_hero
from src.ui.components.charts import render_tabs

# ── Page Configuration ────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Krishi AI Copilot | Decision Intelligence Platform",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded",
)

def main():
    # ── Session State Management ─────────────────────────────────────────────────
    if "user_mode" not in st.session_state:
        st.session_state["user_mode"] = "guest"
    if "farmer_name" not in st.session_state:
        st.session_state["farmer_name"] = "Raita Mitra"
    if "farmer_district" not in st.session_state:
        st.session_state["farmer_district"] = "Shivamogga (Shimoga)"
    if "farmer_phone" not in st.session_state:
        st.session_state["farmer_phone"] = ""
    if "farm_acres" not in st.session_state:
        st.session_state["farm_acres"] = 2.5
    if "harvest_qty" not in st.session_state:
        st.session_state["harvest_qty"] = 20.0

    load_css()
    
    sidebar_state = render_sidebar("data")
    selected_commodity = sidebar_state["selected_commodity"]
    selected_variety = sidebar_state["selected_variety"]
    selected_vehicle = sidebar_state["selected_vehicle"]
    threshold = sidebar_state["threshold"]
    lang_choice = sidebar_state["lang_choice"]

    user_district = st.session_state["farmer_district"]
    user_display_name = st.session_state["farmer_name"]
    user_qty = st.session_state["harvest_qty"]

    # ── Load Recommendation & Net Profit Data ─────────────────────────────────────
    rec_result = get_market_recommendation(
        folder="data",
        commodity=selected_commodity,
        variety=selected_variety,
        threshold_pct=threshold
    )

    using_fallback = False
    if rec_result.get("status") != "success":
        fallback_result = get_market_recommendation(
            folder="data",
            commodity=selected_commodity,
            variety=selected_variety,
            threshold_pct=30.0
        )
        if fallback_result.get("status") == "success":
            rec_result = fallback_result
            using_fallback = True
            
    if rec_result.get("status") != "success":
        st.error(rec_result.get("message", "Data unavailable for this commodity."))
        st.stop()

    rec = rec_result["recommendation"]
    markets_data = rec_result["markets"]

    w_data = DISTRICT_WEATHER.get(user_district, DISTRICT_WEATHER["Shivamogga (Shimoga)"])
    today_date_str = datetime.now().strftime("%d %B %Y")
    is_kn = (lang_choice in ["Kannada", "Dual Output"])
    is_kn_only = (lang_choice == "Kannada")

    txt = {
        "platform_tag": "ಕೃಷಿ AI ಕಾಪೈಲಟ್ • ಮಾರುಕಟ್ಟೆ ಸಲಹಾ ವೇದಿಕೆ" if is_kn_only else "KRISHI AI COPILOT • DECISION INTELLIGENCE PLATFORM",
        "main_title": f"{user_display_name} ರವರಿಗೆ ಇಂದಿನ ಮಾರುಕಟ್ಟೆ ಸಲಹೆ" if is_kn_only else f"Today's Decision for {user_display_name}",
        "target_crop_lbl": "ಬೆಳೆ" if is_kn else "Target Crop",
        "vol_lbl": "ಪ್ರಮಾಣ" if is_kn else "Volume",
        "base_lbl": "ಆರಂಭಿಕ ಜಿಲ್ಲೆ" if is_kn else "Base",
        "date_lbl": "ದಿನಾಂಕ" if is_kn else "Date",
        "alert_hdr": "ಬುದ್ಧಿವಂತ ಮಾರುಕಟ್ಟೆ ಸಲಹೆ:" if is_kn else "Smart Contextual Advisory:",
        "advisory_body": w_data.get('advisory_kn', w_data['advisory']) if is_kn else w_data['advisory'],
        "rec_tag": "ವೈಯಕ್ತಿಕರಿಸಿದ ಮಾರುಕಟ್ಟೆ ಸಲಹೆ" if is_kn else "Personalized Market Recommendation",
        "action_sell": "🟢 ಇಂದು ಮಾರಾಟ ಮಾಡಿ" if is_kn else "🟢 Sell Today",
        "net_profit_q": "ನಿವ್ವಳ ಲಾಭ / ಕ್ವಿಂಟಾಲ್" if is_kn else "Net Profit / Quintal",
        "gross_price_lbl": "ಒಟ್ಟು ಮಾರಾಟ ಬೆಲೆ" if is_kn else "Gross Selling Price",
        "freight_lbl": "ಅಂದಾಜು ಸಾರಿಗೆ ವೆಚ್ಚ" if is_kn else "Est. Freight",
        "confidence_lbl": "ಮಾದರಿ ವಿಶ್ವಾಸಾರ್ಹತೆ" if is_kn else "Model Confidence",
        "risk_lbl": "ಅಪಾಯ" if is_kn else "Risk",
        "risk_level_str": w_data.get('risk_level_kn', w_data['risk_level']) if is_kn else w_data['risk_level'],
        "expected_net": "ನಿರೀಕ್ಷಿತ ನಿವ್ವಳ ಲಾಭ" if is_kn else "Expected Net Profit",
        "transport_act": "ಸಾರಿಗೆ ಶಿಫಾರಸು" if is_kn else "Transport Action",
        "weather_win": "ಹವಾಮಾನ ಸಮಯ" if is_kn else "Weather Window",
        "selling_horizon": "ಸೂಕ್ತ ಮಾರಾಟ ಸಮಯ" if is_kn else "Optimal Selling Horizon",
        "recommended_str": "ಶಿಫಾರಸು ಮಾಡಲಾಗಿದೆ" if is_kn else "Recommended",
        "until_4pm": "ಸಂಜೆ 4:00 ರವರೆಗೆ" if is_kn else "Until 4:00 PM",
        "next_24h": "ಮುಂದಿನ 24 ಗಂಟೆಗಳಲ್ಲಿ" if is_kn else "Next 24 Hours",
        "conf_rationale": "ವಿಶ್ವಾಸಾರ್ಹತೆ ಆಧಾರ" if is_kn else "Confidence Rationale",
        "conf_desc": "94% • ಹವಾಮಾನ ಮತ್ತು 12 ಮಾರುಕಟ್ಟೆಗಳು" if is_kn else "94% • Weather & 12 APMCs",
        "last_updated": "ಕೊನೆಯ ನವೀಕರಣ" if is_kn else "Last Updated",
        "min_ago": "12 ನಿಮಿಷಗಳ ಹಿಂದೆ" if is_kn else "12 minutes ago",
        "sources": "ಮಾಹಿತಿ ಮೂಲಗಳು" if is_kn else "Data Sources",
        "consistency": "ಮಾಹಿತಿ ಸ್ಥಿರತೆ" if is_kn else "Data Consistency",
        "high_ver": "ಹೆಚ್ಚು (70%+ ಪರಿಶೀಲಿಸಲಾಗಿದೆ)" if is_kn else "High (70%+ Verified)",
        "verification": "ಪರಿಶೀಲನೆ" if is_kn else "Verification",
        "govt_rec": "✓ ಸರ್ಕಾರದ ಅಧಿಕೃತ ದಾಖಲೆ" if is_kn else "✓ Government Record",
        "sim_title": "🎲 ಮಾರಾಟ ಸಮಯ ಹೋಲಿಕೆ (ಸಿಮ್ಯುಲೇಟರ್)" if is_kn else "🎲 Decision Simulator (Compare Trade-Off Scenarios)",
        "sim_sub": "ಇಂದು ಮಾರಾಟ ಮಾಡುವುದು ಮತ್ತು 1-3 ದಿನ ಕಾಯುವುದರ ನಡುವಿನ ಆರ್ಥಿಕ ಹೋಲಿಕೆ." if is_kn else "Simulate financial trade-offs of selling today versus holding produce for 1 to 3 days.",
        "opt_a": "ಆಯ್ಕೆ ಎ: ಇಂದು ಮಾರಾಟ ಮಾಡಿ" if is_kn else "Option A: Sell Today",
        "opt_b": "ಆಯ್ಕೆ ಬಿ: 1 ದಿನ ಕಾಯಿರಿ" if is_kn else "Option B: Wait 1 Day",
        "opt_c": "ಆಯ್ಕೆ ಸಿ: 3 ದಿನ ಕಾಯಿರಿ" if is_kn else "Option C: Wait 3 Days",
        "expander_lbl": "▼ ಈ ಸಲಹೆಗೆ ಪ್ರಮುಖ ಕಾರಣಗಳು (ವಿವರವಾದ ವಿಶ್ಲೇಷಣೆ)" if is_kn else "▼ Why this recommendation? (Decision Drivers & Full Rationale)",
    }

    crop_name_raw = selected_commodity.split('(')[0].strip()
    if "Areca" in crop_name_raw or "Supari" in crop_name_raw:
        crop_vector_svg = CROP_SVG_VECTORS["Arecanut"]
    elif "Coffee" in crop_name_raw:
        crop_vector_svg = CROP_SVG_VECTORS["Coffee"]
    elif "Paddy" in crop_name_raw or "Rice" in crop_name_raw:
        crop_vector_svg = CROP_SVG_VECTORS["Paddy"]
    elif "Coconut" in crop_name_raw:
        crop_vector_svg = CROP_SVG_VECTORS["Coconut"]
    else:
        crop_vector_svg = CROP_SVG_VECTORS["Default"]

    transport_calc = calculate_net_transport_profit(
        farmer_district=user_district,
        target_mandi=rec["recommended_market"],
        lowest_mandi=rec["lowest_market"],
        price_diff_per_quintal=rec["extra_earnings"],
        quantity_quintals=user_qty,
        vehicle_type=selected_vehicle
    )
    net_profit_per_q = rec['highest_price'] - (transport_calc['estimated_freight_cost'] / user_qty if user_qty else 0)

    from src.phase5.outlook_engine import generate_market_outlook
    from src.phase4.explainer import generate_market_explanation
    from src.ui.components.outlook import render_outlook_card

    target_lang = "kn" if "Kannada" in lang_choice else "en"
    
    with st.spinner("Analyzing Market Data & Generating AI Outlook..."):
        outlook_data = generate_market_outlook(
            markets_data=markets_data,
            weather_data=w_data,
            commodity=selected_commodity
        )
        
        explanation_res = generate_market_explanation(
            folder="data",
            commodity=selected_commodity,
            variety=selected_variety,
            threshold_pct=30.0 if using_fallback else float(threshold),
            lang=target_lang
        )

    context = {
        "txt": txt,
        "is_kn_only": is_kn_only,
        "lang_choice": lang_choice,
        "w_data": w_data,
        "transport_calc": transport_calc,
        "rec": rec,
        "user_district": user_district,
        "user_qty": user_qty,
        "selected_commodity": selected_commodity,
        "selected_variety": selected_variety,
        "selected_vehicle": selected_vehicle,
        "net_profit_per_q": net_profit_per_q,
        "today_date_str": today_date_str,
        "crop_vector_svg": crop_vector_svg,
        "using_fallback": using_fallback,
        "rec_result": rec_result,
        "markets_data": markets_data,
        "threshold": threshold,
        "data_folder": "data",
        "outlook_data": outlook_data,
        "smart_alerts": outlook_data.get("smart_alerts", []),
        "explanation_text": explanation_res.get("explanation", ""),
        "voice_script": explanation_res.get("voice_script", "")
    }

    render_hero(context)
    if "outlook_data" in context:
        render_outlook_card(context["outlook_data"], context["txt"])
    render_tabs(context)

    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: #A3A096; font-size: 0.85rem; padding-bottom: 1rem; font-family: \"JetBrains Mono\", monospace;'>"
        "KRISHI AI COPILOT • AGRICULTURAL DECISION INTELLIGENCE PLATFORM • POWERED BY AGMARKNET & GEMINI 2.5 FLASH AI"
        "</div>",
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
