"""Markdown extension that monkey patches the Highlight extension to hide lines in code blocks.

- Lines that end with "#! hidden" will be removed from the code block.
- Lines that start with '<chainmock' and end with '>' will be removed from the code block.
- If code block starts with "#! remove-prefix":
    - Remove ">>>" and "..." from the code blocks.
    - Add line separator to Tracebacks in code blocks.

Zensical does not support MkDocs hooks, so this is loaded as a Markdown extension instead.
"""

from typing import Any

from markdown import Markdown
from markdown.extensions import Extension
from pymdownx import highlight


def _hide_lines(src: str) -> str:
    src = "".join(
        line for line in src.splitlines(keepends=True) if not line.strip().endswith("#! hidden")
    )
    src = "".join(
        line
        for line in src.splitlines(keepends=True)
        if not (line.strip().startswith("<chainmock") and line.strip().endswith(">"))
    )
    if src.startswith("#! remove-prefix"):
        new_src = ""
        for line in src.splitlines():
            if line.startswith("#! remove-prefix"):
                continue
            if line.startswith((">>> ", "... ")):
                new_src += line[4:] + "\n"
            elif line.startswith((">>>", "...")):
                new_src += line[3:] + "\n"
            elif line.startswith("Traceback (most recent call last):"):
                new_src += f"|\n{line}\n"
            else:
                new_src += line + "\n"
        return new_src
    return src


_patched = False


def _patch_highlight() -> None:
    global _patched  # noqa: PLW0603
    if _patched:
        return
    original = highlight.Highlight.highlight

    def patched(self: Any, src: str, *args: Any, **kwargs: Any) -> Any:
        return original(self, _hide_lines(src), *args, **kwargs)

    highlight.Highlight.highlight = patched
    _patched = True


class HideLinesExtension(Extension):
    """Hide lines in highlighted code blocks."""

    def extendMarkdown(self, md: Markdown) -> None:  # noqa: ARG002, N802
        """Patch the Highlight extension before any code block is rendered."""
        _patch_highlight()


def makeExtension(**kwargs: Any) -> HideLinesExtension:  # noqa: N802
    """Return the extension instance for Python-Markdown."""
    return HideLinesExtension(**kwargs)
