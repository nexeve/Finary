"""
Finary Settings Component.
AI provider selection, API key status detection, and demo data reset controls.
Modern fintech SaaS settings architecture. Never exposes raw secrets or keys.
"""

import streamlit as st
from config import AI_PROVIDERS, get_available_api_keys, THEME
from ai.factory import get_available_providers
from database import clear_all_transactions, get_transactions_count, get_budget_config
from transaction_parser import parse_mock_transactions_file
from database import insert_transactions_bulk
from components.ui import render_page_header


def render_settings_page(current_provider_name: str):
    # 1. Page Header
    render_page_header(
        title="Settings & System Architecture",
        subtitle="Configure the AI inference layer, inspect API telemetry, and manage demo ledger data",
        badge_text="SYSTEM HEALTHY",
        badge_type="info",
        breadcrumb="Finary"
    )

    col1, col2 = st.columns([1, 1])

    # Section 1: AI Provider Engine
    with col1:
        st.markdown("""
        <div class="finary-card" style="margin-bottom: 0.75rem;">
            <div style="font-size: 1.05rem; font-weight: 700; color: var(--text-primary);">
                AI Provider Engine
            </div>
            <div style="font-size: 0.8rem; color: var(--text-secondary); margin-top: 0.2rem;">
                Select active inference engine. Auto-discovers any configured cloud key, falling back to deterministic local mock:
            </div>
        </div>
        """, unsafe_allow_html=True)

        current_choice = st.session_state.get("selected_ai_provider", "Auto")
        choice_idx = AI_PROVIDERS.index(current_choice) if current_choice in AI_PROVIDERS else 0
        
        provider_choice = st.selectbox(
            "Active Provider Mode",
            options=AI_PROVIDERS,
            index=choice_idx,
            help="Choose an AI engine. 'Auto' automatically selects any configured API key."
        )

        if provider_choice != st.session_state.get("selected_ai_provider"):
            st.session_state["selected_ai_provider"] = provider_choice
            st.toast(f"Switched AI provider mode to: {provider_choice}", icon="🔄")
            st.rerun()

        # Operational Mode Telemetry Card
        avail = get_available_providers()
        is_live = False
        if provider_choice == "Auto":
            is_live = avail["Gemini"] or avail["Groq"] or avail["OpenAI"]
        elif provider_choice in avail:
            is_live = avail[provider_choice]

        mode_title = "Cloud LLM (Production Active)" if is_live else "Deterministic Mock Engine (Offline Mode)"
        mode_pill = "Live Cloud Inference" if is_live else "Offline Heuristic Mode"
        pill_color = "var(--color-success)" if is_live else "var(--color-primary)"
        pill_bg = "var(--color-success-subtle)" if is_live else "var(--color-primary-subtle)"

        st.markdown(f"""
        <div style="background-color: var(--bg-surface); border: 1px solid var(--border-subtle); border-radius: var(--radius-md); padding: 0.9rem 1.15rem; margin-top: 0.75rem; box-shadow: {THEME['shadow_sm']};">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.4rem;">
                <span style="font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.05em; color: var(--text-muted); font-weight: 600;">Status</span>
                <span class="pill-tag" style="background: {pill_bg}; color: {pill_color};">
                    ● {mode_pill}
                </span>
            </div>
            <div style="font-size: 0.95rem; font-weight: 700; color: var(--text-primary);">
                Active Engine: {current_provider_name}
            </div>
            <div style="font-size: 0.78rem; color: var(--text-secondary); margin-top: 0.25rem;">
                {mode_title}
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Section 2: API Credentials Status
    with col2:
        st.markdown("""
        <div class="finary-card" style="margin-bottom: 0.75rem;">
            <div style="font-size: 1.05rem; font-weight: 700; color: var(--text-primary);">
                API Key Telemetry (.env)
            </div>
            <div style="font-size: 0.8rem; color: var(--text-secondary); margin-top: 0.2rem;">
                Environment credential detection. Secret tokens are never exposed:
            </div>
        </div>
        """, unsafe_allow_html=True)

        api_keys = get_available_api_keys()
        for prov in ["Gemini", "OpenAI", "Groq"]:
            configured = prov in api_keys
            status_text = "Configured" if configured else "Not Detected"
            color = "var(--color-success)" if configured else "var(--text-muted)"
            bg = "var(--color-success-subtle)" if configured else "var(--bg-surface-subtle)"
            icon = "✓" if configured else "○"
            
            st.markdown(f"""
            <div style="display: flex; justify-content: space-between; align-items: center; padding: 0.65rem 0.85rem; background-color: var(--bg-surface); border: 1px solid var(--border-subtle); border-radius: var(--radius-sm); margin-bottom: 0.5rem; box-shadow: {THEME['shadow_sm']};">
                <span style="font-size: 0.86rem; font-weight: 600; color: var(--text-primary);">{prov} API</span>
                <span style="font-size: 0.76rem; font-weight: 600; color: {color}; background: {bg}; padding: 0.15rem 0.5rem; border-radius: var(--radius-pill);">
                    {icon} {status_text}
                </span>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)

    # Section 3: Demo Statement & Ledger Management
    st.markdown("""
    <div class="finary-card" style="margin-bottom: 0.75rem;">
        <div style="font-size: 1.05rem; font-weight: 700; color: var(--text-primary);">
            Statement & Ledger Management
        </div>
        <div style="font-size: 0.8rem; color: var(--text-secondary); margin-top: 0.2rem;">
            Quickly reload realistic sample statement transactions or reset the database to a blank state:
        </div>
    </div>
    """, unsafe_allow_html=True)

    d1, d2 = st.columns(2)
    with d1:
        st.markdown(f"""
        <div style="background: var(--bg-surface); border: 1px solid var(--border-subtle); border-radius: var(--radius-md); padding: 1.1rem; box-shadow: {THEME['shadow_sm']};">
            <div style="font-size: 0.92rem; font-weight: 700; color: var(--text-primary); margin-bottom: 0.25rem;">
                Seed Demo Statement
            </div>
            <div style="font-size: 0.8rem; color: var(--text-secondary); margin-bottom: 0.85rem;">
                Loads 20 realistic Indian UPI transactions (Swiggy, Zepto, Metro, Rent, Utilities, etc.) parsed by the active engine.
            </div>
        """, unsafe_allow_html=True)
        if st.button("Re-Seed Realistic Statement Data", use_container_width=True, type="primary"):
            from ai.factory import get_ai_provider
            prov = get_ai_provider(st.session_state.get("selected_ai_provider", "Auto"))
            clear_all_transactions()
            txs = parse_mock_transactions_file(provider=prov)
            insert_transactions_bulk(txs)
            st.toast("✅ Re-seeded 20 Indian UPI transactions!", icon="🔄")
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    with d2:
        st.markdown(f"""
        <div style="background: var(--bg-surface); border: 1px solid var(--border-subtle); border-radius: var(--radius-md); padding: 1.1rem; box-shadow: {THEME['shadow_sm']};">
            <div style="font-size: 0.92rem; font-weight: 700; color: var(--text-primary); margin-bottom: 0.25rem;">
                Clear Ledger
            </div>
            <div style="font-size: 0.8rem; color: var(--text-secondary); margin-bottom: 0.85rem;">
                Wipes all ledger records to test fresh application startup and account onboarding flows.
            </div>
        """, unsafe_allow_html=True)
        if st.button("Clear All Data (Test Fresh Start)", use_container_width=True):
            clear_all_transactions()
            st.session_state["aa_consent_granted"] = False
            st.toast("🧹 Cleared all transactions. App is in fresh state.", icon="🗑️")
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    # Section 4: System Architecture Details
    st.markdown(f"""
    <div style="margin-top: 1.5rem; padding: 1rem 1.25rem; background: var(--bg-surface-subtle); border: 1px solid var(--border-subtle); border-radius: var(--radius-md); font-size: 0.8rem; color: var(--text-muted); display: flex; justify-content: space-between; flex-wrap: wrap; gap: 0.5rem;">
        <span>Architecture: <b>SQLite Deterministic Core + AI Classification</b></span>
        <span>Storage: <b>finary.db</b></span>
        <span>Version: <b>1.0.0-rc (FinTech Pass)</b></span>
    </div>
    """, unsafe_allow_html=True)

