"""
Google Gemini AI Provider for Finary.
Uses Gemini REST API with automatic fallback to MockProvider on errors.
"""

import os
import json
import requests
from typing import Dict, Any, List
from ai.base import AIProvider
from ai.mock import MockProvider
from config import IMPULSE_THRESHOLD, IMPULSE_TAG_POTENTIAL, IMPULSE_TAG_REGULAR


class GeminiProvider(AIProvider):
    name: str = "Google Gemini"
    model_name: str = "gemini-2.5-flash"

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY", "")
        self.fallback = MockProvider()

    def _clean_json(self, text: str) -> str:
        text = text.strip()
        if text.startswith("```json"):
            text = text[7:]
        elif text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        return text.strip()

    def _call_gemini(self, prompt: str, system_instruction: str = "") -> str:
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY is not configured.")

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model_name}:generateContent?key={self.api_key}"
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.3}
        }
        if system_instruction:
            payload["systemInstruction"] = {"parts": [{"text": system_instruction}]}

        resp = requests.post(url, json=payload, timeout=8)
        resp.raise_for_status()
        data = resp.json()
        return data["candidates"][0]["content"]["parts"][0]["text"]

    def parse_transaction(self, raw_text: str, amount: float = 0.0) -> Dict[str, Any]:
        if not self.api_key:
            return self.fallback.parse_transaction(raw_text, amount)

        prompt = f"""
        Extract transaction metadata from this raw bank description: "{raw_text}", amount: ₹{amount}.
        Respond ONLY with a JSON object:
        {{
            "merchant": "<clean merchant name>",
            "category": "<Food|Transport|Shopping|Bills|Entertainment|Subscriptions|Groceries|Healthcare|Education|Rent|Other>",
            "sub_category": "<specific subcategory>",
            "transaction_type": "debit",
            "impulse_score": <float 0.0 to 1.0>,
            "impulse_tag": "<Potential Impulse or Planned / Regular>",
            "is_essential": <true or false>,
            "confidence": <float 0.0 to 1.0>
        }}
        """
        try:
            raw_res = self._call_gemini(prompt, "You are a specialized FinTech transaction classifier.")
            parsed = json.loads(self._clean_json(raw_res))
            score = float(parsed.get("impulse_score", 0.0))
            parsed["impulse_tag"] = IMPULSE_TAG_POTENTIAL if score >= IMPULSE_THRESHOLD else IMPULSE_TAG_REGULAR
            parsed["ai_provider"] = "Gemini"
            parsed["ai_model"] = self.model_name
            return parsed
        except Exception:
            res = self.fallback.parse_transaction(raw_text, amount)
            res["ai_provider"] = "Gemini (Fallback to Mock)"
            return res

    def generate_spending_insight(self, metrics: Dict[str, Any], recent_transactions: List[Dict[str, Any]]) -> str:
        if not self.api_key:
            return self.fallback.generate_spending_insight(metrics, recent_transactions)

        prompt = f"""
        Analyze these monthly spending metrics for a young Indian earner:
        Metrics: {json.dumps(metrics)}
        Recent transactions: {json.dumps(recent_transactions[:5])}

        Write 2-3 concise, witty, actionable FinTech insights in a smart Gen-Z tone.
        Reference exact numbers from the metrics. Avoid generic platitudes like 'spend less'.
        """
        try:
            return self._call_gemini(prompt, "You are Finary's AI Spend Coach.")
        except Exception:
            return self.fallback.generate_spending_insight(metrics, recent_transactions)

    def generate_budget_coaching(self, budget_context: Dict[str, Any]) -> str:
        if not self.api_key:
            return self.fallback.generate_budget_coaching(budget_context)

        prompt = f"""
        Context from dynamic budget engine:
        {json.dumps(budget_context)}

        Explain clearly in 2-3 short paragraphs:
        1. What happened with today's spending vs target
        2. Why the daily allowance adjusted (distributed over remaining days)
        3. Clear recovery target to hit their savings goal.
        Tone: empathetic, smart, Gen-Z, zero financial judgment.
        """
        try:
            return self._call_gemini(prompt, "You are Finary's AI Spend Coach.")
        except Exception:
            return self.fallback.generate_budget_coaching(budget_context)
