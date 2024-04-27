"""Hook that monkey patches the Highlight extension to hide lines in code blocks.

Lines that end with "#! hidden" will be removed from the code block.
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
        return original(self, src, *args, **kwargs)

    highlight.Highlight.highlight = patched
