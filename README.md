<<<<<<< HEAD
# ForexAI Trader — Starter 0.1.0

Semi-automated Forex research and demo-trading starter for MetaTrader 5.

## Stack
- React + Vite dashboard
- Python + FastAPI backend
- MetaTrader5 Python package (Windows terminal integration)
- pandas/numpy indicator calculations
- SQLite journal

## Setup (Windows PowerShell)

### Backend
```powershell
cd backend
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
uvicorn app.main:app --reload
```

### Frontend (new terminal)
```powershell
cd frontend
npm install
npm run dev
```
Open the Vite URL, usually http://localhost:5173. API docs: http://127.0.0.1:8000/docs.

## MT5 connection
Install and open the MetaTrader 5 desktop terminal, log in to a demo account, then set `MT5_ENABLED=true` in `backend/.env`. Broker selection can happen later. If the broker uses suffixes, configure `SYMBOL_MAP` in `.env`.

Execution is disabled by default. For demo execution only, set `EXECUTION_ENABLED=true` after connecting a demo account. Keep `DEMO_ONLY=true`. The backend checks MT5 trade mode and blocks accounts not identified as demo. Never share credentials or commit `.env`.

## Initial strategy
H1 EMA50/EMA200 trend filter + M15 EMA50 pullback/reclaim + RSI14 confirmation; ATR14-based stop distance; default target 2R. It uses closed candles and returns NO TRADE when conditions are absent. These are unvalidated research rules, not a promise of profit.

## Default safeguards
Risk per trade 0.25%; max one open position; daily loss setting 1%; min reward/risk 2; execution disabled initially. The starter's daily loss setting is a configuration placeholder, not yet a complete broker-side daily-loss enforcement ledger. Verify volume and contract specifications in demo before use.

## Important
This is not financial advice or a proven profitable strategy. Backtest and forward-test each symbol separately. The MT5 Python integration requires a compatible Windows environment with the desktop terminal. Do not expose the local API publicly without authentication, HTTPS and network hardening.
=======
# TradingBot
>>>>>>> origin/main
