"""Debt prioritization and allocation strategies."""

from __future__ import annotations

from typing import Dict, List


Debt = Dict[str, float | str]


def sort_debts_avalanche(debts: List[Debt]) -> List[Debt]:
    """Return debts sorted by highest interest first, then by highest total."""
    return sorted(
        debts,
        key=lambda d: (float(d.get("interest", 0.0)), float(d.get("total", 0.0))),
        reverse=True,
    )


def sort_debts_snowball(debts: List[Debt]) -> List[Debt]:
    """Return debts sorted by lowest balance first."""
    return sorted(debts, key=lambda d: float(d.get("total", 0.0)))


def choose_priority_debts(debts: List[Debt], method: str = "avalanche") -> List[Debt]:
    """Select debt ordering strategy."""
    if method.lower() == "snowball":
        return sort_debts_snowball(debts)
    return sort_debts_avalanche(debts)
