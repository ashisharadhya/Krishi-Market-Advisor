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
ಕೆಳಗಿನ ಕೃಷಿ ಮಾರುಕಟ್ಟೆ ದತ್ತಾಂಶವನ್ನು ಆಧರಿಸಿ ಕರ್ನಾಟಕದ ರೈತರಿಗೆ ಸರಳ ಹಾಗೂ ಸಷ್ಟವಾದ ಕನ್ನಡದಲ್ಲಿ ಮಾರುಕಟ್ಟೆ ಸಲಹೆ ನೀಡಿ:

ಮಳೆ/ಬೆಳೆ ವಿವರ:
- ಬೆಳೆ: {commodity} (ತಳಿ: {variety})
- ವಿಶ್ಲೇಷಿಸಿದ ದಿನಗಳು: {total_days} ದಿನಗಳು ({reliable_count} ನಂಬಿಗಸ್ತ ಮಾರುಕಟ್ಟೆಗಳು)
- ಸಿಫಾರಸು ಮಾಡಿದ ಅತ್ಯುತ್ತಮ ಮಾರುಕಟ್ಟೆ: {top_market}
- ಅತ್ಯುಚ್ಚ ಬೆಲೆ: ₹{top_price:,.0f} ಪ್ರತಿಯೊಂದು ಕ್ವಿಂಟಾಲ್‌ಗೆ (ದಿನಾಂಕ: {top_date})
- ಬೆಲೆ ಬದಲಾವಣೆ ಟ್ರೆಂಡ್: {top_trend}
- ಇತರ ಮಾರುಕಟ್ಟೆಗಳ ಕನಿಷ್ಠ ಬೆಲೆ: ₹{lowest_price:,.0f} ({lowest_market})
- ಸರಾಸರಿ ಬೆಲೆ: ₹{avg_price:,.0f}
- ಅತ್ಯುತ್ತಮ ಮಾರುಕಟ್ಟೆಯಲ್ಲಿ ಮಾರಾಟ ಮಾಡುವುದರಿಂದ ಸಿಗುವ ಹೆಚ್ಚುವರಿ ಲಾಭ: ₹{extra_earnings:,.0f}/ಕ್ವಿಂಟಾಲ್ ({extra_earnings_pct:.1f}% ಹೆಚ್ಚು)

ವಿಶ್ವಾಸಾರ್ಹ ಮಾರುಕಟ್ಟೆಗಳ ಪಟ್ಟಿ:
{markets_summary}

ಸಾರಿಗೆ ಎಚ್ಚರಿಕೆ:
{transport_warning}

ದಯವಿಟ್ಟು ಕೆಳಗಿನ ಶೀರ್ಷಿಕೆಗಳೊಂದಿಗೆ ಉತ್ತರ ರೂಪಿಸಿ:
1. 💡 **ಪ್ರಮುಖ ಸಲಹೆ (Recommended Mandi)**: ಅತ್ಯುತ್ತಮ ಮಾರುಕಟ್ಟೆ ಮತ್ತು ಪ್ರಸ್ತುತ ಬೆಲೆ.
2. 📈 **ಬೆಲೆ ಟ್ರೆಂಡ್ ಮತ್ತು ಲಾಭದ ವಿಶ್ಲೇಷಣೆ (Price Trend & Profit)**: ಮಾರುಕಟ್ಟೆಯ ಏರಿಳಿತ ಮತ್ತು ಹೆಚ್ಚುವರಿ ಗಳಿಕೆಯ ವಿವರ.
3. 🚚 **ಸಾರಿಗೆ ವೆಚ್ಚದ ಎಚ್ಚರಿಕೆ (Transport & Distance Caution)**: ಸಾರಿಗೆ ವೆಚ್ಚ ಹಾಗೂ ದೂರದ ನಿರ್ಧಾರ.
4. 🌾 **ರೈತರಿಗೆ ಪ್ರಾಯೋಗಿಕ ಮಾರ್ಗದರ್ಶನ (Action Summary)**: ರೈತರು ಈಗ ಏನು ಮಾಡಬೇಕು.
"""
    else:
        system_prompt = SYSTEM_INSTRUCTION_EN
        user_prompt = f"""
Based on the following agricultural market data for Karnataka, write a clean, encouraging, and clear market recommendation for farmers:

Crop Details:
- Commodity: {commodity} (Variety: {variety})
- Historical Window: {total_days} days of data across {reliable_count} reliable mandis
- Top Recommended Mandi: {top_market}
- Highest Modal Price: ₹{top_price:,.0f} / quintal (as of {top_date})
- Price Trend: {top_trend}
- Lowest Mandi Price: ₹{lowest_price:,.0f} / quintal ({lowest_market})
- Average Mandi Price: ₹{avg_price:,.0f} / quintal
- Extra Earnings Potential: ₹{extra_earnings:,.0f} per quintal ({extra_earnings_pct:.1f}% more than lowest mandi)

Reliable Markets Breakdown:
{markets_summary}

Transport & Distance Disclaimer:
{transport_warning}

Please format your response into 4 distinct sections with Markdown headings:
1. 💡 **Top Recommendation**: State the winning mandi and current modal price clearly.
2. 📈 **Trend & Earnings Advantage**: Explain the price movement (rising/falling) and the extra profit per quintal.
3. 🚚 **Transport & Distance Caution**: Remind the farmer to weigh transport fuel/freight costs against price gains.
4. 🌾 **Actionable Farmer Advisory**: Concise 2-sentence summary of what the farmer should do today.
"""

    return {
        "system_instruction": system_prompt,
        "user_prompt": user_prompt
    }
