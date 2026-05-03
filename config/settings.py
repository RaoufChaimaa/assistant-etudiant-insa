"""
Configuration centrale - INSA Hauts-de-France Valenciennes
"""

import os
from pathlib import Path
from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()

# Chemins
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
LOGS_DIR = BASE_DIR / "logs"

DATA_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)


class LLMConfig(BaseModel):
    """Configuration LLM."""
    provider: str = Field(default_factory=lambda: os.getenv("LLM_PROVIDER", "gemini"))
    google_api_key: str = Field(default_factory=lambda: os.getenv("GOOGLE_API_KEY", ""))
    groq_api_key: str = Field(default_factory=lambda: os.getenv("GROQ_API_KEY", ""))
    model_gemini: str = "gemini-1.5-flash"
    model_groq: str = "llama-3.3-70b-versatile"
    temperature: float = 0.7
    max_tokens: int = 2000


class WeatherConfig(BaseModel):
    """Configuration Météo."""
    api_key: str = Field(default_factory=lambda: os.getenv("OPENWEATHER_API_KEY", ""))
    base_url: str = "https://api.openweathermap.org/data/2.5"
    units: str = "metric"
    lang: str = "fr"


class AppConfig(BaseModel):
    """Configuration App - Valenciennes & INSA."""
    debug: bool = Field(default_factory=lambda: os.getenv("DEBUG_MODE", "true").lower() == "true")
    log_level: str = Field(default_factory=lambda: os.getenv("LOG_LEVEL", "INFO"))
    default_city: str = Field(default_factory=lambda: os.getenv("DEFAULT_CITY", "Valenciennes"))
    default_campus: str = Field(default_factory=lambda: os.getenv("DEFAULT_CAMPUS", "INSA Hauts-de-France"))
    
    # Coordonnées Valenciennes
    city_lat: float = 50.3518
    city_lon: float = 3.5235
    
    # Coordonnées INSA HdF
    campus_lat: float = 50.3287
    campus_lon: float = 3.5117


class Settings(BaseModel):
    """Paramètres globaux."""
    llm: LLMConfig = Field(default_factory=LLMConfig)
    weather: WeatherConfig = Field(default_factory=WeatherConfig)
    app: AppConfig = Field(default_factory=AppConfig)


settings = Settings()

def get_settings() -> Settings:
    return settings