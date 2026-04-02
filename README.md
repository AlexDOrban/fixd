# FixdAI — RAG-Powered Bike Repair Assistant

> Ask natural language questions about bike repair and get accurate, source-cited answers powered by real manufacturer documentation.

![Python](https://img.shields.io/badge/Python-3.11+-blue)
![LangChain](https://img.shields.io/badge/LangChain-0.2-green)
![ChromaDB](https://img.shields.io/badge/ChromaDB-vector--store-orange)
![License](https://img.shields.io/badge/License-MIT-yellow)

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                    FixdAI                            │
│                                                     │
│  ┌──────────┐    ┌───────────┐    ┌──────────────┐  │
│  │  PDFs /  │───▶│  Chunking │───▶│  ChromaDB    │  │
│  │  Manuals │    │  + Embed  │    │  Vector Store│  │
│  └──────────┘    └───────────┘    └──────┬───────┘  │
│                                          │          │
│  ┌──────────┐    ┌───────────┐    ┌──────▼───────┐  │
│  │  User    │───▶│  LangChain│───▶│  Retrieval   │  │
│  │  Query   │    │  Chain    │    │  + LLM Gen   │  │
│  └──────────┘    └───────────┘    └──────┬───────┘  │
│                                          │          │
│                               ┌──────────▼────────┐ │
│                               │  Cited Answer +   │ │
│                               │  Source Chunks    │ │
│                               └───────────────────┘ │
└─────────────────────────────────────────────────────┘
```

## What it demonstrates

- **Document ingestion**: PDF loading, recursive text splitting, metadata enrichment
- **Embeddings + vector storage**: OpenAI embeddings → ChromaDB (persistent, local)
- **RAG chain**: LangChain RetrievalQA with source citations
- **Prompt engineering**: Custom system prompt tuned for bike repair domain
- **Evaluation**: Test suite with real mechanic questions
- **API layer**: FastAPI with streaming support
- **Frontend**: Next.js chat interface with source display

## Quick start

```bash
# 1. Clone and install
git clone https://github.com/yourusername/fixdai.git
cd fixdai
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 2. Set your API key
cp .env.example .env
# Edit .env with your OpenAI key (for embeddings) and Anthropic key (for generation)

# 3. Add PDFs to data/docs/
# Drop any bike repair manuals, service guides, or tech docs here

# 4. Ingest documents
python src/ingest.py

# 5. Query
python src/query.py "How do I bleed Shimano hydraulic disc brakes?"

# 6. Run the API (optional)
python src/api.py
```

## Project structure

```
fixdai/
├── data/
│   └── docs/           # Drop PDF manuals here
├── src/
│   ├── ingest.py       # Document loading + chunking + embedding
│   ├── query.py        # CLI query interface
│   ├── chain.py        # LangChain RAG chain setup
│   ├── api.py          # FastAPI wrapper
│   └── config.py       # Shared configuration
├── tests/
│   └── test_queries.py # Evaluation with real mechanic questions
├── frontend/           # Next.js chat UI (Day 3-4)
├── requirements.txt
├── .env.example
└── README.md
```

## Tech stack

| Layer | Tech | Why |
|-------|------|-----|
| Embeddings | OpenAI `text-embedding-3-small` | Best price/performance for retrieval |
| Vector store | ChromaDB | Zero-infra, persistent, local-first |
| Orchestration | LangChain | Industry standard, shows framework fluency |
| Generation | Claude (Anthropic) | Superior instruction following for technical Q&A |
| API | FastAPI | Async, typed, auto-docs |
| Frontend | Next.js + React | Matches existing skill stack |

## Example

```
> How do I adjust rear derailleur cable tension on a Shimano Deore?

FixdAI: To adjust the cable tension on a Shimano Deore rear derailleur:

1. Shift to the smallest cog (highest gear)
2. Locate the barrel adjuster where the cable enters the derailleur
3. If shifting to larger cogs is sluggish, turn the barrel adjuster
   counter-clockwise in half-turn increments
4. If the chain is slow to drop to smaller cogs, turn clockwise
5. Test by shifting through the full range

📄 Sources:
  - Shimano Deore M6100 Dealer Manual, p.14 (chunk 47)
  - Park Tool: Rear Derailleur Adjustment (chunk 112)
```

## License

MIT
