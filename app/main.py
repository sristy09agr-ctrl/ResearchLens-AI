"""
ResearchLens AI - Enterprise FastAPI Application Entry Point.
Configured with lifespan model pre-warming, structured request-ID middleware,
CORS for React/Vite client, and modular API routers.
"""

from contextlib import asynccontextmanager
import time
import uuid
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

from app.config import settings
from app.db.database import initialize_database
from app.core.logging import get_logger
from app.core.exceptions import (
    AppBaseException,
    app_exception_handler,
    http_exception_handler,
    generic_exception_handler
)
from app.api.routes import health, documents, jobs, search, ask, report, graph

logger = get_logger("researchlens.main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application Lifespan:
    1. Initialize SQLite tables and indexes.
    2. Warm up local SentenceTransformer and CrossEncoder models to eliminate demo cold start.
    """
    logger.info("Initializing ResearchLens AI application lifespan...")
    initialize_database()

    # Preload reranker and embedding model in background thread
    try:
        logger.info("Pre-warming embedding and reranking models...")
        from modules.embeddings import EmbeddingGenerator
        from app.retrieval.reranker import get_reranker
        embedder = EmbeddingGenerator()
        embedder.generate_embedding("warmup scientific query")
        reranker = get_reranker()
        reranker.rerank("warmup query", [{"text": "warmup passage", "document_id": "test"}], top_k=1)
        logger.info("All local models successfully pre-warmed!")
    except Exception as e:
        logger.warning("Model pre-warming skipped or deferred: %s", e)

    yield

    logger.info("Shutting down ResearchLens AI application.")


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Agentic AI System for Research Paper Discovery, Verification, and Scientific Reasoning",
    lifespan=lifespan
)

# ---------------------------------------------------------
# CORS & REQUEST MIDDLEWARE
# ---------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def correlation_id_middleware(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID") or uuid.uuid4().hex[:8]
    request.state.request_id = request_id
    start_time = time.time()

    response = await call_next(request)

    process_time = (time.time() - start_time) * 1000
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Response-Time-MS"] = f"{process_time:.2f}"
    return response


# ---------------------------------------------------------
# EXCEPTION HANDLERS
# ---------------------------------------------------------

app.add_exception_handler(AppBaseException, app_exception_handler)
from fastapi import HTTPException
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)


# ---------------------------------------------------------
# ROUTER REGISTRATION
# ---------------------------------------------------------

app.include_router(health.router)
app.include_router(documents.router)
app.include_router(jobs.router)
app.include_router(search.router)
app.include_router(ask.router)
app.include_router(report.router)
app.include_router(graph.router)


# ---------------------------------------------------------
# ROOT & BROWSER UPLOAD FALLBACK PAGE
# ---------------------------------------------------------

@app.get("/")
def home():
    return {
        "status": "success",
        "app": settings.app_name,
        "version": settings.app_version,
        "docs_url": "/docs",
        "health_url": "/health"
    }


@app.get("/upload-page", response_class=HTMLResponse)
def upload_page():
    """Simple HTML multi-file upload form for rapid manual testing."""
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>ResearchLens AI - Upload</title>
        <style>
            body { font-family: -apple-system, sans-serif; background: #0f172a; color: #f8fafc; padding: 40px; text-align: center; }
            .card { max-width: 600px; margin: 40px auto; background: #1e293b; padding: 30px; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.5); }
            input[type=file] { margin: 20px 0; color: #94a3b8; }
            button { background: #6366f1; color: white; border: none; padding: 12px 24px; border-radius: 8px; font-weight: 600; cursor: pointer; }
            #output { margin-top: 20px; text-align: left; background: #0f172a; padding: 15px; border-radius: 8px; font-size: 13px; font-family: monospace; white-space: pre-wrap; }
        </style>
    </head>
    <body>
        <div class="card">
            <h2>ResearchLens AI</h2>
            <p>Select multiple academic research papers (.pdf) to ingest</p>
            <input type="file" id="files" multiple accept=".pdf,application/pdf">
            <br>
            <button onclick="upload()">Upload & Process</button>
            <div id="output">Status: Ready</div>
        </div>
        <script>
            async function upload() {
                const input = document.getElementById("files");
                const out = document.getElementById("output");
                if (!input.files.length) { alert("Select at least 1 PDF"); return; }
                const formData = new FormData();
                for (const f of input.files) formData.append("files", f);
                out.textContent = "Processing and indexing papers in background...";
                try {
                    const res = await fetch("/upload-pdf", { method: "POST", body: formData });
                    const data = await res.json();
                    out.textContent = JSON.stringify(data, null, 2);
                } catch (e) {
                    out.textContent = "Error: " + e.message;
                }
            }
        </script>
    </body>
    </html>
    """

