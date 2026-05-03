"""
Interface Streamlit - Assistant Étudiant INSA Hauts-de-France
"""
from typing import Dict
import streamlit as st
import asyncio
from datetime import datetime
import sys
from pathlib import Path

# Ajouter le dossier parent au path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.orchestrator import Orchestrator


# ==================== Configuration Page ====================
st.set_page_config(
    page_title="🎓 Assistant INSA HdF",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ==================== CSS Personnalisé ====================
st.markdown("""
<style>
    /* Header gradient */
    .header-container {
        background: linear-gradient(135deg, #1e3a5f 0%, #2d5a87 100%);
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        color: white;
        text-align: center;
    }
    
    .header-title {
        font-size: 2.2rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
    }
    
    .header-subtitle {
        font-size: 1rem;
        opacity: 0.9;
    }
    
    /* Messages */
    .user-message {
        background: linear-gradient(135deg, #1e3a5f 0%, #2d5a87 100%);
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 20px 20px 5px 20px;
        margin: 0.5rem 0;
        max-width: 80%;
        margin-left: auto;
    }
    
    .assistant-message {
        background: #f0f2f6;
        color: #1f1f1f;
        padding: 1rem 1.5rem;
        border-radius: 20px 20px 20px 5px;
        margin: 0.5rem 0;
        max-width: 85%;
    }
    
    /* Info card */
    .info-card {
        background: white;
        border-radius: 10px;
        padding: 1.5rem;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        margin: 1rem 0;
    }
    
    /* Tags */
    .tag {
        display: inline-block;
        padding: 0.2rem 0.6rem;
        border-radius: 15px;
        font-size: 0.75rem;
        margin: 0.2rem;
    }
    
    .tag-info { background: #cce5ff; color: #004085; }
    .tag-vie { background: #d4edda; color: #155724; }
    
    /* Boutons */
    .stButton > button {
        border-radius: 20px;
        padding: 0.5rem 1.5rem;
    }
</style>
""", unsafe_allow_html=True)


# ==================== Initialisation ====================
def init_session_state():
    """Initialise les variables de session."""
    if "orchestrator" not in st.session_state:
        st.session_state.orchestrator = Orchestrator()
    
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    if "processing" not in st.session_state:
        st.session_state.processing = False


# ==================== Composants UI ====================
def render_header():
    """Affiche l'en-tête."""
    st.markdown("""
    <div class="header-container">
        <div class="header-title">🎓 Assistant Étudiant INSA</div>
        <div class="header-subtitle">
            Ton compagnon IA pour la vie étudiante à Valenciennes
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_sidebar():
    """Affiche la sidebar."""
    with st.sidebar:
        st.markdown("## ⚙️ Paramètres")
        
        # Contexte utilisateur
        st.markdown("### 📍 Ton Contexte")
        
        location = st.selectbox(
            "Tu es où ?",
            ["Non défini", "INSA / Campus", "Gare", "Centre-ville", "Résidence"],
            index=0
        )
        
        if location != "Non défini":
            st.session_state.orchestrator.memory.update_location(location)
        
        budget = st.selectbox(
            "Budget",
            ["Non défini", "Serré (gratuit/RU)", "Normal", "Large"]
        )
        
        if budget != "Non défini":
            st.session_state.orchestrator.memory.user_context.budget_preference = budget
        
        st.markdown("---")
        
        # Agents
        st.markdown("### 🤖 Agents Disponibles")
        
        with st.expander("📊 Info-Pratiques"):
            st.markdown("""
            - 🌤️ Météo Valenciennes
            - 🚊 Transports (Transvilles, T1)
            - 🕐 Horaires (BU, RU, etc.)
            """)
        
        with st.expander("🎓 Vie Étudiante"):
            st.markdown("""
            - 🍽️ Restaurants & RU
            - 🎯 Activités & Loisirs  
            - 🎉 Sorties & Bars
            - 💰 Bons plans
            """)
        
        st.markdown("---")
        
        # Exemples
        st.markdown("### 💡 Exemples")
        
        examples = [
            "Quel temps fait-il ?",
            "Comment aller à l'INSA ?",
            "Où manger pas cher ?",
            "Il pleut, que faire ?",
            "Où sortir jeudi soir ?"
        ]
        
        for ex in examples:
            if st.button(ex, key=f"ex_{ex}", use_container_width=True):
                return ex
        
        st.markdown("---")
        
        # Actions
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🗑️ Effacer", use_container_width=True):
                st.session_state.messages = []
                st.session_state.orchestrator.clear_memory()
                st.rerun()
        
        with col2:
            if st.button("📥 Export", use_container_width=True):
                export_conversation()
        
        # Stats
        st.markdown("---")
        st.caption(f"💬 {len(st.session_state.messages)} messages")
        st.caption(f"🕐 {datetime.now().strftime('%H:%M')}")
    
    return None


def render_message(role: str, content: str, metadata: dict = None):
    """Affiche un message."""
    if role == "user":
        st.markdown(f'<div class="user-message">{content}</div>', unsafe_allow_html=True)
    else:
        # Tags des agents utilisés
        tags_html = ""
        if metadata and metadata.get("agents_used"):
            for agent in metadata["agents_used"]:
                if "Info" in agent:
                    tags_html += '<span class="tag tag-info">📊 Info</span>'
                elif "Vie" in agent:
                    tags_html += '<span class="tag tag-vie">🎓 Vie Étu</span>'
        
        st.markdown(f'''
        <div class="assistant-message">
            {content}
            <div style="margin-top: 0.5rem;">{tags_html}</div>
        </div>
        ''', unsafe_allow_html=True)


def render_chat():
    """Affiche l'interface de chat."""
    # Messages
    for msg in st.session_state.messages:
        render_message(msg["role"], msg["content"], msg.get("metadata"))
    
    # Input
    st.markdown("---")
    
    col1, col2 = st.columns([5, 1])
    
    with col1:
        user_input = st.text_input(
            "Message",
            placeholder="Pose ta question ici...",
            key="user_input",
            label_visibility="collapsed"
        )
    
    with col2:
        send = st.button("Envoyer 📤", type="primary", use_container_width=True)
    
    return user_input if send else None


def export_conversation():
    """Exporte la conversation."""
    if not st.session_state.messages:
        st.warning("Aucun message à exporter")
        return
    
    text = "# Conversation - Assistant INSA HdF\n\n"
    text += f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n---\n\n"
    
    for msg in st.session_state.messages:
        role = "🧑 Toi" if msg["role"] == "user" else "🤖 Assistant"
        text += f"**{role}:**\n{msg['content']}\n\n"
    
    st.download_button(
        "📥 Télécharger",
        text,
        f"conversation_{datetime.now().strftime('%Y%m%d_%H%M')}.md",
        "text/markdown"
    )


# ==================== Traitement ====================
async def process_query(query: str) -> Dict:
    """Traite une requête."""
    try:
        result = await st.session_state.orchestrator.process(query)
        return result
    except Exception as e:
        return {
            "response": f"Oups, erreur: {str(e)}",
            "agents_used": [],
            "error": True
        }


def handle_query(query: str):
    """Gère une requête utilisateur."""
    if not query or not query.strip():
        return
    
    # Ajouter message utilisateur
    st.session_state.messages.append({
        "role": "user",
        "content": query
    })
    
    # Traiter
    with st.spinner("🤔 Je réfléchis..."):
        result = asyncio.run(process_query(query))
    
    # Ajouter réponse
    st.session_state.messages.append({
        "role": "assistant",
        "content": result["response"],
        "metadata": {
            "agents_used": result.get("agents_used", []),
            "tools_used": result.get("tools_used", [])
        }
    })


# ==================== Main ====================
def main():
    """Application principale."""
    init_session_state()
    
    render_header()
    
    # Sidebar (peut retourner un exemple)
    example = render_sidebar()
    
    # Zone principale
    col1, col2, col3 = st.columns([1, 4, 1])
    
    with col2:
        # Message de bienvenue
        if not st.session_state.messages:
            st.markdown("""
            <div class="info-card" style="text-align: center;">
                <h3>👋 Salut futur ingénieur !</h3>
                <p>
                    Je suis ton assistant IA pour l'INSA Hauts-de-France à Valenciennes.
                </p>
                <p>
                    Je peux t'aider avec : météo 🌤️, transports 🚊, 
                    restaurants 🍽️, activités 🎯, sorties 🎉...
                </p>
                <p style="color: #6c757d; font-size: 0.9rem;">
                    Essaie un exemple dans la barre latérale ou tape ta question !
                </p>
            </div>
            """, unsafe_allow_html=True)
        
        # Chat
        user_query = render_chat()
        
        # Traiter requête
        query = user_query or example
        if query:
            handle_query(query)
            st.rerun()


if __name__ == "__main__":
    main()