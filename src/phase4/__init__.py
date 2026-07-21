"""
Phase 4: Gemini AI Explanations & Streamlit UI Module
"""

from src.phase4.recommendation_adapter import get_market_recommendation
from src.phase4.prompt_builder import build_explanation_prompt
from src.phase4.gemini_service import call_gemini_api
from src.phase4.explainer import generate_market_explanation
from src.phase4.audio_service import generate_audio_speech
from src.phase4.transport_calculator import calculate_net_transport_profit, DISTANCES_KM, VEHICLE_TYPES

__all__ = [
    "get_market_recommendation",
    "build_explanation_prompt",
    "call_gemini_api",
    "generate_market_explanation",
    "generate_audio_speech",
    "calculate_net_transport_profit",
    "DISTANCES_KM",
    "VEHICLE_TYPES",
]
