from pathlib import Path

from fastapi.testclient import TestClient

from app.common.config import Settings
from app.common.types import GenerationMode
from app.main import create_app
from app.storage.repositories import RepositoryRegistry


def test_export_contract_accepts_output_and_returns_export_job(tmp_path: Path) -> None:
    app = create_app(Settings(data_dir=tmp_path))
    repos = RepositoryRegistry(app.state.database)
    output = repos.academic_outputs.create(
        generation_request_id="request_1",
        mode=GenerationMode.QA,
        title="Grounded Answer",
        sections=[{"heading": "Answer", "blocks": ["Motivation improves persistence."]}],
        references=["motivation.pdf, p. 5"],
        fallback_used=False,
    )
    client = TestClient(app)

    response = client.post(f"/outputs/{output.id}/export", json={"filename": "answer.docx"})

    assert response.status_code == 202
    payload = response.json()
    assert payload["id"]
    assert payload["output_id"] == output.id
    assert payload["status"] == "succeeded"
    assert payload["path"].endswith("answer.docx")
    assert Path(payload["path"]).exists()


def test_export_contract_returns_not_found_for_missing_output(tmp_path: Path) -> None:
    app = create_app(Settings(data_dir=tmp_path))
    client = TestClient(app)

    response = client.post("/outputs/output_missing/export")

    assert response.status_code == 404
    assert response.json()["code"] == "not_found"
