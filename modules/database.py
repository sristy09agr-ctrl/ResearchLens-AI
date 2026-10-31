
import sqlite3
from pathlib import Path
from contextlib import contextmanager


# DATABASE LOCATION

BASE_DIR = Path(__file__).resolve().parent.parent
DATABASE_PATH = BASE_DIR / "data" / "researchlens.db"


# DATABASE CONNECTION

@contextmanager
def get_connection():

    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(DATABASE_PATH)

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


# INITIALIZE DATABASE

def initialize_database():

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
                word_start INTEGER,
                word_end INTEGER,

                FOREIGN KEY (document_id)
                REFERENCES documents(document_id)
                ON DELETE CASCADE,

                UNIQUE(document_id, chunk_id)
            )
        """)

        connection.execute("""
            CREATE INDEX IF NOT EXISTS
            idx_chunks_document_id
            ON chunks(document_id)
        """)


# FIND DOCUMENT BY HASH

def find_document_by_hash(file_hash):

    with get_connection() as connection:

        result = connection.execute(
            """
            SELECT *
            FROM documents
            WHERE sha256 = ?
            """,
            (file_hash,)
        ).fetchone()

        return dict(result) if result else None


# SAVE DOCUMENT AND CHUNKS

def save_document_and_chunks(document, chunks):

    with get_connection() as connection:

        connection.execute(
            """
            INSERT INTO documents (
                document_id,
                filename,
                stored_path,
                sha256,
                total_pages,
                total_chunks
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                document["document_id"],
                document["filename"],
                document["stored_path"],
                document["sha256"],
                document["total_pages"],
                document["total_chunks"]
            )
        )

        connection.executemany(
            """
            INSERT INTO chunks (
                document_id,
                chunk_id,
                text,
                page_start,
                page_end,
                section,
                word_start,
                word_end
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    document["document_id"],
                    chunk["chunk_id"],
                    chunk["text"],
                    chunk.get("page_start"),
                    chunk.get("page_end"),
                    chunk.get("section", "Unidentified"),
                    chunk.get("word_start"),
                    chunk.get("word_end")
                )
                for chunk in chunks
            ]
        )


# GET ALL DOCUMENTS

def get_all_documents():

    with get_connection() as connection:

        results = connection.execute(
            """
            SELECT
                document_id,
                filename,
                stored_path,
                total_pages,
                total_chunks,
                uploaded_at
            FROM documents
            ORDER BY uploaded_at DESC
            """
        ).fetchall()

        return [dict(row) for row in results]


# GET ONE DOCUMENT

def get_document(document_id):

    with get_connection() as connection:

        result = connection.execute(
            """
            SELECT *
            FROM documents
            WHERE document_id = ?
            """,
            (document_id,)
        ).fetchone()

        return dict(result) if result else None


# GET DOCUMENT CHUNKS

def get_document_chunks(document_id):

    with get_connection() as connection:

        results = connection.execute(
            """
            SELECT
                chunk_id,
                text,
                page_start,
                page_end,
                section,
                word_start,
                word_end
            FROM chunks
            WHERE document_id = ?
            ORDER BY chunk_id
            """,
            (document_id,)
        ).fetchall()

        return [dict(row) for row in results]


# DELETE DOCUMENT

def delete_document(document_id):

    with get_connection() as connection:

        cursor = connection.execute(
            """
            DELETE FROM documents
            WHERE document_id = ?
            """,
            (document_id,)
        )

        return cursor.rowcount > 0
