"""
Finary - Zero-Effort AI Personal Finance Co-Pilot.
Main Streamlit application entrypoint.
"""

import streamlit as st
import pandas as pd
from config import get_app_css, THEME
from database import init_db, get_budget_config, get_all_transactions
from budget_engine import evaluate_budget_state
from analytics import calculate_spending_metrics
from ai.factory import get_ai_provider

# Import Components
from components.sidebar import render_sidebar
from components.dashboard import render_dashboard
from components.transactions import render_transactions_page
from components.spending_analysis import render_spending_analysis_page
from components.budget_planner import render_budget_planner_page
from components.spend_coach import render_spend_coach_page
from components.settings import render_settings_page


# Streamlit Page Setup
st.set_page_config(
    page_title="Finary · AI Personal Finance Co-Pilot",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize Database Schema
init_db()

# Inject Reusable Theme CSS (Central Design System)
st.markdown(get_app_css(THEME), unsafe_allow_html=True)

# Discover Active AI Engine
selected_provider_mode = st.session_state.get("selected_ai_provider", "Auto")
ai_provider = get_ai_provider(selected_provider_mode)

# Pre-calculate budget state for sidebar widgets if transactions exist
df = get_all_transactions()
budget_state = None
if not df.empty:
    budget_cfg = get_budget_config()
    dates = pd.to_datetime(df["date"]).sort_values()
    days_elapsed = max(1, min(budget_cfg.days_in_month, (dates.max() - dates.min()).days + 1))
    metrics = calculate_spending_metrics(df, days_elapsed=days_elapsed)
    budget_state = evaluate_budget_state(
        config=budget_cfg,
        spent_so_far=metrics["total_spent"],
        days_elapsed=days_elapsed,
        today_spent=metrics["today_spent"],
        today_essential=metrics["today_essential"],
        today_discretionary=metrics["today_discretionary"]
    )

# Render Sidebar Navigation
current_page = render_sidebar(
    active_provider_name=ai_provider.name,
    budget_state=budget_state
)

# Route to active page component
try:
    if current_page == "Dashboard":
        render_dashboard(ai_provider)
    elif current_page == "Transactions":
        render_transactions_page(ai_provider)
    elif current_page == "Spending Analysis":
        render_spending_analysis_page(ai_provider)
    elif current_page == "Budget Planner":
        render_budget_planner_page()
    elif current_page == "Spend Coach":
        render_spend_coach_page(ai_provider)
    elif current_page == "Settings":
        render_settings_page(ai_provider.name)
except Exception as e:
    st.markdown(f"""
    <div style="background: var(--bg-surface); border: 1px solid var(--border-default); border-radius: var(--radius-lg); padding: 2rem; max-width: 600px; margin: 2rem auto; text-align: center; box-shadow: {THEME['shadow_card']};">
        <div style="font-size: 2rem; margin-bottom: 0.75rem;">⚠️</div>
        <div style="font-size: 1.2rem; font-weight: 700; color: var(--text-primary); margin-bottom: 0.35rem;">
            Unable to Display {current_page}
        </div>
        <div style="font-size: 0.88rem; color: var(--text-secondary); line-height: 1.5; margin-bottom: 1.25rem;">
            A temporary presentation discrepancy was encountered while parsing the statement view.<br>
            Your underlying financial ledger and calculations remain safe.
        </div>
        <div style="font-size: 0.8rem; color: var(--text-muted); background: var(--bg-surface-subtle); padding: 0.5rem 0.75rem; border-radius: var(--radius-sm); border: 1px solid var(--border-subtle); margin-bottom: 1.25rem; font-family: monospace;">
            Diagnostic details: {str(e)}
        </div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Return to Dashboard", type="primary", use_container_width=False):
        st.session_state["current_page"] = "Dashboard"
        st.rerun()
