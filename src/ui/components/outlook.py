import streamlit as st
from typing import Dict, Any

def render_outlook_card(outlook_data: Dict[str, Any], txt: Dict[str, str]):
    """
    Renders the 7-Day Market Outlook based on AI analysis.
    """
    trend = outlook_data.get("trend", "Unknown")
    confidence = outlook_data.get("confidence", 0)
    risk = outlook_data.get("risk", "Unknown")
    drivers = outlook_data.get("drivers", [])
    recommendation = outlook_data.get("recommendation", "")

    # Map colors and icons
    trend_color = "#6ee7b7" if "Upward" in trend else "#f87171" if "Downward" in trend else "#fef08a"
    trend_icon = "📈" if "Upward" in trend else "📉" if "Downward" in trend else "➡️"
    
    risk_color = "#6ee7b7" if risk == "Low" else "#fef08a" if risk == "Medium" else "#f87171"
    
    st.markdown("### 🔮 7-Day Market Outlook Engine")
    
    # Render main card
    st.markdown(f"""
    <div style="background: linear-gradient(160deg, rgba(16, 25, 20, 0.6) 0%, rgba(9, 13, 10, 0.8) 100%);
                border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 20px; padding: 1.8rem; margin-bottom: 1.5rem; backdrop-filter: blur(12px);">
        
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 1rem; margin-bottom: 1.5rem;">
            <div>
                <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.75rem; font-weight: 600; color: #94A3B8; text-transform: uppercase; letter-spacing: 1px;">Trend</div>
                <div style="font-size: 1.2rem; font-weight: 800; color: {trend_color}; margin-top: 0.3rem;">
                    {trend_icon} {trend}
                </div>
            </div>
            <div>
                <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.75rem; font-weight: 600; color: #94A3B8; text-transform: uppercase; letter-spacing: 1px;">Confidence</div>
                <div style="font-size: 1.2rem; font-weight: 800; color: #38bdf8; margin-top: 0.3rem;">
                    {confidence}%
                </div>
            </div>
            <div>
                <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.75rem; font-weight: 600; color: #94A3B8; text-transform: uppercase; letter-spacing: 1px;">Risk Level</div>
                <div style="font-size: 1.2rem; font-weight: 800; color: {risk_color}; margin-top: 0.3rem;">
                    {risk}
                </div>
            </div>
        </div>
        
        <hr style="border-color: rgba(255, 255, 255, 0.05); margin: 1rem 0;">
        
        <div style="margin-bottom: 1rem;">
            <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.75rem; font-weight: 600; color: #94A3B8; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 0.5rem;">Key Drivers</div>
            <ul style="color: #F8FAFC; font-size: 0.9rem; margin-left: -1rem;">
                {"".join([f"<li>{d}</li>" for d in drivers])}
            </ul>
        </div>
        
        <div style="background: rgba(16, 185, 129, 0.1); border-left: 4px solid #10B981; padding: 1rem; border-radius: 0 8px 8px 0;">
            <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.75rem; font-weight: 700; color: #10B981; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 0.3rem;">AI Recommendation</div>
            <div style="color: #F8FAFC; font-size: 0.95rem; line-height: 1.5;">{recommendation}</div>
        </div>
        
    </div>
    """, unsafe_allow_html=True)
