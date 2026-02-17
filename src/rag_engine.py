"""
RAG Engine - Core retrieval and answer generation
Handles: document loading, embeddings, search, answering
"""
import os
import ollama
from langchain_chroma import Chroma
from langchain_community.document_loaders import DirectoryLoader, PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings


class RAGEngine:
    """
    Core RAG Engine that:
    1. Loads documents from a folder
    2. Creates searchable vector database
    3. Finds relevant chunks for any question
    4. Generates grounded answers with sources
    """

    def __init__(self, docs_path="data/documents", db_path="./chroma_db"):
        self.docs_path = docs_path
        self.db_path = db_path
        self.vectorstore = None

        # Load FREE local embeddings
        print("Loading embeddings model...")
        self.embeddings = HuggingFaceEmbeddings(
            model_name="all-MiniLM-L6-v2"
        )

        # Load existing database or create new one
        self._initialize_database()

    def _initialize_database(self):
        """Load existing vector DB or create new one from documents"""
        if os.path.exists(self.db_path) and os.listdir(self.db_path):
            print("Loading existing vector database...")
            self.vectorstore = Chroma(
                persist_directory=self.db_path,
                embedding_function=self.embeddings
            )
            print("Vector database loaded!")
        else:
            print("No database found. Creating from documents...")
            self._build_database()

    def _build_database(self):
        """Build vector database from documents"""
        # Load documents
        print(f"Loading documents from {self.docs_path}...")
        loader = DirectoryLoader(
            self.docs_path,
            glob="**/*.pdf",
            loader_cls=PyPDFLoader
        )
        documents = loader.load()

        if not documents:
            print("No documents found!")
            return

        print(f"Loaded {len(documents)} pages")

        # Split into chunks
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        chunks = splitter.split_documents(documents)
        print(f"Created {len(chunks)} chunks")

        # Create vector database
        print("Building vector database...")
        self.vectorstore = Chroma.from_documents(
            chunks,
            self.embeddings,
            persist_directory=self.db_path
        )
        print("Vector database ready!")

    def search(self, query, k=5):
        """
        Search for relevant document chunks
        Returns list of (document, relevance_score) pairs
        """
        if not self.vectorstore:
            return []

        results = self.vectorstore.similarity_search_with_relevance_scores(
            query, k=k
        )
        return results

    def answer(self, question, conversation_context=""):
        """
        Generate a grounded answer with sources
        Returns: dict with answer, sources, confidence
        """
        # Search for relevant documents
        results = self.search(question, k=5)

        # Filter by minimum confidence
        min_confidence = 0.0
        relevant = [
            (doc, score) for doc, score in results
            if score >= min_confidence
        ]

        # Handle no relevant documents found
        if not relevant:
            return {
                "answer": "I don't have enough information to answer that question confidently. Please make sure relevant documents are loaded.",
                "sources": [],
                "confidence": 0.0,
                "grounded": False
            }

        # Build context from relevant chunks
        context = "\n\n".join([doc.page_content for doc, _ in relevant])

        # Build prompt
        prompt = f"""You are a helpful assistant. Answer the question using ONLY the provided context.
If the answer is not in the context, say "I don't have information about that."
Always be concise and accurate.

{f"Previous conversation:{conversation_context}" if conversation_context else ""}

Context from documents:
{context}

Question: {question}

Answer:"""

        # Generate answer with FREE Ollama
        response = ollama.chat(
            model="llama3.2",
            messages=[{"role": "user", "content": prompt}]
        )
        answer_text = response["message"]["content"]

        # Calculate confidence
        avg_confidence = sum(score for _, score in relevant) / len(relevant)

        # Build sources list
        sources = []
        seen = set()
        for doc, score in relevant:
            source = doc.metadata.get("source", "Unknown")
            page = doc.metadata.get("page", "?")
            key = f"{source}_p{page}"

            if key not in seen:
                seen.add(key)
                sources.append({
                    "file": os.path.basename(source),
                    "page": page,
                    "confidence": round(float(score), 2),
                    "excerpt": doc.page_content[:100] + "..."
                })

        return {
            "answer": answer_text,
            "sources": sources,
            "confidence": round(float(avg_confidence), 2),
            "grounded": True
        }
