# Debt Elimination CLI

Python CLI focused only on getting out of debt with unstable income.

## Features
- Tracks income (`data/income.json`)
- Tracks fixed survival expenses (`data/expenses.json`)
- Tracks debts (`data/debts.json`)
- Subtracts fixed expenses first
- Prevents negative survival balance
- Uses **Avalanche** strategy by default (optional Snowball)
- Covers minimum payments first, then routes extra money aggressively
- Detects low-income survival mode
- Supports scenario simulation (`--simulate-income`)
- Includes OpenAI-based recommendation layer (deterministic engine remains source of truth)

## Project structure

```text
.
├── ai/
│   └── advisor.py
├── data/
│   ├── debts.json
│   ├── expenses.json
│   └── income.json
├── engine/
│   ├── calculator.py
│   └── strategy.py
└── main.py
```

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install openai
```

Optional for AI recommendations:

```bash
export OPENAI_API_KEY="your_key_here"
export OPENAI_MODEL="gpt-4.1-mini"
```

## Run

```bash
python main.py
```

Scenario simulation:

```bash
python main.py --simulate-income 4200
```

Alternative prioritization:

```bash
python main.py --method snowball
```
