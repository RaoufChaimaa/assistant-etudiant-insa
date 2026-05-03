"""
Fonctions utilitaires.
"""

import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional
from datetime import datetime


def load_json(filepath: Path) -> Dict[str, Any]:
    """Charge un fichier JSON."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_json(data: Dict[str, Any], filepath: Path) -> None:
    """Sauvegarde en JSON."""
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def get_current_day_info() -> Dict[str, Any]:
    """Retourne les infos du jour actuel."""
    now = datetime.now()
    
    days_fr = {
        0: "lundi", 1: "mardi", 2: "mercredi",
        3: "jeudi", 4: "vendredi", 5: "samedi", 6: "dimanche"
    }
    
    return {
        "day_name": days_fr[now.weekday()],
        "day_number": now.day,
        "month": now.month,
        "year": now.year,
        "hour": now.hour,
        "minute": now.minute,
        "is_weekend": now.weekday() >= 5,
        "is_evening": now.hour >= 18,
        "formatted": now.strftime("%A %d %B %Y à %H:%M")
    }


def extract_location_from_text(text: str) -> Optional[str]:
    """Extrait une localisation du texte."""
    text_lower = text.lower()
    
    # Lieux connus à Valenciennes
    known_places = {
        "insa": "INSA Hauts-de-France",
        "uphf": "UPHF Mont Houy",
        "mont houy": "Campus Mont Houy",
        "gare": "Gare de Valenciennes",
        "centre": "Centre-ville",
        "centre-ville": "Centre-ville",
        "place d'armes": "Place d'Armes",
        "bu": "Bibliothèque Universitaire",
        "crous": "CROUS",
        "ru": "Restaurant Universitaire"
    }
    
    for key, value in known_places.items():
        if key in text_lower:
            return value
    
    return None