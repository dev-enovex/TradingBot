import pandas as pd
from app.analysis.strategy import indicators, analyze

def candles(n=250):
    close=[1+i*0.0001 for i in range(n)]
    return pd.DataFrame({"open":close,"high":[x+.001 for x in close],"low":[x-.001 for x in close],"close":close})

def test_indicators():
    assert {"ema50","ema200","rsi","atr"}.issubset(indicators(candles()).columns)

def test_short_history_is_no_trade():
    assert analyze("EURUSD",candles(40),candles(40))["direction"]=="NO_TRADE"
