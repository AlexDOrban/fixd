"""FixdAI configuration — loads env vars and defines shared constants."""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Paths
PROJECT_ROOT = Path(__file__).parent.parent
DOCS_DIR = PROJECT_ROOT / "data" / "docs"
CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", str(PROJECT_ROOT / "data" / "chroma_db"))

# API keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

# Embedding model
EMBEDDING_MODEL = "local"  # "local" uses ChromaDB's built-in all-MiniLM-L6-v2 (no API key needed)

# LLM
LLM_MODEL = "claude-sonnet-4-20250514"
LLM_TEMPERATURE = 0.2
LLM_MAX_TOKENS = 1024

# Chunking
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "1000"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "200"))

# Retrieval
TOP_K = 5  # Number of chunks to retrieve

# ChromaDB collection name
COLLECTION_NAME = "fixdai_bike_repair"

# System prompt for the RAG chain
SYSTEM_PROMPT = """You are FixdAI, an expert bike repair assistant built by Alexandru Orban.
You answer questions about bicycle maintenance, repair, and troubleshooting
using ONLY the provided context from manufacturer manuals and repair guides.

Rules:
1. Answer based strictly on the provided context. If the context doesn't contain
   the answer, say so honestly — don't guess or hallucinate.
2. Cite your sources: reference the document name and section when possible.
3. Give step-by-step instructions when the question is about a procedure.
4. Include torque specs, part numbers, or tool requirements when available.
5. If a procedure has safety implications (e.g., brake work, headset preload),
   include a brief safety note.
6. Keep answers practical and mechanic-friendly — no fluff.

Context:
{context}
"""
