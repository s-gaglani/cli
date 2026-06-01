import pathlib

from rich.console import Console
from rich.table import Table

from .parser import ParsedProject

console = Console(highlight=False)


def write_project(project: ParsedProject, output_dir: pathlib.Path) -> list[pathlib.Path]:
    """Write all parsed files to output_dir. Returns list of written paths."""
    if not project.files:
        console.print("[yellow]No files to write — check parse warnings.[/yellow]")
        return []

    output_dir = output_dir.resolve()
    written: list[pathlib.Path] = []

    for gen_file in project.files:
        dest = output_dir / gen_file.path
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(gen_file.content, encoding="utf-8")
        written.append(dest)

    return written


def print_summary(project: ParsedProject, written: list[pathlib.Path], output_dir: pathlib.Path) -> None:
    console.rule("[bold green]Generation Complete[/bold green]")

    if project.architecture_summary:
        console.print("\n[bold]Architecture:[/bold]")
        console.print(project.architecture_summary)
        console.print()

    table = Table(title=f"Generated Files  {output_dir}", show_lines=False)
    table.add_column("File", style="cyan", no_wrap=True)
    table.add_column("Size", justify="right", style="dim")

    for path in written:
        rel = path.relative_to(output_dir)
        size = path.stat().st_size
        table.add_row(str(rel), f"{size:,} B")

    console.print(table)
    console.print(f"\n[bold green]DONE[/bold green] {len(written)} files written to [cyan]{output_dir}[/cyan]")

    if project.parse_warnings:
        console.print()
        for w in project.parse_warnings:
            console.print(f"[yellow]Warning:[/yellow] {w}")

    if project.extension_notes:
        console.print("\n[bold]Extension Notes:[/bold]")
        console.print(project.extension_notes)
