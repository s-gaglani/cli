#!/usr/bin/env python3
"""
backend-gen — Django REST Framework backend scaffold generator.

Usage:
  python -m generator generate -f story.txt
  python -m generator generate -f story.txt -o ./my_project
  python -m generator generate "inline user story"
  python -m generator generate              # interactive prompt
  python -m generator generate --dry-run -f story.txt
"""

import pathlib
import sys

import click
from rich.console import Console
from rich.panel import Panel

from .core import generate_project
from .parser import parse_response
from .writer import print_summary, write_project

console = Console(highlight=False)


def _read_story_file(path: pathlib.Path) -> str:
    suffix = path.suffix.lower()
    if suffix in (".docx", ".docs"):
        try:
            import docx
        except ImportError:
            raise click.ClickException(
                "python-docx is required to read Word files.\n"
                "Install it with: pip install python-docx"
            )
        doc = docx.Document(str(path))
        return "\n".join(p.text for p in doc.paragraphs if p.text.strip())
    return path.read_text(encoding="utf-8")

MODELS = [
    "claude-opus-4-7",
    "claude-sonnet-4-6",
    "claude-haiku-4-5-20251001",
]


@click.group()
def cli() -> None:
    """backend-gen: Generate production-grade Django REST Framework projects from a user story."""


@cli.command()
@click.argument("user_story", required=False)
@click.option(
    "-f", "--file",
    "story_file",
    default=None,
    help="Path to a text file containing the user story.",
    type=click.Path(exists=True, dir_okay=False, readable=True),
)
@click.option(
    "-o", "--output-dir",
    default=".",
    show_default=True,
    help="Directory where the project will be created.",
    type=click.Path(file_okay=False),
)
@click.option(
    "-m", "--model",
    default="claude-sonnet-4-6",
    show_default=True,
    help="Claude model to use for generation.",
    type=click.Choice(MODELS, case_sensitive=False),
)
@click.option(
    "--dry-run",
    is_flag=True,
    default=False,
    help="Print the generated content without writing any files.",
)
@click.option(
    "--no-stream",
    is_flag=True,
    default=False,
    help="Collect response silently, then print summary.",
)
@click.option(
    "--save-response",
    default=None,
    help="Save the raw Claude response to this file path (useful for debugging).",
    type=click.Path(dir_okay=False),
)
@click.option(
    "--mock",
    is_flag=True,
    default=False,
    help="Use a built-in canned response instead of calling the API (no API key needed).",
)
def generate(
    user_story: str | None,
    story_file: str | None,
    output_dir: str,
    model: str,
    dry_run: bool,
    no_stream: bool,
    save_response: str | None,
    mock: bool,
) -> None:
    """Generate a full backend project from USER_STORY or a -f FILE.

    Priority: --file > inline argument > interactive prompt.
    """
    if story_file:
        user_story = _read_story_file(pathlib.Path(story_file)).strip()
        console.print(f"[dim]User story loaded from {story_file} ({len(user_story):,} chars)[/dim]")
    elif not user_story:
        console.print("[bold]Enter your user story[/bold] (press Enter twice when done):\n")
        lines: list[str] = []
        try:
            while True:
                line = input()
                if line == "" and lines and lines[-1] == "":
                    break
                lines.append(line)
        except (KeyboardInterrupt, EOFError):
            console.print("\n[red]Aborted.[/red]")
            sys.exit(1)
        user_story = "\n".join(lines).strip()

    if not user_story.strip():
        console.print("[red]Error:[/red] User story cannot be empty.")
        sys.exit(1)

    out = pathlib.Path(output_dir).resolve()

    story_source = story_file if story_file else "inline / interactive"
    mock_label = " (mock)" if mock else ""
    console.print(
        Panel.fit(
            f"[bold]Story:[/bold] {story_source}\n"
            f"[bold]Model:[/bold] {model}{mock_label}\n"
            f"[bold]Output:[/bold] {out}\n"
            f"[bold]Dry-run:[/bold] {dry_run}",
            title="[bold cyan]backend-gen[/bold cyan]",
        )
    )
    console.print()
    label = "Using mock response — no API call" if mock else "Generating — streaming Claude response"
    console.rule(f"[dim]{label}[/dim]")
    console.print()

    try:
        raw = generate_project(user_story, model=model, show_stream=not no_stream, mock=mock)
    except EnvironmentError as exc:
        console.print(f"\n[red]Configuration error:[/red] {exc}")
        sys.exit(1)
    except Exception as exc:
        console.print(f"\n[red]API error:[/red] {exc}")
        sys.exit(1)

    if save_response:
        pathlib.Path(save_response).write_text(raw, encoding="utf-8")
        console.print(f"\n[dim]Raw response saved to {save_response}[/dim]")

    console.print()
    console.rule("[dim]Parsing response[/dim]")

    project = parse_response(raw)

    if not project.files:
        console.print("[red]Error:[/red] No files were parsed from the response.")
        if project.parse_warnings:
            for w in project.parse_warnings:
                console.print(f"  [yellow]•[/yellow] {w}")
        console.print(
            "\n[dim]Tip: use --save-response response.txt to inspect the raw output.[/dim]"
        )
        sys.exit(1)

    console.print(f"[green]OK[/green] Parsed {len(project.files)} files.")

    if dry_run:
        console.rule("[bold yellow]Dry Run — files not written[/bold yellow]")
        for f in project.files:
            console.print(f"  [cyan]{f.path}[/cyan] ({len(f.content):,} chars)")
        if project.parse_warnings:
            for w in project.parse_warnings:
                console.print(f"[yellow]Warning:[/yellow] {w}")
        return

    console.rule("[dim]Writing files[/dim]")
    written = write_project(project, out)
    console.print()
    print_summary(project, written, out)


def main() -> None:
    cli()


if __name__ == "__main__":
    main()
