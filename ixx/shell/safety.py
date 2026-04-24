"""
IXX Shell — Format Helpers

format_bytes(n)       Human-readable byte sizes  (512 B / 1.2 KB / 14.2 GB ...)
render_table(...)     Plain-text aligned table renderer
"""

from __future__ import annotations


def format_bytes(n: int) -> str:
    """Return a human-friendly size string.

    Examples:
        512        -> "512 B"
        1_230      -> "1.2 KB"
        885_000    -> "842 KB"
        1_258_291  -> "1.2 MB"
        15_254_000 -> "14.5 MB"
    """
    if n < 0:
        return "-"
    for unit, threshold in (
        ("TB", 1 << 40),
        ("GB", 1 << 30),
        ("MB", 1 << 20),
        ("KB", 1 << 10),
    ):
        if n >= threshold:
            value = n / threshold
            if value >= 100:
                return f"{value:.0f} {unit}"
            return f"{value:.1f} {unit}"
    return f"{n} B"


def render_table(
    headers: list[str],
    rows: list[list[str]],
    *,
    min_col_width: int = 4,
) -> str:
    """Return a plain-text aligned table string.

    - All columns are left-aligned.
    - Empty or missing cells render as "-".
    - A separator line is printed beneath the header row.

    Example output:
        Adapter      IPv4
        -----------  ---------------
        Wi-Fi        192.168.1.42
        Ethernet     not connected
    """
    if not headers:
        return ""

    num_cols = len(headers)

    # Normalise rows: fill missing cells, replace blank with "-"
    clean_rows: list[list[str]] = []
    for row in rows:
        clean: list[str] = []
        for i in range(num_cols):
            cell = row[i] if i < len(row) else "-"
            clean.append(str(cell) if cell not in ("", None) else "-")
        clean_rows.append(clean)

    # Calculate column widths
    widths = [max(min_col_width, len(h)) for h in headers]
    for row in clean_rows:
        for i, cell in enumerate(row):
            widths[i] = max(widths[i], len(cell))

    def fmt_row(cells: list[str]) -> str:
        return "  ".join(c.ljust(w) for c, w in zip(cells, widths)).rstrip()

    lines = [fmt_row(headers)]
    lines.append("  ".join("-" * w for w in widths))
    for row in clean_rows:
        lines.append(fmt_row(row))

    return "\n".join(lines)
