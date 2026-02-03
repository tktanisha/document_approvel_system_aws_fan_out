
import logging
import os
from controller.audits_controller import router as audit_router
from controller.auth_controller import router as auth_router
from controller.documents_controller import router as document_router
from controller.presigned_controller import router as presigned_url
from controller.multipart_uplaod_controller import router as multipart_upload
from exceptions.app_exceptions import AppException
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from helpers.common import Common

allowed_origins = os.getenv("CORS_ORIGINS", "").split(",")
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Docs Approvel",
    summary="""
        A FastApi based Documents Approvel System
    """,
    version="v1",
)


app.include_router(auth_router)
app.include_router(audit_router)
app.include_router(document_router)
app.include_router(presigned_url)
app.include_router(multipart_upload)


@app.get("/health")
def health():
    return {"status": "Healthy"}


@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code, content={"success": False, "error": exc.message}
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception(Common.UNHANDLED_EXCEPTION_OCCURRED_LOG)

    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": Common.GENERIC_ERROR_WITH_EXCEPTION.format(error=exc),
        },
    )


app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)
