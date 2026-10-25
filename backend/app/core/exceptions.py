"""StudyPal custom API exceptions and consistent error handling."""

from typing import Any, Optional
from fastapi import HTTPException, status


class StudyPalException(HTTPException):
    def __init__(
        self,
        status_code: int,
        code: str,
        message: str,
        details: Optional[Any] = None,
    ):
        super().__init__(
            status_code=status_code,
            detail={
                "code": code,
                "message": message,
                "details": details,
            }
        )


class EntityNotFoundException(StudyPalException):
    def __init__(self, entity: str, entity_id: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            code="NOT_FOUND",
            message=f"{entity} with identifier '{entity_id}' was not found.",
        )


class UnauthorizedAccessException(StudyPalException):
    def __init__(self, message: str = "Invalid credentials or token expired."):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            code="UNAUTHORIZED",
            message=message,
        )


class ForbiddenCourseAccessException(StudyPalException):
    def __init__(self, course_id: str):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            code="FORBIDDEN_ACCESS",
            message=f"You do not have permission to access course '{course_id}'.",
        )


class ConflictException(StudyPalException):
    def __init__(self, message: str):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            code="CONFLICT",
            message=message,
        )


class UnsupportedFileFormatException(StudyPalException):
    def __init__(self, ext: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            code="UNSUPPORTED_FORMAT",
            message=f"File extension '.{ext}' is not supported. Only PDF (.pdf) and Plain-Text (.txt) files are permitted.",
        )


class DocumentExtractionException(StudyPalException):
    def __init__(self, details: str):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            code="DOCUMENT_EXTRACTION_FAILED",
            message="Failed to extract text from document. Scanned images or password-protected PDFs are not supported without OCR.",
            details=details,
        )
