from pydantic import BaseModel, Field
from typing import Literal, Optional
from datetime import datetime

class AnalyzeRequest(BaseModel):
    symbols: list[str] = Field(default_factory=lambda: ["EURUSD","GBPUSD","XAUUSD","USDJPY","GBPJPY"])

class ApprovalRequest(BaseModel):
    approved: bool

class Signal(BaseModel):
    id: str
    symbol: str
    direction: Literal["BUY","SELL","NO_TRADE"]
    status: str = "PENDING"
    entry: Optional[float] = None
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    volume: Optional[float] = None
    risk_amount: Optional[float] = None
    reward_risk: Optional[float] = None
    confidence: int = 0
    rationale: list[str] = Field(default_factory=list)
    created_at: datetime
    timeframe: str = "H1 + M15"
