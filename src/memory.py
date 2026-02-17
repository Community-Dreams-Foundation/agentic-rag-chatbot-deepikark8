"""
Memory System - Manages conversation history
Handles: saving messages, loading history, context retrieval
"""
import os
import json
from datetime import datetime


class MemorySystem:
    """
    Long-term memory that:
    1. Saves every conversation to disk
    2. Loads past conversations
    3. Provides recent context for better answers
    4. Tracks all user sessions
    """

    def __init__(self, storage_path="./memory_store"):
        self.storage_path = storage_path
        os.makedirs(storage_path, exist_ok=True)

    def save_message(self, session_id, user_id, role, content):
        """Save a single message to conversation history"""
        filepath = os.path.join(self.storage_path, f"{session_id}.json")

        # Load existing conversation
        conversation = self._load_raw(session_id) or {
            "session_id": session_id,
            "user_id": user_id,
            "created_at": datetime.utcnow().isoformat(),
            "messages": []
        }

        # Add new message
        conversation["messages"].append({
            "role": role,
            "content": content,
            "timestamp": datetime.utcnow().isoformat()
        })
        conversation["updated_at"] = datetime.utcnow().isoformat()

        # Save back to disk
        with open(filepath, "w") as f:
            json.dump(conversation, f, indent=2)

    def get_context(self, session_id, n_messages=6):
        """Get recent conversation as formatted string"""
        conversation = self._load_raw(session_id)

        if not conversation:
            return ""

        messages = conversation.get("messages", [])
        recent = messages[-n_messages:]

        lines = []
        for msg in recent:
            role = msg.get("role", "unknown").capitalize()
            content = msg.get("content", "")
            lines.append(f"{role}: {content}")

        return "\n".join(lines)

    def get_all_sessions(self):
        """Get list of all conversation sessions"""
        sessions = []
        for filename in os.listdir(self.storage_path):
            if filename.endswith(".json"):
                session_id = filename.replace(".json", "")
                conv = self._load_raw(session_id)
                if conv:
                    sessions.append({
                        "session_id": session_id,
                        "user_id": conv.get("user_id"),
                        "message_count": len(conv.get("messages", [])),
                        "updated_at": conv.get("updated_at")
                    })
        return sessions

    def _load_raw(self, session_id):
        """Load raw conversation data from disk"""
        filepath = os.path.join(self.storage_path, f"{session_id}.json")

        if not os.path.exists(filepath):
            return None

        with open(filepath, "r") as f:
            return json.load(f)
