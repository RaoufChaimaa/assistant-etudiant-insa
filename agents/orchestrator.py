"""
Orchestrateur : dirige les requêtes vers les bons agents.
"""

from typing import Dict, Any, List, Optional
from enum import Enum
import asyncio

from agents.base_agent import AgentResponse
from agents.info_pratiques_agent import InfoPratiquesAgent
from agents.vie_etudiante_agent import VieEtudianteAgent
from memory.conversation_memory import ConversationMemory
from config.settings import settings
from config.constants import WEATHER_KEYWORDS, TRANSPORT_KEYWORDS, RESTAURANT_KEYWORDS, ACTIVITY_KEYWORDS
from utils.logger import log, log_agent_action
from utils.helpers import extract_location_from_text

# Import LLM selon le provider
from langchain_groq import ChatGroq

from langchain_core.messages import HumanMessage, SystemMessage


class AgentType(Enum):
    """Types d'agents."""
    INFO_PRATIQUES = "info_pratiques"
    VIE_ETUDIANTE = "vie_etudiante"
    BOTH = "both"


class Orchestrator:
    """
    Orchestrateur principal.
    - Analyse les requêtes
    - Route vers les bons agents
    - Gère la mémoire
    - Fusionne les réponses
    """
    
    def __init__(self):
        # Initialiser les agents
        self.info_agent = InfoPratiquesAgent()
        self.vie_agent = VieEtudianteAgent()
        
        # Mémoire
        self.memory = ConversationMemory()
        
        # LLM pour fusion
        
        self.merger_llm = ChatGroq(
                groq_api_key=settings.llm.groq_api_key,
                model=settings.llm.model_groq,
                temperature=0.5
            )
        
        log.info("Orchestrateur initialisé ✅")
    
    async def process(self, user_query: str) -> Dict[str, Any]:
        """
        Traite une requête utilisateur.
        
        Args:
            user_query: Question de l'utilisateur
            
        Returns:
            Dict avec réponse et métadonnées
        """
        log_agent_action("Orchestrator", "Nouvelle requête", {"query": user_query[:50]})
        
        # 1. Construire le contexte
        context = self._build_context(user_query)
        
        # 2. Décider du routing
        routing = self._route_query(user_query)
        log.info(f"Routing décidé: {routing.value}")
        
        # 3. Appeler les agents
        responses = await self._call_agents(user_query, routing, context)
        
        # 4. Fusionner si plusieurs réponses
        if len(responses) > 1:
            final_response = await self._merge_responses(user_query, responses)
        elif responses:
            final_response = responses[0].content
        else:
            final_response = "Désolé, je n'ai pas pu traiter ta demande. Peux-tu reformuler ?"
        
        # 5. Sauvegarder en mémoire
        agents_used = [r.agent_name for r in responses]
        tools_used = []
        for r in responses:
            tools_used.extend(r.tools_used)
        
        self.memory.add_turn(
            user_message=user_query,
            agent_response=final_response,
            agents_used=agents_used,
            context=context
        )
        
        return {
            "response": final_response,
            "agents_used": agents_used,
            "tools_used": list(set(tools_used)),
            "routing": routing.value
        }
    
    def _build_context(self, query: str) -> Dict[str, Any]:
        """Construit le contexte."""
        context = {
            "history": self.memory.get_recent_context(3),
            "location": self.memory.user_context.location,
            "budget_preference": self.memory.user_context.budget_preference
        }
        
        # Extraire localisation
        location = extract_location_from_text(query)
        if location:
            context["location"] = location
            self.memory.update_location(location)
        
        return context
    
    def _route_query(self, query: str) -> AgentType:
        """Détermine quel agent utiliser."""
        query_lower = query.lower()
        
        # Compter les mots-clés
        has_info = any(kw in query_lower for kw in WEATHER_KEYWORDS + TRANSPORT_KEYWORDS)
        has_vie = any(kw in query_lower for kw in RESTAURANT_KEYWORDS + ACTIVITY_KEYWORDS)
        
        # Patterns mixtes
        mixed_patterns = [
            "après" in query_lower and ("cours" in query_lower or "campus" in query_lower),
            "aller" in query_lower and "manger" in query_lower,
            "pleut" in query_lower and "faire" in query_lower,
            "temps" in query_lower and "activité" in query_lower,
        ]
        
        if any(mixed_patterns):
            return AgentType.BOTH
        
        if has_info and has_vie:
            return AgentType.BOTH
        elif has_info:
            return AgentType.INFO_PRATIQUES
        elif has_vie:
            return AgentType.VIE_ETUDIANTE
        else:
            # Par défaut: vie étudiante (plus conversationnel)
            return AgentType.VIE_ETUDIANTE
    
    async def _call_agents(
        self,
        query: str,
        routing: AgentType,
        context: Dict[str, Any]
    ) -> List[AgentResponse]:
        """Appelle les agents selon le routing."""
        responses = []
        
        if routing == AgentType.INFO_PRATIQUES:
            response = await self.info_agent.process(query, context)
            responses.append(response)
            
        elif routing == AgentType.VIE_ETUDIANTE:
            response = await self.vie_agent.process(query, context)
            responses.append(response)
            
        elif routing == AgentType.BOTH:
            # Appeler les deux en parallèle
            results = await asyncio.gather(
                self.info_agent.process(query, context),
                self.vie_agent.process(query, context)
            )
            responses.extend(results)
        
        return responses
    
    async def _merge_responses(
        self,
        query: str,
        responses: List[AgentResponse]
    ) -> str:
        """Fusionne plusieurs réponses."""
        merge_prompt = f"""Combine ces réponses en UNE seule réponse cohérente et naturelle.

Question: {query}

"""
        for r in responses:
            merge_prompt += f"--- {r.agent_name} ---\n{r.content}\n\n"
        
        merge_prompt += """
Crée une réponse unique qui:
1. Intègre toutes les infos importantes
2. Est bien structurée avec des emojis
3. Évite les répétitions
4. Est naturelle et amicale

Réponse:"""
        
        try:
            result = await self.merger_llm.ainvoke([
                HumanMessage(content=merge_prompt)
            ])
            return result.content
        except Exception as e:
            log.error(f"Erreur fusion: {e}")
            # Fallback: concaténation simple
            merged = ""
            for r in responses:
                merged += f"{r.content}\n\n"
            return merged.strip()
    
    def get_conversation_history(self) -> List[Dict[str, str]]:
        """Retourne l'historique."""
        return self.memory.get_recent_context(10)
    
    def clear_memory(self):
        """Efface la mémoire."""
        self.memory.clear()
        log.info("Mémoire effacée")
    
    def get_context_summary(self) -> str:
        """Résumé du contexte."""
        return self.memory.get_context_summary()