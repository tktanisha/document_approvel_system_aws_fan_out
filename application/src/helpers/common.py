class Common:
    AUDIT_LOGS_FETCH_SUCCESS = "Audit logs fetched successfully"
    USER_REGISTRATION_SUCCESS = "User registration successful"
    LOGIN_SUCCESS = "Login successful"
    PRESIGNED_URL_GENERATE_SUCCESS = "Pre-signed URL generated successfully"
    STATUS_UPDATE_SUCCESS = "Status updated successfully"
    DOCUMENT_CREATE_SUCCESS = "Document created successfully"
    DOCUMENT_FETCH_SUCCESS = "Documents fetched successfully"

    REQUEST_INVALID = "request is invalid"
    FORBIDDEN = "forbidden"
    INTERNAL_SERVER_ERROR = "Internal server error"
    USER_ALREADY_EXISTS = "User already exists"
    AUTH_SERVICE_FAILED = "Authentication service failed"
    AUDIT_SERVICE_FAILED = "Audit service failed"
    DOCUMENT_SERVICE_FAILED = "document service failed"
    PRESIGNED_SERVICE_FAILED = "presigned service failed"

    AUTH_VERIFY_USER_FAILED = "Failed to verify user"
    AUTH_REGISTER_FAILED = "Failed to register user"
    AUTH_LOGIN_FAILED = "Login failed"
    INVALID_CREDENTIALS = "Invalid credentials"

    UNAUTHORIZED_OR_INVALID_USER_CONTEXT = "unauthorized or invalid user context"
    MISSING_USER_ID_IN_CONTEXT = "missing user id in context"
    INVALID_USER_CONTEXT = "invalid user context"
    ONLY_APPROVER_CAN_UPDATE_STATUS = "only approver can update status"
    CANNOT_MOVE_FROM_PENDING = "cannot move from PENDING to given"
    STATUS_ALREADY_VALUE = "your status is already {status}"

    MISSING_USER_ROLE_IN_CONTEXT = "missing user role in context"
    MISSING_USER_ID_FOR_AUTHOR = "missing user id for author"
    ROLE_NOT_PERMITTED_VIEW_LOGS = "role not permitted to view logs"

    DDB_TABLE_NAME_NOT_CONFIGURED = "DDB_TABLE_NAME is not configured"
    FAILED_FETCH_USER_FROM_DB = "Failed to fetch user from database"
    FAILED_DESERIALIZE_USER_ITEM = "Failed to deserialize user item from DynamoDB"
    CORRUPTED_USER_DATA_IN_DB = "Corrupted user data in database"
    USER_REPO_DDB_TX_FAILED = "DynamoDB transaction failed in create_user"
    FAILED_CREATE_USER_IN_DB = "Failed to create user in database"
    UNEXPECTED_ERROR_DURING_USER_CREATION = "Unexpected error during user creation"
    FAILED_FIND_USER_BY_ID = "failed to find user by id"
    UNEXPECTED_ERROR_FIND_BY_ID = "unexpected error in find_by_id"
    ERROR_FROM_USER_REPO = "error from user repo : {error}"

    FAILED_CREATE_DOCUMENT = "Failed to create document"
    NO_DOCUMENTS_FOUND = "No documents found"
    DOCUMENT_NOT_FOUND = "document not found"
    FAILED_FETCH_DOCUMENT = "failed to fetch document: {error}"
    DOCUMENT_TRANSACTION_FAILED = "transaction failed"

    ITEMS_NOT_FOUND = "items not found"
    AUDIT_REPOSITORY_FAILURE = "audit repository failure = {error}"

    FAILED_GENERATE_PRESIGNED_URL_LOG = "Failed to generate presigned url"
    FAILED_GENERATE_PRESIGNED_GET_URL_LOG = "Failed to generate presigned get url"
    FAILED_GENERATE_UPLOAD_URL = "Failed to generate upload URL"
    FAILED_GENERATE_DOWNLOAD_URL = "Failed to generate download URL"

    FAILED_CREATE_DOCUMENT_METADATA_LOG = "Failed to create document metadata"
    FAILED_LOADING_DOCUMENT = "failed loading document: {error}"
    FAILED_UPDATING_STATUS = "failed updating status: {error}"
    FAILED_FETCH_AUDIT_LOGS = "failed to fetch audit logs == {error}"

    PASSWORD_MIN_LENGTH = "password must be at least 12 characters"
    PASSWORD_MUST_CONTAIN_DIGIT = "password must contain at least one digit"
    PASSWORD_MUST_CONTAIN_SPECIAL_CHAR = (
        "password must contain at least one special character"
    )
    PASSWORD_MUST_CONTAIN_UPPERCASE = (
        "password must contain at least one uppercase letter"
    )
    PASSWORD_MUST_CONTAIN_LOWERCASE = (
        "password must contain at least one lowercase letter"
    )

    UNHANDLED_EXCEPTION_OCCURRED_LOG = "Unhandled exception occurred"
    GENERIC_ERROR_WITH_EXCEPTION = (
        "Something went wrong. Please try again later ,error = {error}"
    )
