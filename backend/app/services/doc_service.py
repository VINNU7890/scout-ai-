from __future__ import annotations

import os
import uuid
from typing import List

from fastapi import HTTPException, UploadFile, status
from sqlalchemy import delete, select

from backend.app.config import get_settings
from backend.app.db import SessionLocal
from backend.app.models import UploadedDocument
from backend.app.schemas import DocumentUploadResponse
from backend.app.tools.rag import DocumentParser, get_rag_store

settings = get_settings()

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".doc", ".txt", ".md"}
MAX_FILE_SIZE_BYTES = 20 * 1024 * 1024  # 20 MB


class DocumentService:
    @staticmethod
    async def upload_document(file: UploadFile) -> DocumentUploadResponse:
        filename = os.path.basename(file.filename or "uploaded_file")
        ext = os.path.splitext(filename)[1].lower()

        if ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": {
                        "code": "invalid_file_type",
                        "message": f"File extension '{ext}' is not supported. Allowed: pdf, docx, txt, md.",
                    }
                },
            )

        os.makedirs(settings.effective_upload_dir, exist_ok=True)
        doc_id = str(uuid.uuid4())
        stored_filename = f"{doc_id}{ext}"
        storage_path = os.path.join(settings.effective_upload_dir, stored_filename)

        content = await file.read()
        if len(content) > MAX_FILE_SIZE_BYTES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": {
                        "code": "file_too_large",
                        "message": "File exceeds maximum size of 20 MB.",
                    }
                },
            )

        with open(storage_path, "wb") as f:
            f.write(content)

        # Parse file into chunks
        try:
            chunks = DocumentParser.parse_file(storage_path, doc_id=doc_id, filename=filename)
        except Exception as e:
            if os.path.exists(storage_path):
                os.remove(storage_path)
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={
                    "error": {"code": "parsing_failed", "message": f"Could not parse document: {e}"}
                },
            )

        # Index in ChromaDB collection
        rag_store = get_rag_store()
        rag_store.ingest_chunks(collection_name=doc_id, chunks=chunks)

        with SessionLocal() as db:
            doc_record = UploadedDocument(
                id=doc_id,
                filename=filename,
                stored_filename=stored_filename,
                file_type=ext,
                file_size_bytes=len(content),
                chunk_count=len(chunks),
            )
            db.add(doc_record)
            db.commit()
            db.refresh(doc_record)

            return DocumentUploadResponse(
                id=doc_record.id,
                filename=doc_record.filename,
                file_type=doc_record.file_type,
                file_size_bytes=doc_record.file_size_bytes,
                chunk_count=doc_record.chunk_count,
                created_at=doc_record.created_at.isoformat(),
            )

    @staticmethod
    def list_documents() -> List[DocumentUploadResponse]:
        with SessionLocal() as db:
            records = db.scalars(
                select(UploadedDocument).order_by(UploadedDocument.created_at.desc())
            ).all()
            return [
                DocumentUploadResponse(
                    id=r.id,
                    filename=r.filename,
                    file_type=r.file_type,
                    file_size_bytes=r.file_size_bytes,
                    chunk_count=r.chunk_count,
                    created_at=r.created_at.isoformat(),
                )
                for r in records
            ]

    @staticmethod
    def delete_document(doc_id: str) -> bool:
        with SessionLocal() as db:
            record = db.scalar(select(UploadedDocument).where(UploadedDocument.id == doc_id))
            if not record:
                return False

            file_path = os.path.join(settings.effective_upload_dir, record.stored_filename)
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except Exception:
                    pass

            db.execute(delete(UploadedDocument).where(UploadedDocument.id == doc_id))
            db.commit()

        # Delete vector collection
        rag_store = get_rag_store()
        rag_store.delete_collection(doc_id)
        return True
