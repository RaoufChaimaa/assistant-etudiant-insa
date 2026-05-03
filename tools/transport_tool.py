"""
Outil transport - Valenciennes (Transvilles)
"""

from typing import Dict, List, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel
import random

from config.settings import settings, DATA_DIR
from utils.helpers import load_json, get_current_day_info
from utils.logger import log


class TransportOption(BaseModel):
    """Option de transport."""
    mode: str
    ligne: Optional[str] = None
    duree: str
    cout: float
    prochains_departs: List[str] = []
    note: Optional[str] = None


class TransportRoute(BaseModel):
    """Itinéraire."""
    depart: str
    arrivee: str
    options: List[TransportOption]
    meilleure_option: str


class TransportTool:
    """Outil transport Valenciennes."""
    
    def __init__(self):
        self.data = self._load_transport_data()
    
    def _load_transport_data(self) -> Dict:
        """Charge les données transport."""
        try:
            return load_json(DATA_DIR / "transports.json")
        except:
            return self._get_default_data()
    
    def _get_default_data(self) -> Dict:
        """Données par défaut - Valenciennes."""
        return {
            "lignes": [
                {
                    "type": "tramway",
                    "numero": "T1",
                    "nom": "Tramway Valenciennes",
                    "arrets": ["Gare", "Centre-ville", "Université", "Mont Houy"],
                    "frequence_semaine": "8 min",
                    "frequence_weekend": "15 min"
                },
                {
                    "type": "bus",
                    "numero": "3",
                    "nom": "Ligne Campus",
                    "arrets": ["Gare", "Place d'Armes", "INSA", "UPHF"],
                    "frequence_semaine": "15 min"
                }
            ],
            "itineraires": [
                {
                    "de": "gare",
                    "vers": "insa",
                    "options": [
                        {"mode": "tramway", "ligne": "T1", "duree": "20 min", "cout": 1.60},
                        {"mode": "bus", "ligne": "3", "duree": "25 min", "cout": 1.60},
                        {"mode": "vélo", "duree": "25 min", "cout": 0},
                    ]
                },
                {
                    "de": "centre-ville",
                    "vers": "insa",
                    "options": [
                        {"mode": "tramway", "ligne": "T1", "duree": "15 min", "cout": 1.60},
                        {"mode": "vélo", "duree": "20 min", "cout": 0},
                        {"mode": "marche", "duree": "40 min", "cout": 0},
                    ]
                }
            ]
        }
    
    def get_route(self, depart: str, arrivee: str) -> TransportRoute:
        """Trouve un itinéraire."""
        depart_norm = self._normalize(depart)
        arrivee_norm = self._normalize(arrivee)
        
        options = self._find_route(depart_norm, arrivee_norm)
        options = self._add_departures(options)
        
        best = options[0] if options else None
        best_str = f"{best.mode} ({best.duree})" if best else "Non disponible"
        
        return TransportRoute(
            depart=depart,
            arrivee=arrivee,
            options=options,
            meilleure_option=best_str
        )
    
    def _normalize(self, location: str) -> str:
        """Normalise un lieu."""
        loc = location.lower().strip()
        
        mappings = {
            "gare": "gare",
            "station": "gare",
            "centre": "centre-ville",
            "centre-ville": "centre-ville",
            "insa": "insa",
            "uphf": "insa",
            "université": "insa",
            "campus": "insa",
            "mont houy": "insa",
        }
        
        for key, value in mappings.items():
            if key in loc:
                return value
        return loc
    
    def _find_route(self, depart: str, arrivee: str) -> List[TransportOption]:
        """Trouve les options pour un trajet."""
        for route in self.data.get("itineraires", []):
            if route["de"] == depart and route["vers"] == arrivee:
                return [TransportOption(**opt) for opt in route["options"]]
            if route["de"] == arrivee and route["vers"] == depart:
                return [TransportOption(**opt) for opt in route["options"]]
        
        # Par défaut
        return [
            TransportOption(mode="tramway", ligne="T1", duree="~20 min", cout=1.60),
            TransportOption(mode="marche", duree="~35 min", cout=0),
        ]
    
    def _add_departures(self, options: List[TransportOption]) -> List[TransportOption]:
        """Ajoute les prochains départs simulés."""
        now = datetime.now()
        
        for opt in options:
            if opt.mode in ["tramway", "bus"]:
                deps = []
                for i in range(3):
                    next_time = now + timedelta(minutes=random.randint(3, 12) + i * 10)
                    deps.append(next_time.strftime("%H:%M"))
                opt.prochains_departs = deps
        
        return options
    
    def format_route_response(self, route: TransportRoute) -> str:
        """Formate la réponse transport."""
        lines = [
            f"🚊 **Trajet : {route.depart} → {route.arrivee}**",
            "",
            "**Options disponibles :**",
            ""
        ]
        
        icons = {"tramway": "🚊", "bus": "🚌", "vélo": "🚲", "marche": "🚶"}
        
        for opt in route.options:
            icon = icons.get(opt.mode, "🚌")
            line = f"{icon} **{opt.mode.capitalize()}**"
            if opt.ligne:
                line += f" (Ligne {opt.ligne})"
            line += f" - {opt.duree}"
            line += f" - {'Gratuit' if opt.cout == 0 else f'{opt.cout}€'}"
            lines.append(line)
            
            if opt.prochains_departs:
                lines.append(f"   ⏰ Prochains : {', '.join(opt.prochains_departs)}")
            lines.append("")
        
        lines.append(f"✅ **Recommandé :** {route.meilleure_option}")
        
        return "\n".join(lines)


transport_tool = TransportTool()