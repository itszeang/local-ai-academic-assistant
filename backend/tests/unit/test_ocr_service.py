from app.ingestion.ocr_service import OCRService


class FakeRenderedPage:
    original = object()


class FakePage:
    def __init__(self) -> None:
        self.resolutions: list[int] = []

    def to_image(self, *, resolution: int) -> FakeRenderedPage:
        self.resolutions.append(resolution)
        return FakeRenderedPage()


def test_ocr_service_skips_pages_with_enough_text() -> None:
    service = OCRService(enabled=True, min_text_chars=12)

    assert service.should_ocr_page("This page has enough text.") is False


def test_ocr_service_uses_tesseract_boundary_when_text_is_empty() -> None:
    page = FakePage()
    service = OCRService(
        enabled=True,
        min_text_chars=12,
        tesseract_runner=lambda image, language: " OCR result \n",
        language="eng",
        resolution=144,
    )

    assert service.should_ocr_page("   ") is True
    assert service.extract_page_text(page, page_number=3) == "OCR result"
    assert page.resolutions == [144]


def test_ocr_service_returns_empty_text_when_disabled() -> None:
    service = OCRService(enabled=False, tesseract_runner=lambda image, language: "ignored")

    assert service.should_ocr_page("") is False
    assert service.extract_page_text(object(), page_number=1) == ""
