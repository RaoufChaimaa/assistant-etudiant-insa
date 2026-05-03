"""
Classe de base pour les agents.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List
from datetime import datetime
from pydantic import BaseModel, Field

from config.settings import settings
from utils.logger import log, log_agent_action

# Import conditionnel selon le provider

from langchain_groq import ChatGroq

from langchain_core.messages import HumanMessage, SystemMessage, AIMessage


class AgentResponse(BaseModel):
    """Réponse d'un agent."""
    content: str
    agent_name: str
    tools_used: List[str] = []
    metadata: Dict[str, Any] = Field(default_factory=dict)


class BaseAgent(ABC):
    """Classe de base abstraite."""
    
    def __init__(
        self,
        name: str,
        description: str,
        system_prompt: str,
        temperature: float = None
    ):
        self.name = name
        self.description = description
        self.system_prompt = system_prompt
        
        # Initialiser le LLM selon le provider
        
        self.llm = ChatGroq(
                groq_api_key=settings.llm.groq_api_key,
                model=settings.llm.model_groq,
                temperature=temperature or settings.llm.temperature
            )
        
        self.tools: Dict[str, Any] = {}
        log.info(f"Agent '{self.name}' initialisé avec {settings.llm.provider}")
    
    def register_tool(self, name: str, tool: Any):
        """Enregistre un outil."""
        self.tools[name] = tool
    
    @abstractmethod
    async def process(self, query: str, context: Dict[str, Any] = None) -> AgentResponse:
        """Traite une requête."""
        pass
    
    async def _call_llm(
        self,
        user_message: str,
        additional_context: str = "",
        history: List[Dict[str, str]] = None
    ) -> str:
        """Appelle le LLM."""
        messages = [
            SystemMessage(content=self.system_prompt + "\n\n" + additional_context)
        ]
        
        if history:
            for turn in history[-3:]:  # Derniers 3 tours
                messages.append(HumanMessage(content=turn.get("user", "")))
                messages.append(AIMessage(content=turn.get("assistant", "")))
        
        messages.append(HumanMessage(content=user_message))
        
        log_agent_action(self.name, "Appel LLM")
        
        try:
            response = await self.llm.ainvoke(messages)
            return response.content
        except Exception as e:
            log.error(f"Erreur LLM: {e}")
            return f"Désolé, une erreur s'est produite: {str(e)}"
    
    def _create_response(
        self,
        content: str,
        tools_used: List[str] = None,
        metadata: Dict[str, Any] = None
    ) -> AgentResponse:
        """Crée une réponse."""
        return AgentResponse(
            content=content,
            agent_name=self.name,
            tools_used=tools_used or [],
            metadata=metadata or {}
        )