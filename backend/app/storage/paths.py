"""Safe local workspace path helpers."""

from __future__ import annotations

from pathlib import Path

from app.common.errors import AppError, ErrorCode


def ensure_local_directories(paths: tuple[Path, ...]) -> None:
    for path in paths:
        path.mkdir(parents=True, exist_ok=True)


def resolve_inside(root: Path, candidate: Path | str) -> Path:
    root_resolved = root.resolve()
    candidate_path = Path(candidate)
    resolved = (root_resolved / candidate_path).resolve() if not candidate_path.is_absolute() else candidate_path.resolve()

    if resolved == root_resolved or root_resolved in resolved.parents:
        return resolved

    raise AppError(
        code=ErrorCode.INVALID_REQUEST,
        message="Path must stay inside the local workspace.",
        details={"root": str(root_resolved), "candidate": str(candidate)},
    )
