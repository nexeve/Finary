"""
Finary Transactions Page Component.
Searchable, filterable transaction ledger with AI metadata and manual demo entry.
Custom fintech row items replace raw dataframes.
"""

import streamlit as st
import pandas as pd
from datetime import date
from config import CURRENCY_SYMBOL, CATEGORIES, THEME
from database import get_all_transactions, insert_transaction
from transaction_parser import parse_single_transaction
from models import Transaction
from components.ui import render_page_header, render_transaction_row, render_empty_state


def render_transactions_page(ai_provider):
    # 1. Page Header
    render_page_header(
        title="Transaction Ledger",
        subtitle="AI-classified statement transactions with automatic category, essential tag, and impulse risk detection",
        badge_text="LIVE LEDGER",
        badge_type="primary",
        breadcrumb="Finary"
    )

    # 2. Polished Product Controls / Filters
    with st.container():
        f1, f2, f3, f4 = st.columns([1.6, 1, 1, 1])

        with f1:
            search = st.text_input("Search Merchant or UPI String", placeholder="Search by merchant, e.g. Swiggy, Metro, Rent...")

        with f2:
            cat_filter = st.selectbox("Category", ["All Categories"] + CATEGORIES)

        with f3:
            impulse_filter = st.selectbox("Impulse Risk", ["All Transactions", "Potential Impulse Only", "Planned Only"])

        with f4:
            essential_filter = st.selectbox("Type", ["All Types", "Essential Only", "Discretionary Only"])

    # Map filters
    category_arg = cat_filter if cat_filter != "All Categories" else "All"
    impulse_only = (impulse_filter == "Potential Impulse Only")
    essential_val = True if essential_filter == "Essential Only" else (False if essential_filter == "Discretionary Only" else None)

    df = get_all_transactions(
        category=category_arg,
        impulse_only=impulse_only,
        essential_only=essential_val,
        search_query=search
    )

    if impulse_filter == "Planned Only" and not df.empty:
        df = df[df["impulse_score"] < 0.6]

    # Stats Toolbar
    count = len(df)
    total_val = float(df["amount"].sum()) if not df.empty else 0.0

    st.markdown(f"""
    <div style="display: flex; justify-content: space-between; align-items: center; background: var(--bg-surface); border: 1px solid var(--border-subtle); border-radius: var(--radius-sm); padding: 0.65rem 1rem; margin: 0.85rem 0 1.25rem 0; font-size: 0.84rem; box-shadow: {THEME['shadow_sm']};">
        <span style="color: var(--text-secondary);">
            Showing <b style="color: var(--text-primary);">{count}</b> transactions
        </span>
        <span style="color: var(--text-secondary);">
            Filtered Outflow Total: <b style="color: var(--text-primary); font-feature-settings: 'tnum'; font-size: 0.95rem;">{CURRENCY_SYMBOL}{total_val:,.2f}</b>
        </span>
    </div>
    """, unsafe_allow_html=True)

    # Manual Add Transaction Expander (Useful for interactive testing/demo)
    with st.expander("➕ Test Raw Transaction Parsing (Live AI Engine)", expanded=False):
        st.caption("Feed a raw unparsed UPI bank notification to test automated categorization and impulse classification:")
        c1, c2, c3 = st.columns([2, 1, 1])
        with c1:
            raw_input = st.text_input("Raw Bank UPI String", value="UPI-P2M-583921-STARBUCKS-COFFEE-MUMBAI")
        with c2:
            amt_input = st.number_input("Amount (₹)", min_value=1.0, value=350.0, step=50.0)
        with c3:
            date_input = st.date_input("Date", value=date.today())

        if st.button("Parse & Insert Into Ledger", type="primary"):
            new_tx = parse_single_transaction(
                raw_desc=raw_input,
                amount=amt_input,
                date=str(date_input),
                provider=ai_provider
            )
            insert_transaction(new_tx)
            st.toast(f"✅ Classified as '{new_tx.category}' ({new_tx.impulse_tag}) by {ai_provider.name}!", icon="🎯")
            st.rerun()

    # Premium Transaction List Display
    if df.empty:
        render_empty_state(
            icon="🔍",
            title="No Matching Transactions",
            message="No records match your selected filter criteria or search query. Try broadening your search or resetting filters."
        )
        return

    # Pagination Setup (15 items per page)
    page_size = 15
    total_pages = max(1, (len(df) - 1) // page_size + 1)
    
    if "tx_page" not in st.session_state or st.session_state.get("tx_page", 1) > total_pages:
        st.session_state["tx_page"] = 1

    current_page = st.session_state.get("tx_page", 1)
    start_idx = (current_page - 1) * page_size
    end_idx = min(len(df), start_idx + page_size)
    page_df = df.iloc[start_idx:end_idx]

    # Render each transaction using custom component
    for _, row in page_df.iterrows():
        t = Transaction(
            date=str(row["date"]),
            merchant=str(row["merchant"]),
            category=str(row["category"]),
            amount=float(row["amount"]),
            raw_description=str(row.get("raw_description", "")),
            impulse_score=float(row.get("impulse_score", 0.0)),
            impulse_tag=str(row.get("impulse_tag", "Planned / Regular")),
            is_essential=bool(row.get("is_essential", False)),
            confidence=float(row.get("confidence", 1.0))
        )
        render_transaction_row(t)

    # Pagination Controls
    if total_pages > 1:
        st.markdown("<div style='height: 0.5rem;'></div>", unsafe_allow_html=True)
        col_prev, col_info, col_next = st.columns([1, 2, 1])
        with col_prev:
            if current_page > 1:
                if st.button("← Previous", use_container_width=True, key="tx_prev"):
                    st.session_state["tx_page"] = current_page - 1
                    st.rerun()
        with col_info:
            st.markdown(f"""
            <div style="text-align: center; font-size: 0.82rem; color: var(--text-secondary); line-height: 2.2;">
                Page <b>{current_page}</b> of <b>{total_pages}</b> ({count} total records)
            </div>
            """, unsafe_allow_html=True)
        with col_next:
            if current_page < total_pages:
                if st.button("Next →", use_container_width=True, key="tx_next"):
                    st.session_state["tx_page"] = current_page + 1
                    st.rerun()

