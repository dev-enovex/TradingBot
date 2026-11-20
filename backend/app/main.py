from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timezone
from uuid import uuid4
from app.config import settings
from app.schemas import AnalyzeRequest, ApprovalRequest
from app.mt5.connector import MT5
from app.analysis.strategy import analyze
from app.risk import validate, size_for_risk
from app import store

app=FastAPI(title="ForexAI Trader",version="0.1.0")
app.add_middleware(CORSMiddleware,allow_origins=settings.origins,allow_methods=["*"],allow_headers=["*"])
terminal=MT5(); session_signals={}

@app.on_event("startup")
def startup(): store.init()

@app.get("/")
def root(): return {"app":"ForexAI Trader","version":"0.1.0","demo_only":settings.demo_only,"execution_enabled":settings.execution_enabled}

@app.get("/api/status")
def status(): return {"api":"online","mt5":terminal.status(),"demo_only":settings.demo_only,"execution_enabled":settings.execution_enabled}

@app.get("/api/account")
def account():
    a=terminal.account()
    return {"connected":False,"message":terminal.error} if not a else {
        "connected":True,"login":a.get("login"),"server":a.get("server"),"currency":a.get("currency"),
        "balance":a.get("balance"),"equity":a.get("equity"),"profit":a.get("profit"),"trade_mode":a.get("trade_mode")}

@app.get("/api/market")
def market():
    out=[]
    for s in ["EURUSD","GBPUSD","XAUUSD","USDJPY","GBPJPY"]:
        q=terminal.tick(s)
        out.append({"symbol":s,**q} if q else {"symbol":s,"available":False})
    return {"items":out}

@app.post("/api/analyze")
def scan(req:AnalyzeRequest):
    out=[]
    for s in req.symbols:
        result=analyze(s,terminal.candles(s,"H1"),terminal.candles(s,"M15"),settings.min_reward_risk)
        if result["direction"] in ("BUY","SELL"):
            result.update({"id":str(uuid4()),"status":"PENDING","created_at":datetime.now(timezone.utc).isoformat(),
                           "timeframe":"H1 + M15","volume":None,"risk_amount":None})
            session_signals[result["id"]]=result; store.save_signal(result)
        out.append(result)
    return {"items":out}

@app.get("/api/signals")
def signals(): return {"items":list(session_signals.values())[-100:] or store.all_signals()}

@app.post("/api/signals/{sid}/decision")
def decision(sid:str,req:ApprovalRequest):
    s=session_signals.get(sid)
    if not s: raise HTTPException(404,"Signal not found in this session")
    if s["status"]!="PENDING": raise HTTPException(409,"Signal is no longer pending")
    if not req.approved:
        s["status"]="REJECTED"; store.save_signal(s)
        return {"success":True,"status":"REJECTED","message":"Signal rejected"}
    if not settings.execution_enabled:
        return {"success":False,"status":"PENDING","message":"Execution disabled. Review backend/.env; no order was sent."}
    if not settings.demo_only: return {"success":False,"status":"PENDING","message":"DEMO_ONLY must remain true"}
    a=terminal.account()
    if not a or int(a.get("trade_mode",-1))!=0:
        return {"success":False,"status":"PENDING","message":"Safety block: MT5 account is not confirmed as demo"}
    q=terminal.tick(s["symbol"])
    try:
        validate(s,a,terminal.positions(),q)
        volume,risk=size_for_risk(s["entry"],s["stop_loss"],a["equity"],q["tick_value"],q["tick_size"],q["volume_min"],q["volume_max"],q["volume_step"])
    except Exception as e:
        return {"success":False,"status":"PENDING","message":str(e)}
    result=terminal.send(s["symbol"],s["direction"],volume,s["stop_loss"],s["take_profit"])
    if result["success"]:
        s["status"]="EXECUTED";s["volume"]=volume;s["risk_amount"]=risk
        store.save_signal(s);store.add_trade(s,result.get("ticket"))
        return {"success":True,"status":"EXECUTED","message":result["message"],"ticket":result.get("ticket"),"volume":volume,"risk_amount":risk}
    return {"success":False,"status":"PENDING","message":result["message"]}

@app.get("/api/positions")
def positions():
    rows=terminal.positions()
    keys=["ticket","symbol","type","volume","price_open","price_current","sl","tp","profit","time"]
    return {"items":[{k:p.get(k) for k in keys} for p in rows]}

@app.get("/api/journal")
def journal(): return {"items":store.trades()}

@app.get("/api/settings")
def config():
    return {"risk_per_trade":settings.risk_per_trade,"max_daily_loss":settings.max_daily_loss,
            "max_open_positions":settings.max_open_positions,"min_reward_risk":settings.min_reward_risk,
            "max_spread_points":settings.max_spread_points,"execution_enabled":settings.execution_enabled,
            "demo_only":settings.demo_only}
