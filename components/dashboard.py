"""
Finary Primary Dashboard Component.
Answers the 6 core FinTech questions and showcases the Dynamic Daily Budget hero.
Dominant primary visualization, commanding KPIs, and structured intelligence.
"""

import streamlit as st
import pandas as pd
from config import CURRENCY_SYMBOL, THEME
from database import get_all_transactions, get_budget_config
from analytics import (
    calculate_spending_metrics,
    create_category_donut_chart,
    create_daily_spending_bar_chart,
    create_spending_trend_chart,
)
from budget_engine import evaluate_budget_state
from components.aa_consent import render_aa_consent_flow
from components.ui import (
    render_page_header,
    render_kpi_card,
    render_adaptive_budget_hero,
    render_coach_diagnostic,
    render_transaction_row
)


def render_dashboard(ai_provider):
    df = get_all_transactions()

    # If no transactions in database, prompt the Simulated Account Aggregator
    if df.empty:
        st.markdown("""
        <div style="margin-bottom: 1.5rem;">
            <div style="font-size: 1.8rem; font-weight: 800; color: var(--text-primary); letter-spacing: -0.02em;">
                Welcome to Finary
            </div>
            <div style="color: var(--text-secondary); font-size: 1rem; margin-top: 0.25rem;">
                Connect once. Understand automatically. Spend smarter.
            </div>
        </div>
        """, unsafe_allow_html=True)
        render_aa_consent_flow(ai_provider)
        return

    # Calculate metrics & state
    budget_cfg = get_budget_config()
    
    # Days elapsed heuristic from dataset date range
    dates = pd.to_datetime(df["date"]).sort_values()
    days_elapsed = max(1, min(budget_cfg.days_in_month, (dates.max() - dates.min()).days + 1))
    
    metrics = calculate_spending_metrics(df, days_elapsed=days_elapsed)
    
    state = evaluate_budget_state(
        config=budget_cfg,
        spent_so_far=metrics["total_spent"],
        days_elapsed=days_elapsed,
        today_spent=metrics["today_spent"],
        today_essential=metrics["today_essential"],
        today_discretionary=metrics["today_discretionary"]
    )

    # 1. Consistent Application Header with Status Badge
    # Map status label to CSS class
    badge_type_map = {
        "ON TRACK": "on-track",
        "SLIGHTLY OVER": "slightly-over",
        "AT RISK": "at-risk",
        "CRITICAL": "critical"
    }
    badge_type = badge_type_map.get(state.status, "info")
    render_page_header(
        title="Dashboard",
        subtitle=f"Here's how your money is looking · Statement Day {days_elapsed} of {budget_cfg.days_in_month}",
        badge_text=state.status,
        badge_type=badge_type,
        breadcrumb="Finary"
    )

    # 2. PROMINENT DYNAMIC DAILY BUDGET HERO BANNER (Key Differentiator)
    render_adaptive_budget_hero(state, budget_cfg)

    # 3. COMMANDING KPI FINANCIAL SUMMARY (Answers core financial questions)
    m1, m2, m3, m4 = st.columns(4)

    with m1:
        render_kpi_card(
            label="Total Spent",
            value=f"{CURRENCY_SYMBOL}{metrics['total_spent']:,.0f}",
            context=f"of {CURRENCY_SYMBOL}{budget_cfg.allowed_spending:,.0f} allowed monthly spend"
        )

    with m2:
        rem_val = max(0.0, state.remaining_budget)
        rem_delta = "Over budget" if state.remaining_budget <= 0 else None
        render_kpi_card(
            label="Remaining Budget",
            value=f"{CURRENCY_SYMBOL}{rem_val:,.0f}",
            context=f"Across {state.days_remaining} days remaining in cycle",
            delta=rem_delta,
            delta_type="negative" if rem_delta else "neutral",
            border_color="var(--color-danger)" if state.remaining_budget <= 0 else None
        )

    with m3:
        allowance_diff = state.current_daily_allowance - state.base_daily_allowance
        allowance_delta = f"{'-' if allowance_diff < 0 else '+'}{CURRENCY_SYMBOL}{abs(allowance_diff):,.0f}" if allowance_diff != 0 else None
        render_kpi_card(
            label="Today's Allowance",
            value=f"{CURRENCY_SYMBOL}{state.current_daily_allowance:,.0f}",
            context=f"Original baseline: {CURRENCY_SYMBOL}{state.base_daily_allowance:,.0f}/day",
            delta=allowance_delta,
            delta_type="warning" if allowance_diff < 0 else "positive"
        )

    with m4:
        savings_gap = state.projected_savings - budget_cfg.savings_goal
        savings_delta = f"{'-' if savings_gap < 0 else '+'}{CURRENCY_SYMBOL}{abs(savings_gap):,.0f}" if savings_gap != 0 else "On Target"
        render_kpi_card(
            label="Projected Savings",
            value=f"{CURRENCY_SYMBOL}{state.projected_savings:,.0f}",
            context=f"Goal: {CURRENCY_SYMBOL}{budget_cfg.savings_goal:,.0f} untouched",
            delta=savings_delta,
            delta_type="positive" if savings_gap >= 0 else "warning"
        )

    st.markdown("<div style='height: 1.25rem;'></div>", unsafe_allow_html=True)

    # 4. MAIN FINANCIAL STORY (Dominant visual centerpiece)
    burn_rate = metrics['burn_rate']
    st.markdown(f"""
    <div class="finary-card" style="margin-bottom: 0.5rem;">
        <div style="display: flex; justify-content: space-between; align-items: baseline; flex-wrap: wrap;">
            <div>
                <div style="font-size: 1.05rem; font-weight: 700; color: var(--text-primary);">
                    Spending Velocity vs. Ideal Trajectory
                </div>
                <div style="font-size: 0.8rem; color: var(--text-secondary); margin-top: 0.2rem;">
                    Actual cumulative outflow velocity tracked against ideal pace to protect savings
                </div>
            </div>
            <div style="font-size: 0.78rem; font-weight: 600; color: var(--color-primary); background: var(--color-primary-subtle); padding: 0.2rem 0.6rem; border-radius: var(--radius-pill);">
                Pacing: {CURRENCY_SYMBOL}{burn_rate:.0f}/day
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    trend_fig = create_spending_trend_chart(
        df,
        monthly_budget=budget_cfg.monthly_budget,
        savings_goal=budget_cfg.savings_goal,
        days_in_month=budget_cfg.days_in_month
    )
    st.plotly_chart(trend_fig, use_container_width=True, config={"displayModeBar": False})

    st.markdown("<div style='height: 0.75rem;'></div>", unsafe_allow_html=True)

    # 5. SUPPORTING FINANCIAL INSIGHTS: Category Outflow & Daily Spend Pacing
    c1, c2 = st.columns([1, 1.2])

    with c1:
        st.markdown("""
        <div class="finary-card" style="margin-bottom: 0.5rem;">
            <div style="font-size: 0.95rem; font-weight: 700; color: var(--text-primary);">
                Where Did My Money Go?
            </div>
            <div style="font-size: 0.78rem; color: var(--text-secondary); margin-top: 0.15rem;">
                Category distribution across all accounts
            </div>
        </div>
        """, unsafe_allow_html=True)
        donut = create_category_donut_chart(df)
        st.plotly_chart(donut, use_container_width=True, config={"displayModeBar": False})

    with c2:
        st.markdown(f"""
        <div class="finary-card" style="margin-bottom: 0.5rem;">
            <div style="font-size: 0.95rem; font-weight: 700; color: var(--text-primary);">
                Daily Outflow vs. Dynamic Limit
            </div>
            <div style="font-size: 0.78rem; color: var(--text-secondary); margin-top: 0.15rem;">
                Threshold limit: {CURRENCY_SYMBOL}{state.current_daily_allowance:,.0f}/day
            </div>
        </div>
        """, unsafe_allow_html=True)
        bar = create_daily_spending_bar_chart(df, daily_limit=state.current_daily_allowance)
        st.plotly_chart(bar, use_container_width=True, config={"displayModeBar": False})

    # 6. STRUCTURED AI SPEND COACH PROACTIVE DIAGNOSTIC (Observation -> Impact -> Recommendation)
    obs = f"You are averaging ₹{metrics['burn_rate']:,.0f}/day across {days_elapsed} active days, with {metrics['top_category']} accounting for your largest outflow."
    imp = f"At this pace, your projected month-end savings is ₹{state.projected_savings:,.0f} (Goal: ₹{budget_cfg.savings_goal:,.0f})."
    rec = f"Keep discretionary spending under ₹{max(0.0, state.current_discretionary_allowance):,.0f}/day for the next {state.days_remaining} days to ensure complete recovery."
    
    render_coach_diagnostic(
        observation=obs,
        impact=imp,
        recommendation=rec,
        provider_name=ai_provider.name
    )

    # 7. RECENT TRANSACTIONS PREVIEW (Replaced raw div with custom rows)
    st.markdown("""
    <div style="display: flex; justify-content: space-between; align-items: center; margin: 1.5rem 0 0.75rem 0;">
        <div style="font-size: 1.05rem; font-weight: 700; color: var(--text-primary);">
            Recent Activity
        </div>
        <div style="font-size: 0.8rem; color: var(--text-muted);">
            Latest 5 Transactions
        </div>
    </div>
    """, unsafe_allow_html=True)

    from models import Transaction
    recent_df = df.head(5)
    for _, row in recent_df.iterrows():
        t = Transaction(
            date=str(row["date"]),
            merchant=str(row["merchant"]),
            category=str(row["category"]),
            amount=float(row["amount"]),
            raw_description=str(row.get("raw_description", "")),
            impulse_score=float(row.get("impulse_score", 0.0)),
            impulse_tag=str(row.get("impulse_tag", "Planned / Regular")),
            is_essential=bool(row.get("is_essential", False))
        )
        render_transaction_row(t)

