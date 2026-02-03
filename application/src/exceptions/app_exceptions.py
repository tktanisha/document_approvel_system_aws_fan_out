from helpers.common import Common

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
    def __init__(self, message: str =  Common.REQUEST_INVALID):
        super().__init__(message, status_code=400)


class ForbiddenException(AppException):
    def __init__(self, message: str = Common.FORBIDDEN):
        super().__init__(message)
        self.status_code = 403


class InternalServerException(AppException):
    def __init__(self, message: str = Common.INTERNAL_SERVER_ERROR):
        super().__init__(message, status_code=500)


class UserAlreadyExistsError(AppException):
    def __init__(self, message: str = Common.USER_ALREADY_EXISTS):
        super().__init__(message, status_code=409)


class AuthServiceError(AppException):
    def __init__(self, message: str = Common.AUTH_SERVICE_FAILED):
        super().__init__(message, status_code=500)


class AuditServiceError(AppException):
    def __init__(self, message: str = Common.AUDIT_SERVICE_FAILED):
        super().__init__(message, status_code=500)


class DocumentServiceError(AppException):
    def __init__(self, message: str = Common.DOCUMENT_SERVICE_FAILED):
        super().__init__(message, status_code=500)


class PresignedServiceError(AppException):
    def __init__(self, message: str = Common.PRESIGNED_SERVICE_FAILED):
        super().__init__(message, status_code=500)
