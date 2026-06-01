import re
from dataclasses import dataclass, field


@dataclass
class GeneratedFile:
    path: str
    content: str


@dataclass
class ParsedProject:
    raw_response: str
    files: list[GeneratedFile] = field(default_factory=list)
    architecture_summary: str = ""
    extension_notes: str = ""
    parse_warnings: list[str] = field(default_factory=list)


_FILE_BLOCK_RE = re.compile(
    r"<<<FILE:\s*(?P<path>[^\n>]+?)>>>\n(?P<content>.*?)<<<ENDFILE>>>",
    re.DOTALL,
)

_EXTENSION_NOTES_RE = re.compile(
    r"<<<EXTENSION_NOTES>>>\n(?P<notes>.*?)<<<END>>>",
    re.DOTALL,
)

_ARCH_SUMMARY_RE = re.compile(
    r"(?:=== ARCHITECTURE[_\s]SUMMARY ===|=== ARCHITECTURE ===|## Architecture(?:\s+Decision)?(?:\s+Summary)?)"
    r"\s*\n(?P<summary>.*?)(?=\n===|\n##|\n<<<|$)",
    re.DOTALL | re.IGNORECASE,
)


def parse_response(raw: str) -> ParsedProject:
    project = ParsedProject(raw_response=raw)

    arch_match = _ARCH_SUMMARY_RE.search(raw)
    if arch_match:
        project.architecture_summary = arch_match.group("summary").strip()

    notes_match = _EXTENSION_NOTES_RE.search(raw)
    if notes_match:
        project.extension_notes = notes_match.group("notes").strip()

    file_matches = list(_FILE_BLOCK_RE.finditer(raw))
    if not file_matches:
        project.parse_warnings.append(
            "No <<<FILE: ...>>> blocks found in the response. "
            "The model may not have followed the output format."
        )
        return project

    seen_paths: set[str] = set()
    for m in file_matches:
        path = m.group("path").strip().replace("\\", "/")
        content = m.group("content")

        if not content.endswith("\n"):
            content += "\n"

        if path in seen_paths:
            project.parse_warnings.append(f"Duplicate file path skipped: {path}")
            continue

        seen_paths.add(path)
        project.files.append(GeneratedFile(path=path, content=content))

    return project
