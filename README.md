# 🎓 Assistant Étudiant IA - INSA Hauts-de-France

Assistant intelligent multi-agents pour les étudiants de l'INSA Hauts-de-France à Valenciennes.

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

## 🌟 Fonctionnalités

- 🌤️ **Météo** - Conditions actuelles à Valenciennes
- 🚊 **Transports** - Itinéraires Transvilles, tramway T1
- 🍽️ **Restaurants** - RU, kebabs, restos pas chers
- 🎯 **Activités** - Que faire selon la météo
- 🎉 **Sorties** - Bars, soirées, événements

## 🏗️ Architecture
┌─────────────┐
│ Utilisateur │
└──────┬──────┘
│
▼
┌──────────────────┐
│ Orchestrateur │ ← Routing intelligent
└────────┬─────────┘
│
┌────┴────┐
▼ ▼
┌────────┐ ┌────────┐
│ Agent │ │ Agent │
│ Info │ │ Vie │
│Pratique│ │Étudiante│
└────────┘ └────────┘


## 🚀 Installation

### 1. Cloner le repo

```bash
git clone https://github.com/VOTRE_USERNAME/assistant-etudiant-insa.git
cd assistant-etudiant-insa

 2. Créer l'environnement virtuel
bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
3. Installer les dépendances
bash
pip install -r requirements.txt
4. Configurer les clés API
bash
cp .env.example .env
Éditez .env et ajoutez vos clés:

Google Gemini (gratuit): https://makersuite.google.com/app/apikey
OpenWeather (gratuit): https://openweathermap.org/api
5. Lancer l'application
bash
# Interface web (recommandé)
python run.py

# OU mode console
python main.py
📸 Screenshots


🛠️ Technologies
LLM:  Groq
Framework: LangChain
Frontend: Streamlit
APIs: OpenWeatherMap
📝 Exemples de Questions
"Quel temps fait-il à Valenciennes ?"
"Comment aller de la gare à l'INSA ?"
"Où manger pas cher près du campus ?"
"Il pleut, que faire ?"
"Où sortir jeudi soir ?"
👤 Auteur
Raouf Chaimaa

INSA Hauts-de-France
📄 License
