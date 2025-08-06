"""Configuration settings for Ozon Ads Bot."""
import os
from typing import Optional
try:
    from pydantic_settings import BaseSettings
    from pydantic import Field
except ImportError:
    # Fallback for older pydantic versions
    from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    """Application settings."""
    
    # Ozon API
    ozon_client_id: str = Field(..., env="OZON_CLIENT_ID")
    ozon_api_key: str = Field(..., env="OZON_API_KEY")
    
    # Telegram Bot
    telegram_bot_token: Optional[str] = Field(None, env="TELEGRAM_BOT_TOKEN")
    telegram_chat_id: Optional[str] = Field(None, env="TELEGRAM_CHAT_ID")
    
    # External services
    mpstats_api_key: Optional[str] = Field(None, env="MPSTATS_API_KEY")
    keys_so_api_key: Optional[str] = Field(None, env="KEYS_SO_API_KEY")
    
    # Application settings
    log_level: str = Field("INFO", env="LOG_LEVEL")
    report_output_dir: str = Field("./reports", env="REPORT_OUTPUT_DIR")
    auto_optimization_enabled: bool = Field(False, env="AUTO_OPTIMIZATION_ENABLED")
    
    # Optimization thresholds
    min_ctr_threshold: float = 0.5
    max_drr_threshold: float = 15.0
    high_ctr_threshold: float = 3.0
    high_cr_threshold: float = 4.0
    max_acceptable_drr: float = 25.0
    critical_drr_threshold: float = 50.0
    min_clicks_for_analysis: int = 30
    
    # Bid adjustment settings
    bid_increase_percent: float = 20.0
    bid_decrease_percent: float = 30.0
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()