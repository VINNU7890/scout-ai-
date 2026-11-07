from __future__ import annotations

import hashlib
import logging
import os
import re
from typing import List, Optional

import chromadb
from chromadb.api.types import Documents, EmbeddingFunction, Embeddings
from pydantic import BaseModel

from backend.app.config import get_settings

logger = logging.getLogger("scoutai.tools.rag")
settings = get_settings()


class DocumentChunk(BaseModel):
    chunk_id: str
    doc_id: str
    doc_name: str
    page: int
    content: str


class SimpleEmbeddingFunction(EmbeddingFunction):
    """
    Fallback deterministic embedding function when Gemini API key is missing or in tests,
    ensuring vector operations succeed without crashing.
    """

    def __init__(self) -> None:
        pass

    def name(self) -> str:
        return "simple_deterministic_embedding"

    def __call__(self, input: Documents) -> Embeddings:
        embeddings: Embeddings = []
        for text in input:
            # Deterministic pseudo-embedding from hash
            h = hashlib.sha256(text.encode("utf-8")).digest()
            vec = [(b / 255.0) * 2.0 - 1.0 for b in h[:32]]  # 32 dims
            norm = sum(x * x for x in vec) ** 0.5 or 1.0
            embeddings.append([x / norm for x in vec])
        return embeddings


class GeminiEmbeddingFunction(EmbeddingFunction):
    """Embeddings using Google Gemini API."""

    def __init__(self, api_key: str, model_name: str) -> None:
        self.api_key = api_key
        self.model_name = model_name
        from langchain_google_genai import GoogleGenerativeAIEmbeddings

        self._embedder = GoogleGenerativeAIEmbeddings(
            model=model_name,
            google_api_key=api_key,
        )

    def __call__(self, input: Documents) -> Embeddings:
        try:
            return self._embedder.embed_documents(input)
        except Exception as e:
            logger.warning(f"Gemini embeddings failed ({e}), using fallback embedding")
            fallback = SimpleEmbeddingFunction()
            return fallback(input)


def get_embedding_function() -> EmbeddingFunction:
    gemini_key = settings.effective_gemini_key
    if gemini_key and not settings.DEMO_MODE:
        try:
            return GeminiEmbeddingFunction(
                api_key=gemini_key, model_name=settings.GEMINI_EMBED_MODEL
            )
        except Exception as e:
            logger.warning(f"Could not initialize Gemini embeddings ({e}), using fallback")
    return SimpleEmbeddingFunction()


class DocumentParser:
    """Parses PDF, DOCX, TXT, and Markdown files into DocumentChunks."""

    @staticmethod
    def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 150) -> List[str]:
        chunks: List[str] = []
        cleaned = re.sub(r"\r\n|\r", "\n", text).strip()
        if not cleaned:
            return chunks

        start = 0
        while start < len(cleaned):
            end = start + chunk_size
            chunk = cleaned[start:end].strip()
            if chunk:
                chunks.append(chunk)
            start += chunk_size - overlap
            if start >= len(cleaned):
                break
        return chunks

    @classmethod
    def parse_file(cls, file_path: str, doc_id: str, filename: str) -> List[DocumentChunk]:
        ext = os.path.splitext(filename)[1].lower()
        chunks: List[DocumentChunk] = []

        if ext == ".pdf":
            from pypdf import PdfReader

            reader = PdfReader(file_path)
            for page_idx, page in enumerate(reader.pages, start=1):
                page_text = page.extract_text() or ""
                page_chunks = cls.chunk_text(page_text)
                for c_idx, c_text in enumerate(page_chunks):
                    chunks.append(
                        DocumentChunk(
                            chunk_id=f"{doc_id}_p{page_idx}_c{c_idx}",
                            doc_id=doc_id,
                            doc_name=filename,
                            page=page_idx,
                            content=c_text,
                        )
                    )

        elif ext in (".docx", ".doc"):
            from docx import Document

            doc = Document(file_path)
            full_text = "\n\n".join(p.text for p in doc.paragraphs if p.text.strip())
            file_chunks = cls.chunk_text(full_text)
            for c_idx, c_text in enumerate(file_chunks):
                chunks.append(
                    DocumentChunk(
                        chunk_id=f"{doc_id}_c{c_idx}",
                        doc_id=doc_id,
                        doc_name=filename,
                        page=1,
                        content=c_text,
                    )
                )

        else:
            # Plain text or Markdown
            with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()
            file_chunks = cls.chunk_text(content)
            for c_idx, c_text in enumerate(file_chunks):
                chunks.append(
                    DocumentChunk(
                        chunk_id=f"{doc_id}_c{c_idx}",
                        doc_id=doc_id,
                        doc_name=filename,
                        page=1,
                        content=c_text,
                    )
                )

        return chunks


class RagVectorStore:
    """Manages ChromaDB vector collections for document indexing and retrieval."""

    def __init__(self, storage_dir: Optional[str] = None) -> None:
        self.storage_dir = storage_dir or settings.effective_chroma_dir
        os.makedirs(self.storage_dir, exist_ok=True)
        self.client = chromadb.PersistentClient(path=self.storage_dir)

    def get_or_create_collection(self, collection_name: str) -> chromadb.Collection:
        # Chroma collection names must be 3-63 chars alphanumeric
        safe_name = re.sub(r"[^a-zA-Z0-9_-]", "_", collection_name)[:63]
        if len(safe_name) < 3:
            safe_name = f"col_{safe_name}"
        return self.client.get_or_create_collection(
            name=safe_name,
            embedding_function=get_embedding_function(),
        )

    def ingest_chunks(self, collection_name: str, chunks: List[DocumentChunk]) -> None:
        if not chunks:
            return
        collection = self.get_or_create_collection(collection_name)
        collection.upsert(
            ids=[c.chunk_id for c in chunks],
            documents=[c.content for c in chunks],
            metadatas=[
                {"doc_id": c.doc_id, "doc_name": c.doc_name, "page": c.page} for c in chunks
            ],
        )

    def query(self, collection_name: str, query_text: str, top_k: int = 4) -> List[DocumentChunk]:
        try:
            collection = self.get_or_create_collection(collection_name)
            count = collection.count()
            if count == 0:
                return []
            k = min(top_k, count)
            results = collection.query(
                query_texts=[query_text],
                n_results=k,
            )
            chunks: List[DocumentChunk] = []
            if results and results.get("documents") and results["documents"][0]:
                docs = results["documents"][0]
                ids = results["ids"][0]
                metas = results["metadatas"][0]
                for doc_id, doc_text, meta in zip(ids, docs, metas):
                    chunks.append(
                        DocumentChunk(
                            chunk_id=doc_id,
                            doc_id=meta.get("doc_id", ""),
                            doc_name=meta.get("doc_name", "Document"),
                            page=int(meta.get("page", 1)),
                            content=doc_text,
                        )
                    )
            return chunks
        except Exception as e:
            logger.warning(f"Chroma query failed ({e}): returning empty chunks")
            return []

    def delete_collection(self, collection_name: str) -> None:
        safe_name = re.sub(r"[^a-zA-Z0-9_-]", "_", collection_name)[:63]
        try:
            self.client.delete_collection(name=safe_name)
        except Exception:
            pass


_global_rag_store: Optional[RagVectorStore] = None


def get_rag_store() -> RagVectorStore:
    global _global_rag_store
    if _global_rag_store is None:
        _global_rag_store = RagVectorStore()
    return _global_rag_store
