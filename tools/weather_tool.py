"""
Outil météo - Valenciennes
"""

import httpx
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field

from config.settings import settings
from config.constants import WEATHER_DESCRIPTIONS
from utils.logger import log


class WeatherData(BaseModel):
    """Données météo."""
    temperature: float
    feels_like: float
    humidity: int
    description: str
    description_fr: str
    wind_speed: float
    city: str
    is_rainy: bool = False
    is_sunny: bool = False
    recommendation: str = ""


class WeatherTool:
    """Outil pour la météo."""
    
    def __init__(self):
        self.api_key = settings.weather.api_key
        self.base_url = settings.weather.base_url
    
    async def get_current_weather(self, city: str = None) -> WeatherData:
        """Récupère la météo actuelle."""
        city = city or settings.app.default_city
        
        # Si pas de clé API, données simulées
        if not self.api_key:
            log.warning("Pas de clé API météo, données simulées")
            return self._get_simulated_weather(city)
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/weather",
                    params={
                        "q": f"{city},FR",
                        "appid": self.api_key,
                        "units": "metric",
                        "lang": "fr"
                    },
                    timeout=10.0
                )
                response.raise_for_status()
                data = response.json()
                return self._parse_weather_data(data)
                
        except Exception as e:
            log.error(f"Erreur API météo: {e}")
            return self._get_simulated_weather(city)
    
    def _parse_weather_data(self, data: dict) -> WeatherData:
        """Parse les données de l'API."""
        main_weather = data["weather"][0]["main"].lower()
        
        is_rainy = main_weather in ["rain", "drizzle", "thunderstorm"]
        is_sunny = main_weather == "clear"
        
        if is_rainy:
            recommendation = "☔ Prends un parapluie ! Le Nord reste fidèle à lui-même."
        elif data["main"]["temp"] < 10:
            recommendation = "🧥 Il fait frais, couvre-toi bien !"
        elif data["main"]["temp"] > 25:
            recommendation = "☀️ Profite du soleil, c'est rare dans le Nord !"
        else:
            recommendation = "👍 Temps correct pour Valenciennes !"
        
        return WeatherData(
            temperature=round(data["main"]["temp"], 1),
            feels_like=round(data["main"]["feels_like"], 1),
            humidity=data["main"]["humidity"],
            description=data["weather"][0]["description"],
            description_fr=WEATHER_DESCRIPTIONS.get(main_weather, data["weather"][0]["description"]),
            wind_speed=round(data["wind"]["speed"] * 3.6, 1),  # m/s to km/h
            city=data["name"],
            is_rainy=is_rainy,
            is_sunny=is_sunny,
            recommendation=recommendation
        )
    
    def _get_simulated_weather(self, city: str) -> WeatherData:
        """Données simulées pour tests."""
        import random
        
        conditions = [
            {"desc": "nuageux", "temp": 15, "rainy": False, "sunny": False},
            {"desc": "pluvieux", "temp": 12, "rainy": True, "sunny": False},
            {"desc": "partiellement nuageux", "temp": 17, "rainy": False, "sunny": True},
        ]
        
        cond = random.choice(conditions)
        
        return WeatherData(
            temperature=cond["temp"],
            feels_like=cond["temp"] - 2,
            humidity=random.randint(60, 85),
            description=cond["desc"],
            description_fr=cond["desc"],
            wind_speed=random.uniform(10, 25),
            city=city,
            is_rainy=cond["rainy"],
            is_sunny=cond["sunny"],
            recommendation="☔ Parapluie conseillé dans le Nord !" if cond["rainy"] else "👍 Temps acceptable !"
        )
    
    def format_weather_response(self, weather: WeatherData) -> str:
        """Formate la réponse météo."""
        return f"""🌤️ **Météo à {weather.city}**

🌡️ Température : {weather.temperature}°C (ressenti {weather.feels_like}°C)
🌧️ Conditions : {weather.description_fr}
💧 Humidité : {weather.humidity}%
💨 Vent : {weather.wind_speed} km/h

{weather.recommendation}"""


weather_tool = WeatherTool()