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
original.  Use ``preprocess_with_map`` and ``_apply_line_map`` (in
``ixx/__main__.py``) to translate preprocessed line numbers back to original
source lines before displaying them to the user.  This is done automatically
for ``ixx check`` and ``ixx check --json`` output.
"""

from __future__ import annotations
import re

_DASH_LINE = re.compile(r'^(-+)\s*(.*)', re.DOTALL)


def preprocess(source: str) -> str:
    """Convert dash-prefixed lines to space-indented lines and strip blank lines."""
    preprocessed, _ = preprocess_with_map(source)
    return preprocessed


def preprocess_with_map(source: str) -> tuple[str, dict[int, int]]:
    """Preprocess *source* and return ``(preprocessed_source, line_map)``.

    ``line_map`` maps 1-indexed preprocessed line numbers to their
    corresponding 1-indexed original source line numbers.  Because blank lines
    are stripped, every preprocessed line number is >= the same original line
    number, so checker error lines need this map to point back to the editor
    line the user sees.

    Example::

        original  preprocessed  line_map
        1  x = 1  →  1  x = 1  {1: 1}
        2          (blank, stripped)
        3  say x  →  2  say x  {1: 1, 2: 3}
    """
    # Strip UTF-8 BOM (EF BB BF / U+FEFF) that some editors prepend to files.
    source = source.lstrip('\ufeff')
    lines = source.split('\n')
    out: list[str] = []
    line_map: dict[int, int] = {}  # preprocessed_lineno → original_lineno

    for orig_idx, line in enumerate(lines, start=1):
        # Strip blank / whitespace-only lines before Lark's Indenter sees them.
        if line.strip() == '':
            continue
        m = _DASH_LINE.match(line)
        if m:
            depth = len(m.group(1))
            content = m.group(2)
            out.append('    ' * depth + content)
        else:
            out.append(line)
        # Record which original line this preprocessed line came from.
        line_map[len(out)] = orig_idx

    return '\n'.join(out), line_map
