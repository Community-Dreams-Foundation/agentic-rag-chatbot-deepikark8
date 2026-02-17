#!/usr/bin/env python3
import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.chatbot import AgenticRAGChatbot

print("Initializing chatbot...")
bot = AgenticRAGChatbot()

user_id = "sanity_test_user"
token = bot.register_user(user_id)
session_id = "sanity_session"

test_queries = [
    "What is the company revenue?",
    "Who is the CEO?",
    "How many employees?"
]

results = []

for query in test_queries:
    print(f"Testing: {query}")
    result = bot.chat(query, session_id, user_id, token)
    
    if result["status"] == "success":
        results.append({
            "query": query,
            "answer": result["answer"],
            "sources": result["sources"],
            "confidence": result["confidence"],
            "grounded": result["grounded"]
        })

output = {
    "status": "success",
    "test_queries": len(test_queries),
    "successful_responses": len(results),
    "results": results,
    "memory_files": {
        "user_memory": os.path.exists("memory_store/USER_MEMORY.md"),
        "company_memory": os.path.exists("memory_store/COMPANY_MEMORY.md")
    }
}

with open("artifacts/sanity_output.json", "w") as f:
    json.dump(output, f, indent=2)

print(f"\nSanity check complete!")
print(f"Generated: artifacts/sanity_output.json")
print(f"Successful responses: {len(results)}/{len(test_queries)}")
