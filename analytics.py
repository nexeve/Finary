"""
Finary Analytics Engine & Plotly Visualizations.
Pure deterministic aggregation and charting.
All chart styling references central THEME tokens.
"""

import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, Any, Tuple
from config import THEME, CURRENCY_SYMBOL, IMPULSE_THRESHOLD
from models import BudgetConfig


def calculate_spending_metrics(df: pd.DataFrame, days_elapsed: int = 14) -> Dict[str, Any]:
    """
    Computes deterministic statistical summaries from the transactions DataFrame.
    """
    if df.empty:
        return {
            "total_spent": 0.0,
            "transaction_count": 0,
            "average_transaction": 0.0,
            "largest_transaction": 0.0,
            "largest_merchant": "N/A",
            "burn_rate": 0.0,
            "top_category": "N/A",
            "top_category_spent": 0.0,
            "essential_spent": 0.0,
            "discretionary_spent": 0.0,
            "impulse_spent": 0.0,
            "impulse_count": 0,
            "today_spent": 0.0,
            "today_essential": 0.0,
            "today_discretionary": 0.0,
        }

    # Filter for debits (expenses)
    debits = df[df["transaction_type"] == "debit"] if "transaction_type" in df.columns else df
    if debits.empty:
        debits = df

    total_spent = float(debits["amount"].sum())
    tx_count = len(debits)
    avg_tx = total_spent / tx_count if tx_count > 0 else 0.0

    # Largest transaction
    largest_row = debits.loc[debits["amount"].idxmax()] if not debits.empty else None
    largest_amount = float(largest_row["amount"]) if largest_row is not None else 0.0
    largest_merchant = str(largest_row["merchant"]) if largest_row is not None else "N/A"

    # Category aggregations
    cat_group = debits.groupby("category")["amount"].sum()
    top_cat = cat_group.idxmax() if not cat_group.empty else "N/A"
    top_cat_spent = float(cat_group.max()) if not cat_group.empty else 0.0

    # Essential vs Discretionary
    essential_spent = float(debits[debits["is_essential"] == True]["amount"].sum())
    discretionary_spent = total_spent - essential_spent

    # Impulse spending
    impulse_df = debits[debits["impulse_score"] >= IMPULSE_THRESHOLD]
    impulse_spent = float(impulse_df["amount"].sum())
    impulse_count = len(impulse_df)

    # Burn rate (average spend per day elapsed)
    days_elapsed = max(1, int(days_elapsed))
    burn_rate = total_spent / days_elapsed

    # Today's spend (latest transaction date in dataset)
    latest_date = debits["date"].max() if not debits.empty else ""
    today_txs = debits[debits["date"] == latest_date]
    today_spent = float(today_txs["amount"].sum())
    today_essential = float(today_txs[today_txs["is_essential"] == True]["amount"].sum())
    today_discretionary = today_spent - today_essential

    return {
        "total_spent": round(total_spent, 2),
        "transaction_count": tx_count,
        "average_transaction": round(avg_tx, 2),
        "largest_transaction": round(largest_amount, 2),
        "largest_merchant": largest_merchant,
        "burn_rate": round(burn_rate, 2),
        "top_category": top_cat,
        "top_category_spent": round(top_cat_spent, 2),
        "essential_spent": round(essential_spent, 2),
        "discretionary_spent": round(discretionary_spent, 2),
        "impulse_spent": round(impulse_spent, 2),
        "impulse_count": impulse_count,
        "today_spent": round(today_spent, 2),
        "today_essential": round(today_essential, 2),
        "today_discretionary": round(today_discretionary, 2),
        "latest_date": latest_date
    }


def create_category_donut_chart(df: pd.DataFrame, theme: dict = THEME) -> go.Figure:
    """Renders category breakdown as a modern fintech donut chart with center total."""
    if df.empty:
        fig = go.Figure()
        fig.add_annotation(text="No transactions to display", showarrow=False, font=dict(color=theme["text_muted"], size=12))
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=280)
        return fig

    cat_df = df.groupby("category", as_index=False)["amount"].sum().sort_values(by="amount", ascending=False)
    total_val = float(cat_df["amount"].sum())
    
    # Restrained fintech palette
    palette = [
        theme["color_primary"],   # Indigo
        theme["color_info"],      # Sky
        "#8B5CF6",                # Violet
        theme["color_success"],   # Emerald
        theme["color_warning"],   # Amber
        "#EC4899",                # Pink
        "#14B8A6",                # Teal
        "#64748B",                # Slate
        "#94A3B8"                 # Light Slate
    ]

    fig = px.pie(
        cat_df,
        values="amount",
        names="category",
        hole=0.68,
        color_discrete_sequence=palette
    )
    
    fig.update_traces(
        textposition="outside",
        textinfo="percent",
        hoverinfo="label+value+percent",
        hovertemplate="<b>%{label}</b><br>Amount: ₹%{value:,.2f}<br>Share: %{percent}<extra></extra>",
        marker=dict(line=dict(color=theme["bg_surface"], width=2.5))
    )
    
    # Sophisticated center label
    fig.add_annotation(
        text=f"<span style='font-size: 11px; color: {theme['text_muted']}; font-weight: 500;'>TOTAL OUTFLOW</span><br><b style='font-size: 17px; color: {theme['text_primary']};'>{CURRENCY_SYMBOL}{total_val:,.0f}</b>",
        x=0.5, y=0.5,
        showarrow=False,
        font=dict(family=theme["font_family"])
    )

    fig.update_layout(
        showlegend=False,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(t=20, b=20, l=20, r=20),
        height=280,
        font=dict(family=theme["font_family"], color=theme["text_primary"])
    )
    return fig


