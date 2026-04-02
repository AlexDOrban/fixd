"""
FixdAI Ingestion Pipeline
=========================
Loads bike repair PDFs from data/docs/, splits into chunks,
generates embeddings, and stores in ChromaDB.

Usage:
    python src/ingest.py
    python src/ingest.py --reset  # Clear existing DB and re-ingest
"""

import sys
import shutil
from pathlib import Path
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn

from langchain_community.document_loaders import PyPDFLoader, DirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from chromadb.utils.embedding_functions import DefaultEmbeddingFunction

from config import (
    DOCS_DIR,
    CHROMA_PERSIST_DIR,
    OPENAI_API_KEY,
    EMBEDDING_MODEL,
    CHUNK_SIZE,
    CHUNK_OVERLAP,
    COLLECTION_NAME,
)

console = Console()


def load_documents(docs_dir: Path) -> list:
    """Load all PDFs from the docs directory."""
    if not docs_dir.exists():
        console.print(f"[red]Error:[/red] {docs_dir} does not exist.")
        console.print("Create the directory and add bike repair PDFs first.")
        sys.exit(1)

    pdf_files = list(docs_dir.glob("*.pdf"))
    if not pdf_files:
        console.print(f"[yellow]Warning:[/yellow] No PDFs found in {docs_dir}")
        console.print("Add some bike repair manuals (Shimano, SRAM, Park Tool, etc.)")
        console.print("\nFree sources:")
        console.print("  • si.shimano.com — Dealer manuals for all groupsets")
        console.print("  • sram.com/service — SRAM/RockShox service manuals")
        console.print("  • parktool.com/blog/repair-help — Repair articles (save as PDF)")
        sys.exit(1)

    console.print(f"\n[bold]Found {len(pdf_files)} PDF(s):[/bold]")
    for f in pdf_files:
        size_mb = f.stat().st_size / (1024 * 1024)
        console.print(f"  📄 {f.name} ({size_mb:.1f} MB)")

    loader = DirectoryLoader(
        str(docs_dir),
        glob="**/*.pdf",
        loader_cls=PyPDFLoader,
        show_progress=True,
        use_multithreading=True,
    )

    with Progress(
        SpinnerColumn(),
        TextColumn("[bold blue]Loading PDFs..."),
        BarColumn(),
        transient=True,
    ) as progress:
        progress.add_task("loading", total=None)
        documents = loader.load()

    console.print(f"[green]✓[/green] Loaded {len(documents)} pages from {len(pdf_files)} PDF(s)")
    return documents


def enrich_metadata(documents: list) -> list:
    """Add useful metadata to each document chunk."""
    for doc in documents:
        source = doc.metadata.get("source", "")
        filename = Path(source).stem if source else "unknown"

        # Clean up the filename into a readable doc name
        doc_name = filename.replace("_", " ").replace("-", " ").title()
        doc.metadata["doc_name"] = doc_name
        doc.metadata["filename"] = Path(source).name if source else "unknown"

        # Page number (PyPDFLoader provides this)
        page = doc.metadata.get("page", 0)
        doc.metadata["page_label"] = f"p.{page + 1}"

    return documents


def split_documents(documents: list) -> list:
    """Split documents into chunks optimized for retrieval."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        length_function=len,
        separators=["\n\n", "\n", ". ", " ", ""],
        add_start_index=True,
    )

    chunks = splitter.split_documents(documents)
    console.print(f"[green]✓[/green] Split into {len(chunks)} chunks (size={CHUNK_SIZE}, overlap={CHUNK_OVERLAP})")
    return chunks


class _LocalEmbeddings:
    """Thin wrapper around ChromaDB's built-in all-MiniLM-L6-v2."""
    def __init__(self):
        self._ef = DefaultEmbeddingFunction()

    def embed_documents(self, texts: list) -> list:
        return self._ef(texts)

    def embed_query(self, text: str) -> list:
        return self._ef([text])[0]


def create_vector_store(chunks: list) -> Chroma:
    """Embed chunks and store in ChromaDB."""
    if EMBEDDING_MODEL == "local":
        embeddings = _LocalEmbeddings()
        model_label = "all-MiniLM-L6-v2 (local)"
    else:
        if not OPENAI_API_KEY:
            console.print("[red]Error:[/red] OPENAI_API_KEY not set in .env")
            sys.exit(1)
        embeddings = OpenAIEmbeddings(
            model=EMBEDDING_MODEL,
            openai_api_key=OPENAI_API_KEY,
        )
        model_label = EMBEDDING_MODEL

    console.print(f"\n[bold blue]Embedding {len(chunks)} chunks with {model_label}...[/bold blue]")
    console.print(f"Storing in: {CHROMA_PERSIST_DIR}")

    with Progress(
        SpinnerColumn(),
        TextColumn("[bold blue]Generating embeddings..."),
        BarColumn(),
        transient=True,
    ) as progress:
        progress.add_task("embedding", total=None)
        vector_store = Chroma.from_documents(
            documents=chunks,
            embedding=embeddings,
            collection_name=COLLECTION_NAME,
            persist_directory=CHROMA_PERSIST_DIR,
        )

    console.print(f"[green]✓[/green] Vector store created with {len(chunks)} vectors")
    return vector_store


def main():
    console.print("\n[bold]🔧 FixdAI — Document Ingestion Pipeline[/bold]\n")

    # Check for --reset flag
    if "--reset" in sys.argv and Path(CHROMA_PERSIST_DIR).exists():
        console.print("[yellow]Resetting vector store...[/yellow]")
        shutil.rmtree(CHROMA_PERSIST_DIR)
        console.print("[green]✓[/green] Old vector store deleted\n")

    # Pipeline
    documents = load_documents(DOCS_DIR)
    documents = enrich_metadata(documents)
    chunks = split_documents(documents)
    vector_store = create_vector_store(chunks)

    # Quick sanity check
    console.print("\n[bold]Sanity check — test retrieval:[/bold]")
    results = vector_store.similarity_search("brake adjustment", k=3)
    for i, doc in enumerate(results):
        source = doc.metadata.get("doc_name", "?")
        page = doc.metadata.get("page_label", "?")
        preview = doc.page_content[:120].replace("\n", " ")
        console.print(f"  [{i+1}] {source} ({page}): {preview}...")

    console.print("\n[bold green]✅ Ingestion complete![/bold green]")
    console.print(f"Run queries with: [bold]python src/query.py \"your question here\"[/bold]\n")


if __name__ == "__main__":
    main()
