from __future__ import annotations

from typing import List

from fastapi import APIRouter, File, HTTPException, UploadFile, status

from backend.app.schemas import DocumentUploadResponse
from backend.app.services.doc_service import DocumentService

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("", response_model=DocumentUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(file: UploadFile = File(...)) -> DocumentUploadResponse:
    return await DocumentService.upload_document(file)


@router.get("", response_model=List[DocumentUploadResponse])
def list_documents() -> List[DocumentUploadResponse]:
    return DocumentService.list_documents()


@router.delete("/{doc_id}", response_model=dict)
def delete_document(doc_id: str) -> dict:
    deleted = DocumentService.delete_document(doc_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "not_found", "message": f"Document '{doc_id}' not found."}},
        )
    return {"deleted": True, "id": doc_id}
