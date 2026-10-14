"""
Finary Budget Mathematics Engine.
Single source of truth for deterministic financial calculations.
Pure Python - AI never performs financial arithmetic.
"""

from typing import Dict, Any, Tuple
from models import BudgetConfig, BudgetState
from config import (
    STATUS_ON_TRACK,
    STATUS_SLIGHTLY_OVER,
    STATUS_AT_RISK,
    STATUS_CRITICAL,
)


def calculate_base_budget(
    monthly_budget: float,
    savings_goal: float,
    daily_necessary_expense: float,
    days_in_month: int = 30
) -> Dict[str, float]:
    """
    Calculates initial baseline allowances before any dynamic spending occurs.
    """
    days = max(1, int(days_in_month))
    monthly_budget = max(0.0, float(monthly_budget))
    savings_goal = max(0.0, float(savings_goal))
    daily_necessary_expense = max(0.0, float(daily_necessary_expense))

    allowed_spending = max(0.0, monthly_budget - savings_goal)
    base_daily_allowance = allowed_spending / days
    base_discretionary_allowance = base_daily_allowance - daily_necessary_expense

    return {
        "monthly_budget": round(monthly_budget, 2),
        "savings_goal": round(savings_goal, 2),
        "daily_necessary_expense": round(daily_necessary_expense, 2),
        "days_in_month": days,
        "allowed_spending": round(allowed_spending, 2),
        "base_daily_allowance": round(base_daily_allowance, 2),
        "base_discretionary_allowance": round(base_discretionary_allowance, 2),
    }


def calculate_daily_variance(actual_spent: float, daily_target: float) -> float:
    """
    Difference between actual spend and the daily target.
    Positive value indicates overspend; negative indicates underspend.
    """
    return round(float(actual_spent) - float(daily_target), 2)


def calculate_remaining_budget(
    monthly_budget: float,
    spent_so_far: float,
    savings_goal: float
) -> float:
    """
    Calculates remaining allowed spending while preserving the savings goal.
    """
    allowed_spending = max(0.0, float(monthly_budget) - float(savings_goal))
    return round(allowed_spending - float(spent_so_far), 2)


def calculate_recovery_allowance(
    remaining_allowed: float,
    remaining_days: int,
    daily_necessary_expense: float
) -> Dict[str, float]:
    """
    Spreads the remaining allowed spending evenly across remaining days.
    """
    rem_days = max(1, int(remaining_days))
    rem_allowed = float(remaining_allowed)
    daily_nec = float(daily_necessary_expense)

    new_daily_total = rem_allowed / rem_days
    new_daily_discretionary = new_daily_total - daily_nec

    return {
        "remaining_allowed": round(rem_allowed, 2),
        "remaining_days": rem_days,
        "new_daily_total_allowance": round(new_daily_total, 2),
        "new_daily_discretionary_allowance": round(new_daily_discretionary, 2),
    }


def calculate_projected_spending(
    spent_so_far: float,
    days_elapsed: int,
    days_in_month: int
) -> float:
    """
    Estimates month-end spend based on current pace (daily burn rate).
    """
    days_in_month = max(1, int(days_in_month))
    days_elapsed = max(0, min(days_in_month, int(days_elapsed)))

    if days_elapsed <= 0 or spent_so_far <= 0:
        return 0.0

    daily_burn_rate = float(spent_so_far) / days_elapsed
    return round(daily_burn_rate * days_in_month, 2)


def calculate_budget_status(
    monthly_budget: float,
    savings_goal: float,
    spent_so_far: float,
    projected_spend: float,
    days_remaining: int
) -> str:
    """
    Determines status (ON TRACK, SLIGHTLY OVER, AT RISK, CRITICAL).
    """
    allowed_spending = max(0.0, float(monthly_budget) - float(savings_goal))

    # If already spent more than total monthly budget: CRITICAL
    if spent_so_far > monthly_budget:
        return STATUS_CRITICAL

    # If spent more than allowed spending: savings goal breached
    if spent_so_far > allowed_spending:
        return STATUS_AT_RISK

    # Compare projected spend with allowed spending
    if allowed_spending > 0:
        spend_ratio = projected_spend / allowed_spending
    else:
        spend_ratio = 1.0 if spent_so_far == 0 else 2.0

    if spend_ratio <= 1.0:
        return STATUS_ON_TRACK
    elif spend_ratio <= 1.10:
        return STATUS_SLIGHTLY_OVER
    elif spend_ratio <= 1.25:
        return STATUS_AT_RISK
    else:
        return STATUS_CRITICAL


