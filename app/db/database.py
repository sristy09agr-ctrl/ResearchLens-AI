"""
SQLite database management module for ResearchLens AI.
Stores documents metadata, chunks with section/page locations, and asynchronous ingestion jobs.
"""

import sqlite3
from pathlib import Path
from contextlib import contextmanager
from typing import Optional, List, Dict, Any
from datetime import datetime

from app.config import settings

DATABASE_PATH = settings.database_path


@contextmanager
def get_connection():
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(str(DATABASE_PATH), timeout=30.0)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    try:
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def initialize_database():
    """Create all required tables and indexes if they do not exist."""
    with get_connection() as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS documents (
                document_id TEXT PRIMARY KEY,
                filename TEXT NOT NULL,
                stored_path TEXT NOT NULL,
                sha256 TEXT NOT NULL UNIQUE,
                total_pages INTEGER NOT NULL,
                total_chunks INTEGER NOT NULL,
                uploaded_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        connection.execute("""
            CREATE TABLE IF NOT EXISTS chunks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                document_id TEXT NOT NULL,
                chunk_id INTEGER NOT NULL,
                text TEXT NOT NULL,
                page_start INTEGER,
                page_end INTEGER,
                section TEXT,
                chunk_type TEXT DEFAULT 'text',
                word_start INTEGER,
                word_end INTEGER,
                FOREIGN KEY (document_id) REFERENCES documents(document_id) ON DELETE CASCADE,
                UNIQUE(document_id, chunk_id)
            )
        """)

        connection.execute("""
            CREATE TABLE IF NOT EXISTS jobs (
                job_id TEXT PRIMARY KEY,
                filename TEXT NOT NULL,
                status TEXT NOT NULL,
                document_id TEXT,
                total_pages INTEGER DEFAULT 0,
                total_chunks INTEGER DEFAULT 0,
                error_message TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        connection.execute("""
            CREATE INDEX IF NOT EXISTS idx_chunks_document_id ON chunks(document_id)
        """)
        connection.execute("""
            CREATE INDEX IF NOT EXISTS idx_jobs_status ON jobs(status)
        """)

        # Migration: Ensure chunk_type exists for existing databases
        columns = [row[1] for row in connection.execute("PRAGMA table_info(chunks)").fetchall()]
        if "chunk_type" not in columns:
            try:
                connection.execute("ALTER TABLE chunks ADD COLUMN chunk_type TEXT DEFAULT 'text'")
            except Exception:
                pass


def find_document_by_hash(file_hash: str) -> Optional[Dict[str, Any]]:
    with get_connection() as connection:
        result = connection.execute(
            "SELECT * FROM documents WHERE sha256 = ?",
            (file_hash,)
        ).fetchone()
        return dict(result) if result else None


def get_all_documents() -> List[Dict[str, Any]]:
    with get_connection() as connection:
        results = connection.execute(
            "SELECT * FROM documents ORDER BY uploaded_at DESC"
        ).fetchall()
        return [dict(row) for row in results]


def get_document(document_id: str) -> Optional[Dict[str, Any]]:
    with get_connection() as connection:
        result = connection.execute(
            "SELECT * FROM documents WHERE document_id = ?",
            (document_id,)
        ).fetchone()
        return dict(result) if result else None


def get_document_chunks(document_id: str) -> List[Dict[str, Any]]:
    with get_connection() as connection:
        results = connection.execute(
            """
            SELECT id, chunk_id, text, page_start, page_end, section, chunk_type, word_start, word_end
            FROM chunks
            WHERE document_id = ?
            ORDER BY chunk_id ASC
            """,
            (document_id,)
        ).fetchall()
        return [dict(row) for row in results]


def save_document_and_chunks(document_data: Dict[str, Any], chunks: List[Dict[str, Any]]):
    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO documents (
                document_id, filename, stored_path, sha256, total_pages, total_chunks
            ) VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                document_data["document_id"],
                document_data["filename"],
                document_data["stored_path"],
                document_data["sha256"],
                document_data["total_pages"],
                document_data["total_chunks"]
            )
        )

        for chunk in chunks:
            connection.execute(
                """
                INSERT INTO chunks (
                    document_id, chunk_id, text, page_start, page_end, section, chunk_type, word_start, word_end
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    chunk.get("document_id", document_data["document_id"]),
                    chunk["chunk_id"],
                    chunk["text"],
                    chunk.get("page_start"),
                    chunk.get("page_end"),
                    chunk.get("section"),
                    chunk.get("chunk_type", "text"),
                    chunk.get("word_start"),
                    chunk.get("word_end")
                )
            )


def delete_document(document_id: str) -> bool:
    with get_connection() as connection:
        cursor = connection.execute(
            "DELETE FROM documents WHERE document_id = ?",
            (document_id,)
        )
        return cursor.rowcount > 0


# Ingestion Job Queue operations
def create_job(job_id: str, filename: str) -> Dict[str, Any]:
    with get_connection() as connection:
        now = datetime.utcnow().isoformat()
        connection.execute(
            """
            INSERT INTO jobs (job_id, filename, status, created_at, updated_at)
            VALUES (?, ?, 'queued', ?, ?)
            """,
            (job_id, filename, now, now)
        )
        return {"job_id": job_id, "filename": filename, "status": "queued"}


def update_job(
    job_id: str,
    status: str,
    document_id: Optional[str] = None,
    total_pages: Optional[int] = None,
    total_chunks: Optional[int] = None,
    error_message: Optional[str] = None
):
    with get_connection() as connection:
        now = datetime.utcnow().isoformat()
        connection.execute(
            """
            UPDATE jobs
            SET status = ?, document_id = COALESCE(?, document_id),
                total_pages = COALESCE(?, total_pages),
                total_chunks = COALESCE(?, total_chunks),
                error_message = ?, updated_at = ?
            WHERE job_id = ?
            """,
            (status, document_id, total_pages, total_chunks, error_message, now, job_id)
        )


def get_job(job_id: str) -> Optional[Dict[str, Any]]:
    with get_connection() as connection:
        result = connection.execute(
            "SELECT * FROM jobs WHERE job_id = ?",
            (job_id,)
        ).fetchone()
        return dict(result) if result else None
