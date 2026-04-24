"""
IXX Shell — Command Registry

The registry holds the complete command grammar as a tree of CommandNode
objects.  No hardcoded string matching lives here — every command's shape,
metadata, and handler are declared as data.

Adding a new command:

    registry.register(
        CommandNode("foo",
            description="Do foo things",
            subcommands={
                "bar": CommandNode("bar", description="Do bar", handler=_foo_bar),
            },
            examples=["foo bar"],
        )
    )
"""

from __future__ import annotations

import difflib
from dataclasses import dataclass, field
from typing import Callable


@dataclass
class CommandNode:
    """One node in the command grammar tree.

    A node may have subcommands (branches) or a handler (leaf), or both
    (the node is executable on its own *and* accepts further subcommands).
    """

    name: str
    description: str = ""
    subcommands: dict[str, "CommandNode"] = field(default_factory=dict)
    arg_hint: str = ""          # e.g. "<path>", "<process-name>"
    examples: list[str] = field(default_factory=list)
    destructive: bool = False
    requires_admin: bool = False
    warning_text: str = ""      # overrides the generic destructive warning in hints
    handler: Callable[..., None] | None = None  # None = not yet implemented

    def is_leaf(self) -> bool:
        """True when there are no further subcommands expected."""
        return not self.subcommands and not self.arg_hint

    def add(self, node: "CommandNode") -> "CommandNode":
        """Convenience: add a child node and return self for chaining."""
        self.subcommands[node.name] = node
        return self


class CommandRegistry:
    """Top-level container for all registered IXX shell commands."""

    def __init__(self) -> None:
        self._commands: dict[str, CommandNode] = {}

    # ------------------------------------------------------------------
    # Registration
    # ------------------------------------------------------------------

    def register(self, node: CommandNode) -> None:
        """Add a top-level command."""
        self._commands[node.name] = node

    def register_all(self, nodes: list[CommandNode]) -> None:
        for node in nodes:
            self.register(node)

    # ------------------------------------------------------------------
    # Lookup
    # ------------------------------------------------------------------

    def lookup(self, tokens: list[str]) -> CommandNode | None:
        """Walk the tree following *tokens* and return the deepest matching node.

        Returns None if the first token is not a known command.
        Returns the last successfully matched node if tokens run out or
        a subcommand is not found (the caller can inspect .subcommands to
        see what comes next).
        """
        if not tokens:
            return None
        node = self._commands.get(tokens[0])
        if node is None:
            return None
        for tok in tokens[1:]:
            child = node.subcommands.get(tok)
            if child is None:
                break
            node = child
        return node

    def get(self, name: str) -> CommandNode | None:
        """Get a top-level command by exact name."""
        return self._commands.get(name)

    # ------------------------------------------------------------------
    # Discovery
    # ------------------------------------------------------------------

    def root_names(self) -> list[str]:
        """All registered top-level command names."""
        return list(self._commands.keys())

    def all_nodes(self) -> list[CommandNode]:
        """Flat list of all top-level nodes."""
        return list(self._commands.values())

    def suggest(self, word: str, n: int = 3, cutoff: float = 0.5) -> list[str]:
        """Fuzzy-match *word* against all root command names."""
        return difflib.get_close_matches(word, self.root_names(), n=n, cutoff=cutoff)
