"""
IXX Shell — Guidance Engine

Given a list of tokens the user has typed so far, the engine walks the
CommandRegistry tree and returns everything the shell needs to either
display hints or dispatch a command.

Usage:
    result = get_guidance(registry, ["disk", "health"])
    if result.is_executable:
        result.matched_node.handler(result.remaining_args)
    else:
        renderer.show_hints(result)
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .registry import CommandNode, CommandRegistry
from .aliases import ROOT_ALIASES


@dataclass
class GuidanceResult:
    """Everything derived from walking the command tree for a given input."""

    matched_node: CommandNode | None = None
    next_options: list[str] = field(default_factory=list)
    arg_hint: str = ""
    examples: list[str] = field(default_factory=list)
    is_executable: bool = False
    destructive: bool = False
    requires_admin: bool = False
    remaining_args: list[str] = field(default_factory=list)
    # How many tokens were consumed while walking the tree
    depth: int = 0


def _find_child(node: CommandNode, tok: str) -> CommandNode | None:
    """Find a child node by exact name or by alias."""
    if tok in node.subcommands:
        return node.subcommands[tok]
    for child in node.subcommands.values():
        if tok in child.aliases:
            return child
    return None


def get_guidance(registry: CommandRegistry, tokens: list[str]) -> GuidanceResult:
    """Walk the command tree and return a GuidanceResult for *tokens*.

    Handles these cases:
    - Empty input           → list all top-level commands as next_options
    - Unknown first token   → empty result (caller uses registry.suggest())
    - Partial path          → next_options = subcommand names at current node
    - Complete path (leaf)  → is_executable=True, remaining_args = leftover tokens
    - Node has both sub-    → is_executable=True AND next_options populated
      commands and a handler
    """
    if not tokens:
        return GuidanceResult(
            next_options=registry.root_names(),
        )

    # Walk the tree — check root by exact name first, then ROOT_ALIASES
    node = registry.get(tokens[0])
    if node is None:
        canonical = ROOT_ALIASES.get(tokens[0])
        if canonical:
            node = registry.get(canonical)
    if node is None:
        return GuidanceResult()  # unknown command

    depth = 1
    for tok in tokens[1:]:
        child = _find_child(node, tok)
        if child is None:
            # Token doesn't match a subcommand or alias — remaining tokens are free args
            break
        node = child
        depth += 1

    remaining = tokens[depth:]

    # Determine executability:
    # A node is executable when it has a handler or free-form arg_hint AND:
    #   - it is a leaf (no subcommands), OR
    #   - it has executable_with_children=True (runs overview AND keeps subcommands)
    has_handler = node.handler is not None
    has_arg_hint = bool(node.arg_hint)
    executable = (has_handler or has_arg_hint) and (
        not bool(node.subcommands) or node.executable_with_children
    )

    return GuidanceResult(
        matched_node=node,
        next_options=list(node.subcommands.keys()),
        arg_hint=node.arg_hint,
        examples=node.examples,
        is_executable=executable,
        destructive=node.destructive,
        requires_admin=node.requires_admin,
        remaining_args=remaining,
        depth=depth,
    )
