"""SQLite connection and schema management."""

from __future__ import annotations

import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path


SCHEMA = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS workspaces (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    root_path TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS documents (
    id TEXT PRIMARY KEY,
    workspace_id TEXT NOT NULL,
    filename TEXT NOT NULL,
    stored_path TEXT NOT NULL,
    fingerprint TEXT,
    title TEXT,
    authors_json TEXT NOT NULL DEFAULT '[]',
    year INTEGER,
    page_count INTEGER,
    status TEXT NOT NULL,
    failure_reason TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    FOREIGN KEY (workspace_id) REFERENCES workspaces(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS jobs (
    id TEXT PRIMARY KEY,
    kind TEXT NOT NULL,
    status TEXT NOT NULL,
    document_id TEXT,
    output_id TEXT,
    progress REAL,
    error TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS source_segments (
    id TEXT PRIMARY KEY,
    document_id TEXT NOT NULL,
    chunk_index INTEGER NOT NULL,
    text TEXT NOT NULL,
    page_start INTEGER NOT NULL,
    page_end INTEGER,
    source_label TEXT NOT NULL,
    extraction_method TEXT NOT NULL,
    metadata_json TEXT NOT NULL DEFAULT '{}',
    created_at TEXT NOT NULL,
    FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS academic_outputs (
    id TEXT PRIMARY KEY,
    generation_request_id TEXT NOT NULL,
    mode TEXT NOT NULL,
    title TEXT NOT NULL,
    sections_json TEXT NOT NULL,
    references_json TEXT NOT NULL,
    fallback_used INTEGER NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS citations (
    id TEXT PRIMARY KEY,
    academic_output_id TEXT NOT NULL,
    source_segment_id TEXT NOT NULL,
    claim_path TEXT NOT NULL,
    inline_text TEXT NOT NULL,
    source_snippet TEXT NOT NULL,
    page_start INTEGER NOT NULL,
    page_end INTEGER,
    FOREIGN KEY (academic_output_id) REFERENCES academic_outputs(id) ON DELETE CASCADE,
    FOREIGN KEY (source_segment_id) REFERENCES source_segments(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS export_files (
    id TEXT PRIMARY KEY,
    academic_output_id TEXT NOT NULL,
    format TEXT NOT NULL,
    path TEXT NOT NULL,
    status TEXT NOT NULL,
    error_message TEXT,
    created_at TEXT NOT NULL,
    FOREIGN KEY (academic_output_id) REFERENCES academic_outputs(id) ON DELETE CASCADE
);
"""


class SQLiteDatabase:
    def __init__(self, path: Path) -> None:
        self.path = Path(path)

    @contextmanager
    def connect(self) -> Iterator[sqlite3.Connection]:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        connection = sqlite3.connect(self.path)
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

    def initialize(self) -> None:
        with self.connect() as connection:
            connection.executescript(SCHEMA)

    def table_names(self) -> set[str]:
        with self.connect() as connection:
            rows = connection.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table'"
            ).fetchall()
        return {str(row["name"]) for row in rows}
