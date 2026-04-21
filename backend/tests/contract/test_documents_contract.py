from pathlib import Path

from fastapi.testclient import TestClient

from app.common.config import Settings
from app.common.types import ExtractionMethod
from app.main import create_app


def test_document_upload_list_detail_active_delete_and_job_contract(tmp_path: Path) -> None:
    app = create_app(Settings(data_dir=tmp_path))
    client = TestClient(app)

    upload_response = client.post(
        "/documents?filename=paper.pdf",
        content=b"%PDF-1.4 local test document",
        headers={"content-type": "application/pdf"},
    )

    assert upload_response.status_code == 202
    upload_payload = upload_response.json()
    document_id = upload_payload["document"]["id"]
    job_id = upload_payload["job"]["id"]
    assert upload_payload["document"]["filename"] == "paper.pdf"
    assert upload_payload["document"]["status"] in {"pending", "failed"}
    assert upload_payload["job"]["status"] in {"queued", "failed"}

    list_response = client.get("/documents")
    assert list_response.status_code == 200
    list_payload = list_response.json()
    assert list_payload["documents"][0]["id"] == document_id
    assert list_payload["active_document_ids"] == []

    detail_response = client.get(f"/documents/{document_id}")
    assert detail_response.status_code == 200
    assert detail_response.json()["document"]["id"] == document_id

    active_response = client.put("/documents/active", json={"document_ids": [document_id]})
    assert active_response.status_code == 200
    assert active_response.json()["active_document_ids"] == [document_id]

    job_response = client.get(f"/jobs/{job_id}")
    assert job_response.status_code == 200
    assert job_response.json()["job"]["document_id"] == document_id

    delete_response = client.delete(f"/documents/{document_id}")
    assert delete_response.status_code == 200
    assert delete_response.json()["deleted"] is True
    assert client.get(f"/documents/{document_id}").status_code == 404


def test_document_upload_uses_injected_processor_without_pdf_dependencies(tmp_path: Path) -> None:
    app = create_app(Settings(data_dir=tmp_path))

    def processor(document, repositories, settings):
        repositories.source_segments.create(
            document_id=document.id,
            chunk_index=0,
            text="The uploaded paper discusses grounded academic writing.",
            page_start=1,
            source_label=document.filename,
            extraction_method=ExtractionMethod.TEXT,
            metadata={"authors": ["Aksoy"], "year": 2024},
        )
        return {
            "title": "Grounded Academic Writing",
            "authors": ["Aksoy"],
            "year": 2024,
            "page_count": 1,
        }

    app.state.document_processor = processor
    client = TestClient(app)

    response = client.post(
        "/documents?filename=processed.pdf",
        content=b"%PDF-1.4 local test document",
        headers={"content-type": "application/pdf"},
    )

    assert response.status_code == 202
    payload = response.json()
    assert payload["document"]["status"] == "ready"
    assert payload["document"]["title"] == "Grounded Academic Writing"
    assert payload["document"]["authors"] == ["Aksoy"]
    assert payload["document"]["page_count"] == 1
    assert payload["job"]["status"] == "succeeded"
