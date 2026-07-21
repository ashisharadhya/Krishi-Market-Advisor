import os
import json
import google.generativeai as genai
from typing import Dict, Any, List

api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

def generate_market_outlook(markets_data: List[Dict], weather_data: Dict, commodity: str) -> Dict[str, Any]:
    """
    Analyzes historical price movement, seasonal trends, and weather forecasts
    to generate a proactive Market Outlook (7-Day).
    """
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    # Prepare data summary for the prompt
    markets_summary = []
    for m in markets_data:
        history_str = ", ".join([f"{d}: ₹{p}" for d, p in m['history'][-5:]]) # Last 5 days
        markets_summary.append(f"- Market: {m['market']} | Latest: ₹{m['latest_price']} | History: [{history_str}]")
    
    prompt = f"""
    You are an expert Agricultural AI Advisor for Krishi Market Advisor.
    Analyze the following market data and weather forecast to generate a 7-Day Market Outlook for {commodity}.
    
    Weather Context:
    {json.dumps(weather_data, indent=2)}
    
    Market Data (Recent History):
    {chr(10).join(markets_summary)}
    
    Do NOT predict exact future prices. Instead, provide a probabilistic outlook.
    
    Return ONLY a valid JSON object in this exact format:
    {{
        "trend": "Likely Upward", // Must be one of: "Likely Stable", "Likely Upward", "Likely Downward"
        "confidence": 78, // Integer between 0 and 100
        "risk": "Medium", // Must be one of: "Low", "Medium", "High"
        "drivers": [
            "Lower arrivals expected",
            "Festival demand increasing",
            "Rainfall might disrupt transport"
        ], // Array of 3-4 concise bullet points explaining the drivers
        "recommendation": "Waiting 2-3 days could improve returns, but monitor rainfall alerts closely.",
        "smart_alerts": [
            "Heavy rainfall expected after 4 PM.",
            "Buyer demand increasing in regional mandis."
        ] // 1-2 proactive smart context alerts based on the data
    }}
    """
    
    try:
        response = model.generate_content(prompt)
        text = response.text.strip()
        if text.startswith("```json"):
            text = text[7:]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
            
        return json.loads(text.strip())
    except Exception as e:
        print(f"Error generating market outlook: {e}")
        return {
            "trend": "Likely Stable",
            "confidence": 50,
            "risk": "Medium",
            "drivers": ["Historical data processing failed", "Unable to analyze weather context"],
            "recommendation": "Unable to generate AI outlook. Rely on current highest price market.",
            "smart_alerts": []
        }
