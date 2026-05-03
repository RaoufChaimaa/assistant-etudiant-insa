"""
Gestion de la mémoire conversationnelle.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from pydantic import BaseModel, Field
from collections import deque

from utils.logger import log


class UserContext(BaseModel):
    """Contexte utilisateur."""
    location: Optional[str] = None
    budget_preference: Optional[str] = None


class ConversationTurn(BaseModel):
    """Tour de conversation."""
    timestamp: datetime = Field(default_factory=datetime.now)
    user_message: str
    agent_response: str
    agents_used: List[str] = []


class ConversationMemory:
    """Gestionnaire de mémoire."""
    
    def __init__(self, max_history: int = 10):
        self.max_history = max_history
        self.history: deque = deque(maxlen=max_history)
        self.user_context = UserContext()
    
    def add_turn(
        self,
        user_message: str,
        agent_response: str,
        agents_used: List[str] = None,
        context: Dict[str, Any] = None
    ):
        """Ajoute un tour de conversation."""
        turn = ConversationTurn(
            user_message=user_message,
            agent_response=agent_response,
            agents_used=agents_used or []
        )
        self.history.append(turn)
        
        # Extraire le contexte
        if context and "location" in context:
            self.update_location(context["location"])
        
        # Détecter préférence budget
        if "pas cher" in user_message.lower() or "économique" in user_message.lower():
            self.user_context.budget_preference = "économique"
    
    def update_location(self, location: str):
        """Met à jour la localisation."""
        if location:
            self.user_context.location = location
            log.info(f"Localisation mise à jour: {location}")
    
    def get_recent_context(self, n_turns: int = 3) -> List[Dict[str, str]]:
        """Retourne les N derniers tours."""
        recent = list(self.history)[-n_turns:]
        return [
            {"user": turn.user_message, "assistant": turn.agent_response}
            for turn in recent
        ]
    
    def get_context_summary(self) -> str:
        """Résumé du contexte."""
        parts = []
        
        if self.user_context.location:
            parts.append(f"Localisation: {self.user_context.location}")
        
        if self.user_context.budget_preference:
            parts.append(f"Budget: {self.user_context.budget_preference}")
        
        if self.history:
            parts.append(f"Dernière question: {self.history[-1].user_message[:50]}...")
        
        return " | ".join(parts) if parts else "Pas de contexte"
    
    def clear(self):
        """Efface l'historique."""
        self.history.clear()
        log.info("Mémoire effacée")