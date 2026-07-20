"""
src/phase4/gemini_service.py

Handles interaction with the Google Gemini API for natural language crop price
explanations. Includes a rule-based fallback explanation when no API key is
provided or when network API limits are encountered.
"""

import logging
from typing import Dict, Any, Optional
from src.config import Config

logger = logging.getLogger("krishi")


def build_fallback_explanation(result: Dict[str, Any], lang: str = "en") -> str:
    """
    Generates a high-quality, structured rule-based explanation when Gemini API is unavailable.
    """
    if result.get("status") != "success":
        return result.get("message", "Insufficient market data to form a recommendation.")

    rec = result["recommendation"]
    commodity = result["commodity"]
    variety = result.get("variety", "")
    top_mandi = rec["recommended_market"]
    top_price = rec["highest_price"]
    top_date = rec["date"]
    top_trend = rec["trend_desc"]
    lowest_mandi = rec["lowest_market"]
    lowest_price = rec["lowest_price"]
    extra_earnings = rec["extra_earnings"]
    extra_pct = rec["extra_earnings_pct"]

    if lang.lower() == "kn":
        return f"""
💡 **ಪ್ರಮುಖ ಸಲಹೆ (Recommended Mandi)**
ನಂಬಿಗಸ್ತ ಮಾರುಕಟ್ಟೆಗಳಲ್ಲಿ **{top_mandi}** ಮಾರುಕಟ್ಟೆಯು {commodity} (ತಳಿ: {variety}) ಬೆಳೆಗೆ ಅತ್ಯುತ್ತಮ ಬೆಲೆಯನ್ನು ನೀಡುತ್ತಿದೆ. ಪ್ರಸ್ತುತ ದರ: **₹{top_price:,.0f} / ಕ್ವಿಂಟಾಲ್‌ಗೆ** (ದಿನಾಂಕ: {top_date}).

📈 **ಬೆಲೆ ಟ್ರೆಂಡ್ ಮತ್ತು ಲಾಭದ ವಿಶ್ಲೇಷಣೆ (Price Trend & Profit)**
• **ಬೆಲೆ ಟ್ರೆಂಡ್**: {top_trend}.
• **ಹೆಚ್ಚುವರಿ ಲಾಭ**: {lowest_mandi} ಮಾರುಕಟ್ಟೆಗೆ (₹{lowest_price:,.0f}) ಹೋಲಿಸಿದರೆ {top_mandi} ಯಲ್ಲಿ ಮಾರಾಟ ಮಾಡುವುದರಿಂದ ನಿಮಗೆ ಪ್ರತಿಯೊಂದು ಕ್ವಿಂಟಾಲ್‌ಗೆ **₹{extra_earnings:,.0f} ಹೆಚ್ಚುವರಿ ಲಾಭ ({extra_pct:.1f}% ಹೆಚ್ಚು)** ಸಿಗಲಿದೆ.

🚚 **ಸಾರಿಗೆ ವೆಚ್ಚದ ಎಚ್ಚರಿಕೆ (Transport Caution)**
ಈ ಸಲಹೆಯು ವರದಿಯಾದ ಮಾರುಕಟ್ಟೆ ದರಗಳನ್ನು ಆಧರಿಸಿದೆ. ದೂರದ ಮಾರುಕಟ್ಟೆಗೆ ಸಾಗಿಸುವ ಮುನ್ನ ಲಾರಿ/ವಾಹನ ಸಾರಿಗೆ ವೆಚ್ಚ ಮತ್ತು ದೂರವನ್ನು ಲೆಕ್ಕಹಾಕಿ ನಿರ್ಧರಿಸಿ.

🌾 **ರೈತರಿಗೆ ಪ್ರಾಯೋಗಿಕ ಮಾರ್ಗದರ್ಶನ (Action Summary)**
ನಿಮ್ಮ ಸಮೀಪದ ಮಾರುಕಟ್ಟೆಗಿಂತ {top_mandi} ದಲ್ಲಿ ಸಿಗುವ ₹{extra_earnings:,.0f} ಹೆಚ್ಚಿನ ಬೆಲೆಯು ಸಾರಿಗೆ ವೆಚ್ಚಕ್ಕಿಂತ ಹೆಚ್ಚಿದ್ದರೆ, ನಿಮ್ಮ ಬೆಳೆಯನ್ನು {top_mandi} ಮಾರುಕಟ್ಟೆಗೆ ತೆಗೆದುಕೊಂಡು ಹೋಗುವುದು ಸೂಕ್ತ.
"""
    else:
        return f"""
💡 **Top Recommendation**
Among all verified reliable markets in Karnataka, **{top_mandi}** offers the highest reported modal price for **{commodity}** ({variety}) at **₹{top_price:,.0f} / quintal** as of {top_date}.

📈 **Trend & Earnings Advantage**
• **Price Trend**: {top_trend}.
• **Profit Advantage**: Selling at {top_mandi} yields **₹{extra_earnings:,.0f} extra per quintal (+{extra_pct:.1f}%)** compared to the lowest reporting market ({lowest_mandi} at ₹{lowest_price:,.0f}/quintal).

🚚 **Transport & Distance Caution**
This price signal does not automatically include your personal transport or vehicle freight cost. If travel expenses to {top_mandi} are lower than ₹{extra_earnings:,.0f}/quintal, it is your most profitable choice.

🌾 **Actionable Farmer Advisory**
If transport logistics permit, prioritize selling at {top_mandi} to capture the current price peak before market arrivals increase further.
"""


def call_gemini_api(prompt_dict: Dict[str, str], api_key: Optional[str] = None) -> str:
    """
    Invokes Google Gemini API using google-generativeai SDK.
    Falls back gracefully if key is missing or request fails.
    """
    effective_key = api_key or Config.GEMINI_API_KEY
    if not effective_key or effective_key == "your_gemini_api_key_here":
        logger.info("No valid GEMINI_API_KEY configured. Returning structured rule-based explanation.")
        return "[Mode: Rule-Based Advisory Engine (Set GEMINI_API_KEY in .env for Gemini AI)]"

    try:
        import google.generativeai as genai
        genai.configure(api_key=effective_key)

        model_name = "gemini-1.5-flash"
        system_instruction = prompt_dict.get("system_instruction")
        user_prompt = prompt_dict.get("user_prompt", "")

        model = genai.GenerativeModel(
            model_name=model_name,
            system_instruction=system_instruction
        )

        response = model.generate_content(user_prompt)
        if response and response.text:
            return response.text.strip()
        else:
            logger.warning("Gemini API returned an empty response. Falling back to template.")
            return ""

    except Exception as e:
        logger.error(f"Error communicating with Gemini API: {e}")
        return ""
