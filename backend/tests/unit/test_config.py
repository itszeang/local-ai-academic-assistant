from pathlib import Path

from app.common.config import Settings, load_settings


def test_settings_resolve_local_paths(tmp_path: Path) -> None:
    settings = Settings(data_dir=tmp_path / "workspace")

    assert settings.data_dir == tmp_path / "workspace"
    assert settings.documents_dir == tmp_path / "workspace" / "documents"
    assert settings.indexes_dir == tmp_path / "workspace" / "indexes"
    assert settings.exports_dir == tmp_path / "workspace" / "exports"
    assert settings.sqlite_path == tmp_path / "workspace" / "academic_assistant.sqlite"


def test_settings_model_defaults_are_local_first(tmp_path: Path) -> None:
    settings = Settings(data_dir=tmp_path)

    assert settings.embedding_model == "BAAI/bge-m3"
    assert settings.reranker_model == "cross-encoder/ms-marco-MiniLM-L-6-v2"
    assert settings.classifier_model == "llama3.1:8b"
    assert settings.generator_model == "llama3.1:8b"
    assert settings.formatter_model == "llama3.1:8b"
    assert settings.ollama_base_url == "http://127.0.0.1:11434"


def test_load_settings_reads_prefixed_environment(tmp_path: Path) -> None:
    settings = load_settings(
        {
            "ACADEMIC_ASSISTANT_HOST": "0.0.0.0",
            "ACADEMIC_ASSISTANT_PORT": "9000",
            "ACADEMIC_ASSISTANT_DATA_DIR": str(tmp_path),
            "ACADEMIC_ASSISTANT_OCR_ENABLED": "false",
            "ACADEMIC_ASSISTANT_CHUNK_SIZE": "1200",
            "ACADEMIC_ASSISTANT_CHUNK_OVERLAP": "150",
        }
    )

    assert settings.host == "0.0.0.0"
    assert settings.port == 9000
    assert settings.data_dir == tmp_path
    assert settings.ocr_enabled is False
    assert settings.chunk_size == 1200
    assert settings.chunk_overlap == 150
