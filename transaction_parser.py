"""
Transaction Parser Pipeline.
Converts raw bank/UPI transaction strings into structured Transaction domain models.
Delegates to active AI provider with zero-crash fallbacks.
"""

import pandas as pd
from typing import List, Optional
from config import MOCK_DATA_PATH
from models import Transaction
from ai.base import AIProvider
from ai.factory import get_ai_provider


def parse_single_transaction(
    raw_desc: str,
    amount: float,
    date: str,
    provider: Optional[AIProvider] = None
) -> Transaction:
    ai = provider or get_ai_provider()
    
    try:
        parsed = ai.parse_transaction(raw_desc, amount)
    except Exception:
        from ai.mock import MockProvider
        parsed = MockProvider().parse_transaction(raw_desc, amount)

    return Transaction(
        date=date,
        raw_description=raw_desc,
        merchant=parsed.get("merchant", "UPI Merchant"),
        amount=float(amount),
        category=parsed.get("category", "Other"),
        sub_category=parsed.get("sub_category", "General"),
        transaction_type=parsed.get("transaction_type", "debit"),
        impulse_score=float(parsed.get("impulse_score", 0.0)),
        impulse_tag=parsed.get("impulse_tag", "Planned / Regular"),
        is_essential=bool(parsed.get("is_essential", False)),
        ai_provider=parsed.get("ai_provider", ai.name),
        ai_model=parsed.get("ai_model", ai.model_name),
        confidence=float(parsed.get("confidence", 0.95))
    )


def parse_mock_transactions_file(
    csv_path: str = MOCK_DATA_PATH,
    provider: Optional[AIProvider] = None
) -> List[Transaction]:
    """
    Parses transactions from CSV through the AI provider pipeline.
    """
    df = pd.read_csv(csv_path)
    ai = provider or get_ai_provider()
    transactions: List[Transaction] = []

    for _, row in df.iterrows():
        raw_desc = str(row["raw_description"])
        amount = float(row["amount"])
        date = str(row["date"])

        t = parse_single_transaction(raw_desc, amount, date, ai)
        transactions.append(t)

    return transactions
