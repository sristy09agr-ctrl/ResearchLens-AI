from fastapi.responses import HTMLResponse, FileResponse
import hashlib
from pathlib import Path
from uuid import uuid4
from typing import Annotated

from fastapi import (
    FastAPI,
    UploadFile as FastAPIUploadFile,
    File,
    HTTPException
)

from pydantic import WithJsonSchema

from modules.document_processor import extract_text_from_pdf
from modules.chunking import chunk_pages

from modules.database import (
    initialize_database,
    find_document_by_hash,
    save_document_and_chunks,
    get_all_documents,
    get_document,
    get_document_chunks,
    delete_document
)




# --------------------------------------------------
# SWAGGER FILE UPLOAD TYPE
# --------------------------------------------------

PDFUpload = Annotated[
    FastAPIUploadFile,
    WithJsonSchema({
        "type": "string",
        "format": "binary"
    })
]


# --------------------------------------------------
# PROJECT DIRECTORIES
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

UPLOAD_DIR = BASE_DIR / "data" / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


# --------------------------------------------------
# UPLOAD CONFIGURATION
# --------------------------------------------------

MAX_FILE_SIZE = 20 * 1024 * 1024  # 20 MB per PDF


# --------------------------------------------------
# FASTAPI APPLICATION
# --------------------------------------------------

app = FastAPI(
    title="ResearchLens AI",
    description="AI-powered Research Paper Analysis System",
    version="1.0"
)


# Initialize SQLite database when backend starts
initialize_database()


# --------------------------------------------------
# HOME ENDPOINT
# --------------------------------------------------

@app.get("/")
def home():

    return {
        "status": "success",
        "message": "ResearchLens AI Backend is Running!"
    }


# --------------------------------------------------
# MULTIPLE PDF UPLOAD ENDPOINT
# --------------------------------------------------

@app.post("/upload-pdf")
async def upload_pdf(
    files: list[PDFUpload] = File(...)
):

    if not files:

        raise HTTPException(
            status_code=400,
            detail="Please upload at least one PDF."
        )

    documents = []
    duplicate_documents = []
    failed_documents = []

    for file in files:

        original_filename = (
            (file.filename or "uploaded.pdf")
            .replace("\\", "/")
            .split("/")[-1]
        )

        file_path = None

        try:

            # Check file extension
            if not original_filename.lower().endswith(".pdf"):

                failed_documents.append({
                    "filename": original_filename,
                    "error": "Only PDF files are allowed."
                })

                continue

            # Read PDF content
            pdf_bytes = await file.read(MAX_FILE_SIZE + 1)

            if not pdf_bytes:

                failed_documents.append({
                    "filename": original_filename,
                    "error": "The uploaded file is empty."
                })

                continue

            # Check individual file size
            if len(pdf_bytes) > MAX_FILE_SIZE:

                failed_documents.append({
                    "filename": original_filename,
                    "error": "PDF exceeds the 20 MB limit."
                })

                continue

            # Generate SHA-256 hash
            file_hash = hashlib.sha256(pdf_bytes).hexdigest()

            # Check whether the PDF already exists
            existing_document = find_document_by_hash(file_hash)

            if existing_document:

                duplicate_documents.append({
                    "filename": original_filename,
                    "duplicate_of": {
                        "document_id": existing_document["document_id"],
                        "filename": existing_document["filename"]
                    }
                })

                continue

            # Extract text and sections from PDF
            try:

                pages = extract_text_from_pdf(pdf_bytes)

            except ValueError as error:

                failed_documents.append({
                    "filename": original_filename,
                    "error": str(error)
                })

                continue

            # Generate chunks
            chunks = chunk_pages(
                pages,
                original_filename
            )

            # Generate unique document ID
            document_id = uuid4().hex

            # Attach document ID to every chunk
            for chunk in chunks:

                chunk["document_id"] = document_id

            # Save original PDF
            stored_filename = f"{document_id}.pdf"

            file_path = UPLOAD_DIR / stored_filename

            try:

                file_path.write_bytes(pdf_bytes)

            except OSError:

                if file_path.exists():
                    file_path.unlink()

                failed_documents.append({
                    "filename": original_filename,
                    "error": "Could not save this PDF."
                })

                continue

            # Prepare document information
            document_data = {
                "document_id": document_id,
                "filename": original_filename,
                "stored_path": file_path.relative_to(
                    BASE_DIR
                ).as_posix(),
                "sha256": file_hash,
                "total_pages": len(pages),
                "total_chunks": len(chunks)
            }

            # Save document and chunks into SQLite
            try:

                save_document_and_chunks(
                    document_data,
                    chunks
                )

            except Exception:

                if file_path.exists():
                    file_path.unlink()

                failed_documents.append({
                    "filename": original_filename,
                    "error": (
                        "Could not save document information "
                        "to database."
                    )
                })

                continue

            # Add successful document to response
            documents.append({
                "document_id": document_id,
                "filename": original_filename,
                "stored_file": document_data["stored_path"],
                "total_pages": len(pages),
                "total_chunks": len(chunks),
                "message": "PDF processed and saved successfully."
            })

        finally:

            await file.close()

    # Return an error if nothing was processed
    # and nothing was identified as a duplicate
    if not documents and not duplicate_documents:

        raise HTTPException(
            status_code=400,
            detail={
                "message": "No new PDFs could be processed.",
                "failed_documents": failed_documents
            }
        )

    # Final response
    return {
        "status": (
            "success"
            if not failed_documents
            else "partial_success"
        ),

        "total_files_received": len(files),

        "processed_files": len(documents),

        "duplicate_files": len(duplicate_documents),

        "failed_files": len(failed_documents),

        "total_pages": sum(
            document["total_pages"]
            for document in documents
        ),

        "total_chunks": sum(
            document["total_chunks"]
            for document in documents
        ),

        "documents": documents,

        "duplicate_documents": duplicate_documents,

        "failed_documents": failed_documents
    }


