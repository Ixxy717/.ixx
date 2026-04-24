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
  - Everything else is left alone.
  - Blank lines are removed entirely — they confuse the Lark Indenter inside
    indented blocks.  They carry no semantic meaning in IXX.
  - Comment lines (starting with #) pass through unchanged.
"""

from __future__ import annotations
import re

_DASH_LINE = re.compile(r'^(-+)\s*(.*)', re.DOTALL)


def preprocess(source: str) -> str:
    """Convert dash-prefixed lines to space-indented lines and strip blank lines."""
    lines = source.split('\n')
    out = []
    for line in lines:
        m = _DASH_LINE.match(line)
        if m:
            depth = len(m.group(1))
            content = m.group(2)
            out.append('    ' * depth + content)
        else:
            out.append(line)
    # Remove blank lines — the Lark Indenter treats them as DEDENT signals inside
    # indented blocks, breaking indent tracking.  IXX has no blank-line-sensitive syntax.
    out = [l for l in out if l.strip() != ""]
    return '\n'.join(out)
