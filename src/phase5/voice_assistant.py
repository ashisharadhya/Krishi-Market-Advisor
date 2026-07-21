import os
import json
import google.generativeai as genai
from typing import Dict, Any

# Ensure Gemini API is configured
api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

def process_voice_command(audio_bytes: bytes, mime_type: str = "audio/wav") -> Dict[str, Any]:
    """
    Takes raw audio bytes (spoken in Kannada, English, or mixed), sends them to Gemini 2.5 Flash,
    and extracts a structured JSON response containing the agricultural entities.
    """
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    prompt = """
    You are an AI agricultural assistant. Listen to the farmer's voice input.
    The farmer may speak in Kannada, English, or a mix of both.
    
    Extract the following entities if present:
    - "district": The district they are calling from or asking about (e.g., Shivamogga, Uttara Kannada, Dakshina Kannada, Udupi, Chikmagalur, Hassan, Kodagu, Kasaragod). Must match one of these closely, or be null.
    - "crop": The crop they are asking about (e.g., Arecanut, Coffee, Paddy, Coconut).
    - "quantity": The amount they want to sell (number in Quintals). E.g., if they say "20 quintal", output 20.0. If not mentioned, null.
    - "vehicle": The transport vehicle they plan to use (e.g., Small Pickup, Medium Truck, Large Truck, Tractor). If not mentioned, null.
    - "language": The language they predominantly spoke in ("Kannada" or "English").
    
    Return ONLY a valid JSON object in this exact format, with no markdown formatting or extra text:
    {
        "district": "Shivamogga (Shimoga)",
        "crop": "Arecanut(Betelnut/Supari)",
        "quantity": 20.0,
        "vehicle": null,
        "language": "Kannada"
    }
    """
    
    try:
        response = model.generate_content([
            {"mime_type": mime_type, "data": audio_bytes},
            prompt
        ])
        
        # Clean up response (remove markdown code blocks if present)
        text = response.text.strip()
        if text.startswith("```json"):
            text = text[7:]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
            
        result = json.loads(text.strip())
        return result
    except Exception as e:
        print(f"Error processing voice command: {e}")
        return {}
