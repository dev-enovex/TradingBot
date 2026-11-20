from app.config import settings

class MT5:
    def __init__(self):
        self.api=None; self.error="MT5 disabled"; self.connected=False

    def connect(self):
        if not settings.mt5_enabled:
            self.error="Set MT5_ENABLED=true in backend/.env"; return False
        try:
            import MetaTrader5 as api
            self.api=api
            kw={}
            if settings.mt5_path: kw["path"]=settings.mt5_path
            if settings.mt5_login: kw["login"]=int(settings.mt5_login)
            if settings.mt5_password: kw["password"]=settings.mt5_password
            if settings.mt5_server: kw["server"]=settings.mt5_server
            self.connected=bool(api.initialize(**kw))
            self.error=None if self.connected else str(api.last_error())
        except Exception as e:
            self.error=str(e); self.connected=False
        return self.connected

    def ensure(self): return self.connected or self.connect()
    def name(self,s): return settings.symbols.get(s,s)
    def status(self):
        if not self.ensure(): return {"connected":False,"error":self.error}
        a=self.api.account_info()
        return {"connected":bool(a),"login":a.login if a else None,"server":a.server if a else None,
                "currency":a.currency if a else None,"balance":a.balance if a else None,
                "equity":a.equity if a else None,"trade_mode":a.trade_mode if a else None}
    def account(self):
        if not self.ensure(): return None
        a=self.api.account_info()
        return a._asdict() if a else None
    def candles(self,s,tf,count=400):
        if not self.ensure(): return None
        name=self.name(s)
        if not self.api.symbol_select(name,True): return None
        timeframe=self.api.TIMEFRAME_H1 if tf=="H1" else self.api.TIMEFRAME_M15
        rates=self.api.copy_rates_from_pos(name,timeframe,0,count)
        if rates is None: return None
        import pandas as pd
        df=pd.DataFrame(rates)
        if not df.empty: df["time"]=pd.to_datetime(df.time,unit="s",utc=True)
        return df
    def tick(self,s):
        if not self.ensure(): return None
        name=self.name(s)
        if not self.api.symbol_select(name,True): return None
        t=self.api.symbol_info_tick(name); i=self.api.symbol_info(name)
        if not t or not i: return None
        return {"bid":t.bid,"ask":t.ask,"spread_points":(t.ask-t.bid)/i.point,
                "tick_value":i.trade_tick_value,"tick_size":i.trade_tick_size,
                "volume_min":i.volume_min,"volume_max":i.volume_max,"volume_step":i.volume_step}
    def positions(self):
        if not self.ensure(): return []
        ps=self.api.positions_get()
        return [p._asdict() for p in ps] if ps else []
    def send(self,s,direction,volume,sl,tp):
        name=self.name(s); info=self.api.symbol_info(name); tick=self.api.symbol_info_tick(name)
        if not info or not tick: return {"success":False,"message":"Symbol quote unavailable"}
        typ=self.api.ORDER_TYPE_BUY if direction=="BUY" else self.api.ORDER_TYPE_SELL
        price=tick.ask if direction=="BUY" else tick.bid
        req={"action":self.api.TRADE_ACTION_DEAL,"symbol":name,"volume":float(volume),"type":typ,
             "price":price,"sl":float(sl),"tp":float(tp),"deviation":settings.deviation_points,
             "magic":settings.magic_number,"comment":"ForexAI demo approved",
             "type_time":self.api.ORDER_TIME_GTC,"type_filling":info.filling_mode}
        res=self.api.order_send(req)
        if res is None: return {"success":False,"message":str(self.api.last_error())}
        ok=res.retcode==self.api.TRADE_RETCODE_DONE
        return {"success":ok,"message":f"MT5 retcode {res.retcode}: {res.comment}",
                "ticket":getattr(res,"order",None)}
