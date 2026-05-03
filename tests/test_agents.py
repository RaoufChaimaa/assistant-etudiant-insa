"""
Tests automatisés pour les agents.
"""

import pytest
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.orchestrator import Orchestrator, AgentType
from agents.info_pratiques_agent import InfoPratiquesAgent
from agents.vie_etudiante_agent import VieEtudianteAgent
from tools.weather_tool import weather_tool
from tools.transport_tool import transport_tool


class TestRouting:
    """Tests du routing de l'orchestrator."""
    
    def setup_method(self):
        self.orchestrator = Orchestrator()
    
    def test_weather_routing(self):
        """Questions météo → Agent Info-Pratiques."""
        questions = [
            "Quel temps fait-il ?",
            "Il pleut ?",
            "La météo aujourd'hui ?",
            "Il fait combien ?",
        ]
        
        for q in questions:
            routing = self.orchestrator._route_query(q)
            assert routing in [AgentType.INFO_PRATIQUES, AgentType.BOTH], \
                f"'{q}' devrait router vers INFO_PRATIQUES, got {routing}"
    
    def test_transport_routing(self):
        """Questions transport → Agent Info-Pratiques."""
        questions = [
            "Comment aller à l'INSA ?",
            "Quel bus pour le campus ?",
            "Horaires du tramway ?",
        ]
        
        for q in questions:
            routing = self.orchestrator._route_query(q)
            assert routing in [AgentType.INFO_PRATIQUES, AgentType.BOTH], \
                f"'{q}' devrait router vers INFO_PRATIQUES, got {routing}"
    
    def test_restaurant_routing(self):
        """Questions resto → Agent Vie Étudiante."""
        questions = [
            "Où manger ?",
            "Un bon restaurant ?",
            "Où déjeuner pas cher ?",
        ]
        
        for q in questions:
            routing = self.orchestrator._route_query(q)
            assert routing in [AgentType.VIE_ETUDIANTE, AgentType.BOTH], \
                f"'{q}' devrait router vers VIE_ETUDIANTE, got {routing}"
    
    def test_mixed_routing(self):
        """Questions mixtes → Les deux agents."""
        questions = [
            "Il pleut, que faire ?",
            "Je vais au campus, où manger après ?",
        ]
        
        for q in questions:
            routing = self.orchestrator._route_query(q)
            assert routing == AgentType.BOTH, \
                f"'{q}' devrait router vers BOTH, got {routing}"


class TestWeatherTool:
    """Tests de l'outil météo."""
    
    @pytest.mark.asyncio
    async def test_get_weather(self):
        """Test récupération météo."""
        weather = await weather_tool.get_current_weather("Valenciennes")
        
        assert weather is not None
        assert weather.city is not None
        assert -50 < weather.temperature < 50  # Température réaliste
        assert 0 <= weather.humidity <= 100
    
    def test_format_response(self):
        """Test formatage de la réponse."""
        from tools.weather_tool import WeatherData
        
        weather = WeatherData(
            temperature=15.0,
            feels_like=13.0,
            humidity=70,
            description="nuageux",
            description_fr="nuageux",
            wind_speed=20.0,
            city="Valenciennes",
            is_rainy=False,
            is_sunny=False,
            recommendation="Test"
        )
        
        response = weather_tool.format_weather_response(weather)
        
        assert "Valenciennes" in response
        assert "15" in response
        assert "70" in response


class TestTransportTool:
    """Tests de l'outil transport."""
    
    def test_get_route(self):
        """Test récupération itinéraire."""
        route = transport_tool.get_route("gare", "insa")
        
        assert route is not None
        assert len(route.options) > 0
        assert route.depart == "gare"
        assert route.arrivee == "insa"
    
    def test_normalize_location(self):
        """Test normalisation des lieux."""
        assert transport_tool._normalize("Gare de Valenciennes") == "gare"
        assert transport_tool._normalize("INSA") == "insa"
        assert transport_tool._normalize("centre-ville") == "centre-ville"
        assert transport_tool._normalize("Campus Mont Houy") == "insa"


class TestFullConversation:
    """Tests de conversation complète."""
    
    @pytest.mark.asyncio
    async def test_simple_question(self):
        """Test question simple."""
        orchestrator = Orchestrator()
        
        result = await orchestrator.process("Bonjour")
        
        assert result is not None
        assert "response" in result
        assert len(result["response"]) > 0
    
    @pytest.mark.asyncio
    async def test_weather_question(self):
        """Test question météo."""
        orchestrator = Orchestrator()
        
        result = await orchestrator.process("Quel temps fait-il ?")
        
        assert result is not None
        assert "response" in result
        # Devrait mentionner température ou météo
        response_lower = result["response"].lower()
        assert any(word in response_lower for word in ["température", "°c", "temps", "météo"])
    
    @pytest.mark.asyncio
    async def test_memory(self):
        """Test mémoire de conversation."""
        orchestrator = Orchestrator()
        
        # Première question
        await orchestrator.process("Je suis à la gare")
        
        # Vérifier que la localisation est mémorisée
        assert orchestrator.memory.user_context.location is not None


# Lancer les tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])