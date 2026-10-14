"""
Finary Sidebar Component.
Navigation, active AI provider badge, quick status, and live overspending simulator.
"""

import streamlit as st
from config import CURRENCY_SYMBOL
from database import get_transactions_count


def render_sidebar(active_provider_name: str, budget_state=None) -> str:
    with st.sidebar:
        # App Branding Header
        st.markdown(f"""
        <div style="padding: 0.25rem 0 1.25rem 0; border-bottom: 1px solid #E2E8F0; margin-bottom: 1.25rem;">
            <div style="font-size: 1.45rem; font-weight: 800; letter-spacing: -0.03em; color: #0F172A; display: flex; align-items: center; gap: 0.45rem;">
                <span style="color: #4F46E5; font-size: 1.25rem;">✦</span> Finary
            </div>
            <div style="font-size: 0.78rem; color: #475569; margin-top: 0.2rem; font-weight: 500;">
                AI Personal Finance Co-Pilot
            </div>
        </div>
        """, unsafe_allow_html=True)

        # AI Provider Badge
        st.markdown(f"""
        <div style="background-color: var(--bg-surface-subtle); border: 1px solid var(--border-subtle); border-radius: var(--radius-sm); padding: 0.55rem 0.75rem; margin-bottom: 1.25rem; display: flex; justify-content: space-between; align-items: center;">
            <span style="font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.05em; color: var(--text-muted); font-weight: 600;">Engine</span>
            <div style="font-size: 0.82rem; font-weight: 700; color: var(--text-primary); display: flex; align-items: center; gap: 0.4rem;">
                <span style="height: 6px; width: 6px; border-radius: 50%; background-color: var(--color-success); display: inline-block;"></span>
                {active_provider_name}
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Navigation Options
        nav_options = [
            "Dashboard",
            "Transactions",
            "Spending Analysis",
            "Budget Planner",
            "Spend Coach",
            "Settings"
        ]

        nav_icons = {
            "Dashboard": "✦",
            "Transactions": "⇄",
            "Spending Analysis": "◔",
            "Budget Planner": "⚖",
            "Spend Coach": "💬",
            "Settings": "⚙"
        }

        if "current_page" not in st.session_state:
            st.session_state["current_page"] = "Dashboard"

        selected_page = st.radio(
            "Navigation",
            options=nav_options,
            index=nav_options.index(st.session_state["current_page"]) if st.session_state["current_page"] in nav_options else 0,
            format_func=lambda x: f"{nav_icons.get(x, '•')}  {x}",
            label_visibility="collapsed"
        )
        st.session_state["current_page"] = selected_page

        st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)

        # Quick Live Demo Simulation Widget
        st.markdown("""
        <div style="font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.06em; color: var(--text-muted); font-weight: 700; margin-bottom: 0.5rem;">
            Interactive Sandbox
        </div>
        """, unsafe_allow_html=True)
        
        tx_count = get_transactions_count()
        if tx_count > 0 and budget_state:
            with st.expander("⚡ Simulate Overspending", expanded=False):
                st.caption("Instantly inject an unexpected ₹400 Swiggy order to witness dynamic budget adaptation:")
                if st.button("Trigger ₹400 Overspend", use_container_width=True, type="primary"):
                    from database import insert_transaction
                    from models import Transaction
                    t = Transaction(
                        date=budget_state.days_elapsed and "2026-10-14" or "2026-10-14",
                        raw_description="UPI-P2M-991204-SWIGGY-PARTY-ORDER",
                        merchant="Swiggy",
                        amount=400.0,
                        category="Food",
                        sub_category="Food Delivery",
                        transaction_type="debit",
                        impulse_score=0.85,
                        impulse_tag="Potential Impulse",
                        is_essential=False,
                        ai_provider=active_provider_name,
                        ai_model="demo-live",
                        confidence=0.98
                    )
                    insert_transaction(t)
                    st.toast("⚡ Added ₹400 Swiggy overspend! Budget recalculated.", icon="🎯")
                    st.rerun()

        st.markdown("""
        <div style="font-size: 0.72rem; color: var(--text-muted); text-align: center; margin-top: 2rem; border-top: 1px solid var(--border-subtle); padding-top: 1rem;">
            RBI Account Aggregator Protocol<br>
            <span style="font-weight: 600;">Finary Pacing Engine v1.0</span>
        </div>
        """, unsafe_allow_html=True)

        return selected_page
