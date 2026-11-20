from app.config import settings

def size_for_risk(entry, sl, equity, tick_value, tick_size, vmin, vmax, step):
    if not tick_value or not tick_size or tick_size<=0 or step<=0:
        raise ValueError("Broker tick metadata unavailable")
    loss_per_lot=abs(entry-sl)/tick_size*tick_value
    if loss_per_lot<=0: raise ValueError("Invalid stop distance")
    cash=equity*settings.risk_per_trade
    raw=cash/loss_per_lot
    volume=round((raw//step)*step,8)
    if volume<vmin: raise ValueError("Calculated volume below broker minimum; trade rejected")
    return min(volume,vmax),cash

def validate(s,account,positions,tick):
    if not account: raise ValueError("MT5 account unavailable")
    if len(positions)>=settings.max_open_positions: raise ValueError("Max open positions reached")
    if not tick: raise ValueError("No quote/contract information")
    if tick["spread_points"]>settings.max_spread_points: raise ValueError("Spread exceeds configured limit")
    e,sl,tp=s["entry"],s["stop_loss"],s["take_profit"]
    if s["direction"]=="BUY" and not sl<e<tp: raise ValueError("Invalid BUY SL/TP")
    if s["direction"]=="SELL" and not tp<e<sl: raise ValueError("Invalid SELL SL/TP")
    if abs(tp-e)/abs(e-sl)<settings.min_reward_risk: raise ValueError("Reward/risk below minimum")
