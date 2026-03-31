"""Deterministic debt payoff engine."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

from engine.strategy import choose_priority_debts


@dataclass
class PlanResult:
    available_after_expenses: float
    survival_mode: bool
    payments: List[Dict[str, float | str]]
    estimated_months: int | None
    recommendation: str
    method: str


def _sum_expenses(expenses: List[Dict[str, float | str]]) -> float:
    return sum(float(item.get("amount", 0.0)) for item in expenses)


def _sum_min_payments(debts: List[Dict[str, float | str]]) -> float:
    return sum(float(item.get("min_payment", 0.0)) for item in debts)


def _allocate_minimums(
    debts: List[Dict[str, float | str]],
    available: float,
) -> tuple[List[Dict[str, float | str]], float]:
    payments = []
    for debt in debts:
        minimum = min(float(debt["min_payment"]), float(debt["total"]))
        pay = min(minimum, max(0.0, available))
        payments.append({"name": debt["name"], "amount": round(pay, 2)})
        available -= pay
    return payments, available


def _aggressive_allocation(
    ordered_debts: List[Dict[str, float | str]],
    payments: List[Dict[str, float | str]],
    extra: float,
) -> List[Dict[str, float | str]]:
    name_to_payment = {p["name"]: p for p in payments}
    for debt in ordered_debts:
        if extra <= 0:
            break
        already = float(name_to_payment[debt["name"]]["amount"])
        remaining = max(0.0, float(debt["total"]) - already)
        if remaining <= 0:
            continue
        add = min(extra, remaining)
        name_to_payment[debt["name"]]["amount"] = round(already + add, 2)
        extra -= add
    return list(name_to_payment.values())


def _estimate_months(
    debts: List[Dict[str, float | str]],
    payment_total: float,
) -> int | None:
    if payment_total <= 0:
        return None
    total_debt = sum(float(d["total"]) for d in debts)
    weighted_interest = (
        sum(float(d["total"]) * (float(d["interest"]) / 100) for d in debts) / total_debt
        if total_debt > 0
        else 0.0
    )
    monthly_interest = weighted_interest / 12
    effective_payment = payment_total - (total_debt * monthly_interest / 100)
    if effective_payment <= 0:
        return None
    return max(1, int(round(total_debt / effective_payment)))


def generate_plan(
    income: float,
    expenses: List[Dict[str, float | str]],
    debts: List[Dict[str, float | str]],
    method: str = "avalanche",
) -> PlanResult:
    fixed_expenses = _sum_expenses(expenses)
    available_after_expenses = round(income - fixed_expenses, 2)

    if available_after_expenses <= 0:
        return PlanResult(
            available_after_expenses=available_after_expenses,
            survival_mode=True,
            payments=[{"name": d["name"], "amount": 0.0} for d in debts],
            estimated_months=None,
            recommendation="Survival mode: income does not cover essentials. Reduce expenses or increase income immediately.",
            method=method,
        )

    ordered = choose_priority_debts(debts, method=method)
    minimum_total = _sum_min_payments(debts)

    if available_after_expenses < minimum_total:
        payments, _ = _allocate_minimums(debts, available_after_expenses)
        return PlanResult(
            available_after_expenses=available_after_expenses,
            survival_mode=True,
            payments=payments,
            estimated_months=None,
            recommendation="Survival mode: pay as much of minimums as possible and contact lenders to renegotiate terms.",
            method=method,
        )

    payments, extra = _allocate_minimums(debts, available_after_expenses)
    payments = _aggressive_allocation(ordered, payments, extra)

    monthly_total = sum(float(p["amount"]) for p in payments)
    estimate = _estimate_months(debts, monthly_total)

    recommendation = (
        "Aggressive mode: minimums covered, extra cash routed to highest-priority debt."
        if extra > 0
        else "Minimums covered. Increase income or lower expenses to accelerate payoff."
    )

    return PlanResult(
        available_after_expenses=available_after_expenses,
        survival_mode=False,
        payments=sorted(payments, key=lambda p: p["amount"], reverse=True),
        estimated_months=estimate,
        recommendation=recommendation,
        method=method,
    )
