"""AI recommendation layer powered by OpenAI."""

from __future__ import annotations

import os
from typing import Any, Dict


def generate_ai_recommendation(context: Dict[str, Any]) -> str:
    """Generate strategy advice from OpenAI. Gracefully degrades if unavailable."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return "AI advisor unavailable: set OPENAI_API_KEY to receive personalized recommendations."

    try:
        from openai import OpenAI

        client = OpenAI(api_key=api_key)
        prompt = (
            "You are a strict debt-elimination coach. Keep output under 120 words. "
            "Given this plan context, provide 3 actionable recommendations prioritizing debt payoff speed "
            "while protecting essential expenses. Context:\n"
            f"{context}"
        )

        response = client.responses.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4.1-mini"),
            input=prompt,
            temperature=0.2,
        )
        return (response.output_text or "AI advisor returned no text.").strip()
    except Exception as exc:  # pragma: no cover - network/service failures
        return f"AI advisor error: {exc}"
