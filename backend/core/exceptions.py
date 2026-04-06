from fastapi import HTTPException, status


class AppException(Exception):
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


# Auth
class AuthException(AppException):
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, status.HTTP_401_UNAUTHORIZED)

class ForbiddenException(AppException):
    def __init__(self, message: str = "Access forbidden"):
        super().__init__(message, status.HTTP_403_FORBIDDEN)

# Document
class DocumentNotFoundException(AppException):
    def __init__(self, doc_id: int):
        super().__init__(f"Document {doc_id} not found", status.HTTP_404_NOT_FOUND)

class InvalidFileTypeException(AppException):
    def __init__(self):
        super().__init__("Only PDF files are supported", status.HTTP_400_BAD_REQUEST)

class FileTooLargeException(AppException):
    def __init__(self, max_mb: int):
        super().__init__(f"File exceeds {max_mb}MB limit", status.HTTP_413_REQUEST_ENTITY_TOO_LARGE)

# Classification
class ClassificationException(AppException):
    def __init__(self, message: str = "Classification failed"):
        super().__init__(message, status.HTTP_500_INTERNAL_SERVER_ERROR)

class GroqAPIException(AppException):
    def __init__(self, message: str = "Groq API error"):
        super().__init__(message, status.HTTP_502_BAD_GATEWAY)
