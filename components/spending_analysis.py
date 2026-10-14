"""
Finary Spending Analysis Component.
In-depth deterministic breakdowns and clean, professional Plotly visualizations.
Analytics product feel with zero chart junk.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from config import CURRENCY_SYMBOL, THEME
from database import get_all_transactions, get_budget_config
from analytics import (
    calculate_spending_metrics,
    create_category_donut_chart,
    create_spending_trend_chart,
)
from components.ui import render_page_header, render_kpi_card, render_empty_state


def render_spending_analysis_page(ai_provider):
    df = get_all_transactions()
    if df.empty:
        render_page_header(
            title="Spending Intelligence & Analytics",
            subtitle="Granular behavioral patterns, category distributions, burn rates, and impulse leaks",
            breadcrumb="Finary"
        )
        render_empty_state(
            icon="◔",
            title="No Spending Data Available",
            message="Connect your bank account or load demo transactions from Dashboard or Settings to view your spending breakdown."
        )
        return

    budget_cfg = get_budget_config()
    dates = pd.to_datetime(df["date"]).sort_values()
    days_elapsed = max(1, min(budget_cfg.days_in_month, (dates.max() - dates.min()).days + 1))
    
    metrics = calculate_spending_metrics(df, days_elapsed=days_elapsed)

    # 1. Page Header
    render_page_header(
        title="Spending Intelligence & Analytics",
        subtitle=f"Tracking outflows across {days_elapsed} active days · {metrics['transaction_count']} verified transactions",
        badge_text="ANALYTICS ENGINE",
        badge_type="primary",
        breadcrumb="Finary"
    )
    
    # 2. Executive Analytics Metric Ribbon
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        render_kpi_card(
            label="Total Monthly Outflow",
            value=f"{CURRENCY_SYMBOL}{metrics['total_spent']:,.0f}",
            context=f"{metrics['transaction_count']} total transactions recorded"
        )
    with c2:
        render_kpi_card(
            label="Daily Burn Rate",
            value=f"{CURRENCY_SYMBOL}{metrics['burn_rate']:,.0f}",
            context=f"Average outflow per active day"
        )
    with c3:
        render_kpi_card(
            label="Top Spending Category",
            value=str(metrics['top_category']),
            context=f"{CURRENCY_SYMBOL}{metrics['top_category_spent']:,.0f} ({metrics['top_category_spent'] / max(1.0, metrics['total_spent']) * 100:.0f}% of total)"
        )
    with c4:
        render_kpi_card(
            label="Largest Single Outflow",
            value=f"{CURRENCY_SYMBOL}{metrics['largest_transaction']:,.0f}",
            context=str(metrics['largest_merchant'])
        )

    st.markdown("<div style='height: 1.25rem;'></div>", unsafe_allow_html=True)

    # 3. Dominant Trajectory: Cumulative Outflow Velocity vs Allowed Cap
    st.markdown("""
    <div class="finary-card" style="margin-bottom: 0.5rem;">
        <div style="font-size: 1.05rem; font-weight: 700; color: var(--text-primary);">
            Cumulative Outflow Velocity vs. Allowed Budget Cap
        </div>
        <div style="font-size: 0.8rem; color: var(--text-secondary); margin-top: 0.2rem;">
            Real-time burn trajectory plotted against the ideal linear pace and monthly spending ceiling
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

    # 4. Proportional Outflow Distribution & Behavioral Split
    col_left, col_right = st.columns([1, 1.2])

    with col_left:
        st.markdown("""
        <div class="finary-card" style="margin-bottom: 0.5rem;">
            <div style="font-size: 0.95rem; font-weight: 700; color: var(--text-primary);">
                Category Outflow Distribution
            </div>
            <div style="font-size: 0.78rem; color: var(--text-secondary); margin-top: 0.15rem;">
                Relative breakdown across spending categories
            </div>
        </div>
        """, unsafe_allow_html=True)
        donut = create_category_donut_chart(df)
        st.plotly_chart(donut, use_container_width=True, config={"displayModeBar": False})

    with col_right:
        st.markdown("""
        <div class="finary-card" style="margin-bottom: 0.5rem;">
            <div style="font-size: 0.95rem; font-weight: 700; color: var(--text-primary);">
                Behavioral Expenditure Breakdown
            </div>
            <div style="font-size: 0.78rem; color: var(--text-secondary); margin-top: 0.15rem;">
                Essential survival needs vs. planned freedom vs. impulse leakages
            </div>
        </div>
        """, unsafe_allow_html=True)

        pure_discretionary = max(0.0, metrics["discretionary_spent"] - metrics["impulse_spent"])
        split_df = pd.DataFrame([
            {"Type": "Essential Needs", "Amount": metrics["essential_spent"], "Color": THEME["color_info"]},
            {"Type": "Planned Discretionary", "Amount": pure_discretionary, "Color": THEME["color_primary"]},
            {"Type": "Potential Impulse", "Amount": metrics["impulse_spent"], "Color": THEME["color_warning"]},
        ])
        
        split_fig = px.bar(
            split_df,
            x="Type",
            y="Amount",
            color="Type",
            color_discrete_map={
                "Essential Needs": THEME["color_info"],
                "Planned Discretionary": THEME["color_primary"],
                "Potential Impulse": THEME["color_warning"],
            },
            text_auto=".2s"
        )
        split_fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            showlegend=False,
            margin=dict(t=15, b=20, l=15, r=15),
            height=280,
            xaxis=dict(showgrid=False, color=THEME["text_secondary"], tickfont=dict(size=11, family=THEME["font_family"])),
            yaxis=dict(showgrid=True, gridcolor=THEME["border_subtle"], color=THEME["text_secondary"], tickprefix="₹", tickfont=dict(size=11, family=THEME["font_family"]), zeroline=False),
            font=dict(family=THEME["font_family"])
        )
        split_fig.update_traces(marker_line_width=0)
        st.plotly_chart(split_fig, use_container_width=True, config={"displayModeBar": False})

    # 5. Impulse Spending Leakage Highlight
    if metrics["impulse_spent"] > 0:
        impulse_share = (metrics["impulse_spent"] / max(1.0, metrics["total_spent"])) * 100
        st.markdown(f"""
        <div style="background: var(--color-warning-subtle); border: 1px solid rgba(217, 119, 6, 0.25); border-radius: var(--radius-md); padding: 1.1rem 1.35rem; margin: 1rem 0; box-shadow: {THEME['shadow_sm']};">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 0.5rem;">
                <div style="font-size: 0.95rem; font-weight: 700; color: var(--color-warning); display: flex; align-items: center; gap: 0.4rem;">
                    <span>⚠️</span> Impulse Spending Analysis
                </div>
                <span class="pill-tag pill-impulse">
                    {metrics['impulse_count']} flagged purchases · {CURRENCY_SYMBOL}{metrics['impulse_spent']:,.0f} ({impulse_share:.1f}% of total)
                </span>
            </div>
            <div style="font-size: 0.84rem; color: var(--text-primary); margin-top: 0.4rem; line-height: 1.45;">
                Finary's algorithmic classifier tagged {metrics['impulse_count']} purchases as impulse decisions based on timing, amount deviation, and merchant patterns.
                Curtailing these specific triggers preserves an additional <b>{CURRENCY_SYMBOL}{metrics['impulse_spent']:,.0f}</b> for your monthly savings goal.
            </div>
        </div>
        """, unsafe_allow_html=True)

    # 6. Week-over-Week Behavior Comparison
    df_dates = df.copy()
    df_dates["datetime"] = pd.to_datetime(df_dates["date"])
    df_dates["week"] = df_dates["datetime"].dt.isocalendar().week
    
    weekly = df_dates.groupby("week")["amount"].sum().reset_index()
    if len(weekly) > 1:
        st.markdown("""
        <div class="finary-card" style="margin-top: 1rem; margin-bottom: 0.5rem;">
            <div style="font-size: 1rem; font-weight: 700; color: var(--text-primary);">
                Week-over-Week Outflow Progression
            </div>
            <div style="font-size: 0.8rem; color: var(--text-secondary); margin-top: 0.15rem;">
                Comparison of spending pace across consecutive statement weeks
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        w_cols = st.columns(len(weekly))
        for i, (_, row) in enumerate(weekly.iterrows()):
            with w_cols[i]:
                render_kpi_card(
                    label=f"Statement Week {int(row['week'])}",
                    value=f"{CURRENCY_SYMBOL}{row['amount']:,.0f}",
                    context="Weekly aggregated spend"
                )

