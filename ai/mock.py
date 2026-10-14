"""
Deterministic Mock AI Provider for Finary.
Provides zero-latency, realistic, intelligent responses grounded strictly in calculated numbers.
"""

import re
from typing import Dict, Any, List
from ai.base import AIProvider
from config import IMPULSE_THRESHOLD, IMPULSE_TAG_POTENTIAL, IMPULSE_TAG_REGULAR


class MockProvider(AIProvider):
    name: str = "Mock AI (Demo)"
    model_name: str = "deterministic-v1"

    MERCHANT_RULES = [
        (r"SWIGGY", "Swiggy", "Food", "Food Delivery", False, 0.76),
        (r"ZOMATO", "Zomato", "Food", "Food Delivery", False, 0.82),
        (r"ZEPTO", "Zepto", "Groceries", "Quick Commerce", False, 0.78),
        (r"BLINKIT", "Blinkit", "Groceries", "Quick Commerce", True, 0.35),
        (r"BIGBASKET", "BigBasket", "Groceries", "Supermarket", True, 0.15),
        (r"DMART", "DMart", "Groceries", "Supermarket", True, 0.10),
        (r"AMAZON", "Amazon", "Shopping", "E-Commerce", False, 0.72),
        (r"FLIPKART", "Flipkart", "Shopping", "E-Commerce", False, 0.68),
        (r"UBER", "Uber", "Transport", "Ride Hailing", False, 0.40),
        (r"OLA", "Ola", "Transport", "Ride Hailing", False, 0.35),
        (r"METRO", "Delhi Metro", "Transport", "Public Transit", True, 0.05),
        (r"SPOTIFY", "Spotify", "Subscriptions", "Audio Streaming", False, 0.25),
        (r"NETFLIX", "Netflix", "Subscriptions", "Video Streaming", False, 0.30),
        (r"BOOKMYSHOW", "BookMyShow", "Entertainment", "Movies & Events", False, 0.70),
        (r"CANTEEN", "College Canteen", "Food", "Campus Dining", True, 0.15),
        (r"CAFE|CHAAYOS|STARBUCKS", "Chaayos Café", "Food", "Coffee & Tea", False, 0.65),
        (r"APOLLO|PHARMACY|MEDICINE", "Apollo Pharmacy", "Healthcare", "Medication", True, 0.05),
        (r"ELECTRICITY|BESCOM|TNEB|POWER", "Electricity Bill", "Bills", "Utilities", True, 0.02),
        (r"RECHARGE|JIO|AIRTEL|VI", "Mobile Recharge", "Bills", "Telecom", True, 0.05),
        (r"RENT|LANDLORD|HOUSE", "House Rent", "Rent", "Housing", True, 0.00),
    ]

    def parse_transaction(self, raw_text: str, amount: float = 0.0) -> Dict[str, Any]:
        upper_desc = raw_text.upper()
        
        for pattern, merchant, category, sub_cat, is_essential, impulse_score in self.MERCHANT_RULES:
            if re.search(pattern, upper_desc):
                # Small contextual nudge: food orders over ₹500 get higher impulse weight
                if category == "Food" and amount > 500:
                    impulse_score = min(0.95, impulse_score + 0.10)
                tag = IMPULSE_TAG_POTENTIAL if impulse_score >= IMPULSE_THRESHOLD else IMPULSE_TAG_REGULAR
                return {
                    "merchant": merchant,
                    "category": category,
                    "sub_category": sub_cat,
                    "transaction_type": "debit",
                    "impulse_score": round(impulse_score, 2),
                    "impulse_tag": tag,
                    "is_essential": is_essential,
                    "confidence": 0.96
                }

        # Fallback for unrecognized raw strings
        return {
            "merchant": raw_text.split("-")[-2].title() if "-" in raw_text else "UPI Merchant",
            "category": "Other",
            "sub_category": "General",
            "transaction_type": "debit",
            "impulse_score": 0.40,
            "impulse_tag": IMPULSE_TAG_REGULAR,
            "is_essential": False,
            "confidence": 0.75
        }

    def generate_spending_insight(self, metrics: Dict[str, Any], recent_transactions: List[Dict[str, Any]]) -> str:
        total_spent = metrics.get("total_spent", 0.0)
        top_cat = metrics.get("top_category", "Food")
        top_cat_spent = metrics.get("top_category_spent", 0.0)
        impulse_spent = metrics.get("impulse_spent", 0.0)
        burn_rate = metrics.get("burn_rate", 0.0)

        insights = []
        if top_cat == "Food" and top_cat_spent > 0:
            insights.append(
                f"**Food delivery & cafés** are currently leading your outflows at ₹{top_cat_spent:,.0f}. "
                "Late-night orders on Zepto & Swiggy make up a big slice of this."
            )
        else:
            insights.append(
                f"Your highest expenditure category this cycle is **{top_cat}** at ₹{top_cat_spent:,.0f}."
            )

        if impulse_spent > 0:
            pct = (impulse_spent / total_spent * 100) if total_spent > 0 else 0
            insights.append(
                f"Potential impulse transactions account for **₹{impulse_spent:,.0f} ({pct:.0f}%)** of your spending. "
                "Cutting just two takeout deliveries this week recovers ₹600+ of discretionary room."
            )

        if burn_rate > 0:
            insights.append(
                f"Your daily burn rate is hovering around **₹{burn_rate:.0f}/day**."
            )

        return "\n\n".join(insights)

    def generate_budget_coaching(self, ctx: Dict[str, Any]) -> str:
        status = ctx.get("status", "ON TRACK")
        today_variance = ctx.get("today_variance", 0.0)
        current_allowance = ctx.get("current_daily_allowance", 0.0)
        current_disc = ctx.get("current_discretionary_allowance", 0.0)
        days_rem = ctx.get("days_remaining", 0)
        savings_goal = ctx.get("savings_goal", 0.0)
        is_impossible = ctx.get("is_goal_impossible", False)

        if is_impossible:
            revised = ctx.get("revised_achievable_savings", 0.0)
            reduction = ctx.get("minimum_reduction_needed", 0.0)
            return (
                f"⚠️ **Reality Check:** At your current pace, the original ₹{savings_goal:,.0f} savings goal "
                f"is mathematically unreachable. With essential needs locked at ₹{ctx.get('daily_necessary_expense', 0):.0f}/day, "
                f"your realistic achievable savings is **₹{revised:,.0f}** unless you can trim **₹{reduction:,.0f}** from baseline expenses."
            )

        if today_variance > 0:
            return (
                f"You went **₹{today_variance:,.0f}** over today's target. "
                "No panic. We didn't cut tomorrow to zero—I've distributed that overspend across your remaining **"
                f"{days_rem} days** instead of making tomorrow miserable.\n\n"
                f"To still hit your **₹{savings_goal:,.0f}** savings goal, keep discretionary spending around "
                f"**₹{max(0.0, current_disc):,.0f}/day** (Total ₹{current_allowance:,.0f}/day) for the next {days_rem} days."
            )

        if today_variance < 0:
            saved_today = abs(today_variance)
            return (
                f"✨ Solid discipline! You came in **₹{saved_today:,.0f} below** today's cap. "
                f"That gives you a breathing room allowance of **₹{current_allowance:,.0f}/day** "
                f"(₹{max(0.0, current_disc):,.0f}/day discretionary) across your remaining {days_rem} days "
                f"while keeping your ₹{savings_goal:,.0f} savings goal completely locked in."
            )

        return (
            f"You're tracking right in the pocket! Pacing at **₹{current_allowance:,.0f}/day** for the remaining "
            f"{days_rem} days will hit your ₹{savings_goal:,.0f} target smoothly."
        )
