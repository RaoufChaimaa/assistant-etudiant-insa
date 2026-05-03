"""
Agent Info-Pratiques : météo, transports, horaires.
"""

from typing import Dict, Any, List

from agents.base_agent import BaseAgent, AgentResponse
from tools.weather_tool import weather_tool
from tools.transport_tool import transport_tool
from utils.logger import log_agent_action
from utils.helpers import get_current_day_info, extract_location_from_text
from config.constants import WEATHER_KEYWORDS, TRANSPORT_KEYWORDS


SYSTEM_PROMPT = """Tu es un assistant spécialisé pour les étudiants de l'INSA Hauts-de-France à Valenciennes.

Tu aides avec :
- 🌤️ La météo à Valenciennes
- 🚊 Les transports (Transvilles, tramway T1, bus)
- 🕐 Les horaires des services (BU, RU, secrétariat)
- 📍 Les informations pratiques sur le campus

Règles :
1. Sois concis et précis
2. Utilise des emojis
3. Donne des infos pratiques pour Valenciennes
4. Mentionne le tramway T1 qui dessert le campus
5. N'oublie pas que le temps est souvent... nordique 🌧️

Format : utilise des titres en gras (**) et des listes."""


class InfoPratiquesAgent(BaseAgent):
    """Agent infos pratiques."""
    
    def __init__(self):
        super().__init__(
            name="Agent Info-Pratiques",
            description="Météo, transports et horaires à Valenciennes",
            system_prompt=SYSTEM_PROMPT,
            temperature=0.3
        )
        
        self.register_tool("weather", weather_tool)
        self.register_tool("transport", transport_tool)
    
    async def process(self, query: str, context: Dict[str, Any] = None) -> AgentResponse:
        """Traite la requête."""
        context = context or {}
        tools_used = []
        gathered_info = []
        
        query_lower = query.lower()
        location = context.get("location") or extract_location_from_text(query)
        
        # Météo
        if any(kw in query_lower for kw in WEATHER_KEYWORDS):
            weather = await weather_tool.get_current_weather("Valenciennes")
            gathered_info.append(weather_tool.format_weather_response(weather))
            tools_used.append("weather_api")
        
        # Transport
        if any(kw in query_lower for kw in TRANSPORT_KEYWORDS):
            destination = self._extract_destination(query_lower)
            depart = location or "gare"
            route = transport_tool.get_route(depart, destination or "insa")
            gathered_info.append(transport_tool.format_route_response(route))
            tools_used.append("transport_api")
        
        # Horaires
        if any(kw in query_lower for kw in ["horaire", "ouvert", "fermé", "heure"]):
            gathered_info.append(self._get_schedule_info())
            tools_used.append("schedule_data")
        
        # Réponse par défaut
        if not gathered_info:
            day_info = get_current_day_info()
            gathered_info.append(f"📍 Nous sommes {day_info['formatted']}.\n\nJe peux t'aider avec la météo, les transports ou les horaires !")
        
        # Construire contexte
        additional_context = "\n\n---\n\n".join(gathered_info)
        
        # Appeler LLM
        response = await self._call_llm(
            query,
            additional_context,
            context.get("history", [])
        )
        
        return self._create_response(response, tools_used, {"location": location})
    
    def _extract_destination(self, query: str) -> str:
        """Extrait la destination."""
        if "insa" in query or "campus" in query or "université" in query:
            return "insa"
        if "gare" in query:
            return "gare"
        if "centre" in query:
            return "centre-ville"
        return "insa"
    
    def _get_schedule_info(self) -> str:
        """Info horaires."""
        day_info = get_current_day_info()
        
        return f"""📅 **Horaires du {day_info['day_name']}**

• **BU Mont Houy** : 08:00-20:00 (sam: 09:00-12:00)
• **RU Mont Houy** : 11:30-13:30 (fermé weekend)
• **Cafétéria INSA** : 08:00-17:00 (ven: -16:00)
• **Secrétariat** : 09:00-12:00, 14:00-17:00
• **SUAPS (sport)** : 08:00-20:00"""