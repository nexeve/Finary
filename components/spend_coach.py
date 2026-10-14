"""
Finary AI Spend Coach Component.
Dynamic financial intelligence surface that synthesizes exact calculations
into structured, actionable, and guilt-free advice (Observation -> Impact -> Recommendation).
"""

import streamlit as st
import pandas as pd
from config import CURRENCY_SYMBOL, THEME
from database import get_all_transactions, get_budget_config
from analytics import calculate_spending_metrics
from budget_engine import evaluate_budget_state
from components.ui import render_page_header, render_kpi_card, render_empty_state, render_coach_diagnostic


def render_spend_coach_page(ai_provider):
    df = get_all_transactions()
    if df.empty:
        render_page_header(
            title="AI Spend Coach",
            subtitle="Context-aware intelligence explaining your dynamic pacing with zero financial guilt",
            breadcrumb="Finary"
        )
        render_empty_state(
            icon="💬",
            title="Spend Coach Inactive",
            message="Connect your bank account or load sample statements via the Dashboard to activate your AI Spend Coach."
        )
        return

    budget_cfg = get_budget_config()
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

    # 1. Page Header with Status Badge
    render_page_header(
        title="AI Spend Coach",
        subtitle=f"Context-aware financial intelligence · Actively pacing across {state.days_remaining} remaining days",
        badge_text="CO-PILOT ACTIVE",
        badge_type="primary",
        breadcrumb="Finary"
    )

    # 2. State Summary KPI Ribbon
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        render_kpi_card(
            label="Current Status",
            value=state.status,
            context="Dynamic pacing condition",
            border_color="var(--color-primary)"
        )
    with c2:
        render_kpi_card(
            label="Adaptive Daily Limit",
            value=f"{CURRENCY_SYMBOL}{state.current_daily_allowance:,.0f}",
            context=f"Baseline was {CURRENCY_SYMBOL}{state.base_daily_allowance:,.0f}/day"
        )
    with c3:
        disc_color = "var(--color-success)" if state.current_discretionary_allowance > 0 else "var(--color-danger)"
        render_kpi_card(
            label="Discretionary Freedom",
            value=f"{CURRENCY_SYMBOL}{state.current_discretionary_allowance:,.0f}",
            context=f"After {CURRENCY_SYMBOL}{budget_cfg.daily_necessary_expense:,.0f} essential needs",
            border_color=disc_color
        )
    with c4:
        render_kpi_card(
            label="Pacing Window",
            value=f"{state.days_remaining} Days",
            context=f"Statement Day {days_elapsed} of {budget_cfg.days_in_month}"
        )

    st.markdown("<div style='height: 1.25rem;'></div>", unsafe_allow_html=True)

    # 3. STRUCTURED 3-TIER SPEND DIAGNOSTIC SURFACE
    # Visual separation: Observation -> Impact -> Recommendation
    top_cat = metrics["top_category"]
    top_spent = metrics["top_category_spent"]
    obs_text = (
        f"You are spending an average of <b>{CURRENCY_SYMBOL}{metrics['burn_rate']:,.0f}/day</b>. "
        f"<b>{top_cat}</b> is your highest outflow at <b>{CURRENCY_SYMBOL}{top_spent:,.0f}</b>. "
        f"Today's spend is {CURRENCY_SYMBOL}{state.today_spent:,.0f} "
        f"({'▲ +' if state.today_variance > 0 else '▼ -'}{CURRENCY_SYMBOL}{abs(state.today_variance):,.0f} vs target)."
    )

    savings_gap = budget_cfg.savings_goal - state.projected_savings
    if state.is_goal_impossible:
        imp_text = (
            f"At this burn velocity, your {CURRENCY_SYMBOL}{budget_cfg.savings_goal:,.0f} goal cannot be reached. "
            f"Maximum achievable month-end savings is <b>{CURRENCY_SYMBOL}{state.revised_achievable_savings:,.0f}</b>."
        )
    elif savings_gap > 0:
        imp_text = (
            f"At your current trajectory, projected month-end savings is <b>{CURRENCY_SYMBOL}{state.projected_savings:,.0f}</b> "
            f"— falling <b>{CURRENCY_SYMBOL}{savings_gap:,.0f}</b> short of your {CURRENCY_SYMBOL}{budget_cfg.savings_goal:,.0f} goal."
        )
    else:
        imp_text = (
            f"Your current pacing successfully preserves <b>{CURRENCY_SYMBOL}{state.projected_savings:,.0f}</b>. "
            f"You are fully on-track to reach your {CURRENCY_SYMBOL}{budget_cfg.savings_goal:,.0f} savings goal."
        )

    rec_text = (
        f"Cap discretionary spending at <b>{CURRENCY_SYMBOL}{max(0.0, state.current_discretionary_allowance):,.0f}/day</b> "
        f"(total daily spend under <b>{CURRENCY_SYMBOL}{state.current_daily_allowance:,.0f}/day</b>) "
        f"for the remaining {state.days_remaining} days to keep your savings 100% protected."
    )

    render_coach_diagnostic(
        observation=obs_text,
        impact=imp_text,
        recommendation=rec_text,
        provider_name=ai_provider.name
    )

    # 4. Contextual AI Provider Narrative
    coaching_ctx = {
        "monthly_budget": state.monthly_budget,
        "savings_goal": state.savings_goal,
        "allowed_spending": state.allowed_spending,
        "spent_so_far": state.spent_so_far,
        "remaining_budget": state.remaining_budget,
        "days_remaining": state.days_remaining,
        "base_daily_allowance": state.base_daily_allowance,
        "current_daily_allowance": state.current_daily_allowance,
        "daily_necessary_expense": state.daily_necessary_expense,
        "current_discretionary_allowance": state.current_discretionary_allowance,
        "today_spending": state.today_spent,
        "today_target": state.base_daily_allowance,
        "today_variance": state.today_variance,
        "status": state.status,
        "is_goal_impossible": state.is_goal_impossible,
        "minimum_reduction_needed": state.minimum_reduction_needed,
        "revised_achievable_savings": state.revised_achievable_savings,
    }

    coaching_narrative = ai_provider.generate_budget_coaching(coaching_ctx)
    st.markdown(f"""
    <div class="finary-card" style="margin-top: 1rem;">
        <div style="font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.06em; color: var(--text-muted); font-weight: 700; margin-bottom: 0.4rem;">
            Personalized Co-Pilot Synthesis
        </div>
        <div style="font-size: 0.92rem; line-height: 1.6; color: var(--text-primary);">
            {coaching_narrative}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 5. Interactive Co-Pilot Conversation Interface
    st.markdown("""
    <div style="font-size: 1.05rem; font-weight: 700; color: var(--text-primary); margin: 1.5rem 0 0.5rem 0;">
        💬 Ask Your Financial Co-Pilot
    </div>
    <div style="font-size: 0.82rem; color: var(--text-secondary); margin-bottom: 0.85rem;">
        Select a quick diagnostic question or ask anything about your spending trajectory:
    </div>
    """, unsafe_allow_html=True)

    quick_prompts = [
        "Why did my daily allowance change?",
        "How can I save ₹500 extra this week?",
        "Is my weekend food spending normal?",
        "Will I hit my savings goal by month-end?"
    ]

    cols = st.columns(len(quick_prompts))
    selected_prompt = None
    for i, p in enumerate(quick_prompts):
        if cols[i].button(p, use_container_width=True, key=f"qp_{i}"):
            selected_prompt = p

    user_query = st.text_input("Ask a question:", value=selected_prompt or "", placeholder="e.g. Can I afford a ₹600 dinner tonight?")

    if user_query:
        with st.chat_message("assistant"):
            with st.spinner("Consulting budget engine & statement records..."):
                if "why" in user_query.lower() or "allowance" in user_query.lower():
                    resp = (
                        f"Your daily target is currently **₹{state.current_daily_allowance:,.0f}/day** "
                        f"(vs baseline of ₹{state.base_daily_allowance:,.0f}/day). "
                        f"Because previous spending created a variance, our engine smoothed the delta "
                        f"across your remaining **{state.days_remaining} days** so your ₹{state.savings_goal:,.0f} savings goal stays completely protected."
                    )
                elif "500" in user_query.lower() or "save" in user_query.lower():
                    resp = (
                        f"To save an extra ₹500 across your remaining {state.days_remaining} days, "
                        f"you only need to reduce daily discretionary spending by **₹{500 / max(1, state.days_remaining):.0f}/day**. "
                        f"Swapping one food delivery order or taking the metro instead of an auto-rickshaw once covers this effortlessly."
                    )
                elif "goal" in user_query.lower() or "hit" in user_query.lower():
                    if state.is_goal_impossible:
                        resp = (
                            f"At your current burn rate, your ₹{state.savings_goal:,.0f} savings goal is mathematically unreachable. "
                            f"Realistic achievable savings is ₹{state.revised_achievable_savings:,.0f} unless all discretionary spending is paused."
                        )
                    else:
                        resp = (
                            f"Yes! If you keep total daily spend under **₹{state.current_daily_allowance:,.0f}/day** "
                            f"(with up to ₹{max(0.0, state.current_discretionary_allowance):,.0f} discretionary spending), "
                            f"you will finish the month with your entire **₹{state.savings_goal:,.0f}** savings locked in."
                        )
                elif "dinner" in user_query.lower() or "600" in user_query.lower() or "afford" in user_query.lower():
                    if state.current_discretionary_allowance >= 600:
                        resp = f"Yes! You have ₹{state.current_discretionary_allowance:,.0f} discretionary allowance today, so a ₹600 dinner fits comfortably within budget."
                    else:
                        projected_adj = max(0.0, (state.remaining_budget - 600) / max(1, state.days_remaining - 1))
                        resp = (
                            f"A ₹600 dinner will exceed today's discretionary allowance of ₹{state.current_discretionary_allowance:,.0f}. "
                            f"However, if you proceed, our engine will simply adjust your allowance to **₹{projected_adj:,.0f}/day** for the remaining {state.days_remaining - 1} days to keep your savings goal safe."
                        )
                else:
                    resp = (
                        f"Based on your current burn velocity of ₹{metrics['burn_rate']:,.0f}/day and {state.days_remaining} days remaining, "
                        f"staying within your discretionary allowance (₹{max(0.0, state.current_discretionary_allowance):,.0f}/day) "
                        f"is your highest leverage move right now."
                    )
                st.write(resp)

