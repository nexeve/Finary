"""
Simulated RBI Account Aggregator (AA) Flow.
Provides a realistic, trustworthy consent demonstration without real credentials.
Light neutral fintech styling.
"""

import time
import streamlit as st
from config import CURRENCY_SYMBOL, THEME
from database import insert_transactions_bulk, clear_all_transactions
from transaction_parser import parse_mock_transactions_file


def render_aa_consent_flow(ai_provider):
    st.markdown(f"""
    <div class="finary-card-hero">
        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 0.75rem; flex-wrap: wrap; gap: 0.5rem;">
            <div style="font-size: 1.35rem; font-weight: 800; color: var(--text-primary); letter-spacing: -0.02em;">
                🏦 Connect Your Bank Account
            </div>
            <div class="pill-tag" style="background: var(--color-primary-subtle); color: var(--color-primary);">
                ● SIMULATED RBI ACCOUNT AGGREGATOR
            </div>
        </div>
        <div style="color: var(--text-secondary); font-size: 0.92rem; line-height: 1.5; margin-bottom: 1rem;">
            Experience effortless personal finance. Automatically sync and classify transaction statements with zero manual logging, no SMS scraping, and zero credential sharing.
        </div>
        <div style="background-color: var(--bg-surface); border: 1px dashed var(--border-default); border-radius: var(--radius-sm); padding: 0.65rem 0.95rem; font-size: 0.8rem; color: var(--text-muted);">
            ℹ️ <b>Framework Notice:</b> This is an RBI-compliant Account Aggregator framework simulation for hackathon demonstration. No live credentials or real bank accounts are accessed.
        </div>
    </div>
    """, unsafe_allow_html=True)

    if "aa_consent_granted" not in st.session_state:
        st.session_state["aa_consent_granted"] = False

    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown("""
        <div class="finary-card" style="margin-bottom: 0.75rem;">
            <div style="font-weight: 700; font-size: 0.95rem; margin-bottom: 0.25rem; color: var(--text-primary);">
                Step 1: Select Financial Provider (FIP)
            </div>
            <div style="font-size: 0.82rem; color: var(--text-secondary);">
                Select your simulated primary savings / salary account:
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        bank_choice = st.selectbox(
            "Select Bank",
            ["HDFC Bank (UPI / Salary)", "State Bank of India (SBI)", "ICICI Bank", "Axis Bank"],
            index=0,
            label_visibility="collapsed"
        )

        consent_button = st.button(
            "✓ Approve Consent Token" if not st.session_state["aa_consent_granted"] else "Consent Granted",
            type="primary" if not st.session_state["aa_consent_granted"] else "secondary",
            use_container_width=True,
            disabled=st.session_state["aa_consent_granted"]
        )
        if consent_button:
            with st.spinner("Generating encrypted consent artefact via RBI AA protocol..."):
                time.sleep(0.5)
            st.session_state["aa_consent_granted"] = True
            st.session_state["selected_bank"] = bank_choice
            st.toast("✅ Consent token generated successfully!", icon="🔐")
            st.rerun()

    with col2:
        status_text = "✅ Consent Active" if st.session_state["aa_consent_granted"] else "⏳ Awaiting Approval"
        status_color = "var(--color-success)" if st.session_state["aa_consent_granted"] else "var(--text-muted)"
        st.markdown(f"""
        <div class="finary-card" style="margin-bottom: 0.75rem;">
            <div style="font-weight: 700; font-size: 0.95rem; margin-bottom: 0.25rem; color: var(--text-primary);">
                Step 2: Ingest & Parse Statements
            </div>
            <div style="font-size: 0.82rem; color: var(--text-secondary);">
                Status: <b style="color: {status_color};">{status_text}</b>
            </div>
        </div>
        """, unsafe_allow_html=True)

        fetch_button = st.button(
            "Fetch & Categorize Transactions ➔",
            type="primary" if st.session_state["aa_consent_granted"] else "secondary",
            use_container_width=True,
            disabled=not st.session_state["aa_consent_granted"]
        )

        if fetch_button:
            with st.status("Ingesting and analyzing transactions...", expanded=True) as status:
                st.write("Connecting to Financial Information Provider...")
                time.sleep(0.3)
                st.write("Fetching raw UPI statement records...")
                time.sleep(0.3)
                st.write(f"Classifying merchants & impulse signals using {ai_provider.name}...")
                
                # Parse mock transactions and save to database
                parsed_txs = parse_mock_transactions_file(provider=ai_provider)
                clear_all_transactions()
                inserted_count = insert_transactions_bulk(parsed_txs)
                
                status.update(label=f"Successfully ingested {inserted_count} transactions!", state="complete", expanded=False)

            st.toast(f"🎉 Ingested & parsed {inserted_count} transactions!", icon="📊")
            st.session_state["current_page"] = "Dashboard"
            st.rerun()

