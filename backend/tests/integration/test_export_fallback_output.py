from pathlib import Path

from docx import Document as DocxDocument

from app.common.types import GenerationMode, JobStatus, MISSING_INFORMATION_RESPONSE
from app.export.docx_exporter import DocxExporter
from app.storage.repositories import RepositoryRegistry
from app.storage.sqlite import SQLiteDatabase


def test_fallback_output_export_does_not_add_references(tmp_path: Path) -> None:
    db = SQLiteDatabase(tmp_path / "academic_assistant.sqlite")
    db.initialize()
    repos = RepositoryRegistry(db)
    output = repos.academic_outputs.create(
        generation_request_id="request_1",
        mode=GenerationMode.QA,
        title=MISSING_INFORMATION_RESPONSE,
        sections=[{"heading": "Answer", "blocks": [MISSING_INFORMATION_RESPONSE]}],
        references=[],
        fallback_used=True,
    )
    export_path = tmp_path / "exports" / "fallback.docx"

    DocxExporter().export(output=output, path=export_path)
    export_file = repos.export_files.create(
        academic_output_id=output.id,
        path=export_path,
        status=JobStatus.SUCCEEDED,
    )

    paragraphs = [paragraph.text for paragraph in DocxDocument(export_file.path).paragraphs]
    assert MISSING_INFORMATION_RESPONSE in paragraphs
    assert "References" not in paragraphs
