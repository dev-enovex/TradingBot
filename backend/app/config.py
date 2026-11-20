from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
import json

class Settings(BaseSettings):
    app_name: str = "ForexAI Trader"
    cors_origins: str = "http://localhost:5173"
    database_url: str = "sqlite:///./forexai.db"
    mt5_enabled: bool = False
    mt5_path: str = ""
    mt5_login: str = ""
    mt5_password: str = ""
    mt5_server: str = ""
    symbol_map: str = "{}"
    execution_enabled: bool = False
    demo_only: bool = True
    risk_per_trade: float = Field(0.0025, gt=0, le=0.01)
    max_daily_loss: float = Field(0.01, gt=0, le=0.05)
    max_open_positions: int = Field(1, ge=1, le=10)
    min_reward_risk: float = Field(2.0, ge=1)
    max_spread_points: int = 35
    magic_number: int = 6201120
    deviation_points: int = 20
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def origins(self):
        return [x.strip() for x in self.cors_origins.split(",") if x.strip()]

    @property
    def symbols(self):
        try:
            return json.loads(self.symbol_map or "{}")
        except ValueError:
            return {}

settings = Settings()
