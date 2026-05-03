"""
Initialise la base RAG avec toutes les données.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from tools.rag_tool import rag_tool

def main():
    print(" Initialisation de la base RAG...")
    print("   (Cela peut prendre quelques minutes la première fois)")
    print()
    
    rag_tool.initialize()
    
    print()
    print(" Base RAG créée avec succès !")
    print()
    
    # Test
    print(" Test de recherche...")
    results = rag_tool.search("restaurant pas cher", k=2)
    
    for i, r in enumerate(results, 1):
        print(f"\n📄 Résultat {i}:")
        print(f"   {r['content'][:100]}...")
        print(f"   Score: {r['score']:.3f}")


if __name__ == "__main__":
    main()