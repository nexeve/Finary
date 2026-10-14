"""
Finary Budget Planner Component.
Interactive baseline budget configuration, visual adaptation relationship,
and dynamic allowance simulator. Showcases Finary's core differentiator.
"""

import streamlit as st
import pandas as pd
from config import CURRENCY_SYMBOL, THEME
from database import get_budget_config, update_budget_config, get_all_transactions
from models import BudgetConfig
from budget_engine import calculate_base_budget, evaluate_budget_state
from analytics import calculate_spending_metrics
from components.ui import render_page_header, render_kpi_card


def render_budget_planner_page():
    current_cfg = get_budget_config()
    df = get_all_transactions()
    
    # Calculate live budget state if transactions exist
    budget_state = None
    if not df.empty:
        dates = pd.to_datetime(df["date"]).sort_values()
        days_elapsed = max(1, min(current_cfg.days_in_month, (dates.max() - dates.min()).days + 1))
        metrics = calculate_spending_metrics(df, days_elapsed=days_elapsed)
        budget_state = evaluate_budget_state(
            config=current_cfg,
            spent_so_far=metrics["total_spent"],
            days_elapsed=days_elapsed,
            today_spent=metrics["today_spent"],
            today_essential=metrics["today_essential"],
            today_discretionary=metrics["today_discretionary"]
        )

    # 1. Page Header with Status Badge
    status_label = budget_state.status if budget_state else "BASELINE CONFIGURED"
    # Map status label to CSS class
    badge_type_map = {
        "ON TRACK": "on-track",
        "SLIGHTLY OVER": "slightly-over",
        "AT RISK": "at-risk",
        "CRITICAL": "critical",
        "BASELINE CONFIGURED": "baseline-configured"
    }
    badge_type = badge_type_map.get(status_label, "info")
    render_page_header(
        title="Adaptive Budget Architecture",
        subtitle="Establish monthly parameters. The engine continuously smooths daily spending allowances to protect savings.",
        badge_text=status_label,
        badge_type=badge_type,
        breadcrumb="Finary"
    )

    # 2. FINARY'S KEY DIFFERENTIATOR: THE VISUAL ADAPTATION CHAIN
    # Original Plan -> Actual Behavior -> Adjusted Plan -> Savings Goal
    if budget_state:
        diff = budget_state.current_daily_allowance - budget_state.base_daily_allowance
        diff_str = f"{'▲ +' if diff > 0 else '▼ -'}{CURRENCY_SYMBOL}{abs(diff):,.0f}/day"
        diff_color = "var(--color-success)" if diff >= 0 else "var(--color-warning)"
        
        st.markdown(f"""
        <div class="finary-card-hero">
            <div style="font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.08em; color: var(--text-secondary); font-weight: 700; margin-bottom: 0.75rem;">
                ✦ Finary Adaptive Pacing Engine · Live State Demonstration
            </div>
            
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; align-items: stretch;">
                <!-- Step 1: Original Plan -->
                <div style="background: var(--bg-surface); padding: 1rem 1.15rem; border-radius: var(--radius-md); border: 1px solid var(--border-subtle); box-shadow: {THEME['shadow_sm']};">
                    <div style="font-size: 0.68rem; text-transform: uppercase; letter-spacing: 0.06em; color: var(--text-muted); font-weight: 600;">1. Original Baseline</div>
                    <div style="font-size: 1.5rem; font-weight: 800; color: var(--text-primary); margin-top: 0.2rem;">
                        {CURRENCY_SYMBOL}{budget_state.base_daily_allowance:,.0f}<span style="font-size: 0.82rem; font-weight: 500; color: var(--text-muted);">/day</span>
                    </div>
                    <div style="font-size: 0.76rem; color: var(--text-secondary); margin-top: 0.25rem;">
                        {CURRENCY_SYMBOL}{current_cfg.allowed_spending:,.0f} across {current_cfg.days_in_month} days
                    </div>
                </div>

                <!-- Step 2: Actual Behavior -->
                <div style="background: var(--bg-surface); padding: 1rem 1.15rem; border-radius: var(--radius-md); border: 1px solid var(--border-subtle); box-shadow: {THEME['shadow_sm']};">
                    <div style="font-size: 0.68rem; text-transform: uppercase; letter-spacing: 0.06em; color: var(--text-muted); font-weight: 600;">2. Actual Pace</div>
                    <div style="font-size: 1.5rem; font-weight: 800; color: var(--text-primary); margin-top: 0.2rem;">
                        {CURRENCY_SYMBOL}{budget_state.spent_so_far:,.0f}
                    </div>
                    <div style="font-size: 0.76rem; color: var(--text-secondary); margin-top: 0.25rem;">
                        Day {budget_state.days_elapsed} · Today spent {CURRENCY_SYMBOL}{budget_state.today_spent:,.0f}
                    </div>
                </div>

                <!-- Step 3: Adjusted Plan -->
                <div style="background: var(--color-primary-subtle); padding: 1rem 1.15rem; border-radius: var(--radius-md); border: 1px solid rgba(79, 70, 229, 0.25); box-shadow: {THEME['shadow_sm']};">
                    <div style="font-size: 0.68rem; text-transform: uppercase; letter-spacing: 0.06em; color: var(--color-primary); font-weight: 700;">3. Adaptive Allowance</div>
                    <div style="font-size: 1.5rem; font-weight: 800; color: var(--color-primary); margin-top: 0.2rem;">
                        {CURRENCY_SYMBOL}{budget_state.current_daily_allowance:,.0f}<span style="font-size: 0.82rem; font-weight: 600;">/day</span>
                    </div>
                    <div style="font-size: 0.76rem; font-weight: 600; color: {diff_color}; margin-top: 0.25rem;">
                        {diff_str} adjustment
                    </div>
                </div>

                <!-- Step 4: Savings Goal Protected -->
                <div style="background: var(--bg-surface); padding: 1rem 1.15rem; border-radius: var(--radius-md); border: 1px solid var(--border-subtle); box-shadow: {THEME['shadow_sm']};">
                    <div style="font-size: 0.68rem; text-transform: uppercase; letter-spacing: 0.06em; color: var(--text-muted); font-weight: 600;">4. Savings Protected</div>
                    <div style="font-size: 1.5rem; font-weight: 800; color: var(--color-success); margin-top: 0.2rem;">
                        {CURRENCY_SYMBOL}{budget_state.projected_savings:,.0f}
                    </div>
                    <div style="font-size: 0.76rem; color: var(--text-secondary); margin-top: 0.25rem;">
                        Goal: {CURRENCY_SYMBOL}{current_cfg.savings_goal:,.0f} untouched
                    </div>
                </div>
            </div>

            <div style="margin-top: 1rem; padding-top: 0.75rem; border-top: 1px solid var(--border-subtle); font-size: 0.84rem; color: var(--text-secondary); line-height: 1.45;">
                <b>Adaptation Logic:</b> {budget_state.explanation}
            </div>
        </div>
        """, unsafe_allow_html=True)

    # 3. Parameter Inputs & Mathematical Baseline Preview
    col_form, col_calc = st.columns([1, 1.15])

    with col_form:
        st.markdown("""
        <div class="finary-card" style="margin-bottom: 0.75rem;">
            <div style="font-size: 1.05rem; font-weight: 700; color: var(--text-primary);">
                Budget Parameters
            </div>
            <div style="font-size: 0.8rem; color: var(--text-secondary); margin-top: 0.2rem;">
                Adjust monthly financial targets and statements cycle length:
            </div>
        </div>
        """, unsafe_allow_html=True)

        monthly_budget = st.number_input(
            "Monthly Budget / Income (₹)",
            min_value=1000.0,
            max_value=500000.0,
            value=float(current_cfg.monthly_budget),
            step=500.0,
            help="Total income or allowance allocated for this calendar month"
        )

        savings_goal = st.number_input(
            "Desired Monthly Savings Goal (₹)",
            min_value=0.0,
            max_value=monthly_budget,
            value=min(float(current_cfg.savings_goal), monthly_budget),
            step=250.0,
            help="Amount to preserve untouched in your savings account"
        )

        daily_necessary = st.number_input(
            "Fixed Daily Necessary Expenditure (₹)",
            min_value=0.0,
            max_value=monthly_budget / 30,
            value=float(current_cfg.daily_necessary_expense),
            step=25.0,
            help="Unavoidable daily needs (metro commute, meals, mandatory groceries)"
        )

        days_in_month = st.selectbox(
            "Statement Cycle Length (Days)",
            options=[28, 29, 30, 31],
            index=[28, 29, 30, 31].index(current_cfg.days_in_month) if current_cfg.days_in_month in [28, 29, 30, 31] else 2
        )

        if st.button("Save & Recalibrate Budget", type="primary", use_container_width=True):
            new_cfg = BudgetConfig(
                monthly_budget=monthly_budget,
                savings_goal=savings_goal,
                daily_necessary_expense=daily_necessary,
                days_in_month=days_in_month
            )
            update_budget_config(new_cfg)
            st.toast("✅ Budget configuration updated and applied!", icon="🎯")
            st.rerun()

    # Calculate preview
    preview = calculate_base_budget(
        monthly_budget=monthly_budget,
        savings_goal=savings_goal,
        daily_necessary_expense=daily_necessary,
        days_in_month=days_in_month
    )

    with col_calc:
        st.markdown("""
        <div class="finary-card" style="margin-bottom: 0.75rem;">
            <div style="font-size: 1.05rem; font-weight: 700; color: var(--text-primary);">
                Baseline Derivations
            </div>
            <div style="font-size: 0.8rem; color: var(--text-secondary); margin-top: 0.2rem;">
                Deterministic mathematical baseline derived from your parameters:
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div style="background-color: var(--bg-surface); border: 1px solid var(--border-subtle); border-radius: var(--radius-md); padding: 1.1rem 1.25rem; margin-bottom: 0.85rem; box-shadow: {THEME['shadow_sm']};">
            <div style="font-size: 0.72rem; text-transform: uppercase; color: var(--text-muted); font-weight: 600; letter-spacing: 0.05em;">
                Allowed Monthly Outflow
            </div>
            <div style="font-size: 1.25rem; color: var(--text-primary); margin: 0.25rem 0; font-feature-settings: 'tnum';">
                {CURRENCY_SYMBOL}{monthly_budget:,.0f} - {CURRENCY_SYMBOL}{savings_goal:,.0f} = <b>{CURRENCY_SYMBOL}{preview['allowed_spending']:,.0f}</b>
            </div>
            <div style="font-size: 0.8rem; color: var(--text-secondary);">
                Maximum total outflow allowed across the entire {days_in_month}-day cycle.
            </div>
        </div>
        """, unsafe_allow_html=True)

        b1, b2 = st.columns(2)
        with b1:
            st.markdown(f"""
            <div class="metric-container" style="border-color: rgba(79, 70, 229, 0.3);">
                <div class="metric-label">TOTAL DAILY ALLOWANCE</div>
                <div class="metric-value">{CURRENCY_SYMBOL}{preview['base_daily_allowance']:,.0f}<span style="font-size: 0.85rem; font-weight: 500;">/day</span></div>
                <div class="metric-subtitle">{CURRENCY_SYMBOL}{preview['allowed_spending']:,.0f} / {days_in_month} days</div>
            </div>
            """, unsafe_allow_html=True)

        with b2:
            disc_val = preview['base_discretionary_allowance']
            disc_color = "var(--color-success)" if disc_val > 0 else "var(--color-danger)"
            st.markdown(f"""
            <div class="metric-container" style="border-color: {disc_color};">
                <div class="metric-label">DISCRETIONARY ALLOWANCE</div>
                <div class="metric-value" style="color: {disc_color};">{CURRENCY_SYMBOL}{disc_val:,.0f}<span style="font-size: 0.85rem; font-weight: 500;">/day</span></div>
                <div class="metric-subtitle">{CURRENCY_SYMBOL}{preview['base_daily_allowance']:,.0f} - {CURRENCY_SYMBOL}{daily_necessary:,.0f} essential</div>
            </div>
            """, unsafe_allow_html=True)

        if preview['base_discretionary_allowance'] < 0:
            st.warning(
                f"⚠️ Daily necessary expenditure (₹{daily_necessary:.0f}) exceeds your daily allowance "
                f"(₹{preview['base_daily_allowance']:.0f}). Consider reducing your monthly savings target."
            )

    st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)

    # 4. Interactive "What-If" Spending Simulator
    st.markdown("""
    <div style="font-size: 1.15rem; font-weight: 700; color: var(--text-primary); margin-bottom: 0.35rem;">
        ⚡ Interactive "What-If" Spending Simulator
    </div>
    <div style="font-size: 0.84rem; color: var(--text-secondary); margin-bottom: 1.25rem;">
        Experience how an unexpected impulse expense today automatically recalibrates your remaining daily allowance without ruining your month-end savings goal:
    </div>
    """, unsafe_allow_html=True)

    sim_col1, sim_col2 = st.columns([1, 1.2])

    with sim_col1:
        hypo_spend = st.slider("Simulate Extra Spend Today (₹)", min_value=0, max_value=2000, value=400, step=50)
        rem_days_sim = st.slider("Remaining Days in Statement Cycle", min_value=1, max_value=days_in_month, value=12)

    with sim_col2:
        base_allowance = preview['base_daily_allowance']
        sim_variance = hypo_spend - base_allowance
        total_remaining_sim = (base_allowance * rem_days_sim) - sim_variance
        new_daily_sim = max(0.0, total_remaining_sim / rem_days_sim)
        new_disc_sim = new_daily_sim - daily_necessary

        st.markdown(f"""
        <div class="budget-hero">
            <div style="font-size: 0.72rem; font-weight: 700; color: var(--text-secondary); text-transform: uppercase; letter-spacing: 0.06em;">
                Simulator Live Recalculation
            </div>
            <div style="font-size: 2rem; font-weight: 800; color: var(--text-primary); margin: 0.25rem 0; font-feature-settings: 'tnum';">
                {CURRENCY_SYMBOL}{new_daily_sim:,.0f}/day <span style="font-size: 0.85rem; font-weight: 500; color: var(--text-muted);">(was {CURRENCY_SYMBOL}{base_allowance:,.0f})</span>
            </div>
            <div style="font-size: 0.84rem; color: var(--text-secondary); line-height: 1.45;">
                Spending <b>{CURRENCY_SYMBOL}{hypo_spend}</b> today creates a <b>{CURRENCY_SYMBOL}{max(0, sim_variance):,.0f}</b> variance above daily allowance.<br>
                Instead of forcing drastic guilt or immediate budget failure, the engine absorbs the delta across all {rem_days_sim} remaining days.<br>
                <b>New Discretionary Allowance:</b> <span style="color: var(--color-primary); font-weight: 700;">{CURRENCY_SYMBOL}{new_disc_sim:,.0f}/day</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

