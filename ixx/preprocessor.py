"""
IXX preprocessor: converts dash-based indentation to space-based indentation.

A user writes:
    if bomb is YES
    - say "Kill Player"
    -- say "Really dead"

The preprocessor turns that into:
    if bomb is YES
        say "Kill Player"
            say "Really dead"

so the standard Lark Indenter can measure depth as usual.

Rules:
  - Lines that start with one or more dashes (optionally followed by a space)
    are converted: each dash = 4 spaces of indentation.
  - Blank and whitespace-only lines are stripped (they would confuse the Lark
    Indenter by emitting a spurious DEDENT mid-block).
  - Comment lines (starting with #) and all other lines pass through unchanged.

Known limitation: stripping blank lines shifts source line numbers, so syntax
error messages will cite the post-processed line number rather than the
original.  A source-line map can be added in a future release if needed.
"""

from __future__ import annotations
import re

_DASH_LINE = re.compile(r'^(-+)\s*(.*)', re.DOTALL)


def preprocess(source: str) -> str:
    """Convert dash-prefixed lines to space-indented lines and strip blank lines."""
    lines = source.split('\n')
    out = []
    for line in lines:
        # Strip blank / whitespace-only lines before Lark's Indenter sees them.
        # Blank lines inside blocks would emit a spurious DEDENT token.
        if line.strip() == '':
            continue
        m = _DASH_LINE.match(line)
        if m:
            depth = len(m.group(1))
            content = m.group(2)
            out.append('    ' * depth + content)
        else:
            out.append(line)
    return '\n'.join(out)
