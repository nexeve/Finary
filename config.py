"""
Finary Configuration & Design System Tokens.
Central source of truth for app settings, API key discovery, and theme tokens.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load local environment variables
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

DB_PATH = str(BASE_DIR / "finary.db")
MOCK_DATA_PATH = str(DATA_DIR / "mock_transactions.csv")

# Currency & Locale
CURRENCY_SYMBOL = "₹"

# Default Budget Configuration
DEFAULT_BUDGET = {
    "monthly_budget": 10000.0,
    "savings_goal": 3000.0,
    "daily_necessary_expense": 150.0,
    "days_in_month": 30
}

# Transaction Categories & Defaults
CATEGORIES = [
    "Food",
    "Transport",
    "Shopping",
    "Bills",
    "Entertainment",
    "Subscriptions",
    "Groceries",
    "Healthcare",
    "Education",
    "Rent",
    "Other"
]

IMPULSE_THRESHOLD = 0.60
IMPULSE_TAG_POTENTIAL = "Potential Impulse"
IMPULSE_TAG_REGULAR = "Planned / Regular"

# Budget Status Labels
STATUS_ON_TRACK = "ON TRACK"
STATUS_SLIGHTLY_OVER = "SLIGHTLY OVER"
STATUS_AT_RISK = "AT RISK"
STATUS_CRITICAL = "CRITICAL"

# Available AI Providers
AI_PROVIDERS = ["Auto", "Gemini", "OpenAI", "Groq", "Mock"]


def get_available_api_keys() -> dict[str, str]:
    """Inspects environment and returns non-empty API keys without exposing secrets."""
    keys = {}
    if os.getenv("GEMINI_API_KEY"):
        keys["Gemini"] = "Configured"
    if os.getenv("OPENAI_API_KEY"):
        keys["OpenAI"] = "Configured"
    if os.getenv("GROQ_API_KEY"):
        keys["Groq"] = "Configured"
    return keys


# =====================================================================
# REUSABLE THEME SYSTEM - LIGHT / NEUTRAL PREMIUM FINTECH PALETTE
# All colors, typography, borders, and visual tokens are defined centrally.
# Global design system for Finary.
# =====================================================================
THEME = {
    "font_family": "Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
    
    # Canvas & Surface Tokens
    "bg_canvas": "#F8FAFC",          # Soft light slate canvas
    "bg_surface": "#FFFFFF",         # Pure white surface
    "bg_surface_subtle": "#F1F5F9",  # Soft slate for chips and metric cards
    "bg_surface_elevated": "#FFFFFF",
    "bg_surface_hover": "#F8FAFC",
    
    # Legacy aliases for backward compatibility
    "bg_main": "#F8FAFC",
    "bg_card": "#FFFFFF",
    "bg_card_secondary": "#F8FAFC",
    "bg_hover": "#F1F5F9",
    
    # Border Tokens
    "border_subtle": "#E2E8F0",
    "border_default": "#CBD5E1",
    "border_active": "#94A3B8",
    "border_focus": "#4F46E5",
    
    # Typography Colors (Authoritative Dark Charcoal)
    "text_primary": "#0F172A",       # Slate 900
    "text_secondary": "#475569",     # Slate 600
    "text_muted": "#94A3B8",         # Slate 400
    
    # Semantic Accent Colors
    "color_primary": "#4F46E5",        # Deep Indigo
    "color_primary_subtle": "#EEF2FF", # Soft Indigo tint
    "color_primary_light": "#EEF2FF",
    "color_success": "#059669",        # Emerald
    "color_success_subtle": "#ECFDF5",
    "color_warning": "#D97706",        # Amber
    "color_warning_subtle": "#FFFBEB",
    "color_danger": "#DC2626",         # Rose/Red
    "color_danger_subtle": "#FEF2F2",
    "color_info": "#0284C7",           # Sky
    "color_info_subtle": "#F0F9FF",
    
    # Layout Tokens
    "radius_xs": "4px",
    "radius_sm": "6px",
    "radius_md": "10px",
    "radius_lg": "14px",
    "radius_pill": "9999px",
    
    # Shadow Tokens (Crisp, Restrained Fintech Elevation)
    "shadow_sm": "0 1px 2px 0 rgba(15, 23, 42, 0.04)",
    "shadow_card": "0 1px 3px 0 rgba(15, 23, 42, 0.05), 0 1px 2px -1px rgba(15, 23, 42, 0.05)",
    "shadow_elevated": "0 4px 6px -1px rgba(15, 23, 42, 0.05), 0 2px 4px -2px rgba(15, 23, 42, 0.04)",
}


def get_app_css(theme: dict = THEME) -> str:
    """Generates globally injectable CSS based on the active theme dictionary."""
    return f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    :root {{
        --font-family: {theme['font_family']};
        --bg-canvas: {theme['bg_canvas']};
        --bg-surface: {theme['bg_surface']};
        --bg-surface-subtle: {theme['bg_surface_subtle']};
        --bg-surface-hover: {theme['bg_surface_hover']};
        --bg-main: {theme['bg_main']};
        --bg-card: {theme['bg_card']};
        --bg-card-sec: {theme['bg_card_secondary']};
        --bg-hover: {theme['bg_hover']};
        --border-subtle: {theme['border_subtle']};
        --border-default: {theme['border_default']};
        --border-active: {theme['border_active']};
        --border-focus: {theme['border_focus']};
        --text-primary: {theme['text_primary']};
        --text-secondary: {theme['text_secondary']};
        --text-muted: {theme['text_muted']};
        --color-primary: {theme['color_primary']};
        --color-primary-subtle: {theme['color_primary_subtle']};
        --color-success: {theme['color_success']};
        --color-success-subtle: {theme['color_success_subtle']};
        --color-warning: {theme['color_warning']};
        --color-warning-subtle: {theme['color_warning_subtle']};
        --color-danger: {theme['color_danger']};
        --color-danger-subtle: {theme['color_danger_subtle']};
        --color-info: {theme['color_info']};
        --color-info-subtle: {theme['color_info_subtle']};
        --radius-sm: {theme['radius_sm']};
        --radius-md: {theme['radius_md']};
        --radius-lg: {theme['radius_lg']};
        --radius-pill: {theme['radius_pill']};
    }}

    /* Global styling overrides */
    html, body, [class*="st-"] {{
        font-family: var(--font-family);
        font-feature-settings: 'cv02', 'cv03', 'cv04', 'cv11', 'tnum';
    }}

    .stApp {{
        background-color: var(--bg-canvas);
        color: var(--text-primary);
    }}

    /* Container Spacing & Clean Padding */
    .block-container {{
        padding-top: 2rem !important;
        padding-bottom: 3.5rem !important;
        max-width: 1200px !important;
    }}

    /* Hide default Streamlit deploy button & footer for clean SaaS presentation */
    #MainMenu, footer {{visibility: hidden;}}
    header[data-testid="stHeader"] {{display: none !important;}}
    .stDeployButton {{display: none;}}

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {{
        background-color: var(--bg-surface) !important;
        border-right: 1px solid var(--border-subtle) !important;
        box-shadow: none !important;
    }}
    section[data-testid="stSidebar"] > div:first-child {{
        padding-top: 1.5rem !important;
        padding-left: 1.25rem !important;
        padding-right: 1.25rem !important;
    }}

    /* Transform Streamlit Sidebar Radio to Sleek Nav Pills */
    div[data-testid="stSidebar"] div[role="radiogroup"] {{
        display: flex;
        flex-direction: column;
        gap: 0.35rem;
    }}
    div[data-testid="stSidebar"] div[role="radiogroup"] > label {{
        background-color: transparent !important;
        border-radius: var(--radius-md) !important;
        padding: 0.55rem 0.85rem !important;
        margin: 0 !important;
        cursor: pointer !important;
        transition: all 0.15s ease-in-out !important;
        border: 1px solid transparent !important;
        display: flex !important;
        align-items: center !important;
    }}
    div[data-testid="stSidebar"] div[role="radiogroup"] > label:hover {{
        background-color: var(--bg-surface-subtle) !important;
        border-color: var(--border-subtle) !important;
    }}
    /* Hide circular radio input */
    div[data-testid="stSidebar"] div[role="radiogroup"] > label > div:first-child {{
        display: none !important;
    }}
    /* Nav label text */
    div[data-testid="stSidebar"] div[role="radiogroup"] > label > div[data-testid="stMarkdownContainer"] p {{
        font-size: 0.88rem !important;
        font-weight: 500 !important;
        color: #334155 !important;
        margin: 0 !important;
        letter-spacing: -0.01em !important;
    }}
    /* Active Nav Item */
    div[data-testid="stSidebar"] div[role="radiogroup"] > label[data-checked="true"],
    div[data-testid="stSidebar"] div[role="radiogroup"] > label[aria-checked="true"] {{
        background-color: #EEF2FF !important;
        border: 1px solid rgba(79, 70, 229, 0.2) !important;
    }}
    div[data-testid="stSidebar"] div[role="radiogroup"] > label[data-checked="true"] > div[data-testid="stMarkdownContainer"] p,
    div[data-testid="stSidebar"] div[role="radiogroup"] > label[aria-checked="true"] > div[data-testid="stMarkdownContainer"] p {{
        color: #4F46E5 !important;
        font-weight: 700 !important;
    }}

    /* Button Styling */
    .stButton > button {{
        font-family: var(--font-family) !important;
        font-size: 0.86rem !important;
        font-weight: 600 !important;
        border-radius: var(--radius-sm) !important;
        padding: 0.5rem 1rem !important;
        transition: all 0.15s ease !important;
        border: 1px solid var(--border-subtle) !important;
        background-color: var(--bg-surface) !important;
        color: var(--text-primary) !important;
        box-shadow: {theme['shadow_sm']} !important;
    }}
    .stButton > button:hover {{
        background-color: var(--bg-surface-subtle) !important;
        border-color: var(--border-default) !important;
        color: var(--text-primary) !important;
    }}
    .stButton > button[kind="primary"] {{
        background-color: var(--color-primary) !important;
        color: #FFFFFF !important;
        border: 1px solid var(--color-primary) !important;
    }}
    .stButton > button[kind="primary"]:hover {{
        background-color: #4338CA !important;
        border-color: #4338CA !important;
        color: #FFFFFF !important;
        box-shadow: 0 2px 4px rgba(79, 70, 229, 0.25) !important;
    }}

    /* Form Controls & Inputs */
    div[data-baseweb="input"], div[data-baseweb="select"] {{
        border-radius: var(--radius-sm) !important;
        border-color: var(--border-subtle) !important;
        background-color: var(--bg-surface) !important;
    }}
    div[data-baseweb="input"] input {{
        color: var(--text-primary) !important;
        font-family: var(--font-family) !important;
        font-size: 0.88rem !important;
    }}
    div[data-baseweb="input"]:focus-within, div[data-baseweb="select"]:focus-within {{
        border-color: var(--color-primary) !important;
        box-shadow: 0 0 0 2px rgba(79, 70, 229, 0.15) !important;
    }}

    /* Finary custom reusable card containers */
    .finary-card {{
        background-color: var(--bg-surface);
        border: 1px solid var(--border-subtle);
        border-radius: var(--radius-lg);
        padding: 1.25rem 1.5rem;
        margin-bottom: 1rem;
        box-shadow: {theme['shadow_card']};
        transition: border-color 0.15s ease, box-shadow 0.15s ease;
    }}
    .finary-card:hover {{
        border-color: var(--border-default);
    }}

    .finary-card-hero {{
        background: linear-gradient(180deg, #FFFFFF 0%, #FAFAFF 100%);
        border: 1px solid rgba(79, 70, 229, 0.18);
        border-radius: var(--radius-lg);
        padding: 1.5rem 1.75rem;
        margin-bottom: 1.25rem;
        box-shadow: {theme['shadow_elevated']};
    }}

    /* Metric blocks */
    .metric-container {{
        background-color: var(--bg-surface);
        border: 1px solid var(--border-subtle);
        border-radius: var(--radius-md);
        padding: 1.1rem 1.25rem;
        box-shadow: {theme['shadow_sm']};
        transition: transform 0.15s ease, border-color 0.15s ease;
    }}
    .metric-container:hover {{
        border-color: var(--border-default);
    }}
    .metric-label {{
        font-size: 0.72rem;
        text-transform: uppercase;
        letter-spacing: 0.07em;
        color: var(--text-secondary);
        font-weight: 600;
        margin-bottom: 0.35rem;
    }}
    .metric-value {{
        font-size: 1.85rem;
        font-weight: 800;
        color: var(--text-primary);
        line-height: 1.15;
        letter-spacing: -0.02em;
        font-feature-settings: 'tnum';
    }}
    .metric-subtitle {{
        font-size: 0.8rem;
        color: var(--text-muted);
        margin-top: 0.35rem;
        font-weight: 400;
    }}

    /* Status badge pill */
    .status-badge {{
        display: inline-flex;
        align-items: center;
        gap: 0.35rem;
        padding: 0.25rem 0.75rem;
        border-radius: var(--radius-pill);
        font-size: 0.75rem;
        font-weight: 700;
        letter-spacing: 0.05em;
        text-transform: uppercase;
    }}
    .status-on-track {{
        background-color: var(--color-success-subtle);
        color: var(--color-success);
        border: 1px solid rgba(5, 150, 105, 0.25);
    }}
    .status-slightly-over {{
        background-color: var(--color-warning-subtle);
        color: var(--color-warning);
        border: 1px solid rgba(217, 119, 6, 0.25);
    }}
    .status-at-risk {{
        background-color: var(--color-danger-subtle);
        color: var(--color-danger);
        border: 1px solid rgba(220, 38, 38, 0.25);
    }}
    .status-critical {{
        background-color: var(--color-danger-subtle);
        color: #991B1B;
        border: 1px solid rgba(220, 38, 38, 0.4);
        font-weight: 800;
    }}

    /* Dynamic daily budget hero banner */
    .budget-hero {{
        background: linear-gradient(180deg, #FFFFFF 0%, #FAFAFF 100%);
        border: 1px solid rgba(79, 70, 229, 0.2);
        border-radius: var(--radius-lg);
        padding: 1.5rem 1.75rem;
        margin-bottom: 1.25rem;
        box-shadow: {theme['shadow_elevated']};
    }}

    /* Pill tags */
    .pill-tag {{
        display: inline-flex;
        align-items: center;
        font-size: 0.72rem;
        padding: 0.2rem 0.6rem;
        border-radius: var(--radius-pill);
        font-weight: 600;
        letter-spacing: 0.02em;
    }}
    .pill-impulse {{
        background-color: var(--color-warning-subtle);
        color: var(--color-warning);
        border: 1px solid rgba(217, 119, 6, 0.25);
    }}
    .pill-essential {{
        background-color: var(--color-info-subtle);
        color: var(--color-info);
        border: 1px solid rgba(2, 132, 199, 0.25);
    }}
    .pill-discretionary {{
        background-color: var(--color-primary-subtle);
        color: var(--color-primary);
        border: 1px solid rgba(79, 70, 229, 0.25);
    }}

    /* Custom Transaction Ledger Row */
    .tx-item {{
        display: flex;
        align-items: center;
        justify-content: space-between;
        background-color: var(--bg-surface);
        border: 1px solid var(--border-subtle);
        border-radius: var(--radius-md);
        padding: 0.85rem 1.15rem;
        margin-bottom: 0.5rem;
        transition: all 0.15s ease;
    }}
    .tx-item:hover {{
        border-color: var(--border-default);
        box-shadow: {theme['shadow_sm']};
        background-color: var(--bg-surface-hover);
    }}
    .tx-avatar {{
        width: 36px;
        height: 36px;
        border-radius: var(--radius-sm);
        background-color: var(--bg-surface-subtle);
        border: 1px solid var(--border-subtle);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1rem;
        font-weight: 700;
        color: var(--text-secondary);
        flex-shrink: 0;
    }}
    .tx-amount {{
        font-size: 1rem;
        font-weight: 700;
        letter-spacing: -0.01em;
        font-feature-settings: 'tnum';
        color: var(--text-primary);
        text-align: right;
    }}

    /* Clean custom scrollbar */
    ::-webkit-scrollbar {{
        width: 6px;
        height: 6px;
    }}
    ::-webkit-scrollbar-track {{
        background: var(--bg-canvas);
    }}
    ::-webkit-scrollbar-thumb {{
        background: var(--border-default);
        border-radius: 9999px;
    }}
    ::-webkit-scrollbar-thumb:hover {{
        background: var(--border-active);
    }}

    /* Expander card polish */
    div[data-testid="stExpander"] {{
        background-color: var(--bg-surface) !important;
        border: 1px solid var(--border-subtle) !important;
        border-radius: var(--radius-md) !important;
        box-shadow: {theme['shadow_sm']} !important;
        overflow: hidden !important;
    }}
    div[data-testid="stExpander"] details summary {{
        color: var(--text-primary) !important;
        font-weight: 600 !important;
        font-size: 0.88rem !important;
        padding: 0.65rem 1rem !important;
    }}
    div[data-testid="stExpander"] details summary:hover {{
        background-color: var(--bg-surface-subtle) !important;
    }}
    </style>
    """