def evaluate_budget_state(
    config: BudgetConfig,
    spent_so_far: float,
    days_elapsed: int,
    today_spent: float = 0.0,
    today_essential: float = 0.0,
    today_discretionary: float = 0.0
) -> BudgetState:
    """
    Comprehensive evaluation of the budget state, returning a populated BudgetState object.
    """
    days_in_month = max(1, int(config.days_in_month))
    days_elapsed = max(0, min(days_in_month, int(days_elapsed)))
    days_remaining = max(0, days_in_month - days_elapsed)

    # Base calculations
    base = calculate_base_budget(
        config.monthly_budget,
        config.savings_goal,
        config.daily_necessary_expense,
        days_in_month
    )

    allowed_spending = base["allowed_spending"]
    base_daily_allowance = base["base_daily_allowance"]
    base_discretionary = base["base_discretionary_allowance"]

    # Remaining budget
    remaining_budget = calculate_remaining_budget(
        config.monthly_budget,
        spent_so_far,
        config.savings_goal
    )

    # Dynamic allowance across remaining days
    if days_remaining > 0:
        recovery = calculate_recovery_allowance(
            remaining_budget,
            days_remaining,
            config.daily_necessary_expense
        )
        current_daily_allowance = recovery["new_daily_total_allowance"]
        current_discretionary = recovery["new_daily_discretionary_allowance"]
    else:
        # Last day or no days remaining
        current_daily_allowance = max(0.0, remaining_budget)
        current_discretionary = current_daily_allowance - config.daily_necessary_expense

    # Today's variance relative to base daily target
    today_variance = calculate_daily_variance(today_spent, base_daily_allowance)

    # Projected spending & savings
    projected_spend = calculate_projected_spending(spent_so_far, days_elapsed, days_in_month)
    projected_savings = round(config.monthly_budget - projected_spend, 2)

    # Check if savings goal is impossible
    is_goal_impossible = False
    minimum_reduction_needed = 0.0
    revised_achievable_savings = config.savings_goal
    recovery_daily_limit = current_daily_allowance
    explanation = ""

    # Mathematical impossibility checks:
    # 1. Total spent already exceeds allowed spending (spent_so_far + necessary minimum > monthly_budget)
    min_future_necessities = days_remaining * config.daily_necessary_expense
    unavoidable_spend = spent_so_far + min_future_necessities

    if unavoidable_spend > allowed_spending:
        is_goal_impossible = True
        minimum_reduction_needed = round(unavoidable_spend - allowed_spending, 2)
        revised_achievable_savings = max(0.0, round(config.monthly_budget - unavoidable_spend, 2))
        # Daily allowance strictly constrained to necessities or remaining cash
        recovery_daily_limit = round(max(0.0, (config.monthly_budget - spent_so_far) / max(1, days_remaining)), 2)
        explanation = (
            "Your current spending has made the original savings goal unreachable at your current pace. "
            f"Even with zero discretionary spending, necessary expenses of ₹{config.daily_necessary_expense:.0f}/day "
            f"for the remaining {days_remaining} days will reach ₹{unavoidable_spend:.0f}."
        )
    elif today_variance > 0:
        explanation = (
            f"Your daily limit changed because you spent ₹{today_variance:.0f} above today's target. "
            f"The adjustment is distributed over your remaining {days_remaining} days."
        )
    elif today_variance < 0 and today_spent > 0:
        underspend = abs(today_variance)
        explanation = (
            f"Great pacing! You spent ₹{underspend:.0f} under today's target, "
            f"giving you extra buffer for your remaining {days_remaining} days."
        )
    else:
        explanation = f"You are pacing right on track with your ₹{base_daily_allowance:.0f}/day target."

    status = calculate_budget_status(
        config.monthly_budget,
        config.savings_goal,
        spent_so_far,
        projected_spend,
        days_remaining
    )

    if is_goal_impossible:
        status = STATUS_CRITICAL if status != STATUS_CRITICAL else status

    return BudgetState(
        monthly_budget=config.monthly_budget,
        savings_goal=config.savings_goal,
        daily_necessary_expense=config.daily_necessary_expense,
        days_in_month=days_in_month,
        days_elapsed=days_elapsed,
        days_remaining=days_remaining,
        allowed_spending=allowed_spending,
        spent_so_far=round(spent_so_far, 2),
        remaining_budget=remaining_budget,
        base_daily_allowance=base_daily_allowance,
        base_discretionary_allowance=base_discretionary,
        current_daily_allowance=current_daily_allowance,
        current_discretionary_allowance=current_discretionary,
        today_spent=round(today_spent, 2),
        today_essential=round(today_essential, 2),
        today_discretionary=round(today_discretionary, 2),
        today_variance=today_variance,
        projected_month_end_spend=projected_spend,
        projected_savings=projected_savings,
        status=status,
        is_goal_impossible=is_goal_impossible,
        minimum_reduction_needed=minimum_reduction_needed,
        revised_achievable_savings=revised_achievable_savings,
        recovery_daily_limit=recovery_daily_limit,
        explanation=explanation,
    )
