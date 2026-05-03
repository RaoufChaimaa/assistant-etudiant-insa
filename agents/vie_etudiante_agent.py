"""
Agent Vie Étudiante : restaurants, activités, sorties.
"""

from typing import Dict, Any, List

from agents.base_agent import BaseAgent, AgentResponse
from tools.weather_tool import weather_tool
from config.settings import DATA_DIR
from utils.logger import log, log_agent_action
from utils.helpers import load_json, get_current_day_info
from config.constants import RESTAURANT_KEYWORDS, ACTIVITY_KEYWORDS

# Import RAG avec gestion d'erreur
try:
    from tools.rag_tool import rag_tool
    RAG_AVAILABLE = True
except ImportError as e:
    log.warning(f"RAG non disponible: {e}")
    rag_tool = None
    RAG_AVAILABLE = False


SYSTEM_PROMPT = """Tu es un assistant spécialisé dans la vie étudiante à l'INSA Hauts-de-France et Valenciennes.

Tu aides avec :
- 🍽️ Où manger (RU, kebabs, restaurants)
- 🎯 Activités et loisirs
- 🎉 Sorties et soirées
- 💰 Bons plans économiques

Règles :
1. Privilégie les options économiques (budget étudiant !)
2. Adapte selon la météo quand pertinent
3. Sois enthousiaste et amical
4. Mentionne les événements BDE si pertinent
5. Le RU à 3.30€ c'est imbattable !

Format : emojis 🍕🍺📚, prix indiqués, conseils pratiques."""


class VieEtudianteAgent(BaseAgent):
    """Agent vie étudiante."""
    
    def __init__(self):
        super().__init__(
            name="Agent Vie Étudiante",
            description="Restaurants, activités et sorties à Valenciennes",
            system_prompt=SYSTEM_PROMPT,
            temperature=0.7
        )
        
        # Charger les données JSON
        self.lieux_data = self._load_data("lieux.json")
        self.activites_data = self._load_data("activites.json")
        self.register_tool("weather", weather_tool)
        
        # Initialiser RAG si disponible
        self.use_rag = False
        if RAG_AVAILABLE and rag_tool:
            try:
                if rag_tool.initialize():
                    self.use_rag = True
                    log_agent_action(self.name, "RAG activé ✅")
                else:
                    log_agent_action(self.name, "RAG non initialisé, mode JSON")
            except Exception as e:
                log_agent_action(self.name, f"RAG erreur: {e}, mode JSON")
    
    def _load_data(self, filename: str) -> Dict:
        """Charge les données."""
        try:
            return load_json(DATA_DIR / filename)
        except:
            return {}
    
    async def process(self, query: str, context: Dict[str, Any] = None) -> AgentResponse:
        """Traite la requête."""
        context = context or {}
        tools_used = []
        gathered_info = []
        
        query_lower = query.lower()
        
        # 1. Utiliser RAG si disponible
        if self.use_rag:
            try:
                rag_context = rag_tool.get_context_for_query(query, k=3)
                if rag_context:
                    gathered_info.append(rag_context)
                    tools_used.append("rag_search")
            except Exception as e:
                log.warning(f"RAG search failed: {e}")
        
        # 2. Météo si pertinent
        weather_info = None
        if any(kw in query_lower for kw in ["pleut", "pluie", "temps", "dehors"]):
            try:
                weather_info = await weather_tool.get_current_weather("Valenciennes")
                tools_used.append("weather_api")
            except:
                pass
        
        # 3. Données JSON (toujours utilisées comme fallback)
        if any(kw in query_lower for kw in RESTAURANT_KEYWORDS):
            info = self._get_restaurant_recommendations(query_lower, weather_info)
            gathered_info.append(info)
            tools_used.append("lieux_database")
        
        if any(kw in query_lower for kw in ACTIVITY_KEYWORDS):
            info = self._get_activity_recommendations(query_lower, weather_info)
            gathered_info.append(info)
            tools_used.append("activites_database")
        
        if any(kw in query_lower for kw in ["sortir", "soirée", "bar", "fête"]):
            info = self._get_outing_recommendations()
            gathered_info.append(info)
            tools_used.append("sorties_database")
        
        # 4. Par défaut
        if not gathered_info:
            gathered_info.append(self._get_general_recommendations(weather_info))
        
        # 5. Contexte
        additional_context = "\n\n---\n\n".join(gathered_info)
        if weather_info:
            additional_context += f"\n\n🌤️ Météo: {weather_info.temperature}°C, {weather_info.description_fr}"
        
        response = await self._call_llm(
            query,
            additional_context,
            context.get("history", [])
        )
        
        return self._create_response(response, tools_used)
    
    def _get_restaurant_recommendations(self, query: str, weather) -> str:
        """Recommandations restaurants."""
        restaurants = self.lieux_data.get("restaurants", [])
        
        if "pas cher" in query or "économique" in query:
            restaurants = [r for r in restaurants if r.get("budget") in ["très économique", "économique"]]
        
        day_info = get_current_day_info()
        day = day_info["day_name"]
        
        result = "🍽️ **Où manger à Valenciennes :**\n\n"
        
        for resto in restaurants[:4]:
            horaires = resto.get("horaires", {})
            h = horaires.get(day, horaires.get("tous_jours", "Vérifier"))
            
            result += f"""**{resto['nom']}** ({resto['type']})
💰 ~{resto['prix_moyen']}€ | 📍 {resto['localisation']}
🕐 {h} | ⭐ {resto.get('note', 'N/A')}/5

"""
        
        return result
    
    def _get_activity_recommendations(self, query: str, weather) -> str:
        """Recommandations activités."""
        activities = self.activites_data.get("par_meteo", {})
        
        if weather and weather.is_rainy:
            activity_list = activities.get("pluie", [])
            title = "🌧️ **Activités quand il pleut :**"
        else:
            activity_list = activities.get("beau_temps", [])
            title = "☀️ **Activités par beau temps :**"
        
        result = f"{title}\n\n"
        
        for act in activity_list[:4]:
            cout = "Gratuit" if act["cout"] == 0 else f"{act['cout']}€"
            result += f"• **{act['nom']}** ({act['type']}) - {cout}\n  {act['description']}\n\n"
        
        return result
    
    def _get_outing_recommendations(self) -> str:
        """Recommandations sorties."""
        sorties = self.lieux_data.get("sorties", [])
        
        result = "🎉 **Sorties à Valenciennes :**\n\n"
        
        for sortie in sorties:
            prix = sortie.get("prix_etudiant", sortie.get("prix_moyen", 0))
            prix_str = "Gratuit" if prix == 0 else f"{prix}€"
            
            result += f"""**{sortie['nom']}** ({sortie['type']})
💰 {prix_str} | 📍 {sortie['localisation']}
"""
            if sortie.get("evenements"):
                result += f"🎭 {', '.join(sortie['evenements'])}\n"
            result += "\n"
        
        return result
    
    def _get_general_recommendations(self, weather) -> str:
        """Recommandations générales."""
        day_info = get_current_day_info()
        
        daily = self.activites_data.get("par_jour", {})
        today = daily.get(day_info["day_name"], [])
        
        result = f"📅 **Suggestions pour {day_info['day_name']} :**\n\n"
        
        for act in today:
            result += f"• {act}\n"
        
        if weather:
            result += f"\n🌡️ Il fait {weather.temperature}°C ({weather.description_fr})"
        
        return result