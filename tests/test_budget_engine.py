"""
Test suite for Finary Budget Engine.
Tests all required deterministic financial calculations and edge cases.
"""

import pytest
from models import BudgetConfig
from budget_engine import (
    calculate_base_budget,
    calculate_daily_variance,
    calculate_remaining_budget,
    calculate_recovery_allowance,
    calculate_projected_spending,
    calculate_budget_status,
    evaluate_budget_state,
)
from config import (
    STATUS_ON_TRACK,
    STATUS_SLIGHTLY_OVER,
    STATUS_AT_RISK,
    STATUS_CRITICAL,
)


def test_base_budget_calculation():
    """Verify standard example: 10,000 budget, 3,000 savings, 150 daily necessary, 30 days."""
    res = calculate_base_budget(10000, 3000, 150, 30)
    assert res["allowed_spending"] == 7000.0
    assert res["base_daily_allowance"] == 233.33
    assert res["base_discretionary_allowance"] == 83.33


def test_daily_variance():
    """Verify daily variance for overspend and underspend."""
    # Target 233.33, spent 400 => +166.67
    var_over = calculate_daily_variance(400.0, 233.33)
    assert var_over == 166.67

    # Target 233.33, spent 150 => -83.33
    var_under = calculate_daily_variance(150.0, 233.33)
    assert var_under == -83.33


def test_single_day_overspending_spread():
    """
    Verify dynamic budget spreading:
    Monthly: 10,000, Savings: 3,000 => Allowed: 7,000
    Base daily: 233.33, Base discretionary: 83.33
    Spent on day 1: 400 (variance +166.67).
    Remaining allowed: 7000 - 400 = 6600 across 29 days => 6600 / 29 = 227.59 / day.
    """
    config = BudgetConfig(monthly_budget=10000, savings_goal=3000, daily_necessary_expense=150, days_in_month=30)
    state = evaluate_budget_state(
        config=config,
        spent_so_far=400,
        days_elapsed=1,
        today_spent=400,
        today_essential=150,
        today_discretionary=250
    )
    assert state.remaining_budget == 6600.0
    assert state.days_remaining == 29
    assert state.current_daily_allowance == round(6600 / 29, 2)  # ~227.59
    assert state.current_discretionary_allowance == round(6600 / 29 - 150, 2)
    assert state.today_variance > 0


def test_multiple_overspending_days():
    """
    Verify multiple overspending days successively compress discretionary allowance.
    Day 10 elapsed: spent 5,200 out of 7,000 allowed.
    Remaining days = 20. Remaining allowed = 1,800.
    New daily limit = 1800 / 20 = 90/day.
    Discretionary = 90 - 150 = -60/day (shows necessity compression).
    """
    config = BudgetConfig(monthly_budget=10000, savings_goal=3000, daily_necessary_expense=150, days_in_month=30)
    state = evaluate_budget_state(
        config=config,
        spent_so_far=5200,
        days_elapsed=10,
        today_spent=520,
    )
    assert state.remaining_budget == 1800.0
    assert state.days_remaining == 20
    assert state.current_daily_allowance == 90.0
    assert state.current_discretionary_allowance == -60.0


def test_underspending():
    """
    Verify underspending increases flexibility for remaining days.
    Day 15: spent only 2,000 out of 7,000 allowed (was paced for 3,500).
    Remaining: 5,000 across 15 days => 333.33/day (higher than base 233.33).
    """
    config = BudgetConfig(monthly_budget=10000, savings_goal=3000, daily_necessary_expense=150, days_in_month=30)
    state = evaluate_budget_state(
        config=config,
        spent_so_far=2000,
        days_elapsed=15,
        today_spent=100,
    )
    assert state.remaining_budget == 5000.0
    assert state.current_daily_allowance == 333.33
    assert state.current_discretionary_allowance == round(333.33 - 150, 2)
    assert state.status == STATUS_ON_TRACK


def test_impossible_savings_goal():
    """
    When total spent so far + remaining necessities exceeds allowed spending,
    the system flags the savings goal as mathematically impossible,
    without inventing fake numbers.
    """
    # 7,000 allowed spending.
    # Day 20: Spent 6,500.
    # Remaining 10 days * 150 = 1,500 unavoidable necessities.
    # Unavoidable total = 6,500 + 1,500 = 8,000 > 7,000.
    config = BudgetConfig(monthly_budget=10000, savings_goal=3000, daily_necessary_expense=150, days_in_month=30)
    state = evaluate_budget_state(
        config=config,
        spent_so_far=6500,
        days_elapsed=20,
        today_spent=300,
    )
    assert state.is_goal_impossible is True
    assert state.minimum_reduction_needed == 1000.0  # 8000 - 7000
    assert state.revised_achievable_savings == 2000.0  # 10000 - 8000
    assert "unreachable" in state.explanation


def test_zero_transactions():
    """Zero transactions on day 0 handles gracefully."""
    config = BudgetConfig(monthly_budget=10000, savings_goal=3000, daily_necessary_expense=150, days_in_month=30)
    state = evaluate_budget_state(
        config=config,
        spent_so_far=0,
        days_elapsed=0,
        today_spent=0,
    )
    assert state.spent_so_far == 0.0
    assert state.remaining_budget == 7000.0
    assert state.current_daily_allowance == 233.33
    assert state.status == STATUS_ON_TRACK


def test_last_day_of_month():
    """Verify handling when on the 30th of a 30-day month (days_remaining = 0)."""
    config = BudgetConfig(monthly_budget=10000, savings_goal=3000, daily_necessary_expense=150, days_in_month=30)
    state = evaluate_budget_state(
        config=config,
        spent_so_far=6800,
        days_elapsed=30,
        today_spent=100,
    )
    assert state.days_remaining == 0
    assert state.remaining_budget == 200.0
    assert state.current_daily_allowance == 200.0


def test_different_month_lengths():
    """Test 28 (Feb), 29 (Leap Feb), 31 (Jan/Mar/etc.) days."""
    for days in [28, 29, 31]:
        config = BudgetConfig(monthly_budget=10000, savings_goal=3000, daily_necessary_expense=150, days_in_month=days)
        base = calculate_base_budget(10000, 3000, 150, days)
        assert base["days_in_month"] == days
        assert base["base_daily_allowance"] == round(7000 / days, 2)


def test_necessary_expense_greater_than_allowance():
    """When daily necessity (e.g. 250) > base daily allowance (233.33), discretionary is negative."""
    config = BudgetConfig(monthly_budget=10000, savings_goal=3000, daily_necessary_expense=250, days_in_month=30)
    base = calculate_base_budget(config.monthly_budget, config.savings_goal, config.daily_necessary_expense, 30)
    assert base["base_discretionary_allowance"] < 0
    state = evaluate_budget_state(config, spent_so_far=0, days_elapsed=0)
    assert state.base_discretionary_allowance < 0
