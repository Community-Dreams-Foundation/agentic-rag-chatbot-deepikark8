"""
Main Entry Point - Run this to start the chatbot
"""
import uuid
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.chatbot import AgenticRAGChatbot


def run_chatbot():
    """Start the interactive chatbot"""

    # Initialize chatbot
    bot = AgenticRAGChatbot()

    # Welcome message
    print("\n" + "="*70)
    print("🤖  AGENTIC RAG CHATBOT")
    print("="*70)
    print("Features:")
    print("  ✅ Data Grounding    - Every answer cites its source")
    print("  ✅ Long-term Memory  - Remembers your conversation")
    print("  ✅ Secure            - Auth + sanitization + rate limiting")
    print("  ✅ 100% Free         - Runs locally on your machine")
    print("="*70)
    print("\nCommands:")
    print("  'quit'     - Exit chatbot")
    print("  'history'  - Show conversation history")
    print("  'sessions' - Show all past sessions")
    print("  'clear'    - Start new session")
    print("="*70 + "\n")

    # Get user info
    username = input("Enter your name: ").strip()
    if not username:
        username = "user"

    # Register user and create session
    token = bot.register_user(username)
    session_id = str(uuid.uuid4())[:8]

    print(f"\n✅ Welcome {username}!")
    print(f"Session ID: {session_id}")
    print(f"Type your questions below...\n")

    # Main chat loop
    while True:
        try:
            user_input = input(f"{username}: ").strip()

            # Handle commands
            if not user_input:
                continue

            if user_input.lower() == "quit":
                print("\nGoodbye! 👋\n")
                break

            if user_input.lower() == "history":
                context = bot.memory.get_context(session_id, n_messages=10)
                print("\n📜 Conversation History:")
                print(context if context else "No history yet")
                print()
                continue

            if user_input.lower() == "sessions":
                sessions = bot.memory.get_all_sessions()
                print(f"\n📁 All Sessions ({len(sessions)} total):")
                for s in sessions:
                    print(f"  - {s['session_id']} | {s['user_id']} | {s['message_count']} messages")
                print()
                continue

            if user_input.lower() == "clear":
                session_id = str(uuid.uuid4())[:8]
                print(f"\n✅ New session started: {session_id}\n")
                continue

            # Process question
            print("\n🔍 Searching documents...")
            result = bot.chat(user_input, session_id, username, token)

            # Display result
            if result["status"] == "error":
                print(f"\n❌ Error: {result['error']}\n")
                continue

            # Show answer
            print(f"\n🤖 Answer:")
            print(f"{result['answer']}")

            # Show confidence
            confidence = result["confidence"]
            if confidence >= 0.7:
                conf_label = "🟢 High"
            elif confidence >= 0.4:
                conf_label = "🟡 Medium"
            else:
                conf_label = "🔴 Low"

            print(f"\n📊 Confidence: {conf_label} ({confidence:.0%})")

            # Show sources
            if result["sources"]:
                print(f"\n📚 Sources:")
                for i, src in enumerate(result["sources"], 1):
                    print(f"  {i}. {src['file']} | Page {src['page']} | {src['confidence']:.0%} match")

            # Show request count
            print(f"\n💬 Requests this hour: {result['requests_used']}/100")
            print("-"*70 + "\n")

        except KeyboardInterrupt:
            print("\n\nGoodbye! 👋\n")
            break
        except Exception as e:
            print(f"\n❌ Unexpected error: {e}\n")


if __name__ == "__main__":
    run_chatbot()
