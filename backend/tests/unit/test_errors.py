from app.common.errors import AppError, ErrorCode, error_payload


def test_app_error_payload_contains_stable_shape() -> None:
    error = AppError(
        code=ErrorCode.INVALID_REQUEST,
        message="Document selection is required.",
        details={"field": "active_document_ids"},
    )

    assert error_payload(error) == {
        "code": "invalid_request",
        "message": "Document selection is required.",
        "details": {"field": "active_document_ids"},
    }


def test_app_error_uses_default_status_code() -> None:
    error = AppError(code=ErrorCode.NOT_FOUND, message="Missing document.")

    assert error.status_code == 400
    assert error.details == {}
