"""
Outil RAG - Retrieval-Augmented Generation
Permet de chercher dans une base de connaissances.
"""

import json
from pathlib import Path
from typing import List, Dict, Any

# Imports corrigés pour les nouvelles versions de LangChain
try:
    from langchain_community.vectorstores import Chroma
except ImportError:
    from langchain.vectorstores import Chroma

try:
    from langchain_community.embeddings import HuggingFaceEmbeddings
except ImportError:
    from langchain.embeddings import HuggingFaceEmbeddings

try:
    from langchain_text_splitters import RecursiveCharacterTextSplitter
except ImportError:
    try:
        from langchain.text_splitter import RecursiveCharacterTextSplitter
    except ImportError:
        from langchain_core.documents import Document
        RecursiveCharacterTextSplitter = None

from langchain_core.documents import Document

from config.settings import DATA_DIR, BASE_DIR
from utils.logger import log


class RAGTool:
    """
    Outil RAG pour rechercher des informations pertinentes.
    """
    
    def __init__(self):
        self.persist_directory = BASE_DIR / "data" / "chroma_db"
        self.embeddings = None
        self.vectorstore = None
        self.is_initialized = False
        self._initialization_failed = False
        
    def initialize(self):
        """Initialise le RAG avec les données."""
        if self.is_initialized:
            return True
        
        if self._initialization_failed:
            return False
        
        log.info("🔄 Initialisation du RAG...")
        
        try:
            # Créer les embeddings (modèle gratuit et local)
            self.embeddings = HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-MiniLM-L6-v2",
                model_kwargs={'device': 'cpu'}
            )
            
            # Charger ou créer la base de vecteurs
            if (self.persist_directory / "chroma.sqlite3").exists():
                log.info("📂 Chargement de la base existante...")
                self.vectorstore = Chroma(
                    persist_directory=str(self.persist_directory),
                    embedding_function=self.embeddings
                )
            else:
                log.info("📝 Création de la nouvelle base...")
                documents = self._load_all_documents()
                if documents:
                    self._create_vectorstore(documents)
                else:
                    log.warning("⚠️ Aucun document à charger")
                    self._initialization_failed = True
                    return False
            
            self.is_initialized = True
            log.info("✅ RAG initialisé !")
            return True
            
        except Exception as e:
            log.error(f"❌ Erreur initialisation RAG: {e}")
            self._initialization_failed = True
            return False
    
    def _load_all_documents(self) -> List[Document]:
        """Charge tous les documents depuis les fichiers JSON."""
        documents = []
        
        try:
            # Charger lieux.json
            lieux_path = DATA_DIR / "lieux.json"
            if lieux_path.exists():
                documents.extend(self._load_lieux(lieux_path))
            
            # Charger activites.json
            activites_path = DATA_DIR / "activites.json"
            if activites_path.exists():
                documents.extend(self._load_activites(activites_path))
            
            # Charger transports.json
            transports_path = DATA_DIR / "transports.json"
            if transports_path.exists():
                documents.extend(self._load_transports(transports_path))
            
            # Ajouter des documents sur l'INSA
            documents.extend(self._get_insa_documents())
            
            log.info(f"📄 {len(documents)} documents chargés")
            
        except Exception as e:
            log.error(f"Erreur chargement documents: {e}")
        
        return documents
    
    def _load_lieux(self, path: Path) -> List[Document]:
        """Charge les lieux depuis le JSON."""
        documents = []
        
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Restaurants
            for resto in data.get("restaurants", []):
                content = f"""
Restaurant: {resto['nom']}
Type: {resto['type']}
Budget: {resto['budget']} (environ {resto['prix_moyen']}€)
Localisation: {resto['localisation']}
Spécialités: {', '.join(resto.get('specialites', []))}
Note: {resto.get('note', 'N/A')}/5
                """.strip()
                
                documents.append(Document(
                    page_content=content,
                    metadata={"source": "lieux", "type": "restaurant", "nom": resto['nom']}
                ))
            
            # Cafés
            for cafe in data.get("cafes", []):
                content = f"""
Lieu: {cafe['nom']}
Type: {cafe['type']}
Localisation: {cafe['localisation']}
WiFi: {'Oui' if cafe.get('wifi') else 'Non'}
Calme: {'Oui' if cafe.get('calme') else 'Non'}
                """.strip()
                
                documents.append(Document(
                    page_content=content,
                    metadata={"source": "lieux", "type": "cafe", "nom": cafe['nom']}
                ))
            
            # Sorties
            for sortie in data.get("sorties", []):
                content = f"""
Sortie: {sortie['nom']}
Type: {sortie['type']}
Localisation: {sortie['localisation']}
Prix: {sortie.get('prix_moyen', 'N/A')}€
                """.strip()
                
                documents.append(Document(
                    page_content=content,
                    metadata={"source": "lieux", "type": "sortie", "nom": sortie['nom']}
                ))
                
        except Exception as e:
            log.error(f"Erreur chargement lieux: {e}")
        
        return documents
    
    def _load_activites(self, path: Path) -> List[Document]:
        """Charge les activités depuis le JSON."""
        documents = []
        
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            for meteo, activites in data.get("par_meteo", {}).items():
                for act in activites:
                    content = f"""
Activité: {act['nom']}
Type: {act['type']}
Météo conseillée: {meteo}
Description: {act['description']}
Coût: {'Gratuit' if act['cout'] == 0 else f"{act['cout']}€"}
                    """.strip()
                    
                    documents.append(Document(
                        page_content=content,
                        metadata={"source": "activites", "type": "activite", "meteo": meteo}
                    ))
                    
        except Exception as e:
            log.error(f"Erreur chargement activites: {e}")
        
        return documents
    
    def _load_transports(self, path: Path) -> List[Document]:
        """Charge les transports depuis le JSON."""
        documents = []
        
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            for ligne in data.get("lignes", []):
                arrets = ligne.get('arrets_principaux', ligne.get('arrets', []))
                content = f"""
Transport: {ligne.get('nom', '')}
Type: {ligne['type']}
Numéro: {ligne.get('numero', 'N/A')}
Arrêts: {', '.join(arrets) if arrets else 'N/A'}
Tarif: {ligne.get('tarif', 'N/A')}€
                """.strip()
                
                documents.append(Document(
                    page_content=content,
                    metadata={"source": "transports", "type": "transport"}
                ))
                
        except Exception as e:
            log.error(f"Erreur chargement transports: {e}")
        
        return documents
    
    def _get_insa_documents(self) -> List[Document]:
        """Documents spécifiques sur l'INSA."""
        insa_docs = [
            """
L'INSA Hauts-de-France est une école d'ingénieurs située à Valenciennes.
Adresse: Campus Mont Houy, 59313 Valenciennes
Formations: Ingénieur en 5 ans
            """,
            """
Services INSA Hauts-de-France:
- BU (Bibliothèque): 08:00-20:00 semaine
- RU (Restaurant): 11:30-13:30, tarif 3.30€
- Cafétéria: 08:00-17:00
- SUAPS (sport): 08:00-20:00
            """,
            """
Accès campus INSA:
- Tramway T1: arrêt Université ou Mont Houy
- Bus ligne 3: depuis la gare
- Depuis la gare: 20 minutes en tramway
            """
        ]
        
        return [
            Document(
                page_content=doc.strip(),
                metadata={"source": "insa", "type": "info"}
            )
            for doc in insa_docs
        ]
    
    def _create_vectorstore(self, documents: List[Document]):
        """Crée la base de vecteurs."""
        try:
            # Découper si le splitter est disponible
            if RecursiveCharacterTextSplitter:
                text_splitter = RecursiveCharacterTextSplitter(
                    chunk_size=500,
                    chunk_overlap=50
                )
                splits = text_splitter.split_documents(documents)
            else:
                splits = documents
            
            log.info(f"📊 {len(splits)} chunks créés")
            
            # Créer le dossier
            self.persist_directory.mkdir(parents=True, exist_ok=True)
            
            # Créer la base
            self.vectorstore = Chroma.from_documents(
                documents=splits,
                embedding=self.embeddings,
                persist_directory=str(self.persist_directory)
            )
            
            log.info("💾 Base de vecteurs créée")
            
        except Exception as e:
            log.error(f"Erreur création vectorstore: {e}")
            raise
    
    def search(self, query: str, k: int = 3) -> List[Dict[str, Any]]:
        """Recherche les documents pertinents."""
        if not self.is_initialized:
            if not self.initialize():
                return []
        
        try:
            results = self.vectorstore.similarity_search_with_score(query, k=k)
            
            formatted = []
            for doc, score in results:
                formatted.append({
                    "content": doc.page_content,
                    "metadata": doc.metadata,
                    "score": float(score)
                })
            
            return formatted
            
        except Exception as e:
            log.error(f"Erreur recherche RAG: {e}")
            return []
    
    def get_context_for_query(self, query: str, k: int = 3) -> str:
        """Retourne le contexte formaté pour une requête."""
        results = self.search(query, k=k)
        
        if not results:
            return ""
        
        context = "📚 **Informations trouvées:**\n\n"
        
        for i, result in enumerate(results, 1):
            context += f"**Info {i}:**\n{result['content']}\n\n"
        
        return context


# Instance globale
rag_tool = RAGTool()