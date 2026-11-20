import pandas as pd
import numpy as np

def indicators(df):
    d = df.copy()
    d["ema50"] = d.close.ewm(span=50, adjust=False).mean()
    d["ema200"] = d.close.ewm(span=200, adjust=False).mean()
    delta = d.close.diff()
    gain = delta.clip(lower=0).ewm(alpha=1/14, adjust=False).mean()
    loss = (-delta.clip(upper=0)).ewm(alpha=1/14, adjust=False).mean()
    rs = gain / loss.replace(0, np.nan)
    d["rsi"] = 100 - 100/(1+rs)
    prev = d.close.shift(1)
    tr = pd.concat([d.high-d.low, (d.high-prev).abs(), (d.low-prev).abs()], axis=1).max(axis=1)
    d["atr"] = tr.ewm(alpha=1/14, adjust=False).mean()
    return d

def analyze(symbol, h1, m15, rr=2.0):
    empty = {"symbol":symbol,"direction":"NO_TRADE","confidence":0,
             "rationale":["Insufficient data or no qualifying setup"]}
    if h1 is None or m15 is None or len(h1)<210 or len(m15)<210:
        return empty
    h, d, prev = indicators(h1).iloc[-2], indicators(m15).iloc[-2], indicators(m15).iloc[-3]
    if pd.isna(d.atr) or d.atr <= 0: return empty
    up, down = h.ema50 > h.ema200, h.ema50 < h.ema200
    buy = up and prev.close <= prev.ema50 and d.close > d.ema50 and 50 <= d.rsi <= 68
    sell = down and prev.close >= prev.ema50 and d.close < d.ema50 and 32 <= d.rsi <= 50
    if buy:
        entry=float(d.close); sl=entry-1.5*float(d.atr)
        return {"symbol":symbol,"direction":"BUY","entry":entry,"stop_loss":sl,
                "take_profit":entry+(entry-sl)*rr,"reward_risk":rr,"confidence":70,
                "rationale":["H1 EMA50 above EMA200","M15 EMA50 pullback/reclaim","RSI confirmation","Closed candles only"]}
    if sell:
        entry=float(d.close); sl=entry+1.5*float(d.atr)
        return {"symbol":symbol,"direction":"SELL","entry":entry,"stop_loss":sl,
                "take_profit":entry-(sl-entry)*rr,"reward_risk":rr,"confidence":70,
                "rationale":["H1 EMA50 below EMA200","M15 EMA50 pullback/rejection","RSI confirmation","Closed candles only"]}
    return {"symbol":symbol,"direction":"NO_TRADE","confidence":0,
            "rationale":["No qualifying H1 trend and M15 entry confirmation"]}
