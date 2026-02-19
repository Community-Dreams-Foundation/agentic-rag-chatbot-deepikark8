# 🤖 Agentic RAG Chatbot

**Author**: Deepika Rajakumar  
**GitHub**: deepikark8

Built for CDF Agentic RAG Hackathon Challenge (Feb 2026)

## ✨ Features

- ✅ **File-grounded Q&A with citations**
- ✅ **Durable markdown memory** (USER_MEMORY.md + COMPANY_MEMORY.md)
- ✅ **Security layer** (auth, sanitization, rate limiting)
- ✅ **100% FREE** (runs locally with Ollama)

## 🚀 Quick Start
```bash

# 🤖 Agentic RAG Chatbot

**Author**: Deepika Rajakumar  
**GitHub**: deepikark8

Built for CDF Agentic RAG Hackathon Challenge (Feb 2026)

## ✨ Features

- ✅ **File-grounded Q&A with citations**
- ✅ **Durable markdown memory** (USER_MEMORY.md + COMPANY_MEMORY.md)
- ✅ **Security layer** (auth, sanitization, rate limiting)
- ✅ **100% FREE** (runs locally with Ollama)

## 🚀 Quick Start
```bash
# Install dependencies
pip install -r requirements.txt

# Download AI model
ollama pull llama3.2

# Run chatbot
python run.py
```

**Or use Makefile:**
```bash
make install
make run
make sanity  # Run tests
```

## 📹 Video Walkthrough

https://drive.google.com/file/d/1BRnYspMZEDJJbQBuXprQxdJxjyciM9Eg/view?usp=drive_link

## 🏗️ Architecture

See [ARCHITECTURE.md](ARCHITECTURE.md)

**Components:**
- `src/rag_engine.py` - Document loading, search, answer generation
- `src/memory.py` - Markdown-based memory
- `src/security.py` - Auth, sanitization, rate limiting
- `src/chatbot.py` - Main orchestrator
- `src/main.py` - CLI interface

## 🧪 Testing
```bash
make sanity
```

Produces: `artifacts/sanity_output.json`

## 📊 Tech Stack

- Ollama + Llama3.2 (FREE local LLM)
- ChromaDB (vector database)
- HuggingFace embeddings (FREE)
- LangChain framework
- Python 3


