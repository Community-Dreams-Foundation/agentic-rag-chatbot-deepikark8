"""
Agentic RAG Chatbot - Main orchestrator
Combines RAG + Memory + Security into one chatbot
"""
import uuid
from src.rag_engine import RAGEngine
from src.memory import MemorySystem
from src.security import SecurityLayer


class AgenticRAGChatbot:
    """
    Main chatbot that orchestrates:
    1. Security checks (auth + sanitization + rate limiting)
    2. Memory retrieval (past conversation context)
    3. RAG search and answer generation
    4. Response formatting with sources
    """

    def __init__(self):
        print("\n" + "="*60)
        print("Initializing Agentic RAG Chatbot...")
        print("="*60)

        self.rag = RAGEngine()
        self.memory = MemorySystem()
        self.security = SecurityLayer()

        print("\nChatbot ready!")

    def register_user(self, user_id):
        """Register a user and return their auth token"""
        token = self.security.create_token(user_id)
        return token

    def chat(self, question, session_id, user_id, token):
        """
        Main chat function - full pipeline:
        1. Verify token
        2. Check rate limit
        3. Sanitize input
        4. Get memory context
        5. Generate RAG answer
        6. Save to memory
        7. Return formatted response
        """

        # Step 1: Verify authentication
        verified_user = self.security.verify_token(token)
        if not verified_user:
            return {
                "status": "error",
                "error": "Authentication failed. Please login again.",
                "code": 401
            }

        # Step 2: Check rate limit
        if not self.security.check_rate_limit(user_id):
            return {
                "status": "error",
                "error": "Rate limit exceeded. Max 100 requests per hour.",
                "code": 429
            }

        # Step 3: Sanitize input
        clean_question = self.security.sanitize(question)
        if not clean_question:
            return {
                "status": "error",
                "error": "Invalid input after sanitization.",
                "code": 400
            }

        # Step 4: Get conversation memory
        context = self.memory.get_context(session_id, n_messages=6)

        # Step 5: Generate answer using RAG
        result = self.rag.answer(clean_question, context)

        # Step 6: Save to memory
        self.memory.save_message(session_id, user_id, "user", clean_question)
        self.memory.save_message(session_id, user_id, "assistant", result["answer"])

        # Step 7: Return formatted response
        return {
            "status": "success",
            "question": clean_question,
            "answer": result["answer"],
            "sources": result["sources"],
            "confidence": result["confidence"],
            "grounded": result["grounded"],
            "requests_used": self.security.get_request_count(user_id)
        }
