from pathlib import Path

from docx import Document as DocxDocument

from app.common.types import GenerationMode, JobStatus
from app.export.docx_exporter import DocxExporter
from app.storage.repositories import RepositoryRegistry
from app.storage.sqlite import SQLiteDatabase


def test_supported_output_export_is_persisted_and_readable(tmp_path: Path) -> None:
    db = SQLiteDatabase(tmp_path / "academic_assistant.sqlite")
    db.initialize()
    repos = RepositoryRegistry(db)
    output = repos.academic_outputs.create(
        generation_request_id="request_1",
        mode=GenerationMode.SUMMARIZATION,
        title="Structured Summary",
        sections=[{"heading": "Overview", "blocks": ["Motivation improves persistence. (Aksoy, 2024)"]}],
        references=["motivation.pdf, p. 5"],
        fallback_used=False,
    )
    export_path = tmp_path / "exports" / "summary.docx"

    DocxExporter().export(output=output, path=export_path)
    export_file = repos.export_files.create(
        academic_output_id=output.id,
        path=export_path,
        status=JobStatus.SUCCEEDED,
    )

    assert export_file.path.exists()
    paragraphs = [paragraph.text for paragraph in DocxDocument(export_file.path).paragraphs]
    assert "Structured Summary" in paragraphs
    assert "motivation.pdf, p. 5" in paragraphs
