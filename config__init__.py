"""
Configuration module for risk management system.
Centralizes all configurable parameters with validation.
"""

from dataclasses import dataclass
from typing import Optional
import os
from dotenv import load_dotenv

load_dotenv()

@dataclass
class ExchangeConfig:
    """Exchange API configuration"""
    api_key: str = os.getenv('BINANCE_API_KEY', '')
    api_secret: str = os.getenv('BINANCE_SECRET_KEY', '')
    sandbox_mode: bool = True
    
@dataclass
class RiskConfig:
    """Risk parameter configuration"""
    max_portfolio_risk: float = float(os.getenv('MAX_PORTFOLIO_RISK', 0.02))
    max_position_size: float = float(os.getenv('MAX_POSITION_SIZE', 0.1))
    volatility_lookback: int = int(os.getenv('VOLATILITY_LOOKBACK', 20))
    stop_loss_multiplier: float = 2.0
    take_profit_ratio: float = 1.5
    correlation_threshold: float = 0.7
    
@dataclass
class SystemConfig:
    """System operation configuration"""
    data_refresh_interval: int = 300  # seconds
    risk_recalc_interval: int = 60    # seconds
    firestore_collection: str = 'risk_parameters'
    telegram_alerts: bool = False
    
    def __post_init__(self):
        if os.getenv('TELEGRAM_BOT_TOKEN'):
            self.telegram_alerts = True