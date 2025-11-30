"""
CLI entry point for markdown-vault.

Provides command-line interface for:
- Starting the server with uvicorn
- Configuration management
- SSL certificate handling
"""

import logging
import sys
from pathlib import Path

import typer
import uvicorn
from rich.console import Console
from rich.logging import RichHandler
from rich.panel import Panel

from markdown_vault.core.config import AppConfig, ConfigError, load_config
from markdown_vault.main import create_app

app = typer.Typer(
    name="markdown-vault",
    help="REST API service compatible with Obsidian API",
    add_completion=False,
)

console = Console()


def setup_logging(config: AppConfig) -> None:
    """
    Set up logging based on configuration.

    Args:
        config: Application configuration
    """
    log_level = getattr(logging, config.logging.level)

    if config.logging.format == "json":
        # JSON logging format
        logging.basicConfig(
            level=log_level,
            format="%(message)s",
            handlers=[
                logging.FileHandler(config.logging.file)
                if config.logging.file
                else logging.StreamHandler()
            ],
        )
    else:
        # Rich text logging format
        logging.basicConfig(
            level=log_level,
            format="%(message)s",
            datefmt="[%X]",
            handlers=[RichHandler(console=console, rich_tracebacks=True)],
        )


@app.command()
def start(
    config_file: str | None = typer.Option(
        None,
        "--config",
        "-c",
        help="Path to YAML configuration file",
        envvar="MARKDOWN_VAULT_CONFIG",
    ),
    host: str | None = typer.Option(
        None,
        "--host",
        "-h",
        help="Server bind address (overrides config)",
    ),
    port: int | None = typer.Option(
        None,
        "--port",
        "-p",
        help="Server port (overrides config)",
    ),
    reload: bool = typer.Option(
        False,
        "--reload",
        "-r",
        help="Enable auto-reload on code changes (development only)",
    ),
) -> None:
    """
    Start the markdown-vault server.

    Loads configuration, sets up SSL certificates if needed, and starts
    the HTTPS server using uvicorn.

    Examples:
        # Start with default configuration
        $ markdown-vault start

        # Start with custom config file
        $ markdown-vault start --config config.yaml

        # Override host and port
        $ markdown-vault start --host 0.0.0.0 --port 8080

        # Development mode with auto-reload
        $ markdown-vault start --reload
    """
    try:
        # Load configuration
        console.print("[bold blue]Loading configuration...[/bold blue]")
        config = load_config(config_file)

        # Apply CLI overrides
        if host:
            config.server.host = host
        if port:
            config.server.port = port
        if reload:
            config.server.reload = reload

        # Setup logging
        setup_logging(config)

        # Display startup information
        startup_info = f"""
[bold green]markdown-vault Server[/bold green]

[bold]Configuration:[/bold]
  Host:       {config.server.host}
  Port:       {config.server.port}
  HTTPS:      {config.server.https}
  Vault:      {config.vault.path if config.vault else "Not configured"}
  Log Level:  {config.logging.level}

[bold]Security:[/bold]
  API Key:    {"Configured" if config.security.api_key else "Not configured"}
  Cert Path:  {config.security.cert_path}
  Key Path:   {config.security.key_path}
"""
        console.print(Panel(startup_info.strip(), expand=False))

        # Warn if API key was auto-generated
        if config.security.api_key and not config_file:
            console.print(
                "\n[bold yellow]⚠️  API Key Auto-Generated[/bold yellow]",
                style="yellow",
            )
            console.print(
                f"[yellow]API Key: {config.security.api_key}[/yellow]\n",
            )
            console.print(
                "[yellow]Save this key! Set it via config file or "
                "MARKDOWN_VAULT_SECURITY__API_KEY environment variable.[/yellow]\n"
            )

        # Create the FastAPI app
        fastapi_app = create_app(config)

        # Configure uvicorn
        uvicorn_config = {
            "app": fastapi_app,
            "host": config.server.host,
            "port": config.server.port,
            "reload": config.server.reload,
            "log_level": config.logging.level.lower(),
            "access_log": config.logging.level == "DEBUG",
        }

        # Add SSL if HTTPS is enabled
        if config.server.https:
            cert_path = Path(config.security.cert_path).expanduser().resolve()
            key_path = Path(config.security.key_path).expanduser().resolve()

            uvicorn_config.update(
                {
                    "ssl_keyfile": str(key_path),
                    "ssl_certfile": str(cert_path),
                }
            )

            protocol = "https"
        else:
            protocol = "http"

        # Display server URL
        console.print(
            f"\n[bold green]✓[/bold green] Server starting at "
            f"[bold]{protocol}://{config.server.host}:{config.server.port}[/bold]\n"
        )

        if config.logging.level == "DEBUG":
            console.print(
                f"[dim]API Docs: {protocol}://{config.server.host}:{config.server.port}/docs[/dim]\n"
            )

        # Start server
        uvicorn.run(**uvicorn_config)

    except ConfigError as e:
        console.print(f"[bold red]Configuration Error:[/bold red] {e}", style="red")
        raise typer.Exit(code=1)
    except KeyboardInterrupt:
        console.print("\n[yellow]Server stopped by user[/yellow]")
        raise typer.Exit(code=0)
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}", style="red")
        if "--debug" in sys.argv:
            raise
        raise typer.Exit(code=1)


@app.command()
def version() -> None:
    """Show version information."""
    console.print("[bold]markdown-vault[/bold] version [green]0.2.0[/green]")


def main() -> None:
    """Main entry point."""
    app()


if __name__ == "__main__":
    main()
