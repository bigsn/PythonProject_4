"""FastAPI application factory and router registration."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from pythonproject_4.db import init_db
from pythonproject_4.api.endpoints import router as api_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database on startup."""
    logger.info("Initializing database...")
    init_db()
    logger.info("Database initialized.")
    yield
    logger.info("Shutting down...")


app = FastAPI(
    title="AINEWS",
    description="AI-генератор постов для Telegram",
    version="0.1.0",
    lifespan=lifespan,
)

# Include API router
app.include_router(api_router)


def main():
    """Entry point for running the app."""
    import uvicorn
    from pythonproject_4.config import get_settings
    settings = get_settings()
    uvicorn.run(
        "pythonproject_4.main:app",
        host=settings.APP_HOST,
        port=settings.APP_PORT,
        reload=True,
    )


if __name__ == "__main__":
    main()
