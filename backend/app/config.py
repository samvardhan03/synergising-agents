import os
from typing import Optional
from pydantic import BaseSettings, validator
from functools import lru_cache

class Settings(BaseSettings):
    # Application Settings
    APP_NAME: str = "NIQ Synergistic Agents"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # API Keys
    OPENAI_API_KEY: str
    OPENAI_AZURE_ENDPOINT: str
    OPENAI_AZURE_API_VERSION: str = "2024-02-15-preview"
    TIMEGPT_API_KEY: Optional[str] = None
    
    # External API Keys
    WORLD_BANK_API_KEY: Optional[str] = None
    FRED_API_KEY: Optional[str] = None
    GOOGLE_TRENDS_API_KEY: Optional[str] = None
    USDA_API_KEY: Optional[str] = None
    NEWS_API_KEY: Optional[str] = None
    
    # Flowise Configuration
    FLOWISE_BASE_URL: str = "http://localhost:3000"
    FLOWISE_NEWS_FLOW_ID: Optional[str] = None
    FLOWISE_SUMMARY_FLOW_ID: Optional[str] = None
    
    # Database Configuration
    DATABASE_URL: Optional[str] = "sqlite:///./synergistic_agents.db"
    REDIS_URL: str = "redis://localhost:6379"
    
    # File Storage
    UPLOAD_DIR: str = "./uploads"
    MAX_FILE_SIZE: int = 50 * 1024 * 1024  # 50MB
    ALLOWED_FILE_TYPES: list = ["xlsx", "xls", "csv"]
    
    # Workflow Configuration
    MAX_CONCURRENT_WORKFLOWS: int = 5
    WORKFLOW_TIMEOUT: int = 300  # 5 minutes
    
    # Agent Configuration
    FORECASTING_MODEL: str = "timegpt-1"
    SIMULATION_ITERATIONS: int = 1000
    NEWS_SOURCES: list = ["reuters", "bloomberg", "wsj", "financial-times"]
    
    # Cache Settings
    CACHE_TTL: int = 3600  # 1 hour
    ENABLE_CACHING: bool = True
    
    # Logging Configuration
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_FILE: str = "synergistic_agents.log"
    
    # CORS Settings
    CORS_ORIGINS: list = ["http://localhost:3000", "http://localhost:3001"]
    CORS_METHODS: list = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    CORS_HEADERS: list = ["*"]
    
    # WebSocket Settings
    WS_HEARTBEAT_INTERVAL: int = 30
    WS_MAX_CONNECTIONS: int = 100
    
    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW: int = 60  # 1 minute
    
    @validator("OPENAI_API_KEY")
    def validate_openai_key(cls, v):
        if not v:
            raise ValueError("OPENAI_API_KEY is required")
        return v
    
    @validator("UPLOAD_DIR")
    def create_upload_dir(cls, v):
        os.makedirs(v, exist_ok=True)
        return v
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True

@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()

# Environment-specific configurations
class DevelopmentConfig(Settings):
    DEBUG: bool = True
    LOG_LEVEL: str = "DEBUG"
    
class ProductionConfig(Settings):
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    
class TestingConfig(Settings):
    DEBUG: bool = True
    DATABASE_URL: str = "sqlite:///./test.db"
    REDIS_URL: str = "redis://localhost:6379/1"

def get_config(env: str = None) -> Settings:
    """Get configuration based on environment"""
    env = env or os.getenv("ENVIRONMENT", "development")
    
    if env == "production":
        return ProductionConfig()
    elif env == "testing":
        return TestingConfig()
    else:
        return DevelopmentConfig()

# Export commonly used settings
settings = get_settings()
