import hashlib
import secrets
from pathlib import Path

import typer
from dotenv import load_dotenv, set_key
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text


app = typer.Typer(add_completion=False, no_args_is_help=True)
console = Console()


def sha256_hex(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def get_project_root() -> Path:
    # This file lives in <root>/tools/, so parent of parent is root
    return Path(__file__).resolve().parents[1]


@app.command(help="Generate a new API key, print it, and store its SHA-256 in .env")
def main(
    bytes_length: int = typer.Option(
        32,
        "--bytes",
        min=16,
        help="Number of random bytes for key generation (token_urlsafe).",
    ),
    env_var: str = typer.Option(
        "MASTER_API_KEY_SHA256",
        "--env-var",
        help="Environment variable name to write the hash to.",
    ),
):
    project_root = get_project_root()
    env_path = project_root.parent / ".env" # Place on the .env at the same level as the docker compose file

    # Load existing .env (non-fatal if missing)
    load_dotenv(dotenv_path=env_path)

    # Generate secure API key
    api_key = secrets.token_urlsafe(bytes_length)
    api_key_hash = sha256_hex(api_key)

    # Persist the hash to .env (creates the file if it does not exist)
    set_key(str(env_path), env_var, api_key_hash)

    # Pretty terminal output
    title = Text("API Key Generated", style="bold green")

    table = Table(show_header=False, box=None, padding=(0, 1))
    table.add_row(Text("Project root:", style="bold cyan"), str(project_root))
    table.add_row(Text(".env path:", style="bold cyan"), str(env_path))
    table.add_row(Text("Env var:", style="bold cyan"), env_var)
    table.add_row(Text("SHA-256 hash:", style="bold cyan"), api_key_hash)

    key_panel = Panel(
        Text(api_key, style="bold yellow"),
        title="Raw API Key (copy and store securely)",
        border_style="yellow",
        padding=(1, 2),
    )

    console.print(Panel(title, border_style="green"))
    console.print(key_panel)
    console.print(Panel(table, title="Details", border_style="cyan"))

    console.print(
        Text(
            "Note: The raw key is NOT stored on disk. Only its hash was written to .env.",
            style="dim",
        )
    )


if __name__ == "__main__":
    app()