"""
OpenAI Provider for Finary.
Uses standard chat completion endpoint with automatic fallback.
"""

import os
import json
import requests
from typing import Dict, Any, List
from ai.base import AIProvider
from ai.mock import MockProvider
from config import IMPULSE_THRESHOLD, IMPULSE_TAG_POTENTIAL, IMPULSE_TAG_REGULAR


class OpenAIProvider(AIProvider):
    name: str = "OpenAI"
    model_name: str = "gpt-4o-mini"

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY", "")
        self.fallback = MockProvider()

    def _call_openai(self, messages: List[Dict[str, str]]) -> str:
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY is not configured.")

        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.model_name,
            "messages": messages,
            "temperature": 0.3
        }
        resp = requests.post(url, headers=headers, json=payload, timeout=8)
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"]

    def parse_transaction(self, raw_text: str, amount: float = 0.0) -> Dict[str, Any]:
        if not self.api_key:
            return self.fallback.parse_transaction(raw_text, amount)

        prompt = f"""
        Extract transaction metadata from raw string: "{raw_text}", amount: ₹{amount}.
        Respond strictly with JSON:
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
            raw_res = self._call_openai([
                {"role": "system", "content": "You are a specialized FinTech transaction classifier. Return JSON only."},
                {"role": "user", "content": prompt}
            ])
            text = raw_res.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
            parsed = json.loads(text)
            score = float(parsed.get("impulse_score", 0.0))
            parsed["impulse_tag"] = IMPULSE_TAG_POTENTIAL if score >= IMPULSE_THRESHOLD else IMPULSE_TAG_REGULAR
            parsed["ai_provider"] = "OpenAI"
            parsed["ai_model"] = self.model_name
            return parsed
        except Exception:
            res = self.fallback.parse_transaction(raw_text, amount)
            res["ai_provider"] = "OpenAI (Fallback to Mock)"
            return res

    def generate_spending_insight(self, metrics: Dict[str, Any], recent_transactions: List[Dict[str, Any]]) -> str:
        if not self.api_key:
            return self.fallback.generate_spending_insight(metrics, recent_transactions)

        try:
            return self._call_openai([
                {"role": "system", "content": "You are Finary's Gen-Z AI Spend Coach."},
                {"role": "user", "content": f"Analyze metrics: {json.dumps(metrics)}. Recent: {json.dumps(recent_transactions[:5])}. Give 2-3 concise insights."}
            ])
        except Exception:
            return self.fallback.generate_spending_insight(metrics, recent_transactions)

    def generate_budget_coaching(self, budget_context: Dict[str, Any]) -> str:
        if not self.api_key:
            return self.fallback.generate_budget_coaching(budget_context)

        try:
            return self._call_openai([
                {"role": "system", "content": "You are Finary's Gen-Z AI Spend Coach."},
                {"role": "user", "content": f"Budget state: {json.dumps(budget_context)}. Explain changes and recovery plan with zero judgment."}
            ])
        except Exception:
            return self.fallback.generate_budget_coaching(budget_context)
