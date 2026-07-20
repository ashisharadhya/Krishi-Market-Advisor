"""
src/phase4/audio_service.py

Text-to-Speech (TTS) module for Krishi Market Advisor.
Converts Kannada & English market advisory text into audio bytes for Streamlit playback.
"""

import io
import logging
import re
from typing import Optional
from gtts import gTTS

logger = logging.getLogger("krishi")


def clean_text_for_speech(text: str) -> str:
    """Removes Markdown syntax, emojis, and symbols for smooth voice reading."""
    # Remove markdown headers and bold/italic indicators
    text = re.sub(r'[#*`_~]', '', text)
    # Remove emojis
    text = re.sub(r'[\U00010000-\U0010ffff]', '', text)
    # Clean multiple spaces/newlines
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def generate_audio_speech(text: str, lang: str = "kn") -> Optional[bytes]:
    """
    Generates MP3 audio bytes for the given text.
    
    :param text: Text content to speak
    :param lang: Language code ("kn" for Kannada, "en" for English)
    :return: Bytes object containing MP3 audio data
    """
    cleaned = clean_text_for_speech(text)
    if not cleaned:
        return None

    try:
        tts = gTTS(text=cleaned, lang=lang, slow=False)
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        return fp.read()
    except Exception as e:
        logger.error(f"Error generating audio speech with gTTS ({lang}): {e}")
        return None
