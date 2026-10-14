# ✦ Finary — Zero-Effort AI Personal Finance Co-Pilot

> **"Connect once. Understand automatically. Spend smarter."**

Finary is an AI-powered personal finance assistant specifically designed for students and young earners in India. It eliminates manual expense tracking through a simulated RBI Account Aggregator (AA) consent flow, classifies raw UPI statements into structured data, deterministically calculates dynamic daily spending allowances, and provides empathetic, guilt-free AI coaching.

---

## ⚡ 3-Minute Hackathon Demo Script

1. **Simulated Bank Connection**:
   - Open the app. The landing view shows the **Connect your bank account** card.
   - Select your bank (e.g., HDFC) and click **[ Give Consent ]** (simulating the RBI AA consent artefact).
   - Click **[ Fetch Transactions ]** to ingest and parse 20 realistic Indian UPI transactions (Swiggy, Blinkit, Zepto, Metro, Netflix, Rent, etc.).
2. **Dashboard Overview**:
   - Notice the **Adaptive Daily Limit** hero card showing **₹180/day** (vs. baseline ₹233/day), split into **Essentials (₹150/day)** and **Discretionary (₹30/day)**.
   - The 6 key FinTech questions are answered immediately via metrics and interactive Plotly charts.
3. **Dynamic Budget Architecture**:
   - Navigate to **Budget Planner**. Inspect the parameters (Monthly Budget: ₹10,000 | Savings Goal: ₹3,000 | Daily Necessities: ₹150).
   - See how **Allowed Spend (₹7,000)** translates into **Total Daily Allowance (₹233/day)** and **Discretionary Allowance (₹83/day)**.
   - Use the **What-If Scenario Simulator** to see how an extra ₹400 spend today smoothly distributes across remaining days.
4. **Live Overspending & Recovery**:
   - In the sidebar, expand **"Simulate Overspend"** and click **Trigger ₹400 Overspend**.
   - Watch the Dashboard instantly recalculate: the daily limit compresses to protect the ₹3,000 savings goal.
   - Read the **AI Spend Coach** card: it explains exactly what happened without financial shame or generic clichés.
5. **Multi-Model AI Selector**:
   - Navigate to **Settings**. View auto-detected API keys and switch between Auto, Gemini, OpenAI, Groq, or Mock AI.

---

## 🏗️ Architecture & Core Components

```
Finary/
├── app.py                      # Main Streamlit app entrypoint
├── config.py                   # Centralized configuration, API discovery & THEME tokens
├── database.py                 # SQLite persistence & CRUD operations
├── models.py                   # Data classes (Transaction, BudgetConfig, BudgetState)
├── analytics.py                # Pure deterministic financial analytics & Plotly charts
├── budget_engine.py            # Mathematical dynamic budget & recovery engine
├── transaction_parser.py       # Raw transaction processing & heuristic fallback
├── ai/
│   ├── base.py                 # Abstract AIProvider interface
│   ├── gemini.py               # Google Gemini provider
│   ├── openai.py               # OpenAI provider
│   ├── groq.py                 # Groq provider
│   ├── mock.py                 # High-fidelity deterministic Mock provider
│   └── factory.py              # Provider discovery & factory
├── components/
│   ├── sidebar.py              # Navigation & live demo simulation trigger
│   ├── dashboard.py            # 6-question dashboard & dynamic daily budget banner
│   ├── transactions.py         # Searchable, filterable transaction table
│   ├── spending_analysis.py    # Deep-dive analytics, burn rates & trend charts
│   ├── budget_planner.py       # Budget inputs, daily allowance preview & sandbox
│   ├── spend_coach.py          # AI coaching, dynamic limit explanations & chat
│   ├── aa_consent.py           # Simulated RBI Account Aggregator flow
│   └── settings.py             # Model selection, demo data reset, budget config
├── data/
│   └── mock_transactions.csv   # Realistic Indian UPI transactions
├── tests/
│   └── test_budget_engine.py   # Complete mathematical test suite
├── .env.example                # Optional API key template
└── requirements.txt            # Python dependencies
```

---

## 🧮 Budget Mathematics (Single Source of Truth)

All financial mathematics are strictly computed by Python (`budget_engine.py`). The AI **never** computes or invents financial figures.

- **Allowed Monthly Spending**:
  $$\text{Allowed Spending} = \max(0, \text{Monthly Budget} - \text{Savings Goal})$$
- **Base Daily Allowance**:
  $$\text{Base Daily} = \frac{\text{Allowed Spending}}{\text{Days in Month}}$$
- **Base Discretionary Allowance**:
  $$\text{Discretionary} = \text{Base Daily} - \text{Daily Necessary Expense}$$
- **Dynamic Daily Recovery Allowance**:
  When actual spending deviates from the daily target, the variance is distributed across the remaining days:
  $$\text{New Daily Allowance} = \frac{\text{Remaining Allowed Spending}}{\text{Remaining Days}}$$
  $$\text{New Discretionary Allowance} = \text{New Daily Allowance} - \text{Daily Necessary Expense}$$

---

## 🚀 Running the Application

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run Tests
```bash
python -m pytest tests/test_budget_engine.py
```

### 3. Launch App
```bash
streamlit run app.py
```
