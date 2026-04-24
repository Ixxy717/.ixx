"""
IXX Shell — Alias and normalization definitions.

Two layers of normalization:

1. PHRASE_ALIASES: multi-word token sequences → canonical token sequences.
   Applied first, before guidance lookup.  Handles reordering and cross-domain
   synonyms (e.g. "wifi ip" → "ip wifi").

2. ROOT_ALIASES: single-token root synonyms → canonical root command name.
   Applied as a fallback when phrase aliases did not match and the first token
   is not a known command.

PROTECTED_COMMANDS: commands that must never execute via loose normalization.
   Fuzzy suggestions for these are fine, but normalization will not silently
   reroute into them.
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# Protected — never normalize INTO these
# ---------------------------------------------------------------------------

PROTECTED_COMMANDS: frozenset[str] = frozenset([
    "delete", "kill", "copy", "move", "native", "ssh", "server", "servers",
])

# ---------------------------------------------------------------------------
# Root-level single-token aliases (safe commands only)
# ---------------------------------------------------------------------------

ROOT_ALIASES: dict[str, str] = {
    "memory":    "ram",
    "processor": "cpu",
    "storage":   "disk",
    "drive":     "disk",
    "drives":    "disk",
    # "address" / "addresses" intentionally NOT here — too vague for future
    # address-book / server-contact features.  Phrase aliases below handle
    # the specific "wifi address", "ethernet address" cases explicitly.
}

# ---------------------------------------------------------------------------
# Multi-word phrase aliases
# tuple[str, ...] → tuple[str, ...]
# Keys are matched against the START of the token list (prefix match).
# Longer keys take priority over shorter ones.
# ---------------------------------------------------------------------------

PHRASE_ALIASES: dict[tuple[str, ...], tuple[str, ...]] = {
    # --- IP / network ---
    ("wifi", "ip"):                    ("ip", "wifi"),
    ("ethernet", "ip"):                ("ip", "ethernet"),
    ("network", "wifi", "ip"):         ("ip", "wifi"),
    ("network", "ethernet", "ip"):     ("ip", "ethernet"),
    ("wifi", "address"):               ("ip", "wifi"),
    ("ethernet", "address"):           ("ip", "ethernet"),
    ("network", "address"):            ("ip",),

    # --- RAM / memory ---
    ("memory", "used"):                ("ram", "usage"),
    ("memory", "usage"):               ("ram", "usage"),
    ("memory", "free"):                ("ram", "free"),
    ("memory", "available"):           ("ram", "free"),
    ("memory", "total"):               ("ram", "total"),
    ("memory", "speed"):               ("ram", "speed"),

    # --- CPU / processor ---
    ("processor", "cores"):            ("cpu", "core-count"),
    ("processor", "threads"):          ("cpu", "core-count"),
    ("processor", "core-count"):       ("cpu", "core-count"),
    ("processor", "usage"):            ("cpu", "usage"),
    ("processor", "used"):             ("cpu", "usage"),
    ("processor", "speed"):            ("cpu", "speed"),
    ("processor", "temperature"):      ("cpu", "temperature"),
    ("processor", "info"):             ("cpu", "info"),

    # --- Disk / storage ---
    ("storage", "usage"):              ("disk", "space"),
    ("storage", "used"):               ("disk", "space"),
    ("storage", "space"):              ("disk", "space"),
    ("storage", "partitions"):         ("disk", "partitions"),

    # --- Folder size — known path aliases only ---
    ("downloads", "size"):             ("folder", "size", "downloads"),
    ("desktop", "size"):               ("folder", "size", "desktop"),
    ("documents", "size"):             ("folder", "size", "documents"),
    ("home", "size"):                  ("folder", "size", "home"),
    ("size", "downloads"):             ("folder", "size", "downloads"),
    ("size", "desktop"):               ("folder", "size", "desktop"),
    ("size", "documents"):             ("folder", "size", "documents"),
    ("size", "home"):                  ("folder", "size", "home"),
}

# Pre-sort keys longest-first so longer patterns always win over shorter ones
_SORTED_PHRASES: list[tuple[tuple[str, ...], tuple[str, ...]]] = sorted(
    PHRASE_ALIASES.items(),
    key=lambda kv: len(kv[0]),
    reverse=True,
)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def apply_aliases(tokens: list[str]) -> list[str]:
    """Return the canonical token list for *tokens*.

    Applies phrase aliases first (prefix match, longest wins), then falls
    back to ROOT_ALIASES on the first token.

    The original token list is returned unchanged if:
    - No alias matches, OR
    - The resolved canonical root is a PROTECTED_COMMAND.
    """
    if not tokens:
        return tokens

    # 1. Phrase alias — try longest prefix match
    for key, replacement in _SORTED_PHRASES:
        key_len = len(key)
        if len(tokens) >= key_len and tuple(tokens[:key_len]) == key:
            # Resolved root must not be protected
            resolved_root = replacement[0] if replacement else ""
            if resolved_root in PROTECTED_COMMANDS:
                return tokens
            # Replacement tokens + any trailing tokens not consumed by the key
            result = list(replacement) + tokens[key_len:]
            return result

    # 2. Root alias fallback — first token only
    canonical = ROOT_ALIASES.get(tokens[0])
    if canonical is not None:
        if canonical in PROTECTED_COMMANDS:
            return tokens
        return [canonical] + tokens[1:]

    return tokens
