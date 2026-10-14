"""
Finary Data Models.
Structured data representations for Transactions, Budget Configuration, and State.
"""

from dataclasses import dataclass, asdict
from typing import Optional, Dict, Any


@dataclass
class Transaction:
    id: Optional[int] = None
    date: str = ""
    raw_description: str = ""
    merchant: str = "Unknown"
    amount: float = 0.0
    category: str = "Other"
    sub_category: str = "General"
    transaction_type: str = "debit"
    impulse_score: float = 0.0
    impulse_tag: str = "Planned / Regular"
    is_essential: bool = False
    ai_provider: str = "Mock"
    ai_model: str = "demo-heuristic"
    confidence: float = 1.0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class BudgetConfig:
    monthly_budget: float = 10000.0
    savings_goal: float = 3000.0
    daily_necessary_expense: float = 150.0
    days_in_month: int = 30

    @property
    def allowed_spending(self) -> float:
        return max(0.0, self.monthly_budget - self.savings_goal)


@dataclass
class BudgetState:
    monthly_budget: float
    savings_goal: float
    daily_necessary_expense: float
    days_in_month: int
    days_elapsed: int
    days_remaining: int
    allowed_spending: float
    spent_so_far: float
    remaining_budget: float
    base_daily_allowance: float
    base_discretionary_allowance: float
    current_daily_allowance: float
    current_discretionary_allowance: float
    today_spent: float
    today_essential: float
    today_discretionary: float
    today_variance: float
    projected_month_end_spend: float
    projected_savings: float
    status: str
    is_goal_impossible: bool
    minimum_reduction_needed: float
    revised_achievable_savings: float
    recovery_daily_limit: float
    explanation: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
