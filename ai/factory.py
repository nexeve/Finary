"""
AI Provider Factory.
Inspects environment variables, auto-detects configured LLMs, and instantiates the chosen provider.
"""

import os
from typing import Dict
from ai.base import AIProvider
from ai.mock import MockProvider
from ai.gemini import GeminiProvider
from ai.openai import OpenAIProvider
from ai.groq import GroqProvider


def get_available_providers() -> Dict[str, bool]:
    """Returns availability status for each supported provider."""
    return {
        "Mock": True,
        "Gemini": bool(os.getenv("GEMINI_API_KEY")),
        "OpenAI": bool(os.getenv("OPENAI_API_KEY")),
        "Groq": bool(os.getenv("GROQ_API_KEY")),
    }


def get_ai_provider(provider_name: str | None = None) -> AIProvider:
    """
    Returns an AIProvider instance.
    If 'Auto' or None, automatically selects the first available live provider,
    or falls back to MockProvider.
    """
    avail = get_available_providers()
    choice = (provider_name or "Auto").strip().title()

    if choice == "Auto":
        if avail["Gemini"]:
            return GeminiProvider()
        elif avail["Groq"]:
            return GroqProvider()
        elif avail["OpenAI"]:
            return OpenAIProvider()
        else:
            return MockProvider()

    if choice == "Gemini":
        return GeminiProvider() if avail["Gemini"] else MockProvider()
    elif choice == "Openai":
        return OpenAIProvider() if avail["OpenAI"] else MockProvider()
    elif choice == "Groq":
        return GroqProvider() if avail["Groq"] else MockProvider()
    elif choice in ["Mock", "Demo"]:
        return MockProvider()

    return MockProvider()
