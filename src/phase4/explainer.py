"""
src/phase4/explainer.py

Coordinator module connecting Recommendation Adapter, Prompt Builder, and Gemini Service.
Produces ready-to-display explanation objects in English and Kannada.
"""

from typing import Dict, Any, Optional
from src.phase4.recommendation_adapter import get_market_recommendation
from src.phase4.prompt_builder import build_explanation_prompt
from src.phase4.gemini_service import call_gemini_api, build_fallback_explanation


def generate_market_explanation(
    folder: str = "data",
    commodity: str = "Arecanut(Betelnut/Supari)",
    variety: Optional[str] = None,
    threshold_pct: float = 70.0,
    lang: str = "en",
    api_key: Optional[str] = None
) -> Dict[str, Any]:
    """
    Runs recommendation engine and generates Gemini AI (or fallback) natural language explanation.
    """
    recommendation_data = get_market_recommendation(
        folder=folder,
        commodity=commodity,
        variety=variety,
        threshold_pct=threshold_pct
    )

    if recommendation_data.get("status") != "success":
        return {
            "status": recommendation_data.get("status"),
            "recommendation_data": recommendation_data,
            "explanation": recommendation_data.get("message", "No data available."),
            "mode": "error"
        }

    # Build prompt
    prompt_dict = build_explanation_prompt(recommendation_data, lang=lang)

    # Attempt Gemini API
    ai_text = call_gemini_api(prompt_dict, api_key=api_key)

    if ai_text and not ai_text.startswith("[Mode: Rule-Based"):
        mode = "gemini_ai"
        final_explanation = ai_text
    else:
        mode = "fallback_engine"
        fallback_text = build_fallback_explanation(recommendation_data, lang=lang)
        if ai_text.startswith("[Mode: Rule-Based"):
            final_explanation = f"{ai_text}\n\n{fallback_text}"
        else:
            final_explanation = fallback_text

    return {
        "status": "success",
        "recommendation_data": recommendation_data,
        "explanation": final_explanation,
        "mode": mode,
        "language": lang
    }
