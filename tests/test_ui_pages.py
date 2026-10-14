"""
UI Pages AppTest verification suite.
Renders all pages using Streamlit's official AppTest runner to catch any rendering errors.
"""

from pathlib import Path
import pytest
from streamlit.testing.v1 import AppTest
from database import init_db, clear_all_transactions, insert_transactions_bulk
from transaction_parser import parse_mock_transactions_file
from ai.mock import MockProvider

APP_PATH = str(Path(__file__).resolve().parent.parent / "app.py")


@pytest.fixture(autouse=True)
def setup_test_db():
    init_db()
    clear_all_transactions()
    ai = MockProvider()
    txs = parse_mock_transactions_file(provider=ai)
    insert_transactions_bulk(txs)


def test_dashboard_renders():
    at = AppTest.from_file(APP_PATH, default_timeout=15)
    at.session_state["current_page"] = "Dashboard"
    at.run()
    assert not at.exception


def test_transactions_page_renders():
    at = AppTest.from_file(APP_PATH, default_timeout=15)
    at.session_state["current_page"] = "Transactions"
    at.run()
    assert not at.exception


def test_spending_analysis_page_renders():
    at = AppTest.from_file(APP_PATH, default_timeout=15)
    at.session_state["current_page"] = "Spending Analysis"
    at.run()
    assert not at.exception


def test_budget_planner_page_renders():
    at = AppTest.from_file(APP_PATH, default_timeout=15)
    at.session_state["current_page"] = "Budget Planner"
    at.run()
    assert not at.exception


def test_spend_coach_page_renders():
    at = AppTest.from_file(APP_PATH, default_timeout=15)
    at.session_state["current_page"] = "Spend Coach"
    at.run()
    assert not at.exception


def test_settings_page_renders():
    at = AppTest.from_file(APP_PATH, default_timeout=15)
    at.session_state["current_page"] = "Settings"
    at.run()
    assert not at.exception


def test_empty_states_render_without_error():
    clear_all_transactions()
    for page in ["Dashboard", "Transactions", "Spending Analysis", "Budget Planner", "Spend Coach", "Settings"]:
        at = AppTest.from_file(APP_PATH, default_timeout=15)
        at.session_state["current_page"] = page
        at.run()
        assert not at.exception

