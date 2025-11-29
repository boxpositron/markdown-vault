"""
FastAPI application factory for markdown-vault.

This module creates and configures the FastAPI application with:
- CORS middleware for cross-origin requests
- Error handling middleware
- API router registration
- Startup/shutdown event handlers
- OpenAPI documentation configuration
"""

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from markdown_vault.core.active_file import ActiveFileManager
from markdown_vault.core.config import AppConfig, ConfigError

# Global configuration instance
_app_config: AppConfig | None = None

# Global active file manager instance
_active_file_manager: ActiveFileManager | None = None

logger = logging.getLogger(__name__)


def get_app_config() -> AppConfig:
    """
    Get the global application configuration.

    Returns:
        The application configuration instance

    Raises:
        RuntimeError: If configuration has not been initialized
    """
    if _app_config is None:
        raise RuntimeError(
            "Application configuration not initialized. "
            "Call create_app() with a config parameter first."
        )
    return _app_config


def set_app_config(config: AppConfig) -> None:
    """
    Set the global application configuration.

    Args:
        config: Application configuration instance
    """
    global _app_config
    _app_config = config


def get_active_file_manager() -> ActiveFileManager:
    """
    Get the global active file manager.

    Returns:
        The active file manager instance

    Raises:
        RuntimeError: If active file manager has not been initialized
    """
    if _active_file_manager is None:
        raise RuntimeError(
            "Active file manager not initialized. Call create_app() first."
        )
    return _active_file_manager


def set_active_file_manager(manager: ActiveFileManager) -> None:
    """
    Set the global active file manager.

    Args:
        manager: Active file manager instance
    """
    global _active_file_manager
    _active_file_manager = manager


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Application lifespan manager.

    Handles startup and shutdown events for the FastAPI application.

    Args:
        app: FastAPI application instance

    Yields:
        None
    """
    # Startup
    config = get_app_config()
    logger.info(
        f"Starting markdown-vault server",
        extra={
            "host": config.server.host,
            "port": config.server.port,
            "https": config.server.https,
            "vault_path": config.vault.path if config.vault else None,
        },
    )

    yield

    # Shutdown
    logger.info("Shutting down markdown-vault server")


async def config_error_handler(request: Request, exc: ConfigError) -> JSONResponse:
    """
    Handle configuration errors.

    Args:
        request: The request that triggered the error
        exc: The configuration error

    Returns:
        JSON response with error details
    """
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Configuration Error",
            "message": str(exc),
            "type": "config_error",
        },
    )


async def validation_error_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """
    Handle request validation errors.

    Args:
        request: The request that triggered the error
        exc: The validation error

    Returns:
        JSON response with validation error details
    """
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "Validation Error",
            "message": "Invalid request parameters",
            "details": exc.errors(),
            "type": "validation_error",
        },
    )


async def generic_error_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Handle generic unhandled exceptions.

    Args:
        request: The request that triggered the error
        exc: The exception

    Returns:
        JSON response with error details
    """
    logger.exception("Unhandled exception", exc_info=exc)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal Server Error",
            "message": "An unexpected error occurred",
            "type": "internal_error",
        },
    )


def create_app(config: AppConfig) -> FastAPI:
    """
    Create and configure the FastAPI application.

    Args:
        config: Application configuration

    Returns:
        Configured FastAPI application instance
    """
    # Store configuration globally
    set_app_config(config)

    # Initialize active file manager
    set_active_file_manager(ActiveFileManager())

    # Create FastAPI app with metadata
    app = FastAPI(
        title="markdown-vault",
        description=(
            "Drop-in replacement for Obsidian Local REST API with standalone "
            "service capabilities. Provides a REST API for managing markdown "
            "notes, supporting Obsidian vault compatibility and advanced features."
        ),
        version="0.1.0",
        lifespan=lifespan,
        docs_url="/docs" if config.logging.level == "DEBUG" else None,
        redoc_url="/redoc" if config.logging.level == "DEBUG" else None,
        openapi_url="/openapi.json" if config.logging.level == "DEBUG" else None,
    )

    # Configure CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # In production, configure specific origins
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["*"],
    )

    # Register error handlers
    app.add_exception_handler(ConfigError, config_error_handler)
    app.add_exception_handler(RequestValidationError, validation_error_handler)
    app.add_exception_handler(Exception, generic_error_handler)

    # Register API routers
    from markdown_vault.api.routes import active, periodic, search, system, vault

    app.include_router(system.router, tags=["system"])
    app.include_router(vault.router, tags=["vault"])
    app.include_router(active.router, tags=["active"])
    app.include_router(periodic.router, tags=["periodic"])
    app.include_router(search.router, tags=["search"])

    # Add health check endpoint
    @app.get("/health", tags=["system"])
    async def health_check() -> dict[str, str]:
        """
        Health check endpoint.

        Returns:
            Status information
        """
        return {"status": "ok", "version": "0.1.0"}

    return app


__all__ = [
    "create_app",
    "get_app_config",
    "set_app_config",
    "get_active_file_manager",
    "set_active_file_manager",
]
