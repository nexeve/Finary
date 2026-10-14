"""
Finary Reusable UI Component Primitives.
Centralized, token-driven UI elements for clean fintech presentation.
Ensures visual consistency across all pages and charts.
"""

import streamlit as st
import plotly.graph_objects as go
from config import THEME, CURRENCY_SYMBOL


def apply_chart_theme(fig: go.Figure, height: int = 280) -> go.Figure:
    """Applies unified, clean fintech chart styling based on central design tokens."""
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=height,
        margin=dict(t=24, b=24, l=16, r=16),
        font=dict(
            family=THEME["font_family"],
            color=THEME["text_primary"],
            size=12
        ),
        hoverlabel=dict(
            bgcolor=THEME["bg_surface"],
            bordercolor=THEME["border_default"],
            font=dict(
                family=THEME["font_family"],
                color=THEME["text_primary"],
                size=12
            )
        ),
        xaxis=dict(
            showgrid=False,
            color=THEME["text_secondary"],
            tickfont=dict(size=11, family=THEME["font_family"], color=THEME["text_secondary"]),
            linecolor=THEME["border_subtle"],
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor=THEME["border_subtle"],
            gridwidth=1,
            color=THEME["text_secondary"],
            tickfont=dict(size=11, family=THEME["font_family"], color=THEME["text_secondary"]),
            zeroline=False,
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(
                size=11,
                family=THEME["font_family"],
                color=THEME["text_secondary"]
            )
        )
    )
    return fig


def render_page_header(
    title: str,
    subtitle: str,
    badge_text: str = None,
    badge_type: str = "primary",
    breadcrumb: str = "Finary"
):
    """Renders a consistent, calm top-level page header with breadcrumb and status."""
    # Render the main header content
    st.markdown(f"<div style='margin-bottom: 1.5rem; display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 1rem;'>", unsafe_allow_html=True)
    
    st.markdown(f"<div>", unsafe_allow_html=True)
    st.markdown(f"<div style='font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.08em; color: var(--text-muted); font-weight: 600; margin-bottom: 0.2rem;'>{breadcrumb} · {title}</div>", unsafe_allow_html=True)
    st.markdown(f"<div style='font-size: 1.75rem; font-weight: 800; color: var(--text-primary); letter-spacing: -0.025em; line-height: 1.2;'>{title}</div>", unsafe_allow_html=True)
    st.markdown(f"<div style='font-size: 0.88rem; color: var(--text-secondary); margin-top: 0.25rem;'>{subtitle}</div>", unsafe_allow_html=True)
    st.markdown(f"</div>", unsafe_allow_html=True)
    
    # Render badge if provided
    if badge_text:
        type_class = f"status-{badge_type.lower().replace(' ', '-')}"
        st.markdown(f"<div class='status-badge {type_class}'><span style='height: 6px; width: 6px; border-radius: 50%; background-color: currentColor; display: inline-block;'></span>{badge_text}</div>", unsafe_allow_html=True)
    
    st.markdown(f"</div>", unsafe_allow_html=True)


def render_kpi_card(
    label: str,
    value: str,
    context: str,
    delta: str = None,
    delta_type: str = "neutral",
    border_color: str = None
):
    """Renders a visually commanding financial KPI answering a direct question."""
    border_style = f"border-color: {border_color};" if border_color else ""
    
    delta_html = ""
    if delta:
        delta_color = {
            "positive": "var(--color-success)",
            "negative": "var(--color-danger)",
            "warning": "var(--color-warning)",
            "neutral": "var(--text-muted)"
        }.get(delta_type, "var(--text-muted)")
        delta_html = f"<span style='font-size: 0.75rem; font-weight: 600; color: {delta_color}; margin-left: 0.35rem;'>{delta}</span>"

    st.markdown(f"""
    <div class="metric-container" style="{border_style}">
        <div class="metric-label">{label}</div>
        <div class="metric-value">{value} {delta_html}</div>
        <div class="metric-subtitle">{context}</div>
    </div>
    """, unsafe_allow_html=True)


