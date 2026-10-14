"""
Abstract Base Class for AI Providers.
All LLM providers and Mock AI must implement this interface.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List


class AIProvider(ABC):
    name: str = "BaseAI"
    model_name: str = "unknown"

    @abstractmethod
    def parse_transaction(self, raw_text: str, amount: float = 0.0) -> Dict[str, Any]:
        """
        Parses raw bank/UPI transaction description into structured metadata:
        {
            "merchant": str,
            "category": str,
            "sub_category": str,
            "transaction_type": "debit" | "credit",
            "impulse_score": float (0.0 to 1.0),
            "impulse_tag": "Potential Impulse" | "Planned / Regular",
            "is_essential": bool,
            "confidence": float (0.0 to 1.0)
        }
        """
        pass

    @abstractmethod
    def generate_spending_insight(self, metrics: Dict[str, Any], recent_transactions: List[Dict[str, Any]]) -> str:
        """
        Generates an intelligent Gen-Z spending insight based on deterministic analytics.
        """
        pass

    @abstractmethod
    def generate_budget_coaching(self, budget_context: Dict[str, Any]) -> str:
        """
        Generates an empathetic, actionable budget coaching message explaining
        why daily allowances changed and how to stay on track.
        """
        pass
