import warnings
warnings.filterwarnings('ignore')

"""
RAG Engine - Multi-format OPTIMIZED FOR SPEED
"""
import os
from typing import List, Dict
import ollama
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document
from src.document_processor import DocumentProcessor


class RAGEngine:
    def __init__(self, documents_path: str = "data/documents"):
        print("\n" + "="*60)
        print("Initializing Agentic RAG Chatbot...")
        print("="*60)
        
        self.documents_path = documents_path
        self.vectorstore = None
        
        print("Loading embeddings model...")
        self.embeddings = HuggingFaceEmbeddings(
            model_name="all-MiniLM-L6-v2"
        )
        
        self.load_documents()
    
    def load_documents(self):
        if os.path.exists("./chroma_db"):
            print("Loading existing vector database...")
            self.vectorstore = Chroma(
                persist_directory="./chroma_db",
                embedding_function=self.embeddings
            )
            print("Vector database loaded!")
        else:
            print("Building new vector database...")
            self._build_database()
    
    def _build_database(self):
        print(f"Loading documents from {self.documents_path}...")
        all_docs = []
        
        for filename in os.listdir(self.documents_path):
            filepath = os.path.join(self.documents_path, filename)
            
            if os.path.isfile(filepath):
                try:
                    docs = DocumentProcessor.process_file(filepath)
                    all_docs.extend(docs)
                    print(f"  ✓ {filename}")
                except Exception as e:
                    print(f"  ✗ {filename}: {e}")
        
        print(f"Loaded {len(all_docs)} pages")
        
        documents = [
            Document(page_content=doc['text'], metadata=doc['metadata'])
            for doc in all_docs
        ]
        
        # SMALLER CHUNKS = FASTER
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=600,
            chunk_overlap=100
        )
        splits = text_splitter.split_documents(documents)
        print(f"Created {len(splits)} chunks")
        
        self.vectorstore = Chroma.from_documents(
            documents=splits,
            embedding=self.embeddings,
            persist_directory="./chroma_db"
        )
        
        print("Vector database ready!")
    
    def search(self, query: str, k: int = 3) -> List:  # ONLY 3 RESULTS
        results = self.vectorstore.similarity_search_with_relevance_scores(
            query, k=k
        )
        return results
    
    def answer(self, question: str, context: str = "") -> Dict:
        results = self.search(question)
        
        if not results:
            return {
                "answer": "No information available.",
                "sources": [],
                "confidence": 0.0,
                "grounded": False
            }
        
        # USE ONLY TOP 2 DOCS FOR SPEED
        relevant_docs = [doc for doc, score in results[:2]]
        context_text = "\n\n".join([doc.page_content for doc in relevant_docs])
        
        # MINIMAL PROMPT
        prompt = f"""Context: {context_text}

Question: {question}

Answer in 1-2 sentences:"""
        
        response = ollama.chat(
            model="llama3.2",
            messages=[{"role": "user", "content": prompt}],
            options={
                "temperature": 0,
                "num_predict": 100
            }
        )
        
        answer_text = response["message"]["content"].strip()
        
        sources = []
        for doc, score in results[:2]:
            source_info = {
                "file": os.path.basename(doc.metadata.get("source", "unknown")),
                "type": doc.metadata.get("type", "pdf")
            }
            if "page" in doc.metadata:
                source_info["page"] = doc.metadata["page"]
            sources.append(source_info)
        
        return {
            "answer": answer_text,
            "sources": sources,
            "confidence": 1.0,
            "grounded": True
        }
