"""Hook that monkey patches the Highlight extension to hide lines in code blocks.

- Lines that end with "#! hidden" will be removed from the code block.
- Lines that start with '<chainmock' and end with '>' will be removed from the code block.
- If code block starts with "#! remove-prefix":
    - Remove ">>>" and "..." from the code blocks.
    - Add line separator to Tracebacks in code blocks.
"""

from typing import Any

import mkdocs.plugins
from pymdownx import highlight  # type: ignore


@mkdocs.plugins.event_priority(0)
# pylint: disable=unused-argument
def on_startup(command: str, dirty: bool) -> None:
    """Monkey patch Highlight extension to hide lines in code blocks."""
    original = highlight.Highlight.highlight

    def patched(self: Any, src: str, *args: Any, **kwargs: Any) -> Any:
        src = "".join(
            line for line in src.splitlines(keepends=True) if not line.strip().endswith("#! hidden")
        )
        src = "".join(
            line for line in src.splitlines(keepends=True) if not (line.strip().startswith("<chainmock") and line.strip().endswith(">"))
        )
        if src.startswith("#! remove-prefix"):
            new_src = ""
            for line in src.splitlines():
                if line.startswith("#! remove-prefix"):
                    continue
                elif line.startswith(">>> ") or line.startswith("... "):
                    new_src += line[4:] + "\n"
                elif line.startswith(">>>") or line.startswith("..."):
                    new_src += line[3:] + "\n"
                elif line.startswith("Traceback (most recent call last):"):
                    new_src += f"|\n{line}\n"
                else:
                    new_src += line + "\n"
            return original(self, new_src, *args, **kwargs)
        return original(self, src, *args, **kwargs)

    highlight.Highlight.highlight = patched
