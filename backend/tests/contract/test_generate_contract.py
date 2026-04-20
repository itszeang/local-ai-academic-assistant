from pathlib import Path

from fastapi.testclient import TestClient

from app.common.config import Settings
from app.common.types import DocumentStatus, ExtractionMethod
from app.main import create_app
from app.storage.repositories import RepositoryRegistry


def test_generate_contract_returns_grounded_output_shape(tmp_path: Path) -> None:
    app = create_app(Settings(data_dir=tmp_path))
    repos = RepositoryRegistry(app.state.database)
    workspace = repos.workspaces.create(name="Default", root_path=tmp_path)
    document = repos.documents.create(
        workspace_id=workspace.id,
        filename="paper.pdf",
        stored_path=tmp_path / "paper.pdf",
        status=DocumentStatus.READY,
        authors=("Aksoy",),
        year=2024,
    )
    repos.source_segments.create(
        document_id=document.id,
        chunk_index=0,
        text="Motivation improves persistence in learning tasks.",
        page_start=5,
        source_label="paper.pdf",
        extraction_method=ExtractionMethod.TEXT,
        metadata={"authors": ["Aksoy"], "year": 2024},
    )
    client = TestClient(app)

    response = client.post(
        "/generate",
        json={
            "mode": "qa",
            "query": "What improves persistence?",
            "active_document_ids": [document.id],
            "language": "en",
            "top_k": 3,
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["mode"] == "qa"
    assert payload["fallback_used"] is False
    assert payload["sections"][0]["heading"] == "Answer"
    assert payload["citations"][0]["source_segment_id"]
    assert payload["references"]


def test_generate_contract_returns_exact_fallback_for_no_context(tmp_path: Path) -> None:
    app = create_app(Settings(data_dir=tmp_path))
    client = TestClient(app)

    response = client.post(
        "/generate",
        json={
            "mode": "qa",
            "query": "What improves persistence?",
            "active_document_ids": ["doc_missing"],
            "language": "en",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["fallback_used"] is True
    assert payload["title"] == "Bilgi bulunamadı"
    assert payload["sections"][0]["blocks"] == ["Bilgi bulunamadı"]
    assert payload["citations"] == []
