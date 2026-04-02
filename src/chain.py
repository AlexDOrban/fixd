"""
FixdAI RAG Chain
================
Sets up the LangChain retrieval chain with:
- ChromaDB retriever
- Claude LLM for generation
- Custom prompt with source citation instructions
"""

from langchain_anthropic import ChatAnthropic
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableParallel, RunnableLambda
from chromadb.utils.embedding_functions import DefaultEmbeddingFunction

from config import (
    CHROMA_PERSIST_DIR,
    ANTHROPIC_API_KEY,
    OPENAI_API_KEY,
    EMBEDDING_MODEL,
    LLM_MODEL,
    LLM_TEMPERATURE,
    LLM_MAX_TOKENS,
    COLLECTION_NAME,
    TOP_K,
    SYSTEM_PROMPT,
)


class _LocalEmbeddings:
    """Thin wrapper around ChromaDB's built-in all-MiniLM-L6-v2."""
    def __init__(self):
        self._ef = DefaultEmbeddingFunction()

    def embed_documents(self, texts: list) -> list:
        return self._ef(texts)

    def embed_query(self, text: str) -> list:
        return self._ef([text])[0]


def get_vector_store() -> Chroma:
    """Load the existing ChromaDB vector store."""
    if EMBEDDING_MODEL == "local":
        embeddings = _LocalEmbeddings()
    else:
        from langchain_openai import OpenAIEmbeddings
        embeddings = OpenAIEmbeddings(
            model=EMBEDDING_MODEL,
            openai_api_key=OPENAI_API_KEY,
        )
    return Chroma(
        collection_name=COLLECTION_NAME,
        persist_directory=CHROMA_PERSIST_DIR,
        embedding_function=embeddings,
    )


def get_retriever(vector_store: Chroma = None, top_k: int = TOP_K):
    """Create a retriever from the vector store."""
    if vector_store is None:
        vector_store = get_vector_store()
    return vector_store.as_retriever(
        search_type="similarity",
        search_kwargs={"k": top_k},
    )


def get_llm() -> ChatAnthropic:
    """Initialize the Claude LLM."""
    return ChatAnthropic(
        model=LLM_MODEL,
        anthropic_api_key=ANTHROPIC_API_KEY,
        temperature=LLM_TEMPERATURE,
        max_tokens=LLM_MAX_TOKENS,
    )


def get_prompt() -> ChatPromptTemplate:
    """Build the RAG prompt template."""
    return ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        ("human", "{question}"),
    ])


def build_chain():
    """Assemble the full RAG chain using LCEL."""
    vector_store = get_vector_store()
    retriever = get_retriever(vector_store)
    llm = get_llm()
    prompt = get_prompt()

    generate = (
        RunnableLambda(lambda x: {
            "context": "\n\n".join(d.page_content for d in x["source_documents"]),
            "question": x["question"],
        })
        | prompt
        | llm
        | StrOutputParser()
    )

    chain = RunnableParallel(
        source_documents=retriever,
        question=RunnablePassthrough(),
    ).assign(result=generate)

    return chain


def query_with_sources(question: str, chain=None) -> dict:
    """
    Run a query and return the answer + source documents.

    Returns:
        {
            "answer": str,
            "sources": [
                {"content": str, "doc_name": str, "page": str, "filename": str},
                ...
            ]
        }
    """
    if chain is None:
        chain = build_chain()

    result = chain.invoke(question)

    sources = []
    seen = set()
    for doc in result.get("source_documents", []):
        doc_name = doc.metadata.get("doc_name", "Unknown")
        page = doc.metadata.get("page_label", "?")
        filename = doc.metadata.get("filename", "?")
        key = f"{filename}:{page}"

        if key not in seen:
            seen.add(key)
            sources.append({
                "content": doc.page_content[:300],
                "doc_name": doc_name,
                "page": page,
                "filename": filename,
            })

    return {
        "answer": result["result"],
        "sources": sources,
    }
