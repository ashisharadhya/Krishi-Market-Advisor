"""
src/phase4/prompt_builder.py

Formats structured market recommendation results into rich, well-instructed
prompts for the Google Gemini API to produce clear, multi-lingual explanations
for Karnataka farmers.
"""

from typing import Dict, Any


SYSTEM_INSTRUCTION_EN = """
You are Krishi Market Advisor, an expert agricultural economist and AI advisor for Karnataka farmers.
Your job is to explain crop price recommendations in clear, concise, practical, and empathetic language.
Provide actionable insights based on market modal prices, price trends, earnings gaps, and transport cautions.
Do not use overly complex jargon or fake facts.
"""

SYSTEM_INSTRUCTION_KN = """
ನೀವು ಕೃಷಿ ಮಾರುಕಟ್ಟೆ ಸಲಹೆಗಾರರು (Krishi Market Advisor), ಕರ್ನಾಟಕದ ರೈತರಿಗೆ ಎಐ ಕೃಷಿ ಸಲಹೆಗಾರರು.
ಮಾರುಕಟ್ಟೆ ಬೆಲೆಗಳು, ದರ ಬದಲಾವಣೆಯ ಟ್ರೆಂಡ್, ಮತ್ತು ಲಾಭದ ವ್ಯತ್ಯಾಸಗಳ ಆಧಾರದ ಮೇಲೆ ಅತ್ಯುತ್ತಮ ಮಾರುಕಟ್ಟೆಯ ಸಲಹೆಯನ್ನು ಸ್ಪಷ್ಟ, ಸರಳ ಹಾಗೂ ವ್ಯವಹಾರಿಕ ಕನ್ನಡದಲ್ಲಿ ನೀಡಿ.
ರೈತರಿಗೆ ಅನುಕೂಲವಾಗುವಂತೆ ನೇರ ಹಾಗೂ ಪ್ರಾಯೋಗಿಕ ಮಾಹಿತಿ ನೀಡಿ.
"""


def build_explanation_prompt(result: Dict[str, Any], lang: str = "en") -> Dict[str, str]:
    """
    Constructs system prompt and user prompt based on recommendation result and language choice.
    
    :param result: Recommendation dictionary from recommendation_adapter.get_market_recommendation()
    :param lang: "en" for English, "kn" for Kannada
    :return: Dict with "system_instruction" and "user_prompt"
    """
    if result.get("status") != "success":
        msg = result.get("message", "No valid recommendation data available.")
        return {
            "system_instruction": SYSTEM_INSTRUCTION_EN if lang == "en" else SYSTEM_INSTRUCTION_KN,
            "user_prompt": f"Data notice: {msg}. Please provide a polite message explaining that insufficient data is available today."
        }

    rec = result["recommendation"]
    commodity = result["commodity"]
    variety = result.get("variety", "General")
    top_market = rec["recommended_market"]
    top_price = rec["highest_price"]
    top_date = rec["date"]
    top_trend = rec["trend_desc"]
    lowest_market = rec["lowest_market"]
    lowest_price = rec["lowest_price"]
    avg_price = rec["average_price"]
    extra_earnings = rec["extra_earnings"]
    extra_earnings_pct = rec["extra_earnings_pct"]
    reliable_count = result["reliable_markets_count"]
    total_days = result["total_days"]
    transport_warning = result["transport_warning"]

    # Market summary list
    market_lines = []
    for m in result.get("markets", []):
        market_lines.append(f"- {m['market']}: ₹{m['latest_price']:,.0f}/quintal (Date: {m['latest_date']}, Trend: {m['trend_desc']})")
    markets_summary = "\n".join(market_lines)

    if lang.lower() == "kn":
        system_prompt = SYSTEM_INSTRUCTION_KN
        user_prompt = f"""
ಮಾರುಕಟ್ಟೆ ದತ್ತಾಂಶ (Market Data):
- ಬೆಳೆ: {commodity}
- ಅತ್ಯುತ್ತಮ ಮಾರುಕಟ್ಟೆ: {top_market} (₹{top_price:,.0f})
- ಲಾಭ: ₹{extra_earnings:,.0f} ಹೆಚ್ಚುವರಿ

ದಯವಿಟ್ಟು ಕೆಳಗಿನ 5 ಪ್ರಶ್ನೆಗಳಿಗೆ ನೇರವಾದ ಉತ್ತರಗಳನ್ನು ನೀಡಿ:
1. ನಾನು ಏನು ಮಾಡಬೇಕು? (What should I do?)
2. ಏಕೆ? (Why?)
3. ಅಪಾಯಗಳೇನು? (What are the risks?)
4. ಈ ಸಲಹೆ ಎಷ್ಟು ವಿಶ್ವಾಸಾರ್ಹ? (How confident is the recommendation?)
5. ಪರ್ಯಾಯಗಳೇನು? (What alternatives exist?)
"""
        voice_prompt = f"""
Create a short, natural-sounding voice script (30-45 seconds) in Kannada for a farmer. 
Do not read exact raw numbers unnecessarily, speak conversationally.
Data: {commodity} is best at {top_market} today.
"""
    else:
        system_prompt = SYSTEM_INSTRUCTION_EN
        user_prompt = f"""
Based on the market data for {commodity} (Top market: {top_market} at ₹{top_price:,.0f} with extra earnings ₹{extra_earnings:,.0f}), provide a structured explanation answering exactly these 5 questions concisely:

1. What should I do?
2. Why?
3. What are the risks?
4. How confident is the recommendation?
5. What alternatives exist?
"""
        voice_prompt = f"""
Create a short, natural-sounding voice script (30-45 seconds) in English for a farmer. 
Do not read exact raw numbers unnecessarily, speak conversationally like an agricultural expert.
Data: {commodity} is best at {top_market} today.
"""

    return {
        "system_instruction": system_prompt,
        "user_prompt": user_prompt,
        "voice_prompt": voice_prompt
    }
