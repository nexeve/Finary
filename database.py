"""
Finary SQLite Database Layer.
Handles schema initialization, persistence, retrieval, and demo resets.
"""

import sqlite3
import pandas as pd
from typing import Optional, List, Dict, Any
from config import DB_PATH, DEFAULT_BUDGET
from models import Transaction, BudgetConfig


def get_connection(db_path: str = DB_PATH) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path: str = DB_PATH):
    """Creates tables if they do not exist."""
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        
        # Transactions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                raw_description TEXT NOT NULL,
                merchant TEXT NOT NULL,
                amount REAL NOT NULL,
                category TEXT NOT NULL,
                sub_category TEXT NOT NULL,
                transaction_type TEXT NOT NULL DEFAULT 'debit',
                impulse_score REAL NOT NULL DEFAULT 0.0,
                impulse_tag TEXT NOT NULL DEFAULT 'Planned / Regular',
                is_essential INTEGER NOT NULL DEFAULT 0,
                ai_provider TEXT NOT NULL DEFAULT 'Mock',
                ai_model TEXT NOT NULL DEFAULT 'demo',
                confidence REAL NOT NULL DEFAULT 1.0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Budget configuration table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS budget_config (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                monthly_budget REAL NOT NULL,
                savings_goal REAL NOT NULL,
                daily_necessary_expense REAL NOT NULL,
                days_in_month INTEGER NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Insert default budget if empty
        cursor.execute("SELECT COUNT(*) FROM budget_config WHERE id = 1")
        if cursor.fetchone()[0] == 0:
            cursor.execute("""
                INSERT INTO budget_config (id, monthly_budget, savings_goal, daily_necessary_expense, days_in_month)
                VALUES (1, ?, ?, ?, ?)
            """, (
                DEFAULT_BUDGET["monthly_budget"],
                DEFAULT_BUDGET["savings_goal"],
                DEFAULT_BUDGET["daily_necessary_expense"],
                DEFAULT_BUDGET["days_in_month"]
            ))

        conn.commit()


def get_budget_config(db_path: str = DB_PATH) -> BudgetConfig:
    init_db(db_path)
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT monthly_budget, savings_goal, daily_necessary_expense, days_in_month FROM budget_config WHERE id = 1")
        row = cursor.fetchone()
        if row:
            return BudgetConfig(
                monthly_budget=float(row["monthly_budget"]),
                savings_goal=float(row["savings_goal"]),
                daily_necessary_expense=float(row["daily_necessary_expense"]),
                days_in_month=int(row["days_in_month"])
            )
        return BudgetConfig(**DEFAULT_BUDGET)


def update_budget_config(config: BudgetConfig, db_path: str = DB_PATH):
    init_db(db_path)
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO budget_config (id, monthly_budget, savings_goal, daily_necessary_expense, days_in_month, updated_at)
            VALUES (1, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(id) DO UPDATE SET
                monthly_budget = excluded.monthly_budget,
                savings_goal = excluded.savings_goal,
                daily_necessary_expense = excluded.daily_necessary_expense,
                days_in_month = excluded.days_in_month,
                updated_at = CURRENT_TIMESTAMP
        """, (config.monthly_budget, config.savings_goal, config.daily_necessary_expense, config.days_in_month))
        conn.commit()


def insert_transaction(t: Transaction, db_path: str = DB_PATH) -> int:
    init_db(db_path)
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO transactions (
                date, raw_description, merchant, amount, category, sub_category,
                transaction_type, impulse_score, impulse_tag, is_essential,
                ai_provider, ai_model, confidence
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            t.date, t.raw_description, t.merchant, t.amount, t.category, t.sub_category,
            t.transaction_type, t.impulse_score, t.impulse_tag, 1 if t.is_essential else 0,
            t.ai_provider, t.ai_model, t.confidence
        ))
        conn.commit()
        return cursor.lastrowid


def insert_transactions_bulk(transactions: List[Transaction], db_path: str = DB_PATH) -> int:
    init_db(db_path)
    records = [
        (
            t.date, t.raw_description, t.merchant, t.amount, t.category, t.sub_category,
            t.transaction_type, t.impulse_score, t.impulse_tag, 1 if t.is_essential else 0,
            t.ai_provider, t.ai_model, t.confidence
        )
        for t in transactions
    ]
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.executemany("""
            INSERT INTO transactions (
                date, raw_description, merchant, amount, category, sub_category,
                transaction_type, impulse_score, impulse_tag, is_essential,
                ai_provider, ai_model, confidence
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, records)
        conn.commit()
        return len(records)


def get_all_transactions(
    category: Optional[str] = None,
    impulse_only: bool = False,
    essential_only: Optional[bool] = None,
    search_query: Optional[str] = None,
    db_path: str = DB_PATH
) -> pd.DataFrame:
    init_db(db_path)
    query = "SELECT * FROM transactions WHERE 1=1"
    params: List[Any] = []

    if category and category != "All":
        query += " AND category = ?"
        params.append(category)

    if impulse_only:
        query += " AND impulse_score >= 0.6"

    if essential_only is not None:
        query += " AND is_essential = ?"
        params.append(1 if essential_only else 0)

    if search_query:
        query += " AND (merchant LIKE ? OR raw_description LIKE ?)"
        wildcard = f"%{search_query}%"
        params.extend([wildcard, wildcard])

    query += " ORDER BY date DESC, id DESC"

    with get_connection(db_path) as conn:
        df = pd.read_sql_query(query, conn, params=params)
        if not df.empty:
            df["is_essential"] = df["is_essential"].astype(bool)
        return df


def clear_all_transactions(db_path: str = DB_PATH):
    init_db(db_path)
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM transactions")
        conn.commit()


def get_transactions_count(db_path: str = DB_PATH) -> int:
    init_db(db_path)
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM transactions")
        return cursor.fetchone()[0]
