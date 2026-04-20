from pathlib import Path

from app.storage.repositories import RepositoryRegistry
from app.storage.sqlite import SQLiteDatabase


def test_sqlite_initializes_foundation_tables(tmp_path: Path) -> None:
    database = SQLiteDatabase(tmp_path / "academic_assistant.sqlite")
    database.initialize()

    tables = database.table_names()

    assert "workspaces" in tables
    assert "documents" in tables
    assert "jobs" in tables
    assert "source_segments" in tables
    assert "academic_outputs" in tables
    assert "citations" in tables
    assert "export_files" in tables


def test_repository_registry_can_create_and_read_workspace(tmp_path: Path) -> None:
    database = SQLiteDatabase(tmp_path / "academic_assistant.sqlite")
    database.initialize()
    repositories = RepositoryRegistry(database)

    workspace = repositories.workspaces.create(name="Default", root_path=tmp_path)
    loaded = repositories.workspaces.get(workspace.id)

    assert loaded is not None
    assert loaded.id == workspace.id
    assert loaded.name == "Default"
    assert loaded.root_path == tmp_path
