"""FastAPI application entry point."""

from dotenv import load_dotenv

load_dotenv()
import sys
from pathlib import Path

# When running app/main.py directly (e.g. `python app/main.py`), Python
# doesn't treat `app` as an installed package, so `from app import ...`
# fails. Add project root to sys.path as a fallback so package imports work
# when invoked directly (this keeps behavior consistent for debugging).
project_root = Path(__file__).resolve().parents[1]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.routes import eval
from app.config.config import get_settings
from app.utils.logger import get_logger, setup_logging

settings = get_settings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    setup_logging(settings.log_level)
    logger = get_logger(__name__)
    logger.info(f"Starting {settings.app_name}")
    logger.info(f"Log level: {settings.log_level}")

    yield

    # Shutdown
    logger.info("Shutting down application")


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    description="""
## RAG Evaluation Service (FastAPI)

A **production-ready, reusable Evaluation Microservice** for **RAG / Chatbot systems**, 
designed to be shared across **multiple projects** without requiring **ground-truth reference answers**.
This service evaluates:
- Retriever quality
- Hallucination risk
- Answer relevance

All evaluations run **asynchronously**, without blocking user responses.
    """,
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include routers
app.include_router(eval.router)


@app.get("/", tags=["Root"])
async def root():
    """Serve the main UI."""
  
    return {"message": "Welcome to the RAG Evaluation Service. Visit /docs for API documentation."}


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler."""
    logger = get_logger(__name__)
    logger.error(f"Unhandled exception: {exc}", exc_info=True)

    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": str(exc),
        },
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True,
    )
