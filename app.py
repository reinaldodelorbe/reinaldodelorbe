import math
from datetime import date

import pandas as pd
import streamlit as st

st.set_page_config(page_title="Debt Elimination Planner", page_icon="💳", layout="wide")

st.title("💳 Debt Elimination Planner")
st.caption("Focused only on debt payoff while protecting essential living costs.")

st.subheader("Monthly Income")
income = st.number_input("Enter your monthly income", min_value=0.0, value=3500.0, step=50.0)

sample_expenses = [
    {"name": "Rent", "amount": 1200.0},
    {"name": "Utilities", "amount": 220.0},
    {"name": "Food", "amount": 450.0},
    {"name": "Transport", "amount": 180.0},
]

sample_debts = [
    {"name": "Credit Card A", "total": 4200.0, "min_payment": 140.0, "interest": 29.9},
    {"name": "Personal Loan", "total": 8000.0, "min_payment": 210.0, "interest": 14.5},
    {"name": "Credit Card B", "total": 1900.0, "min_payment": 75.0, "interest": 24.0},
]

left, right = st.columns(2)

with left:
    st.subheader("Fixed Expenses")
    expenses_df = st.data_editor(
        pd.DataFrame(sample_expenses),
        num_rows="dynamic",
        use_container_width=True,
        key="expenses_editor",
    )

with right:
    st.subheader("Debts")
    debts_df = st.data_editor(
        pd.DataFrame(sample_debts),
        num_rows="dynamic",
        use_container_width=True,
        key="debts_editor",
    )

method = st.selectbox("Prioritization strategy", ["Avalanche", "Snowball"], index=0)

expenses = expenses_df.fillna(0).to_dict(orient="records")
debts = debts_df.fillna(0).to_dict(orient="records")

fixed_expenses = sum(float(x.get("amount", 0) or 0) for x in expenses)
available = round(float(income) - fixed_expenses, 2)

st.subheader("Summary")
a, b, c = st.columns(3)
a.metric("Income", f"${income:,.2f}")
b.metric("Fixed Expenses", f"${fixed_expenses:,.2f}")
c.metric("Available After Expenses", f"${available:,.2f}")

ordered_debts = debts.copy()
if method == "Avalanche":
    ordered_debts = sorted(ordered_debts, key=lambda d: (float(d.get("interest", 0) or 0), float(d.get("total", 0) or 0)), reverse=True)
else:
    ordered_debts = sorted(ordered_debts, key=lambda d: float(d.get("total", 0) or 0))

payments = []

if available <= 0:
    for d in debts:
        payments.append({"debt": d.get("name", "Debt"), "payment": 0.0})
    recommendation = "Survival mode: your income does not cover essential expenses. Reduce expenses or increase income first."
    est_months = None
else:
    remaining = available
    min_total = 0.0

    for d in debts:
        minimum = min(float(d.get("min_payment", 0) or 0), float(d.get("total", 0) or 0))
        min_total += minimum
        pay = min(minimum, max(0.0, remaining))
        payments.append({"debt": d.get("name", "Debt"), "payment": round(pay, 2)})
        remaining -= pay

    by_name = {p["debt"]: p for p in payments}

    if available < min_total:
        recommendation = "Survival mode: pay as much of minimums as possible and contact lenders for hardship options."
        est_months = None
    else:
        extra = remaining
        for d in ordered_debts:
            if extra <= 0:
                break
            name = d.get("name", "Debt")
            already = float(by_name[name]["payment"])
            total = float(d.get("total", 0) or 0)
            room = max(0.0, total - already)
            add = min(extra, room)
            by_name[name]["payment"] = round(already + add, 2)
            extra -= add

        recommendation = "Aggressive mode: minimums are covered and extra cash is attacking the priority debt."

        monthly_total = sum(float(x["payment"]) for x in by_name.values())
        total_debt = sum(float(d.get("total", 0) or 0) for d in debts)
        if monthly_total <= 0 or total_debt <= 0:
            est_months = None
        else:
            weighted_apr = sum((float(d.get("total", 0) or 0) * float(d.get("interest", 0) or 0)) for d in debts) / total_debt
            monthly_interest_cost = total_debt * (weighted_apr / 100) / 12
            effective = monthly_total - monthly_interest_cost
            est_months = None if effective <= 0 else max(1, int(round(total_debt / effective)))

    payments = list(by_name.values())

plan_df = pd.DataFrame(payments).sort_values("payment", ascending=False).reset_index(drop=True)

st.subheader("Debt Payment Plan")
st.dataframe(plan_df, use_container_width=True)

if est_months is None:
    st.info("Rough payoff estimate: N/A")
else:
    target_date = date.today().replace(day=1)
    years_add, month_add = divmod(target_date.month - 1 + est_months, 12)
    payoff_year = target_date.year + years_add
    payoff_month = month_add + 1
    st.success(f"Rough payoff estimate: ~{est_months} months (around {payoff_month:02d}/{payoff_year})")

st.subheader("Strategic Recommendation")
st.write(recommendation)
