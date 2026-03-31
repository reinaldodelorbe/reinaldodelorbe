"""CLI for personal debt-elimination engine."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List

from ai.advisor import generate_ai_recommendation
from engine.calculator import generate_plan

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"


def load_json(filename: str) -> Dict[str, Any] | List[Dict[str, Any]]:
    path = DATA_DIR / filename
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def run_plan(simulated_income: float | None, method: str) -> None:
    income_data = load_json("income.json")
    expenses = load_json("expenses.json")
    debts = load_json("debts.json")

    base_income = float(income_data["monthly_income"])
    income_type = income_data.get("type", "variable")
    income = simulated_income if simulated_income is not None else base_income

    plan = generate_plan(income=income, expenses=expenses, debts=debts, method=method)

    print("\n=== DEBT ELIMINATION ENGINE ===")
    print(f"Income used: ${income:.2f} ({income_type})")
    print(f"Strategy: {method.title()}")
    print(f"Available money after fixed expenses: ${plan.available_after_expenses:.2f}")

    print("\nPayment plan:")
    for payment in plan.payments:
        print(f"- {payment['name']}: ${float(payment['amount']):.2f}")

    est = "N/A" if plan.estimated_months is None else f"~{plan.estimated_months} months"
    print(f"\nRough time estimate to finish debts: {est}")
    print(f"Strategic recommendation: {plan.recommendation}")

    ai_context = {
        "income": income,
        "base_income": base_income,
        "income_type": income_type,
        "available_after_expenses": plan.available_after_expenses,
        "survival_mode": plan.survival_mode,
        "payments": plan.payments,
        "estimated_months": plan.estimated_months,
        "method": plan.method,
    }

    print("\nAI recommendation:")
    print(generate_ai_recommendation(ai_context))

    if simulated_income is not None and simulated_income > base_income:
        print("\nIncome increase detected: Recalculation suggests accelerated debt payoff potential.")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Personal debt-elimination CLI")
    parser.add_argument(
        "--simulate-income",
        type=float,
        default=None,
        help="Run a scenario simulation with a different monthly income.",
    )
    parser.add_argument(
        "--method",
        choices=["avalanche", "snowball"],
        default="avalanche",
        help="Debt prioritization strategy.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    run_plan(simulated_income=args.simulate_income, method=args.method)


if __name__ == "__main__":
    main()
