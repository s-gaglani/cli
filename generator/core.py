import os
import pathlib
import time
from typing import Iterator

import anthropic
from rich.console import Console

console = Console(highlight=False)

_PROMPT_PATH = pathlib.Path(__file__).parent.parent / "prompt.md"

_OUTPUT_FORMAT_ADDENDUM = """
--------------------------------------------------
OUTPUT FORMAT — FOLLOW EXACTLY
--------------------------------------------------

After your architecture summary, emit every file using this exact block format:

<<<FILE: relative/path/to/file>>>
file content here
<<<ENDFILE>>>

Rules:
- relative/path/to/file must be relative to the project/service root (no leading slash)
- Do NOT wrap content in markdown fences inside file blocks
- Every file mentioned in the folder structure must be emitted
- Emit ALL files — no omissions, no "same as above", no "..." placeholders
- After all files, add an EXTENSION_NOTES section:

<<<EXTENSION_NOTES>>>
notes here
<<<END>>>
"""


def _load_system_prompt() -> str:
    if not _PROMPT_PATH.exists():
        raise FileNotFoundError(f"prompt.md not found at {_PROMPT_PATH}")
    return _PROMPT_PATH.read_text(encoding="utf-8") + _OUTPUT_FORMAT_ADDENDUM


def stream_generation(
    user_story: str,
    model: str = "claude-sonnet-4-6",
) -> Iterator[str]:
    """Yield raw text chunks from the Claude API as they stream in."""
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise EnvironmentError(
            "ANTHROPIC_API_KEY environment variable is not set.\n"
            "Export it with: set ANTHROPIC_API_KEY=sk-ant-..."
        )

    system_prompt = _load_system_prompt()
    client = anthropic.Anthropic(api_key=api_key)

    with client.messages.stream(
        model=model,
        max_tokens=16000,
        system=system_prompt,
        messages=[{"role": "user", "content": user_story}],
    ) as stream:
        for text in stream.text_stream:
            yield text


def _mock_stream() -> Iterator[str]:
    """Yield the canned mock response word-by-word to simulate streaming."""
    from .mock import MOCK_RESPONSE

    words = MOCK_RESPONSE.split(" ")
    for i, word in enumerate(words):
        yield word + (" " if i < len(words) - 1 else "")
        if i % 40 == 0:
            time.sleep(0.01)


def generate_project(
    user_story: str,
    model: str = "claude-sonnet-4-6",
    show_stream: bool = True,
    mock: bool = False,
) -> str:
    """Call Claude (or use mock), optionally stream to terminal, return full response."""
    chunks: list[str] = []
    source = _mock_stream() if mock else stream_generation(user_story, model=model)

    for chunk in source:
        chunks.append(chunk)
        if show_stream:
            console.print(chunk, end="", highlight=False, markup=False)

    if show_stream:
        console.print()

    return "".join(chunks)