def render_adaptive_budget_hero(state, config):
    """
    Renders Finary's signature Adaptive Daily Limit Hero Banner.
    Clearly shows Original Plan -> Actual Spend -> Adaptive Limit -> Savings Goal relationship.
    """
    diff = state.current_daily_allowance - state.base_daily_allowance
    diff_sign = "▲ +" if diff > 0 else "▼ -"
    diff_color = "var(--color-success)" if diff >= 0 else "var(--color-warning)"
    adjustment_text = f"{diff_sign}{CURRENCY_SYMBOL}{abs(diff):,.0f}/day adjusted"

    st.markdown(f"""
    <div class="budget-hero">
        <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 1.25rem;">
            <div style="flex: 1; min-width: 280px;">
                <div style="display: flex; align-items: center; gap: 0.6rem; margin-bottom: 0.35rem;">
                    <span style="font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.08em; color: var(--text-secondary); font-weight: 700;">
                        SAFE DAILY SPENDING ALLOWANCE
                    </span>
                    <span class="pill-tag" style="background: var(--color-primary-subtle); color: var(--color-primary); font-size: 0.68rem;">
                        ✦ DYNAMIC PACING ACTIVE
                    </span>
                </div>
                
                <div style="display: flex; align-items: baseline; gap: 0.85rem; margin-top: 0.15rem;">
                    <span style="font-size: 2.5rem; font-weight: 800; color: var(--text-primary); letter-spacing: -0.03em;">
                        {CURRENCY_SYMBOL}{state.current_daily_allowance:,.0f}
                    </span>
                    <span style="font-size: 0.88rem; color: var(--text-muted);">
                        Original: <span style="text-decoration: line-through;">{CURRENCY_SYMBOL}{state.base_daily_allowance:,.0f}/day</span>
                    </span>
                    <span style="font-size: 0.82rem; font-weight: 600; color: {diff_color}; background: var(--bg-surface); padding: 0.15rem 0.5rem; border-radius: var(--radius-sm); border: 1px solid var(--border-subtle);">
                        {adjustment_text}
                    </span>
                </div>

                <div style="display: flex; gap: 0.85rem; margin-top: 1rem; flex-wrap: wrap;">
                    <div style="background: var(--bg-surface); padding: 0.5rem 0.85rem; border-radius: var(--radius-sm); border: 1px solid var(--border-subtle); box-shadow: {THEME['shadow_sm']};">
                        <span style="font-size: 0.68rem; color: var(--text-muted); font-weight: 600; text-transform: uppercase;">Fixed Essentials</span>
                        <div style="font-size: 0.95rem; font-weight: 700; color: var(--text-primary);">{CURRENCY_SYMBOL}{config.daily_necessary_expense:,.0f}/day</div>
                    </div>
                    <div style="background: var(--bg-surface); padding: 0.5rem 0.85rem; border-radius: var(--radius-sm); border: 1px solid var(--border-subtle); box-shadow: {THEME['shadow_sm']};">
                        <span style="font-size: 0.68rem; color: var(--text-muted); font-weight: 600; text-transform: uppercase;">Discretionary Room</span>
                        <div style="font-size: 0.95rem; font-weight: 700; color: var(--color-primary);">{CURRENCY_SYMBOL}{state.current_discretionary_allowance:,.0f}/day</div>
                    </div>
                    <div style="background: var(--bg-surface); padding: 0.5rem 0.85rem; border-radius: var(--radius-sm); border: 1px solid var(--border-subtle); box-shadow: {THEME['shadow_sm']};">
                        <span style="font-size: 0.68rem; color: var(--text-muted); font-weight: 600; text-transform: uppercase;">Cycle Window</span>
                        <div style="font-size: 0.95rem; font-weight: 700; color: var(--text-primary);">{state.days_remaining} days left</div>
                    </div>
                </div>
            </div>

            <div style="background-color: var(--bg-surface); border: 1px solid var(--border-subtle); border-radius: var(--radius-md); padding: 1rem 1.25rem; min-width: 250px; box-shadow: {THEME['shadow_sm']};">
                <div style="font-size: 0.72rem; text-transform: uppercase; color: var(--text-muted); font-weight: 600; letter-spacing: 0.05em;">
                    Today's Activity
                </div>
                <div style="font-size: 1.4rem; font-weight: 800; color: var(--text-primary); margin-top: 0.2rem;">
                    {CURRENCY_SYMBOL}{state.today_spent:,.0f}
                    <span style="font-size: 0.78rem; font-weight: 600; color: {'var(--color-danger)' if state.today_variance > 0 else 'var(--color-success)'}; margin-left: 0.35rem;">
                        {'▲ +' if state.today_variance > 0 else '▼ -'}{CURRENCY_SYMBOL}{abs(state.today_variance):,.0f} {'over' if state.today_variance > 0 else 'under'}
                    </span>
                </div>
                <div style="font-size: 0.78rem; color: var(--text-secondary); margin-top: 0.4rem; line-height: 1.4;">
                    Smooth Recovery: Pacing adjusted across {state.days_remaining} remaining days to protect your <b>{CURRENCY_SYMBOL}{config.savings_goal:,.0f}</b> goal.
                </div>
            </div>
        </div>

        <div style="margin-top: 1.1rem; padding-top: 0.85rem; border-top: 1px solid var(--border-subtle); font-size: 0.84rem; color: var(--text-secondary); display: flex; align-items: center; gap: 0.5rem;">
            <span>💡</span>
            <span>{state.explanation}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)


def get_category_icon(category: str) -> str:
    """Returns a simple, clean monogram/glyph for each transaction category."""
    icons = {
        "Food": "🍔",
        "Transport": "🚕",
        "Shopping": "🛍️",
        "Bills": "📄",
        "Entertainment": "🎬",
        "Subscriptions": "🔄",
        "Groceries": "🛒",
        "Healthcare": "💊",
        "Education": "📚",
        "Rent": "🏠",
        "Other": "💳"
    }
    return icons.get(category, "💳")


def render_transaction_row(tx, is_first: bool = False):
    """Renders a single premium transaction ledger row with structured metadata."""
    is_impulse = (getattr(tx, "impulse_tag", "") == "Potential Impulse") or (getattr(tx, "impulse_score", 0.0) >= 0.6)
    
    # Pills
    type_pill = '<span class="pill-tag pill-essential">Essential</span>' if tx.is_essential else '<span class="pill-tag pill-discretionary">Discretionary</span>'
    impulse_pill = '<span class="pill-tag pill-impulse" style="margin-left: 0.35rem;">⚠️ Potential Impulse</span>' if is_impulse else ''
    
    icon = get_category_icon(tx.category)
    raw_desc = getattr(tx, "raw_description", "")
    short_raw = f"{raw_desc[:28]}..." if len(raw_desc) > 28 else raw_desc
    
    st.markdown(f"""
    <div class="tx-item">
        <div style="display: flex; align-items: center; gap: 0.85rem; flex: 1; min-width: 0;">
            <div class="tx-avatar">
                {icon}
            </div>
            <div style="min-width: 0;">
                <div style="display: flex; align-items: center; gap: 0.5rem; flex-wrap: wrap;">
                    <span style="font-size: 0.92rem; font-weight: 700; color: var(--text-primary); white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">
                        {tx.merchant}
                    </span>
                    {type_pill}
                    {impulse_pill}
                </div>
                <div style="font-size: 0.78rem; color: var(--text-muted); margin-top: 0.15rem; display: flex; gap: 0.5rem; align-items: center;">
                    <span>{tx.date}</span>
                    <span>·</span>
                    <span>{tx.category}</span>
                    <span>·</span>
                    <span style="font-family: monospace; font-size: 0.72rem; color: var(--text-muted);">{short_raw}</span>
                </div>
            </div>
        </div>
        <div class="tx-amount">
            - {CURRENCY_SYMBOL}{tx.amount:,.2f}
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_empty_state(icon: str, title: str, message: str):
    """Renders an intentional, polished empty state."""
    st.markdown(f"""
    <div style="text-align: center; padding: 3rem 1.5rem; background: var(--bg-surface); border: 1px dashed var(--border-default); border-radius: var(--radius-lg); margin: 1.5rem 0;">
        <div style="font-size: 2.2rem; margin-bottom: 0.75rem;">{icon}</div>
        <div style="font-size: 1.1rem; font-weight: 700; color: var(--text-primary); margin-bottom: 0.35rem;">
            {title}
        </div>
        <div style="font-size: 0.86rem; color: var(--text-secondary); max-width: 440px; margin: 0 auto; line-height: 1.5;">
            {message}
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_coach_diagnostic(observation: str, impact: str, recommendation: str, provider_name: str = "AI"):
    """
    Renders structured 3-tier financial intelligence:
    1. OBSERVATION
    2. IMPACT
    3. RECOMMENDATION
    """
    st.markdown(f"""
    <div class="finary-card" style="border-left: 3px solid var(--color-primary);">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; border-bottom: 1px solid var(--border-subtle); padding-bottom: 0.5rem;">
            <div style="font-size: 0.85rem; font-weight: 700; color: var(--text-primary); display: flex; align-items: center; gap: 0.4rem;">
                <span style="color: var(--color-primary);">✦</span> Real-Time Spend Diagnostic
            </div>
            <div style="font-size: 0.72rem; color: var(--text-muted); font-weight: 500;">
                Calculated by {provider_name}
            </div>
        </div>
        
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 1rem;">
            <div style="background: var(--bg-surface-subtle); padding: 0.85rem 1rem; border-radius: var(--radius-sm); border: 1px solid var(--border-subtle);">
                <div style="font-size: 0.68rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.06em; color: var(--text-secondary); margin-bottom: 0.3rem;">
                    1. Observation
                </div>
                <div style="font-size: 0.86rem; color: var(--text-primary); line-height: 1.45;">
                    {observation}
                </div>
            </div>

            <div style="background: var(--bg-surface-subtle); padding: 0.85rem 1rem; border-radius: var(--radius-sm); border: 1px solid var(--border-subtle);">
                <div style="font-size: 0.68rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.06em; color: var(--color-warning); margin-bottom: 0.3rem;">
                    2. Trajectory Impact
                </div>
                <div style="font-size: 0.86rem; color: var(--text-primary); line-height: 1.45;">
                    {impact}
                </div>
            </div>

            <div style="background: var(--color-primary-subtle); padding: 0.85rem 1rem; border-radius: var(--radius-sm); border: 1px solid rgba(79, 70, 229, 0.2);">
                <div style="font-size: 0.68rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.06em; color: var(--color-primary); margin-bottom: 0.3rem;">
                    3. Actionable Recommendation
                </div>
                <div style="font-size: 0.86rem; color: var(--text-primary); line-height: 1.45; font-weight: 600;">
                    {recommendation}
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
