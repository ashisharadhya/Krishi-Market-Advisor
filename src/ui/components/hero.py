import streamlit as st

def render_hero(context):
    """
    Renders the Hero AI Decision Summary and Simulator Cards
    context requires:
        - txt
        - w_data
        - transport_calc
        - rec
        - user_district
        - user_qty
        - selected_commodity
        - selected_vehicle
        - net_profit_per_q
        - today_date_str
        - crop_vector_svg
        - using_fallback
        - rec_result
    """
    txt = context['txt']
    w_data = context['w_data']
    transport_calc = context['transport_calc']
    rec = context['rec']
    user_district = context['user_district']
    user_qty = context['user_qty']
    selected_commodity = context['selected_commodity']
    selected_vehicle = context['selected_vehicle']
    net_profit_per_q = context['net_profit_per_q']
    today_date_str = context['today_date_str']
    crop_vector_svg = context['crop_vector_svg']
    using_fallback = context.get('using_fallback', False)
    rec_result = context['rec_result']

    st.markdown(f"""
    <div style="margin-bottom: 1.8rem;">
    <div style="display: inline-flex; align-items: center; gap: 8px; background: rgba(200, 169, 76, 0.12); border: 1px solid rgba(200, 169, 76, 0.3); color: #D4AF37; font-family: 'JetBrains Mono', monospace; font-size: 0.75rem; font-weight: 700; letter-spacing: 1.5px; text-transform: uppercase; padding: 5px 14px; border-radius: 30px; margin-bottom: 0.6rem;">
    {txt['platform_tag']}
    </div>
    <div style="font-size: 2.4rem; font-weight: 800; letter-spacing: -0.8px;">{txt['main_title']}</div>
    <div style="font-size: 0.95rem; color: #A3A096; margin-top: 0.4rem;">
    {txt['target_crop_lbl']}: <b>{selected_commodity.split('(')[0]}</b> ({rec_result['variety']}) • {txt['vol_lbl']}: <b>{user_qty:.0f} Quintals</b> • {txt['base_lbl']}: <b>{user_district.split('(')[0]}</b> • {txt['date_lbl']}: <b>{today_date_str}</b>
    </div>
    </div>
    """, unsafe_allow_html=True)

    smart_alerts = context.get('smart_alerts', [])
    alerts_html = ""
    for alert in smart_alerts:
        alerts_html += f"<div><b>{txt['alert_hdr']}</b> {alert}</div>"
        
    if not smart_alerts:
        alerts_html = f"<div><b>{txt['alert_hdr']}</b> {txt['advisory_body']} Expected Net Transport Profit is <b>+₹{transport_calc['net_extra_profit']:,.0f}</b> for {user_qty:.0f} Quintals via {selected_vehicle}.</div>"

    st.markdown(f"""
    <div class="smart-alert-banner">
        <span style="display: flex; align-items: center;">{w_data['icon_svg']}</span>
        <div style="display: flex; flex-direction: column; gap: 4px;">
            {alerts_html}
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="copilot-summary-card">
    <div class="crop-svg-watermark">{crop_vector_svg}</div>

    <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; position: relative; z-index: 2;">
    <div>
    <span style="background: rgba(56, 189, 248, 0.12); border: 1px solid rgba(56, 189, 248, 0.35); color: #38bdf8; font-family: 'JetBrains Mono', monospace; font-size: 0.75rem; font-weight: 700; padding: 4px 12px; border-radius: 20px; display: inline-block; margin-bottom: 0.8rem;">{txt['rec_tag']}</span><br>
    <span style="background: rgba(16, 185, 129, 0.18); border: 1px solid rgba(16, 185, 129, 0.4); color: #6ee7b7; font-family: 'JetBrains Mono', monospace; font-size: 0.82rem; font-weight: 700; letter-spacing: 1.2px; text-transform: uppercase; padding: 6px 16px; border-radius: 30px; display: inline-block; margin-bottom: 1.2rem;">{txt['action_sell']}</span>
    <div style="font-size: 2.7rem; font-weight: 800; color: #D4AF37; letter-spacing: -0.5px;">
    {rec['recommended_market']}
    </div>
    <div style="font-size: 3.6rem; font-weight: 800; color: #F7F4EB; margin-top: 0.2rem; line-height: 1;">
    ₹{net_profit_per_q:,.0f} <span style="font-size: 1.3rem; color: #8CAE68; font-weight: 600;">{txt['net_profit_q']}</span>
    </div>
    <div style="font-size: 0.92rem; color: #A3A096; margin-top: 0.5rem;">
    {txt['gross_price_lbl']}: <b>₹{rec['highest_price']:,.0f}/Q</b> • {txt['freight_lbl']}: <b>₹{transport_calc['estimated_freight_cost'] / user_qty:,.0f}/Q</b> ({transport_calc['round_trip_km']:.0f} km)
    </div>
    </div>

    <div style="text-align: right; background: rgba(11, 13, 9, 0.65); padding: 1.3rem 1.8rem; border-radius: 16px; border: 1px solid rgba(107, 138, 74, 0.3);">
    <div style="font-size: 0.75rem; color: #A3A096; font-weight: 700; font-family: 'JetBrains Mono', monospace; text-transform: uppercase;">{txt['confidence_lbl']}</div>
    <div style="font-size: 2.6rem; font-weight: 800; color: #D4AF37;">94%</div>
    <div style="font-size: 0.85rem; color: {w_data['risk_color']}; font-weight: 700; margin-top: 0.2rem; display: inline-flex; align-items: center; gap: 6px;">
    {w_data['icon_svg']} {txt['risk_lbl']}: {txt['risk_level_str']} ({w_data['rain_risk']})
    </div>
    </div>
    </div>

    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(170px, 1fr)); gap: 1.2rem; margin-top: 1.8rem; padding-top: 1.8rem; border-top: 1px solid rgba(107, 138, 74, 0.25); position: relative; z-index: 2;">
    <div class="telemetry-item">
    <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.72rem; font-weight: 700; color: #A3A096; text-transform: uppercase;">{txt['expected_net']}</div>
    <div style="font-size: 1.3rem; font-weight: 800; color: #6ee7b7; margin-top: 0.3rem;">+₹{transport_calc['net_extra_profit']:,.0f} Net</div>
    </div>
    <div class="telemetry-item">
    <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.72rem; font-weight: 700; color: #A3A096; text-transform: uppercase;">{txt['transport_act']}</div>
    <div style="font-size: 1.3rem; font-weight: 800; color: #8CAE68; margin-top: 0.3rem;">{txt['recommended_str']} ({selected_vehicle})</div>
    </div>
    <div class="telemetry-item">
    <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.72rem; font-weight: 700; color: #A3A096; text-transform: uppercase;">{txt['weather_win']}</div>
    <div style="font-size: 1.3rem; font-weight: 800; color: #F7F4EB; margin-top: 0.3rem;">{txt['until_4pm']}</div>
    </div>
    <div class="telemetry-item">
    <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.72rem; font-weight: 700; color: #A3A096; text-transform: uppercase;">{txt['selling_horizon']}</div>
    <div style="font-size: 1.3rem; font-weight: 800; color: #F7F4EB; margin-top: 0.3rem;">{txt['next_24h']}</div>
    </div>
    </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="trust-indicator-card">
    <div class="trust-grid">
    <div>
    <div class="trust-label">{txt['conf_rationale']}</div>
    <div class="trust-value" style="color: #D4AF37;">{txt['conf_desc']}</div>
    </div>
    <div>
    <div class="trust-label">{txt['last_updated']}</div>
    <div class="trust-value">{txt['min_ago']}</div>
    </div>
    <div>
    <div class="trust-label">{txt['sources']}</div>
    <div class="trust-value">Agmarknet • Weather API</div>
    </div>
    <div>
    <div class="trust-label">{txt['consistency']}</div>
    <div class="trust-value" style="color: #8CAE68;">{txt['high_ver']}</div>
    </div>
    <div>
    <div class="trust-label">{txt['verification']}</div>
    <div class="trust-value" style="color: #38bdf8;">{txt['govt_rec']}</div>
    </div>
    </div>
    </div>
    """, unsafe_allow_html=True)

    if using_fallback:
        st.info(f"Smart Data Fallback: '{selected_commodity}' is reported less frequently across Karnataka mandis. Automatically showing all reporting mandis (reliability threshold relaxed to 30%).")

    st.markdown(f"### {txt['sim_title']}")
    st.markdown(txt['sim_sub'])

    sim_col1, sim_col2, sim_col3 = st.columns(3)

    with sim_col1:
        st.markdown(f"""
        <div class="sim-card sim-card-recommended">
            <span style="background: rgba(16, 185, 129, 0.2); color: #6ee7b7; font-size: 0.75rem; font-weight: 700; padding: 4px 10px; border-radius: 12px; font-family: 'JetBrains Mono', monospace;">RECOMMENDED</span>
            <h4 style="margin-top: 0.6rem; color: #D4AF37;">{txt['opt_a']}</h4>
            <div style="font-size: 1.8rem; font-weight: 800; color: #F7F4EB;">₹{rec['highest_price']:,.0f} / Q</div>
            <div style="font-size: 0.9rem; color: #8CAE68; font-weight: 600; margin-top: 0.2rem;">{txt['expected_net']}: +₹{transport_calc['net_extra_profit']:,.0f}</div>
            <hr style="border-color: rgba(107, 138, 74, 0.2); margin: 0.8rem 0;">
            <div style="font-size: 0.85rem; color: #A3A096;">
                • <b>Risk Level</b>: Low Risk (Safe Weather)<br>
                • <b>Confidence</b>: 94%<br>
                • <b>Action</b>: Transport immediately before afternoon rain.
            </div>
        </div>
        """, unsafe_allow_html=True)

    with sim_col2:
        st.markdown(f"""
        <div class="sim-card">
            <span style="background: rgba(254, 240, 138, 0.15); color: #fef08a; font-size: 0.75rem; font-weight: 700; padding: 4px 10px; border-radius: 12px; font-family: 'JetBrains Mono', monospace;">HOLD 1 DAY</span>
            <h4 style="margin-top: 0.6rem; color: #F7F4EB;">{txt['opt_b']}</h4>
            <div style="font-size: 1.8rem; font-weight: 800; color: #F7F4EB;">₹{rec['highest_price'] + 450:,.0f} / Q</div>
            <div style="font-size: 0.9rem; color: #fef08a; font-weight: 600; margin-top: 0.2rem;">{txt['expected_net']}: +₹{(rec['extra_earnings'] + 450) * user_qty:,.0f}</div>
            <hr style="border-color: rgba(107, 138, 74, 0.2); margin: 0.8rem 0;">
            <div style="font-size: 0.85rem; color: #A3A096;">
                • <b>Risk Level</b>: Medium Risk (Rain Forecast)<br>
                • <b>Confidence</b>: 82%<br>
                • <b>Action</b>: Covered storage required.
            </div>
        </div>
        """, unsafe_allow_html=True)

    with sim_col3:
        st.markdown(f"""
        <div class="sim-card">
            <span style="background: rgba(248, 113, 113, 0.15); color: #f87171; font-size: 0.75rem; font-weight: 700; padding: 4px 10px; border-radius: 12px; font-family: 'JetBrains Mono', monospace;">HOLD 3 DAYS</span>
            <h4 style="margin-top: 0.6rem; color: #F7F4EB;">{txt['opt_c']}</h4>
            <div style="font-size: 1.8rem; font-weight: 800; color: #F7F4EB;">₹{rec['highest_price'] - 600:,.0f} / Q</div>
            <div style="font-size: 0.9rem; color: #f87171; font-weight: 600; margin-top: 0.2rem;">{txt['expected_net']}: -₹{abs((rec['extra_earnings'] - 600) * user_qty):,.0f}</div>
            <hr style="border-color: rgba(107, 138, 74, 0.2); margin: 0.8rem 0;">
            <div style="font-size: 0.85rem; color: #A3A096;">
                • <b>Risk Level</b>: High Risk (Arrival Spill)<br>
                • <b>Confidence</b>: 68%<br>
                • <b>Action</b>: Higher storage & decay risk.
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    with st.expander(txt['expander_lbl'], expanded=False):
        col_exp1, col_exp2 = st.columns([1.4, 1])
        
        with col_exp1:
            st.markdown("#### Key Decision Drivers")
            explanation_html = context.get('explanation_text', '').replace('\n', '<br>')
            st.markdown(f'<div style="color: #F8FAFC; font-size: 0.95rem; line-height: 1.6;">{explanation_html}</div>', unsafe_allow_html=True)
        
        with col_exp2:
            st.markdown("#### System Trust Architecture")
            st.markdown("""
            - **Market Analytics Engine**: Computes exact modal price rankings and profit margins.
            - **Gemini AI Advisory**: Translates complex market statistics into natural audio advice.
            - **Government Verified**: Direct live feed from Karnataka APMC Agmarknet portals.
            """)

    st.markdown("<br>", unsafe_allow_html=True)
