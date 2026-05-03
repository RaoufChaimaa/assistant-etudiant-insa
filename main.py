"""
Point d'entrée principal - Assistant Étudiant INSA HdF
"""

import asyncio
import sys
from pathlib import Path

# Ajouter le dossier au path
sys.path.insert(0, str(Path(__file__).parent))

from agents.orchestrator import Orchestrator
from utils.logger import log


async def main():
    """Mode console interactif."""
    print("\n" + "="*60)
    print("🎓 Assistant Étudiant INSA Hauts-de-France - Valenciennes")
    print("="*60)
    print("\nCommandes spéciales:")
    print("  'quit' ou 'exit' - Quitter")
    print("  'clear' - Effacer l'historique")
    print("  'help' - Aide")
    print("\n" + "-"*60 + "\n")
    
    orchestrator = Orchestrator()
    
    while True:
        try:
            # Input utilisateur
            user_input = input("\n🧑 Toi: ").strip()
            
            if not user_input:
                continue
            
            # Commandes spéciales
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("\n👋 À bientôt à l'INSA !")
                break
            
            if user_input.lower() == 'clear':
                orchestrator.clear_memory()
                print("✅ Historique effacé")
                continue
            
            if user_input.lower() == 'help':
                print("""
📚 Aide - Je peux t'aider avec:
   • Météo: "Quel temps fait-il ?"
   • Transport: "Comment aller à l'INSA ?"
   • Restaurants: "Où manger pas cher ?"
   • Activités: "Que faire s'il pleut ?"
   • Sorties: "Où sortir ce soir ?"
                """)
                continue
            
            # Traiter la requête
            print("\n🤔 Je réfléchis...")
            result = await orchestrator.process(user_input)
            
            # Afficher la réponse
            print(f"\n🤖 Assistant: {result['response']}")
            
            # Afficher les métadonnées
            if result.get('agents_used'):
                agents = ", ".join(result['agents_used'])
                print(f"\n   📊 Agents: {agents}")
            
        except KeyboardInterrupt:
            print("\n\n👋 À bientôt !")
            break
        except Exception as e:
            log.error(f"Erreur: {e}")
            print(f"\n❌ Erreur: {e}")


if __name__ == "__main__":
    asyncio.run(main())