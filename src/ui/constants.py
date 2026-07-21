"""
UI Constants for Krishi Market Advisor
"""

# ── Monochromatic Crop SVG Vector Library ─────────────────────────────────────
CROP_SVG_VECTORS = {
    "Arecanut": """<svg width="140" height="140" viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg" style="opacity:0.22; position:absolute; right:20px; top:20px; pointer-events:none;">
        <path d="M50 90C50 90 52 50 80 20C80 20 60 40 50 90Z" stroke="#D4AF37" stroke-width="2.5" stroke-linecap="round"/>
        <path d="M50 90C50 90 48 50 20 20C20 20 40 40 50 90Z" stroke="#D4AF37" stroke-width="2.5" stroke-linecap="round"/>
        <circle cx="50" cy="35" r="5" fill="#D4AF37"/>
        <circle cx="42" cy="45" r="4.5" fill="#D4AF37"/>
        <circle cx="58" cy="45" r="4.5" fill="#D4AF37"/>
        <circle cx="50" cy="55" r="4" fill="#D4AF37"/>
    </svg>""",
    "Coffee": """<svg width="140" height="140" viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg" style="opacity:0.22; position:absolute; right:20px; top:20px; pointer-events:none;">
        <path d="M50 85V15M50 40C30 30 20 45 50 40M50 60C70 50 80 65 50 60" stroke="#D4AF37" stroke-width="2.5" stroke-linecap="round"/>
        <ellipse cx="32" cy="36" rx="6" ry="9" fill="#D4AF37" transform="rotate(-20 32 36)"/>
        <ellipse cx="68" cy="56" rx="6" ry="9" fill="#D4AF37" transform="rotate(20 68 56)"/>
    </svg>""",
    "Paddy": """<svg width="140" height="140" viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg" style="opacity:0.22; position:absolute; right:20px; top:20px; pointer-events:none;">
        <path d="M30 90C40 60 50 30 80 15" stroke="#D4AF37" stroke-width="2.5" stroke-linecap="round"/>
        <path d="M60 28C65 22 75 22 70 30" stroke="#D4AF37" stroke-width="2" stroke-linecap="round"/>
        <path d="M50 42C55 36 65 36 60 44" stroke="#D4AF37" stroke-width="2" stroke-linecap="round"/>
        <path d="M40 56C45 50 55 50 50 58" stroke="#D4AF37" stroke-width="2" stroke-linecap="round"/>
    </svg>""",
    "Coconut": """<svg width="140" height="140" viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg" style="opacity:0.22; position:absolute; right:20px; top:20px; pointer-events:none;">
        <path d="M50 90C45 60 35 35 15 25M50 90C55 60 65 35 85 25M50 90V20" stroke="#D4AF37" stroke-width="2.5" stroke-linecap="round"/>
        <circle cx="45" cy="50" r="7" fill="#D4AF37"/>
        <circle cx="56" cy="52" r="6.5" fill="#D4AF37"/>
    </svg>""",
    "Default": """<svg width="140" height="140" viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg" style="opacity:0.22; position:absolute; right:20px; top:20px; pointer-events:none;">
        <path d="M50 85V20M50 45C30 35 25 50 50 45M50 65C70 55 75 70 50 65" stroke="#D4AF37" stroke-width="2.5" stroke-linecap="round"/>
    </svg>"""
}

