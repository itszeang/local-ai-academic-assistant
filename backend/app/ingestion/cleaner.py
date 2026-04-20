"""Text cleanup rules for PDF extraction output."""

from __future__ import annotations

import re


_CONTROL_CHARS = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f]")
_SPACES = re.compile(r"[ \t]+")
_BLANK_LINES = re.compile(r"\n{3,}")


def clean_text(text: str) -> str:
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    normalized = _CONTROL_CHARS.sub("", normalized)
    normalized = re.sub(r"(\w)-\n(\w)", r"\1\2", normalized)
    normalized = _SPACES.sub(" ", normalized)
    normalized = re.sub(r" *\n *", "\n", normalized)
    normalized = _BLANK_LINES.sub("\n\n", normalized)
    return normalized.strip()
