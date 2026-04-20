from pathlib import Path

from fastapi.testclient import TestClient

from app.common.config import Settings
from app.common.types import DocumentStatus
from app.main import create_app
from app.storage.repositories import RepositoryRegistry


def test_active_document_selection_is_scoped_to_workspace(tmp_path: Path) -> None:
    app = create_app(Settings(data_dir=tmp_path))
    repositories = RepositoryRegistry(app.state.database)
    workspace = repositories.workspaces.create(name="Thesis", root_path=tmp_path / "thesis")
    first_document = repositories.documents.create(
        workspace_id=workspace.id,
        filename="first.pdf",
        stored_path=tmp_path / "first.pdf",
        status=DocumentStatus.READY,
    )
    second_document = repositories.documents.create(
        workspace_id=workspace.id,
        filename="second.pdf",
        stored_path=tmp_path / "second.pdf",
        status=DocumentStatus.READY,
    )
    other_workspace = repositories.workspaces.create(name="Other", root_path=tmp_path / "other")
    other_document = repositories.documents.create(
        workspace_id=other_workspace.id,
        filename="other.pdf",
        stored_path=tmp_path / "other.pdf",
        status=DocumentStatus.READY,
    )
    client = TestClient(app)

    response = client.put(
        "/documents/active",
        json={
            "workspace_id": workspace.id,
            "document_ids": [second_document.id, first_document.id],
        },
    )

    assert response.status_code == 200
    assert response.json()["active_document_ids"] == [second_document.id, first_document.id]

    list_response = client.get(f"/documents?workspace_id={workspace.id}")
    assert list_response.status_code == 200
    assert list_response.json()["active_document_ids"] == [second_document.id, first_document.id]

    invalid_response = client.put(
        "/documents/active",
        json={
            "workspace_id": workspace.id,
            "document_ids": [other_document.id],
        },
    )

    assert invalid_response.status_code == 400
    assert invalid_response.json()["code"] == "invalid_request"