# --------------------------------------------------
# MULTIPLE PDF UPLOAD PAGE
# --------------------------------------------------

@app.get("/upload-page", response_class=HTMLResponse)
def upload_page():

    return """
    <!DOCTYPE html>
    <html lang="en">

    <head>
        <meta charset="UTF-8">
        <title>ResearchLens AI - Upload Papers</title>

        <style>
            body {
                font-family: Arial, sans-serif;
                background: #f4f6fa;
                padding: 40px;
                text-align: center;
            }

            .container {
                max-width: 650px;
                margin: 50px auto;
                background: white;
                padding: 35px;
                border-radius: 12px;
                box-shadow: 0 4px 20px rgba(0,0,0,0.07);
            }

            button {
                margin-top: 20px;
                padding: 12px 25px;
                background: #2457d6;
                color: white;
                border: none;
                border-radius: 7px;
                cursor: pointer;
            }

            #result {
                margin-top: 25px;
                text-align: left;
                white-space: pre-wrap;
                overflow-wrap: anywhere;
            }
        </style>
    </head>

    <body>

        <div class="container">

            <h1>ResearchLens AI</h1>
            <h3>Upload Research Papers</h3>

            <p>Select multiple PDF files together.</p>

            <input
                type="file"
                id="pdfFiles"
                accept=".pdf,application/pdf"
                multiple
            >

            <br>

            <button onclick="uploadFiles()">
                Upload All PDFs
            </button>

            <div id="result"></div>

        </div>

        <script>

            async function uploadFiles() {

                const input = document.getElementById("pdfFiles");

                const files = Array.from(input.files);

                const result = document.getElementById("result");

                if (files.length === 0) {

                    alert("Please select at least one PDF.");

                    return;
                }

                for (const file of files) {

                    if (
                        !file.name.toLowerCase().endsWith(".pdf") ||
                        file.size > 20 * 1024 * 1024
                    ) {
                        alert(
                            "Invalid PDF or file larger than 20 MB: "
                            + file.name
                        );

                        return;
                    }
                }

                const formData = new FormData();

                files.forEach(file => {
                    formData.append("files", file);
                });

                result.textContent =
                    "Uploading and processing PDFs...";

                try {

                    const response = await fetch("/upload-pdf", {
                        method: "POST",
                        body: formData
                    });

                    const data = await response.json();

                    result.textContent =
                        JSON.stringify(data, null, 2);

                } catch (error) {

                    result.textContent =
                        "Upload failed: " + error.message;

                }
            }

        </script>

    </body>
    </html>
    """