# ── District Weather & Risk Matrix ───────────────────────────────────────────
DISTRICT_WEATHER = {
    "Shivamogga (Shimoga)": {"temp": "26°C", "condition": "Light Monsoon Rain", "humidity": "84%", "wind": "14 km/h", "rain_risk": "Low Rain Risk", "advisory": "Safe transport window open until 4:00 PM today.", "advisory_kn": "ಇಂದು ಸಂಜೆ 4:00 ಗಂಟೆಯವರೆಗೆ ಸುರಕ್ಷಿತ ಸಾರಿಗೆ ಸಮಯವಿದೆ.", "risk_level": "Low Risk", "risk_level_kn": "ಕಡಿಮೆ ಅಪಾಯ", "risk_color": "#6ee7b7", "icon_svg": """<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#6ee7b7" stroke-width="2" stroke-linecap="round"><circle cx="12" cy="12" r="5"/><path d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42"/></svg>"""},
    "Chikmagalur (Chikkamagaluru)": {"temp": "24°C", "condition": "Moderate Rain", "humidity": "88%", "wind": "16 km/h", "rain_risk": "Moderate Rain Risk", "advisory": "Transport in covered vehicles recommended.", "advisory_kn": "ಮುಚ್ಚಿದ ವಾಹನಗಳಲ್ಲಿ ಸಾರಿಗೆ ಮಾಡಲು ಶಿಫಾರಸು ಮಾಡಲಾಗಿದೆ.", "risk_level": "Medium Risk", "risk_level_kn": "ಮಧ್ಯಮ ಅಪಾಯ", "risk_color": "#fef08a", "icon_svg": """<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#fef08a" stroke-width="2" stroke-linecap="round"><path d="M20 16.58A5 5 0 0 0 18 7h-1.26A8 8 0 1 0 4 15.25"/><path d="M8 19v2M12 19v2M16 19v2"/></svg>"""},
    "Uttara Kannada (Sirsi / Karwar)": {"temp": "27°C", "condition": "Heavy Showers", "humidity": "90%", "wind": "18 km/h", "rain_risk": "High Rain Risk", "advisory": "Verify APMC operating hours due to coastal rain.", "advisory_kn": "ಕರಾವಳಿ ಮಳೆಯಿಂದಾಗಿ ಎಪಿಎಂಸಿ ಸಮಯವನ್ನು ಪರಿಶೀಲಿಸಿ.", "risk_level": "High Risk", "risk_level_kn": "ಹೆಚ್ಚಿನ ಅಪಾಯ", "risk_color": "#f87171", "icon_svg": """<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#f87171" stroke-width="2" stroke-linecap="round"><path d="M19 16.9A5 5 0 0 0 18 7h-1.26a8 8 0 1 0-11.62 9"/><polygon points="13 11 9 17 15 17 11 23"/></svg>"""},
    "Hassan": {"temp": "25°C", "condition": "Partly Cloudy", "humidity": "78%", "wind": "12 km/h", "rain_risk": "No Rain Risk", "advisory": "Ideal drying & market transport weather today.", "advisory_kn": "ಇಂದು ಒಣಗಿಸಲು ಮತ್ತು ಸಾರಿಗೆಗೆ ಸೂಕ್ತ ಹವಾಮಾನವಿದೆ.", "risk_level": "Low Risk", "risk_level_kn": "ಕಡಿಮೆ ಅಪಾಯ", "risk_color": "#6ee7b7", "icon_svg": """<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#6ee7b7" stroke-width="2" stroke-linecap="round"><circle cx="12" cy="12" r="5"/></svg>"""},
    "Dakshina Kannada (Mangaluru / Bantwal)": {"temp": "28°C", "condition": "Humid Showers", "humidity": "85%", "wind": "15 km/h", "rain_risk": "Moderate Rain Risk", "advisory": "Keep produce ventilated during transport.", "advisory_kn": "ಸಾರಿಗೆ ಸಮಯದಲ್ಲಿ ಬೆಳೆಗೆ ಗಾಳಿ ಆಡುವಂತೆ ನೋಡಿಕೊಳ್ಳಿ.", "risk_level": "Medium Risk", "risk_level_kn": "ಮಧ್ಯಮ ಅಪಾಯ", "risk_color": "#fef08a", "icon_svg": """<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#fef08a" stroke-width="2" stroke-linecap="round"><path d="M20 16.58A5 5 0 0 0 18 7h-1.26A8 8 0 1 0 4 15.25"/></svg>"""},
    "Chitradurga": {"temp": "29°C", "condition": "Sunny", "humidity": "62%", "wind": "10 km/h", "rain_risk": "No Rain Risk", "advisory": "Dry weather. Excellent for drying & transport.", "advisory_kn": "ಒಣ ಹವಾಮಾನ. ಒಣಗಿಸಲು ಮತ್ತು ಸಾರಿಗೆಗೆ ಅತ್ಯುತ್ತಮ.", "risk_level": "Low Risk", "risk_level_kn": "ಕಡಿಮೆ ಅಪಾಯ", "risk_color": "#6ee7b7", "icon_svg": """<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#6ee7b7" stroke-width="2" stroke-linecap="round"><circle cx="12" cy="12" r="5"/></svg>"""},
    "Davanagere": {"temp": "30°C", "condition": "Mostly Clear", "humidity": "65%", "wind": "11 km/h", "rain_risk": "No Rain Risk", "advisory": "Optimal market transport conditions.", "advisory_kn": "ಸೂಕ್ತ ಮಾರುಕಟ್ಟೆ ಸಾರಿಗೆ ಪರಿಸ್ಥಿತಿಗಳು.", "risk_level": "Low Risk", "risk_level_kn": "ಕಡಿಮೆ ಅಪಾಯ", "risk_color": "#6ee7b7", "icon_svg": """<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#6ee7b7" stroke-width="2" stroke-linecap="round"><circle cx="12" cy="12" r="5"/></svg>"""},
    "Tumakuru (Tumkur)": {"temp": "28°C", "condition": "Partly Cloudy", "humidity": "70%", "wind": "12 km/h", "rain_risk": "Low Rain Risk", "advisory": "Clear highways to Tumakuru & Bangalore mandis.", "advisory_kn": "ತುಮಕೂರು ಮತ್ತು ಬೆಂಗಳೂರು ಮಾರುಕಟ್ಟೆಗೆ ದಾರಿ ಮುಕ್ತವಾಗಿದೆ.", "risk_level": "Low Risk", "risk_level_kn": "ಕಡಿಮೆ ಅಪಾಯ", "risk_color": "#6ee7b7", "icon_svg": """<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#6ee7b7" stroke-width="2" stroke-linecap="round"><circle cx="12" cy="12" r="5"/></svg>"""},
    "Ramanagara / Bengaluru Rural": {"temp": "27°C", "condition": "Pleasant", "humidity": "72%", "wind": "13 km/h", "rain_risk": "No Rain Risk", "advisory": "Optimal market trading weather.", "advisory_kn": "ಉತ್ತಮ ವ್ಯಾಪಾರ ಹವಾಮಾನ.", "risk_level": "Low Risk", "risk_level_kn": "ಕಡಿಮೆ ಅಪಾಯ", "risk_color": "#6ee7b7", "icon_svg": """<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#6ee7b7" stroke-width="2" stroke-linecap="round"><circle cx="12" cy="12" r="5"/></svg>"""}
}