def create_daily_spending_bar_chart(
    df: pd.DataFrame,
    daily_limit: float = 233.0,
    theme: dict = THEME
) -> go.Figure:
    """Renders daily spend against the dynamic daily target line."""
    if df.empty:
        fig = go.Figure()
        fig.add_annotation(text="No transactions to display", showarrow=False, font=dict(color=theme["text_muted"], size=12))
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=280)
        return fig

    daily_df = df.groupby("date", as_index=False)["amount"].sum().sort_values("date")
    
    # Color bars: danger if exceeded daily limit, otherwise primary indigo
    colors = [
        theme["color_danger"] if amt > daily_limit else theme["color_primary"]
        for amt in daily_df["amount"]
    ]

    fig = go.Figure()
    
    # Spending bars
    fig.add_trace(go.Bar(
        x=daily_df["date"],
        y=daily_df["amount"],
        marker=dict(
            color=colors,
            line=dict(width=0)
        ),
        name="Daily Spend",
        hovertemplate="<b>Date: %{x}</b><br>Spent: ₹%{y:,.2f}<extra></extra>"
    ))

    # Daily target threshold line
    fig.add_trace(go.Scatter(
        x=daily_df["date"],
        y=[daily_limit] * len(daily_df),
        mode="lines",
        name=f"Daily Limit (₹{daily_limit:.0f})",
        line=dict(color=theme["color_warning"], width=2, dash="dash"),
        hoverinfo="skip"
    ))

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(t=25, b=25, l=20, r=20),
        height=280,
        xaxis=dict(
            showgrid=False,
            color=theme["text_secondary"],
            tickfont=dict(size=11, family=theme["font_family"]),
            linecolor=theme["border_subtle"]
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor=theme["border_subtle"],
            color=theme["text_secondary"],
            tickfont=dict(size=11, family=theme["font_family"]),
            tickprefix="₹",
            zeroline=False
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(size=11, family=theme["font_family"], color=theme["text_secondary"])
        ),
        font=dict(family=theme["font_family"])
    )
    return fig


def create_spending_trend_chart(
    df: pd.DataFrame,
    monthly_budget: float = 10000.0,
    savings_goal: float = 3000.0,
    days_in_month: int = 30,
    theme: dict = THEME
) -> go.Figure:
    """Cumulative spend progression vs allowed spending ceiling and ideal linear pace."""
    if df.empty:
        fig = go.Figure()
        return fig

    daily_df = df.groupby("date", as_index=False)["amount"].sum().sort_values("date")
    daily_df["cumulative"] = daily_df["amount"].cumsum()

    allowed_spending = max(0.0, monthly_budget - savings_goal)
    ideal_daily = allowed_spending / days_in_month

    dates = list(daily_df["date"])
    ideal_values = [round(ideal_daily * (i + 1), 2) for i in range(len(dates))]

    fig = go.Figure()

    # Ideal target pace
    fig.add_trace(go.Scatter(
        x=dates,
        y=ideal_values,
        mode="lines",
        name="Ideal Target Pace",
        line=dict(color=theme["color_success"], width=2, dash="dot"),
        hovertemplate="<b>Ideal Pace:</b> ₹%{y:,.2f}<extra></extra>"
    ))

    # Allowed spending ceiling
    fig.add_trace(go.Scatter(
        x=dates,
        y=[allowed_spending] * len(dates),
        mode="lines",
        name=f"Allowed Spend Cap (₹{allowed_spending:,.0f})",
        line=dict(color=theme["color_danger"], width=1.5, dash="dash"),
        hoverinfo="skip"
    ))

    # Actual cumulative spend (Dominant line)
    fig.add_trace(go.Scatter(
        x=dates,
        y=daily_df["cumulative"],
        mode="lines+markers",
        name="Actual Spending",
        line=dict(color=theme["color_primary"], width=3),
        marker=dict(size=6, color=theme["color_primary"], line=dict(color=theme["bg_surface"], width=1.5)),
        hovertemplate="<b>Date: %{x}</b><br>Total Spent: ₹%{y:,.2f}<extra></extra>"
    ))

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(t=25, b=25, l=20, r=20),
        height=320,
        xaxis=dict(
            showgrid=False,
            color=theme["text_secondary"],
            tickfont=dict(size=11, family=theme["font_family"]),
            linecolor=theme["border_subtle"]
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor=theme["border_subtle"],
            color=theme["text_secondary"],
            tickfont=dict(size=11, family=theme["font_family"]),
            tickprefix="₹",
            zeroline=False
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(size=11, family=theme["font_family"], color=theme["text_secondary"])
        ),
        font=dict(family=theme["font_family"])
    )
    return fig
