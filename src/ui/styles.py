import streamlit as st

def load_css():
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@500;600;700&display=swap');

        html, body, .stApp, .stMarkdown, p, h1, h2, h3, h4, h5, h6, label, button, input, select, textarea {
            font-family: 'Plus Jakarta Sans', system-ui, -apple-system, sans-serif;
            background-color: #0B0D09 !important;
            color: #F7F4EB;
            -webkit-font-smoothing: antialiased;
        }

        [data-testid="stIconMaterial"], [class*="Material"], [class*="icon"], [data-testid="stSidebarCollapseButton"] * {
            font-family: 'Material Symbols Rounded', 'Material Icons', sans-serif !important;
        }

        @keyframes ambientMotion {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }
        @keyframes gentleFloat {
            0% { transform: translateY(0px); }
            50% { transform: translateY(-4px); }
            100% { transform: translateY(0px); }
        }

        .stApp {
            background-color: #050806 !important; /* Deepest forest black */
            background-image: 
                radial-gradient(circle at 15% 0%, rgba(16, 185, 129, 0.12) 0%, transparent 45%), /* Emerald glow top-left */
                radial-gradient(circle at 85% 100%, rgba(56, 189, 248, 0.1) 0%, transparent 45%), /* Ocean blue glow bottom-right */
                repeating-linear-gradient(45deg, rgba(255,255,255,0.015) 0, rgba(255,255,255,0.015) 1px, transparent 0, transparent 30px);
            background-size: 100% 100%;
            animation: ambientMotion 30s ease infinite;
            background-attachment: fixed;
        }

        .block-container {
            padding-top: 2.2rem !important;
            padding-bottom: 5rem !important;
            max-width: 1240px;
        }

        [data-testid="stSidebar"] {
            background-color: #070A08 !important; /* Slightly lighter than background */
            border-right: 1px solid rgba(255, 255, 255, 0.05) !important;
        }

        .sidebar-section-title {
            font-size: 0.85rem;
            font-weight: 700;
            color: #10B981; /* Vibrant Emerald */
            letter-spacing: 1px;
            margin-top: 1.4rem;
            margin-bottom: 0.8rem;
            text-transform: uppercase;
            font-family: 'JetBrains Mono', monospace;
        }

        .copilot-summary-card {
            position: relative;
            background: linear-gradient(160deg, rgba(16, 25, 20, 0.8) 0%, rgba(9, 13, 10, 0.95) 100%);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 24px;
            padding: 2.8rem;
            color: #F8FAFC;
            box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.7), inset 0 1px 0 rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            margin-bottom: 1.8rem;
            overflow: hidden;
            transition: transform 0.4s cubic-bezier(0.16, 1, 0.3, 1), box-shadow 0.4s cubic-bezier(0.16, 1, 0.3, 1), border-color 0.4s ease;
        }
        .copilot-summary-card:hover {
            transform: translateY(-5px);
            border-color: rgba(16, 185, 129, 0.4); /* Glow border on hover */
            box-shadow: 0 30px 60px -15px rgba(16, 185, 129, 0.15), 0 0 40px rgba(16, 185, 129, 0.1);
        }
        .crop-svg-watermark {
            animation: gentleFloat 8s ease-in-out infinite;
            opacity: 0.15 !important;
            filter: brightness(1.5) drop-shadow(0 0 10px rgba(16, 185, 129, 0.2));
        }

        .telemetry-item {
            background: rgba(255, 255, 255, 0.03);
            border: 1px solid rgba(255, 255, 255, 0.06);
            border-radius: 16px;
            padding: 1.3rem 1.5rem;
            backdrop-filter: blur(10px);
            transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1);
            position: relative;
            overflow: hidden;
        }
        .telemetry-item:hover {
            transform: translateY(-3px) scale(1.02);
            background: rgba(255, 255, 255, 0.05);
            border-color: rgba(16, 185, 129, 0.4);
            box-shadow: 0 10px 30px -10px rgba(16, 185, 129, 0.2);
        }
        .telemetry-item::before {
            content: ""; position: absolute; top: 0; left: -100%; width: 50%; height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.06), transparent);
            transition: left 0.6s ease-in-out;
        }
        .telemetry-item:hover::before { left: 100%; }

        .trust-indicator-card {
            background: rgba(255, 255, 255, 0.02);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 20px;
            padding: 1.5rem 2rem;
            margin-bottom: 2.2rem;
            transition: all 0.4s ease;
            backdrop-filter: blur(12px);
        }
        .trust-indicator-card:hover {
            border-color: rgba(56, 189, 248, 0.3); /* Ocean blue border on hover */
            box-shadow: 0 15px 35px -10px rgba(0, 0, 0, 0.6);
            background: rgba(255, 255, 255, 0.03);
        }
        .trust-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
            gap: 1.5rem;
        }
        .trust-label {
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.75rem;
            font-weight: 600;
            color: #94A3B8; /* Slate gray */
            text-transform: uppercase;
            letter-spacing: 1.2px;
        }
        .trust-value {
            font-size: 1.15rem;
            font-weight: 800;
            color: #F8FAFC;
            margin-top: 0.4rem;
            transition: color 0.3s ease;
        }
        .trust-indicator-card:hover .trust-value {
            text-shadow: 0 0 12px rgba(255, 255, 255, 0.2);
        }

        .summary-check-card {
            background: rgba(255, 255, 255, 0.02);
            border: 1px solid rgba(255, 255, 255, 0.05);
            border-radius: 16px;
            padding: 1.2rem 1.4rem;
            margin-bottom: 0.8rem;
            display: flex;
            align-items: center;
            gap: 14px;
            transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
        }
        .summary-check-card:hover {
            transform: translateX(8px);
            background: rgba(255, 255, 255, 0.05);
            border-color: rgba(16, 185, 129, 0.3);
            box-shadow: -6px 6px 20px -5px rgba(0, 0, 0, 0.4);
        }

        .sim-card {
            background: rgba(255, 255, 255, 0.02);
            border: 1px solid rgba(255, 255, 255, 0.06);
            border-radius: 20px;
            padding: 1.8rem;
            margin-bottom: 1rem;
            transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1);
            cursor: default;
            backdrop-filter: blur(10px);
        }
        .sim-card:hover {
            transform: translateY(-6px);
            border-color: rgba(255, 255, 255, 0.15);
            box-shadow: 0 20px 40px -15px rgba(0, 0, 0, 0.5);
            background: rgba(255, 255, 255, 0.04);
        }
        .sim-card-recommended {
            border-color: rgba(16, 185, 129, 0.4);
            box-shadow: 0 10px 30px -10px rgba(16, 185, 129, 0.15);
            background: linear-gradient(160deg, rgba(16, 185, 129, 0.05) 0%, rgba(0,0,0,0) 100%);
        }
        .sim-card-recommended:hover {
            border-color: #10B981;
            box-shadow: 0 15px 40px -10px rgba(16, 185, 129, 0.3);
        }
        
        @keyframes pulseGlow {
            0% { box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.4); }
            70% { box-shadow: 0 0 0 10px rgba(16, 185, 129, 0); }
            100% { box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }
        }

        .smart-alert-banner {
            background: linear-gradient(90deg, rgba(245, 158, 11, 0.1) 0%, rgba(217, 119, 6, 0.05) 100%);
            border: 1px solid rgba(245, 158, 11, 0.3);
            border-radius: 16px;
            padding: 1.1rem 1.6rem;
            margin-bottom: 2rem;
            display: flex;
            align-items: center;
            gap: 16px;
            color: #F8FAFC;
            animation: pulseGlow 3s infinite;
            transition: all 0.4s ease;
            backdrop-filter: blur(8px);
        }
        .smart-alert-banner:hover {
            background: linear-gradient(90deg, rgba(245, 158, 11, 0.15) 0%, rgba(217, 119, 6, 0.1) 100%);
            border-color: rgba(245, 158, 11, 0.6);
            animation-play-state: paused;
            transform: scale(1.01);
        }

        .stTabs [data-baseweb="tab-list"] {
            gap: 16px;
            background-color: transparent;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
            padding-bottom: 10px;
        }
        .stTabs [data-baseweb="tab"] {
            height: 52px;
            background-color: transparent;
            border-radius: 12px;
            border: 1px solid transparent;
            color: #94A3B8;
            font-weight: 600;
            padding: 0 28px;
            transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
        }
        .stTabs [data-baseweb="tab"]:hover {
            background-color: rgba(255, 255, 255, 0.05);
            color: #F8FAFC;
        }
        .stTabs [aria-selected="true"] {
            background-color: #10B981 !important;
            border-color: #059669 !important;
            color: #ffffff !important;
            box-shadow: 0 8px 20px -6px rgba(16, 185, 129, 0.5);
        }
    </style>
    """, unsafe_allow_html=True)
