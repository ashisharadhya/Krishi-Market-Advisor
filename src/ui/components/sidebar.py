import streamlit as st
from src.phase4.recommendation_adapter import get_available_commodities, get_available_varieties
from src.phase4.transport_calculator import DISTANCES_KM, VEHICLE_TYPES
from main import run_pipeline as fetch_data_pipeline

def render_sidebar(data_folder="data"):
    available_commodities = get_available_commodities(data_folder)
    default_crop = "Arecanut(Betelnut/Supari)"
    default_idx = available_commodities.index(default_crop) if default_crop in available_commodities else 0

    st.sidebar.markdown('<div class="sidebar-section-title">Farmer Profile & Preferences</div>', unsafe_allow_html=True)
    
    from streamlit_mic_recorder import mic_recorder
    from src.phase5.voice_assistant import process_voice_command
    
    st.sidebar.markdown("### 🎙️ AI Voice Assistant")
    st.sidebar.markdown("<small>Speak naturally (e.g. 'I have 20 quintals of Arecanut in Shimoga')</small>", unsafe_allow_html=True)
    audio = mic_recorder(start_prompt="Record Audio", stop_prompt="Stop Recording", key='sidebar_mic')
    
    if audio:
        with st.sidebar.spinner("Processing Voice..."):
            entities = process_voice_command(audio['bytes'])
            if entities:
                if entities.get("district"):
                    # Find closest match in DISTANCES_KM
                    for d in DISTANCES_KM.keys():
                        if entities["district"].lower() in d.lower():
                            st.session_state["farmer_district"] = d
                            break
                if entities.get("crop"):
                    # Find closest match
                    for c in available_commodities:
                        if entities["crop"].lower() in c.lower():
                            st.session_state["selected_commodity"] = c
                            break
                if entities.get("quantity"):
                    st.session_state["harvest_qty"] = float(entities["quantity"])
                if entities.get("language"):
                    st.session_state["lang_choice"] = "Kannada" if "kannada" in entities["language"].lower() else "English"
                st.sidebar.success("Updated preferences from voice!")
                # Force a rerun to reflect the newly populated session state
                st.rerun()

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

    # Read from session state if voice populated them
    if "selected_commodity" in st.session_state and st.session_state["selected_commodity"] in available_commodities:
        default_idx = available_commodities.index(st.session_state["selected_commodity"])

    selected_commodity = st.sidebar.selectbox(
        "Select Crop / Commodity",
        options=available_commodities,
        index=default_idx
    )
    st.session_state["selected_commodity"] = selected_commodity

    available_varieties = get_available_varieties(data_folder, selected_commodity)
    variety_options = ["Auto-Detect (Best Variety)"] + available_varieties
    selected_variety_option = st.sidebar.selectbox(
        "Crop Variety",
        options=variety_options,
        index=0
    )

    selected_variety = None if selected_variety_option.startswith("Auto-Detect") else selected_variety_option

    vehicle_options = list(VEHICLE_TYPES.keys())
    vehicle_idx = 0
    if "selected_vehicle" in st.session_state and st.session_state["selected_vehicle"] in vehicle_options:
        vehicle_idx = vehicle_options.index(st.session_state["selected_vehicle"])
        
    selected_vehicle = st.sidebar.selectbox(
        "Transport Vehicle Fleet",
        options=vehicle_options,
        index=vehicle_idx
    )
    st.session_state["selected_vehicle"] = selected_vehicle

    threshold = st.sidebar.slider(
        "Data Reliability Threshold (%)",
        min_value=30,
        max_value=100,
        value=70,
        step=5
    )

    lang_options = ["English", "Kannada", "Dual Output"]
    lang_idx = 0
    if "lang_choice" in st.session_state and st.session_state["lang_choice"] in lang_options:
        lang_idx = lang_options.index(st.session_state["lang_choice"])
        
    lang_choice = st.sidebar.radio(
        "Advisory Language",
        options=lang_options,
        index=lang_idx
    )
    st.session_state["lang_choice"] = lang_choice

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
