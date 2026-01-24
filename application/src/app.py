from dotenv import load_dotenv

load_dotenv()
import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from src.controller.audits_controller import router as audit_router
from src.controller.auth_controller import router as auth_router
from src.controller.documents_controller import router as document_router
from src.controller.presigned_controller import router as presigned_url
from src.exceptions.app_exceptions import AppException

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Docs Approvel",
    summary="""
        A FastApi based Documents Approvel System
    """,
    version="v1",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(auth_router)
app.include_router(audit_router)
app.include_router(document_router)
app.include_router(presigned_url)


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
    logger.exception("Unhandled exception occurred")

    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "Something went wrong. Please try again later.",
        },
    )
