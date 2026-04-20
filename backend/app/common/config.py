"""Local-first configuration loading."""

from __future__ import annotations

import os
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path


ENV_PREFIX = "ACADEMIC_ASSISTANT_"


def _to_bool(value: str | bool) -> bool:
    if isinstance(value, bool):
        return value
    return value.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True, slots=True)
class Settings:
    host: str = "127.0.0.1"
    port: int = 8765
    data_dir: Path = Path("./data")
    embedding_model: str = "BAAI/bge-m3"
    reranker_model: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"
    classifier_model: str = "llama3.1:8b"
    generator_model: str = "llama3.1:8b"
    formatter_model: str = "llama3.1:8b"
    ollama_base_url: str = "http://127.0.0.1:11434"
    ocr_enabled: bool = True
    chunk_size: int = 1100
    chunk_overlap: int = 200

    def __post_init__(self) -> None:
        object.__setattr__(self, "data_dir", Path(self.data_dir))

    @property
    def documents_dir(self) -> Path:
        return self.data_dir / "documents"

    @property
    def indexes_dir(self) -> Path:
        return self.data_dir / "indexes"

    @property
    def exports_dir(self) -> Path:
        return self.data_dir / "exports"

    @property
    def sqlite_path(self) -> Path:
        return self.data_dir / "academic_assistant.sqlite"

    @property
    def local_directories(self) -> tuple[Path, ...]:
        return (self.data_dir, self.documents_dir, self.indexes_dir, self.exports_dir)


def load_settings(env: Mapping[str, str] | None = None) -> Settings:
    source = os.environ if env is None else env

    def read(name: str, default: str) -> str:
        return source.get(f"{ENV_PREFIX}{name}", default)

    return Settings(
        host=read("HOST", "127.0.0.1"),
        port=int(read("PORT", "8765")),
        data_dir=Path(read("DATA_DIR", "./data")),
        embedding_model=read("EMBEDDING_MODEL", "BAAI/bge-m3"),
        reranker_model=read("RERANKER_MODEL", "cross-encoder/ms-marco-MiniLM-L-6-v2"),
        classifier_model=read("CLASSIFIER_MODEL", "llama3.1:8b"),
        generator_model=read("GENERATOR_MODEL", "llama3.1:8b"),
        formatter_model=read("FORMATTER_MODEL", "llama3.1:8b"),
        ollama_base_url=read("OLLAMA_BASE_URL", "http://127.0.0.1:11434"),
        ocr_enabled=_to_bool(read("OCR_ENABLED", "true")),
        chunk_size=int(read("CHUNK_SIZE", "1100")),
        chunk_overlap=int(read("CHUNK_OVERLAP", "200")),
    )
