import sqlite3, json
from pathlib import Path
from app.config import settings

def conn():
    path=settings.database_url.replace("sqlite:///","")
    c=sqlite3.connect(Path(path)); c.row_factory=sqlite3.Row
    return c

def init():
    with conn() as c:
        c.execute("CREATE TABLE IF NOT EXISTS signals (id TEXT PRIMARY KEY, payload TEXT)")
        c.execute("CREATE TABLE IF NOT EXISTS trades (id INTEGER PRIMARY KEY, signal_id TEXT, symbol TEXT, direction TEXT, volume REAL, entry REAL, ticket INTEGER, status TEXT, created_at TEXT)")

def save_signal(s):
    with conn() as c: c.execute("INSERT OR REPLACE INTO signals VALUES (?,?)",(s["id"],json.dumps(s,default=str)))

def all_signals():
    with conn() as c: return [json.loads(r["payload"]) for r in c.execute("SELECT payload FROM signals").fetchall()]

def add_trade(s,ticket):
    with conn() as c:
        c.execute("INSERT INTO trades(signal_id,symbol,direction,volume,entry,ticket,status,created_at) VALUES(?,?,?,?,?,?,?,?)",
                  (s["id"],s["symbol"],s["direction"],s["volume"],s["entry"],ticket,"OPEN",s["created_at"]))

def trades():
    with conn() as c: return [dict(r) for r in c.execute("SELECT * FROM trades ORDER BY id DESC LIMIT 100").fetchall()]
