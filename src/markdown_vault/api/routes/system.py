"""
System API routes for markdown-vault.

This module provides system-level endpoints:
- GET / - Server status (no authentication required)
- GET /openapi.yaml - OpenAPI specification (authenticated)
- GET /obsidian-local-rest-api.crt - SSL certificate download (authenticated)
"""

import logging
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import FileResponse, PlainTextResponse

import yaml

from markdown_vault.api.deps import ApiKeyDep, ConfigDep, get_config
from markdown_vault.models.api import ServerStatus

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get(
    "/",
    response_model=ServerStatus,
    summary="Server status",
    description=(
        "Returns server status information including authentication state and "
        "version information. This endpoint does NOT require authentication and "
        "can be used to verify server availability."
    ),
    tags=["system"],
)
async def get_server_status(
    request: Request,
    config: ConfigDep,
) -> ServerStatus:
    """
    Get server status and authentication state.

    This is the only endpoint that doesn't require authentication.
    It can be used to check if the server is running and whether
    the request includes valid authentication.

    Args:
        request: The HTTP request
        config: Application configuration

    Returns:
        Server status information including authentication state
    """
    # Check if Authorization header is present
    auth_header = request.headers.get("Authorization")
    is_authenticated = False

    if auth_header:
        # Verify if it's a valid API key
        api_key = auth_header
        if api_key.startswith("Bearer "):
            api_key = api_key[7:]

        expected_key = config.security.api_key
        is_authenticated = expected_key is not None and api_key == expected_key

    return ServerStatus(
        ok="OK",
        service="markdown-vault",
        authenticated=is_authenticated,
        versions={
            "self": "0.1.0",
            "api": "1.0",
        },
    )


@router.get(
    "/openapi.yaml",
    response_class=PlainTextResponse,
    summary="OpenAPI specification",
    description=(
        "Returns the OpenAPI 3.0 specification for this API in YAML format. "
        "Requires authentication."
    ),
    tags=["system"],
    responses={
        200: {
            "description": "OpenAPI specification in YAML format",
            "content": {"application/yaml": {}},
        },
        401: {"description": "Authentication required"},
    },
)
async def get_openapi_spec(
    request: Request,
    api_key: ApiKeyDep,
) -> PlainTextResponse:
    """
    Get the OpenAPI specification in YAML format.

    This endpoint returns the complete OpenAPI 3.0 specification
    describing all available API endpoints, request/response models,
    and authentication requirements.

    Args:
        request: The HTTP request
        api_key: Validated API key (from dependency)

    Returns:
        OpenAPI specification as YAML
    """
    # Get the FastAPI app from the request
    app = request.app

    # Generate OpenAPI schema
    openapi_schema = app.openapi()

    # Convert to YAML
    yaml_content = yaml.dump(openapi_schema, sort_keys=False, default_flow_style=False)

    return PlainTextResponse(
        content=yaml_content,
        media_type="application/yaml",
    )


@router.get(
    "/obsidian-local-rest-api.crt",
    response_class=FileResponse,
    summary="Download SSL certificate",
    description=(
        "Downloads the SSL certificate file for the server. "
        "This certificate can be installed on clients to trust the "
        "self-signed certificate used by the server. Requires authentication."
    ),
    tags=["system"],
    responses={
        200: {
            "description": "SSL certificate file",
            "content": {"application/x-pem-file": {}},
        },
        401: {"description": "Authentication required"},
        404: {"description": "Certificate file not found"},
        500: {"description": "Certificate path not configured"},
    },
)
async def get_ssl_certificate(
    api_key: ApiKeyDep,
    config: ConfigDep,
) -> FileResponse:
    """
    Download the SSL certificate file.

    Returns the SSL certificate file that can be installed on client
    systems to trust the self-signed certificate. The certificate path
    is read from the application configuration.

    Args:
        api_key: Validated API key (from dependency)
        config: Application configuration

    Returns:
        SSL certificate file for download

    Raises:
        HTTPException: If certificate path is not configured (500)
        HTTPException: If certificate file is not found (404)
    """
    # Get certificate path from config
    cert_path_str = config.security.cert_path
    if not cert_path_str:
        logger.error("Certificate path not configured")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Certificate path not configured",
        )

    # Resolve certificate path
    cert_path = Path(cert_path_str).expanduser().resolve()

    # Check if certificate file exists
    if not cert_path.exists():
        logger.error(f"Certificate file not found: {cert_path}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Certificate file not found: {cert_path}",
        )

    if not cert_path.is_file():
        logger.error(f"Certificate path is not a file: {cert_path}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Certificate path is not a file: {cert_path}",
        )

    # Return certificate file
    logger.info(f"Serving certificate file: {cert_path}")
    return FileResponse(
        path=cert_path,
        media_type="application/x-pem-file",
        filename="obsidian-local-rest-api.crt",
        headers={
            "Content-Disposition": "attachment; filename=obsidian-local-rest-api.crt"
        },
    )


__all__ = ["router"]
