"""
Constantes - Valenciennes & INSA Hauts-de-France
"""

# Mots-clés météo
WEATHER_KEYWORDS = [
    "météo", "temps", "pluie", "soleil", "température",
    "pleut", "neige", "chaud", "froid", "vent",
    "parapluie", "nuageux", "beau temps"
]

# Mots-clés transport
TRANSPORT_KEYWORDS = [
    "transport", "bus", "tram", "tramway", "train",
    "aller", "trajet", "itinéraire", "comment aller",
    "rejoindre", "arriver", "vélo", "transvilles",
    "gare", "ter"
]

# Mots-clés restaurant
RESTAURANT_KEYWORDS = [
    "manger", "restaurant", "resto", "café", "déjeuner",
    "dîner", "faim", "repas", "crous", "ru", "self",
    "kebab", "pizza", "sandwich"
]

# Mots-clés activités
ACTIVITY_KEYWORDS = [
    "faire", "activité", "sortie", "sortir", "loisir",
    "soirée", "bar", "ciné", "cinéma", "sport",
    "bde", "événement", "fête"
]

# Descriptions météo
WEATHER_DESCRIPTIONS = {
    "clear": "ensoleillé",
    "clouds": "nuageux",
    "rain": "pluvieux",
    "drizzle": "bruine",
    "thunderstorm": "orageux",
    "snow": "neigeux",
    "mist": "brumeux",
    "fog": "brouillard"
}

# Lieux importants Valenciennes
LIEUX_VALENCIENNES = {
    "insa": {"lat": 50.3287, "lon": 3.5117, "nom": "INSA Hauts-de-France"},
    "gare": {"lat": 50.3597, "lon": 3.5097, "nom": "Gare de Valenciennes"},
    "centre": {"lat": 50.3577, "lon": 3.5235, "nom": "Centre-ville"},
    "place_armes": {"lat": 50.3582, "lon": 3.5228, "nom": "Place d'Armes"},
    "uphf": {"lat": 50.3287, "lon": 3.5117, "nom": "UPHF Mont Houy"},
}