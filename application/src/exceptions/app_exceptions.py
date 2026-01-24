class AppException(Exception):
    """Base exception for the application"""

    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class NotFoundException(AppException):
    def __init__(self, message: str):
        super().__init__(message, status_code=404)


class BadRequestException(AppException):
    def __init__(self, message: str = "request is invalid"):
        super().__init__(message, status_code=400)


class ForbiddenException(AppException):
    def __init__(self, message: str = "forbidden"):
        super().__init__(message)
        self.status_code = 403


class InternalServerException(AppException):
    def __init__(self, message: str = "Internal server error"):
        super().__init__(message, status_code=500)


class UserAlreadyExistsError(AppException):
    def __init__(self, message: str = "User already exists"):
        super().__init__(message, status_code=409)


class AuthServiceError(AppException):
    def __init__(self, message: str = "Authentication service failed"):
        super().__init__(message, status_code=500)


class AuditServiceError(AppException):
    def __init__(self, message: str = "Audit service failed"):
        super().__init__(message, status_code=500)


class DocumentServiceError(AppException):
    def __init__(self, message: str = "document service failed"):
        super().__init__(message, status_code=500)


class PresignedServiceError(AppException):
    def __init__(self, message: str = "presigned service failed"):
        super().__init__(message, status_code=500)
