"""
Document management routes: multi-PDF upload, metadata listing, chunk inspection, and deletion.
Fully compatible with both React UI and PRD /v1 specification.
"""

import hashlib
from uuid import uuid4
from pathlib import Path
from typing import List, Annotated
from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks, status
from fastapi.responses import FileResponse, HTMLResponse
from pydantic import WithJsonSchema

from app.config import settings
from app.core.security import validate_pdf_content
from app.ingestion.validator import validate_uploaded_pdf
from app.ingestion.parser import parse_pdf_document
from app.ingestion.chunker import chunk_academic_pages
from app.db.database import (
    find_document_by_hash,
    save_document_and_chunks,
    get_all_documents,
    get_document,
    get_document_chunks,
    delete_document,
    create_job,
    update_job
)
from app.retrieval.qdrant_store import vector_store
from app.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(tags=["Documents"])

PDFUploadType = Annotated[UploadFile, WithJsonSchema({"type": "string", "format": "binary"})]


@router.post("/v1/documents", status_code=status.HTTP_202_ACCEPTED)
@router.post("/upload-pdf")
async def upload_documents(
    files: List[PDFUploadType] = File(...),
    background_tasks: BackgroundTasks = None
):
    """
    Upload one or multiple research paper PDFs.
    Performs SHA-256 deduplication, %PDF- magic-byte validation, PyMuPDF layout parsing,
    table-caption binding, reference exclusion, and SQLite + vector storage.
    """
    if not files:
        raise HTTPException(status_code=400, detail="Please upload at least one PDF file.")

    processed_docs = []
    duplicate_docs = []
    failed_docs = []

    for file in files:
        raw_name = (file.filename or "uploaded.pdf").replace("\\", "/").split("/")[-1]
        try:
            pdf_bytes = await file.read(settings.max_file_size_bytes + 1)

            # 1. Validation (magic bytes + size)
            is_valid, error_msg = validate_uploaded_pdf(raw_name, pdf_bytes)
            if not is_valid:
                failed_docs.append({"filename": raw_name, "error": error_msg})
                continue

            # 2. SHA-256 Deduplication check
            file_hash = hashlib.sha256(pdf_bytes).hexdigest()
            existing = find_document_by_hash(file_hash)
            if existing:
                duplicate_docs.append({
                    "filename": raw_name,
                    "duplicate_of": {
                        "document_id": existing["document_id"],
                        "filename": existing["filename"]
                    }
                })
                continue

            # 3. Layout parsing & section detection
            try:
                parsed_data = parse_pdf_document(pdf_bytes, max_pages=settings.max_pdf_pages)
                pages = parsed_data["pages"]
            except Exception as parse_err:
                failed_docs.append({"filename": raw_name, "error": f"Parsing failed: {parse_err}"})
                continue

            # 4. Semantic chunking with table retention and reference filtering
            chunks = chunk_academic_pages(pages, raw_name, chunk_size=250, overlap=40)
            document_id = uuid4().hex

            for chunk in chunks:
                chunk["document_id"] = document_id

            # 5. Persist original PDF file
            stored_filename = f"{document_id}.pdf"
            file_path = settings.upload_dir / stored_filename
            try:
                file_path.write_bytes(pdf_bytes)
            except OSError as io_err:
                failed_docs.append({"filename": raw_name, "error": f"Disk write failed: {io_err}"})
                continue

            doc_meta = {
                "document_id": document_id,
                "filename": raw_name,
                "stored_path": file_path.relative_to(settings.data_dir.parent).as_posix(),
                "sha256": file_hash,
                "total_pages": len(pages),
                "total_chunks": len(chunks)
            }

            # 6. Save in SQLite
            save_document_and_chunks(doc_meta, chunks)

            # 7. Asynchronously or synchronously index embeddings into vector store
            try:
                from modules.embeddings import EmbeddingGenerator
                embedder = EmbeddingGenerator()
                texts = [c["text"] for c in chunks if c.get("text")]
                if texts:
                    vecs = embedder.generate_embeddings(texts)
                    vector_store.upsert_chunks(document_id, chunks, vecs)
            except Exception as embed_err:
                logger.warning("Vector index generation warning: %s", embed_err)

            processed_docs.append({
                "document_id": document_id,
                "filename": raw_name,
                "stored_file": doc_meta["stored_path"],
                "total_pages": len(pages),
                "total_chunks": len(chunks),
                "message": "PDF processed and indexed successfully."
            })

        finally:
            await file.close()

    if not processed_docs and not duplicate_docs:
        raise HTTPException(
            status_code=400,
            detail={"message": "No valid PDFs could be processed.", "failed_documents": failed_docs}
        )

    return {
        "status": "success" if not failed_docs else "partial_success",
        "total_files_received": len(files),
        "processed_files": len(processed_docs),
        "duplicate_files": len(duplicate_docs),
        "failed_files": len(failed_docs),
        "documents": processed_docs,
        "duplicate_documents": duplicate_docs,
        "failed_documents": failed_docs
    }


@router.get("/v1/documents")
@router.get("/documents")
def list_documents():
    """List all stored research documents."""
    docs = get_all_documents()
    return {
        "status": "success",
        "total_documents": len(docs),
        "documents": [
            {
                **d,
                "chunks_url": f"/documents/{d['document_id']}/chunks",
                "download_url": f"/documents/{d['document_id']}/download"
            }
            for d in docs
        ]
    }


@router.get("/v1/documents/{document_id}")
@router.get("/documents/{document_id}")
def get_document_details(document_id: str):
    """Get metadata for a specific document."""
    doc = get_document(document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")
    return {"status": "success", "document": doc}


@router.get("/v1/documents/{document_id}/chunks")
@router.get("/documents/{document_id}/chunks")
def get_chunks(document_id: str):
    """Retrieve all extracted text chunks for a document."""
    doc = get_document(document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")
    chunks = get_document_chunks(document_id)
    return {
        "status": "success",
        "document_id": document_id,
        "filename": doc["filename"],
        "total_chunks": len(chunks),
        "chunks": chunks
    }


@router.get("/v1/documents/{document_id}/download")
@router.get("/documents/{document_id}/download")
def download_pdf(document_id: str):
    """Download the original PDF file."""
    doc = get_document(document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")

    file_path = (settings.data_dir.parent / doc["stored_path"]).resolve()
    if not file_path.is_file():
        raise HTTPException(status_code=404, detail="PDF file not found on disk.")

    return FileResponse(
        path=file_path,
        media_type="application/pdf",
        filename=doc["filename"]
    )


@router.delete("/v1/documents/{document_id}")
@router.delete("/documents/{document_id}")
def remove_document(document_id: str):
    """Delete document, its chunks, and disk file."""
    doc = get_document(document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")

    file_path = (settings.data_dir.parent / doc["stored_path"]).resolve()
    deleted = delete_document(document_id)

    file_deleted = False
    if file_path.is_file():
        try:
            file_path.unlink()
            file_deleted = True
        except OSError:
            pass

    return {
        "status": "success",
        "message": "Document deleted successfully.",
        "document_id": document_id,
        "filename": doc["filename"],
        "file_deleted": file_deleted
    }

