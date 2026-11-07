from __future__ import annotations

import logging
import os
import time
import uuid
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from backend.app.api.documents import router as documents_router
from backend.app.api.export import router as export_router
from backend.app.api.research import router as research_router
from backend.app.config import get_settings
from backend.app.db import init_db
from backend.app.schemas import HealthResponse

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format='{"time": "%(asctime)s", "level": "%(levelname)s", "logger": "%(name)s", "message": "%(message)s"}',
)
logger = logging.getLogger("scoutai")
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    logger.info("Initializing database and storage directories...")
    init_db()
    os.makedirs(settings.effective_upload_dir, exist_ok=True)
    os.makedirs(settings.effective_chroma_dir, exist_ok=True)
    yield
    logger.info("Shutting down ScoutAI service...")


app = FastAPI(
    title="ScoutAI API",
    description="Autonomous Competitor & Market Research Intelligence Agent",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request ID, Security Headers & Optional Auth Middleware
@app.middleware("http")
async def scoutai_security_middleware(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
    request.state.request_id = request_id

    # Optional API key authentication
    if settings.APP_API_KEY:
        path = request.url.path
        if path.startswith("/api") and path not in (
            "/api/health",
            "/api/openapi.json",
            "/api/docs",
        ):
            client_key = request.headers.get("X-API-Key")
            if client_key != settings.APP_API_KEY:
                return JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content={
                        "error": {
                            "code": "unauthorized",
                            "message": "Invalid or missing X-API-Key header.",
                        }
                    },
                    headers={"X-Request-ID": request_id},
                )

    start_time = time.time()
    try:
        response = await call_next(request)
    except Exception as exc:
        logger.exception(f"Unhandled exception on {request.method} {request.url.path}: {exc}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": {
                    "code": "internal_error",
                    "message": "An unexpected server error occurred.",
                }
            },
            headers={"X-Request-ID": request_id},
        )

    duration_ms = round((time.time() - start_time) * 1000, 2)
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Server-Timing"] = f"total;dur={duration_ms}"

    return response


# Consistent Exception Handler
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    detail = exc.detail
    if isinstance(detail, dict) and "error" in detail:
        content = detail
    else:
        content = {"error": {"code": "http_error", "message": str(detail)}}
    return JSONResponse(
        status_code=exc.status_code,
        content=content,
        headers={"X-Request-ID": getattr(request.state, "request_id", "")},
    )


# Health Check
@app.get("/api/health", response_model=HealthResponse, tags=["system"])
def health_check() -> HealthResponse:
    has_key = bool(settings.effective_gemini_key)
    search_prov = "Tavily" if settings.TAVILY_API_KEY else "DuckDuckGo"
    return HealthResponse(
        status="ok",
        gemini_configured=has_key,
        gemini_model=settings.GEMINI_MODEL,
        search_provider=search_prov,
        demo_mode=settings.DEMO_MODE,
    )


# Register API Routers
app.include_router(research_router, prefix="/api")
app.include_router(export_router, prefix="/api")
app.include_router(documents_router, prefix="/api")

# Static files & SPA mounting
static_dir = os.path.abspath(settings.STATIC_DIR)
if os.path.isdir(static_dir):
    app.mount("/assets", StaticFiles(directory=os.path.join(static_dir, "assets")), name="assets")

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        # Do not intercept /api routes
        if full_path.startswith("api"):
            raise HTTPException(status_code=404, detail="API endpoint not found")

        file_path = os.path.join(static_dir, full_path)
        if full_path and os.path.isfile(file_path):
            return FileResponse(file_path)

        index_file = os.path.join(static_dir, "index.html")
        if os.path.isfile(index_file):
            return FileResponse(index_file)

        return JSONResponse({"status": "ScoutAI API active. Frontend assets building..."})
else:

    @app.get("/")
    def index_root():
        return {
            "app": "ScoutAI - AI Competitor & Market Research Agent",
            "docs": "/docs",
            "health": "/api/health",
        }
