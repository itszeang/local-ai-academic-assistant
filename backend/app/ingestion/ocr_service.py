"""OCR fallback boundary for scanned PDF pages."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any, Protocol


class PdfPageForOCR(Protocol):
    def to_image(self, *, resolution: int) -> Any:
        ...


TesseractRunner = Callable[[Any, str], str]


def _default_tesseract_runner(image: Any, language: str) -> str:
    import pytesseract

    return str(pytesseract.image_to_string(image, lang=language))


class OCRService:
    def __init__(
        self,
        *,
        enabled: bool = True,
        min_text_chars: int = 20,
        language: str = "eng",
        resolution: int = 200,
        tesseract_runner: TesseractRunner | None = None,
    ) -> None:
        self.enabled = enabled
        self.min_text_chars = min_text_chars
        self.language = language
        self.resolution = resolution
        self.tesseract_runner = tesseract_runner or _default_tesseract_runner

    def should_ocr_page(self, text: str) -> bool:
        if not self.enabled:
            return False
        return len(text.strip()) < self.min_text_chars

    def extract_page_text(self, page: PdfPageForOCR | object, *, page_number: int) -> str:
        if not self.enabled:
            return ""

        if not hasattr(page, "to_image"):
            return ""

        try:
            rendered = page.to_image(resolution=self.resolution)  # type: ignore[attr-defined]
            image = getattr(rendered, "original", rendered)
            return self.tesseract_runner(image, self.language).strip()
        except Exception:
            return ""
