import streamlit as st
from src.phase4.recommendation_adapter import get_available_commodities, get_available_varieties
from src.phase4.transport_calculator import DISTANCES_KM, VEHICLE_TYPES
from main import run_pipeline as fetch_data_pipeline

def render_sidebar(data_folder="data"):
    available_commodities = get_available_commodities(data_folder)
    default_crop = "Arecanut(Betelnut/Supari)"
    default_idx = available_commodities.index(default_crop) if default_crop in available_commodities else 0

    st.sidebar.markdown('<div class="sidebar-section-title">Farmer Profile & Preferences</div>', unsafe_allow_html=True)

    auth_mode = st.sidebar.radio(
        "Operator Mode",
        options=["Guest Mode (Quick Access)", "Registered Farmer Profile"],
        index=0 if st.session_state.get("user_mode", "guest") == "guest" else 1
    )

    if auth_mode.startswith("Registered"):
        st.session_state["user_mode"] = "profile"
        input_name = st.sidebar.text_input("Operator Name", value=st.session_state.get("farmer_name", "Raita Mitra") if st.session_state.get("farmer_name") != "Raita Mitra" else "Ramesh Gowda")
        input_district = st.sidebar.selectbox("Base District", options=list(DISTANCES_KM.keys()), index=0)
        input_phone = st.sidebar.text_input("Farmer ID / Phone", value=st.session_state.get("farmer_phone", ""))
        st.session_state["farm_acres"] = st.sidebar.number_input("Land Area (Acres)", min_value=0.5, value=2.5, step=0.5)
        st.session_state["harvest_qty"] = st.sidebar.number_input("Typical Harvest Volume (Quintals)", min_value=1.0, value=20.0, step=5.0)
        
        st.session_state["farmer_name"] = input_name if input_name else "Ramesh Gowda"
        st.session_state["farmer_district"] = input_district
        st.session_state["farmer_phone"] = input_phone
    else:
        st.session_state["user_mode"] = "guest"
        st.session_state["farmer_name"] = "Raita Mitra"
        input_district = st.sidebar.selectbox("Base District", options=list(DISTANCES_KM.keys()), index=0)
        st.session_state["farmer_district"] = input_district

    st.sidebar.markdown("---")
    st.sidebar.markdown('<div class="sidebar-section-title">Commodity & Transport Target</div>', unsafe_allow_html=True)

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

    selected_vehicle = st.sidebar.selectbox(
        "Transport Vehicle Fleet",
        options=list(VEHICLE_TYPES.keys()),
        index=0
    )

    threshold = st.sidebar.slider(
        "Data Reliability Threshold (%)",
        min_value=30,
        max_value=100,
        value=70,
        step=5
    )

    lang_choice = st.sidebar.radio(
        "Advisory Language",
        options=["English", "Kannada", "Dual Output"],
        index=0
    )

    st.sidebar.markdown("---")
    if st.sidebar.button("Refresh Government Market Data"):
        with st.spinner("Connecting to Agmarknet Portal..."):
            try:
                fetch_data_pipeline()
                st.sidebar.success("Market data updated!")
                st.rerun()
            except Exception as e:
                st.sidebar.error(f"Fetch failed: {e}")

    return {
        "selected_commodity": selected_commodity,
        "selected_variety": selected_variety,
        "selected_vehicle": selected_vehicle,
        "threshold": float(threshold),
        "lang_choice": lang_choice
    }
