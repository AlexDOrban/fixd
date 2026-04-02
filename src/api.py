"""
FixdAI API
==========
FastAPI wrapper around the RAG chain.

Usage:
    python src/api.py
    # Then: curl http://localhost:8000/query -X POST -H "Content-Type: application/json" \
    #       -d '{"question": "How do I true a wheel?"}'

Docs: http://localhost:8000/docs
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn

from chain import build_chain, query_with_sources

# Global chain instance — loaded once at startup
_chain = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load the chain on startup."""
    global _chain
    print("🔧 Loading FixdAI chain...")
    _chain = build_chain()
    print("✅ FixdAI ready")
    yield
    print("👋 Shutting down")


app = FastAPI(
    title="FixdAI",
    description="RAG-powered bike repair assistant",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS — allow the Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Models ---

class QueryRequest(BaseModel):
    question: str = Field(..., min_length=3, max_length=500, examples=["How do I bleed Shimano brakes?"])


class Source(BaseModel):
    doc_name: str
    page: str
    content: str


class QueryResponse(BaseModel):
    answer: str
    sources: list[Source]
    question: str


# --- Routes ---

@app.get("/health")
async def health():
    return {"status": "ok", "chain_loaded": _chain is not None}


@app.post("/query", response_model=QueryResponse)
async def query(req: QueryRequest):
    """Ask a bike repair question and get a source-cited answer."""
    if _chain is None:
        raise HTTPException(status_code=503, detail="Chain not loaded yet")

    try:
        result = query_with_sources(req.question, _chain)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")

    return QueryResponse(
        answer=result["answer"],
        sources=[Source(**s) for s in result["sources"]],
        question=req.question,
    )


if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
