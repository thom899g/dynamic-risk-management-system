"""
Market Data Collector with real-time streaming and historical data fetch.
Robust error handling for exchange connectivity issues.
"""

import ccxt
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
import logging
from datetime import datetime, timedelta
import time

logger = logging.getLogger(__name__)

class MarketDataCollector:
    """Real-time market data collection with fallback mechanisms"""
    
    def __init__(self, exchange_config):
        self.exchange_config = exchange_config
        self.exchange = self._initialize_exchange()
        self.cache = {}
        self.cache_ttl = 60  # seconds
        
    def _initialize_exchange(self) -> ccxt.Exchange:
        """Initialize exchange connection with error handling"""
        try:
            exchange_class = getattr(ccxt, 'binance')
            exchange = exchange_class({
                'apiKey': self.exchange_config.api_key,
                'secret': self.exchange_config.api_secret,
                'enableRateLimit': True,
                'options': {
                    'defaultType': 'spot',
                    'adjustForTimeDifference': True
                }
            })
            
            # Test connection
            if not self.exchange_config.sandbox_mode:
                exchange.fetch_status()
                
            logger.info(f"Successfully connected to {exchange.name}")
            return exchange
            
        except ccxt.NetworkError as e:
            logger.error(f"Network error initializing exchange: {e}")
            raise
        except ccxt.ExchangeError as e:
            logger.error(f"Exchange error: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            raise
            
    def get_ohlcv_data(self, symbol: str, timeframe: str = '1h', 
                      limit: int = 100) -> pd.DataFrame:
        """Fetch OHLCV data with caching and retry logic"""
        cache_key = f"{symbol}_{timeframe}_{limit}"
        
        # Check cache
        if cache_key in self.cache:
            cached_time, data = self.cache[cache_key]
            if (datetime.now() - cached_time).seconds < self.cache_ttl:
                return data.copy()
                
        max_retries = 3
        for attempt in range