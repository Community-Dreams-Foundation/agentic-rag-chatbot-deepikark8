# Architecture Overview

## Goal
Provide a brief, readable overview of how your chatbot works:
- ingestion
- indexing
- retrieval + grounding with citations
- memory writing
- optional safe tool execution

Keep this short (1–2 pages).

---

## High-Level Flow

### 1) Ingestion (Upload → Parse → Chunk)
- Supported inputs:
- Parsing approach:
- Chunking strategy:
- Metadata captured per chunk (recommended):
  - source — original filename
  - page — page or sheet number (where available)
  - type — file format (pdf, docx, xlsx, etc.)

### 2) Indexing / Storage
- Vector store choice (Chroma):
- Persistence:
- Optional lexical index (BM25):

### 3) Retrieval + Grounded Answering
- Retrieval method:** Top-3 similarity search using cosine distance against ChromaDB; top 2 chunks passed to LLM for speed
- LLM: Llama 3.2 via Ollama — runs fully locally
- How citations are built:
  - Each source includes: filename, file type, and page number (if available)
  - Sources are attached to every response so answers are fully traceable
- Failure behavior:**
  - If no results are returned, responds with "No information available"
  - If retrieved chunks are from wrong documents (low relevance), LLM states the information is not present

### 4) Memory System (Selective)
- What counts as “high-signal” memory:
- What you explicitly do NOT store (PII/secrets/raw transcript):
- How you decide when to write:
- Format written to:
  - `USER_MEMORY.md`
  - `COMPANY_MEMORY.md`

### 5) Security Layer
- Authentication: Each user receives a unique SHA-256 token on registration; every request verifies the token before processing
- Input sanitization: Strips SQL keywords and dangerous characters to prevent prompt injection and SQL injection attacks
- Rate limiting: Max 100 requests per hour per user to prevent abuse
- Safety boundaries:
  - No external network calls (fully local stack)
  - No file system access outside defined document and memory paths
---

## Tradeoffs & Next Steps
- Why this design?
  Each of the four components (RAG Engine, Memory System, Security Layer, Chatbot Orchestrator) has a single responsibility, making them independently testable and swappable. Using local models (HuggingFace + Ollama) means zero API costs and no data leaving the machine.
- What you would improve with more time:
  Add chunk-level source highlighting so users can see exactly which sentence the answer came from
  Support document re-indexing without full DB rebuild (incremental updates)
 Upgrade to a reranker model (e.g. cross-encoder) for more accurate top-k selection