# --------------------------------------------------
# LIST ALL UPLOADED DOCUMENTS
# --------------------------------------------------

@app.get("/documents")
def list_documents():

    documents = get_all_documents()

    return {
        "status": "success",
        "total_documents": len(documents),
        "documents": [
            {
                **document,
                "chunks_url": (
                    f"/documents/{document['document_id']}/chunks"
                ),
                "download_url": (
                    f"/documents/{document['document_id']}/download"
                )
            }
            for document in documents
        ]
    }


# --------------------------------------------------
# GET ONE DOCUMENT'S DETAILS
# --------------------------------------------------

@app.get("/documents/{document_id}")
def document_details(document_id: str):

    document = get_document(document_id)

    if not document:

        raise HTTPException(
            status_code=404,
            detail="Document not found."
        )

    return {
        "status": "success",
        "document": {
            "document_id": document["document_id"],
            "filename": document["filename"],
            "total_pages": document["total_pages"],
            "total_chunks": document["total_chunks"],
            "uploaded_at": document["uploaded_at"],
            "stored_path": document["stored_path"]
        }
    }


# --------------------------------------------------
# GET ALL CHUNKS OF A DOCUMENT
# --------------------------------------------------

@app.get("/documents/{document_id}/chunks")
def document_chunks(document_id: str):

    document = get_document(document_id)

    if not document:

        raise HTTPException(
            status_code=404,
            detail="Document not found."
        )

    chunks = get_document_chunks(document_id)

    return {
        "status": "success",
        "document_id": document_id,
        "filename": document["filename"],
        "total_chunks": len(chunks),
        "chunks": chunks
    }


# --------------------------------------------------
# DOWNLOAD ORIGINAL PDF
# --------------------------------------------------

@app.get("/documents/{document_id}/download")
def download_document(document_id: str):

    document = get_document(document_id)

    if not document:

        raise HTTPException(
            status_code=404,
            detail="Document not found."
        )

    file_path = (
        BASE_DIR / document["stored_path"]
    ).resolve()

    # Ensure the stored path belongs to the upload folder
    try:

        file_path.relative_to(UPLOAD_DIR.resolve())

    except ValueError:

        raise HTTPException(
            status_code=400,
            detail="Invalid document storage path."
        )

    if not file_path.is_file():

        raise HTTPException(
            status_code=404,
            detail="Original PDF file not found on disk."
        )

    return FileResponse(
        path=file_path,
        media_type="application/pdf",
        filename=document["filename"]
    )


# --------------------------------------------------
# DELETE DOCUMENT AND ITS CHUNKS
# --------------------------------------------------

@app.delete("/documents/{document_id}")
def remove_document(document_id: str):

    document = get_document(document_id)

    if not document:

        raise HTTPException(
            status_code=404,
            detail="Document not found."
        )

    file_path = (
        BASE_DIR / document["stored_path"]
    ).resolve()

    # Ensure the stored path belongs to the upload folder
    try:

        file_path.relative_to(UPLOAD_DIR.resolve())

    except ValueError:

        raise HTTPException(
            status_code=400,
            detail="Invalid document storage path."
        )

    # Deleting the document also deletes its chunks
    # because the database uses ON DELETE CASCADE
    deleted = delete_document(document_id)

    if not deleted:

        raise HTTPException(
            status_code=404,
            detail="Document could not be deleted."
        )

    file_deleted = False

    if file_path.is_file():

        try:

            file_path.unlink()
            file_deleted = True

        except OSError:

            file_deleted = False

    return {
        "status": "success",
        "message": "Document and its database chunks were deleted.",
        "document_id": document_id,
        "filename": document["filename"],
        "file_deleted": file_deleted
    }
