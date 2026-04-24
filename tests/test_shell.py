"""
Tests for the IXX shell skeleton — registry, guidance engine, renderer,
fuzzy correction, and the REPL dispatch logic.

Run with:
    python -m unittest tests.test_shell
"""

from __future__ import annotations

import io
import sys
import unittest
from unittest.mock import patch

from ixx.shell.registry import CommandNode, CommandRegistry
from ixx.shell.guidance import GuidanceResult, get_guidance
from ixx.shell.commands.stubs import register_all
from ixx.shell.repl import _tokenize, _make_registry


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_simple_registry() -> CommandRegistry:
    """A small hand-built registry for testing without side effects."""
    registry = CommandRegistry()

    cpu = CommandNode(
        "cpu",
        description="CPU info",
        handler=lambda *_: None,
        subcommands={
            "usage": CommandNode("usage", description="Usage %", handler=lambda *_: None),
            "core-count": CommandNode("core-count", handler=lambda *_: None),
        },
        examples=["cpu", "cpu usage"],
    )
    disk = CommandNode(
        "disk",
        description="Disk info",
        handler=lambda *_: None,
        subcommands={
            "health": CommandNode(
                "health",
                description="SMART health",
                requires_admin=True,
                handler=lambda *_: None,
            ),
            "space": CommandNode("space", handler=lambda *_: None),
        },
    )
    delete_node = CommandNode(
        "delete",
        description="Delete stuff",
        destructive=True,
        subcommands={
            "temp": CommandNode(
                "temp",
                description="Clean temp files",
                destructive=True,
                handler=lambda *_: None,
            ),
            "folder": CommandNode(
                "folder",
                description="Delete a folder",
                arg_hint="<path>",
                destructive=True,
                handler=lambda *_: None,
            ),
        },
    )
    copy_node = CommandNode(
        "copy",
        description="Copy a file",
        arg_hint="<source> to <destination>",
        handler=lambda *_: None,
        examples=["copy report.pdf to desktop"],
    )
    registry.register_all([cpu, disk, delete_node, copy_node])
    return registry


# ---------------------------------------------------------------------------
# Registry tests
# ---------------------------------------------------------------------------

class TestRegistry(unittest.TestCase):

    def setUp(self) -> None:
        self.registry = _make_simple_registry()

    def test_root_names_contains_all_commands(self) -> None:
        names = self.registry.root_names()
        self.assertIn("cpu", names)
        self.assertIn("disk", names)
        self.assertIn("delete", names)
        self.assertIn("copy", names)

    def test_get_known_command(self) -> None:
        node = self.registry.get("cpu")
        self.assertIsNotNone(node)
        self.assertEqual(node.name, "cpu")

    def test_get_unknown_command_returns_none(self) -> None:
        self.assertIsNone(self.registry.get("xyzzy"))

    def test_lookup_top_level(self) -> None:
        node = self.registry.lookup(["cpu"])
        self.assertIsNotNone(node)
        self.assertEqual(node.name, "cpu")

    def test_lookup_subcommand(self) -> None:
        node = self.registry.lookup(["cpu", "usage"])
        self.assertIsNotNone(node)
        self.assertEqual(node.name, "usage")

    def test_lookup_deep_subcommand(self) -> None:
        node = self.registry.lookup(["disk", "health"])
        self.assertIsNotNone(node)
        self.assertEqual(node.name, "health")

    def test_lookup_unknown_returns_none(self) -> None:
        self.assertIsNone(self.registry.lookup(["xyzzy"]))

    def test_lookup_empty_returns_none(self) -> None:
        self.assertIsNone(self.registry.lookup([]))

    def test_lookup_stops_at_deepest_known(self) -> None:
        # "cpu bogus" — should return the cpu node, not None
        node = self.registry.lookup(["cpu", "bogus"])
        self.assertIsNotNone(node)
        self.assertEqual(node.name, "cpu")

    def test_register_replaces_existing(self) -> None:
        new_cpu = CommandNode("cpu", description="replaced")
        self.registry.register(new_cpu)
        self.assertEqual(self.registry.get("cpu").description, "replaced")

    def test_all_nodes_length(self) -> None:
        self.assertEqual(len(self.registry.all_nodes()), 4)


# ---------------------------------------------------------------------------
# Fuzzy suggestion tests
# ---------------------------------------------------------------------------

class TestFuzzySuggestions(unittest.TestCase):

    def setUp(self) -> None:
        self.registry = _make_simple_registry()

    def test_suggests_copy_for_cpoy(self) -> None:
        suggestions = self.registry.suggest("cpoy")
        self.assertIn("copy", suggestions)

    def test_suggests_cpu_for_cpy(self) -> None:
        suggestions = self.registry.suggest("cpu")
        self.assertIn("cpu", suggestions)

    def test_no_suggestion_for_gibberish(self) -> None:
        suggestions = self.registry.suggest("zzzzzzzz")
        self.assertEqual(suggestions, [])

    def test_exact_match_returned_first(self) -> None:
        suggestions = self.registry.suggest("disk")
        self.assertEqual(suggestions[0], "disk")


# ---------------------------------------------------------------------------
# Guidance engine tests
# ---------------------------------------------------------------------------

class TestGuidance(unittest.TestCase):

    def setUp(self) -> None:
        self.registry = _make_simple_registry()

    # Empty input
    def test_empty_tokens_returns_all_root_commands(self) -> None:
        result = get_guidance(self.registry, [])
        self.assertFalse(result.is_executable)
        self.assertIn("cpu", result.next_options)
        self.assertIn("disk", result.next_options)

    # Unknown command
    def test_unknown_command_returns_empty_result(self) -> None:
        result = get_guidance(self.registry, ["xyzzy"])
        self.assertIsNone(result.matched_node)
        self.assertFalse(result.is_executable)
        self.assertEqual(result.next_options, [])

    # Top-level node with handler + subcommands — should show guidance, NOT execute
    def test_top_level_with_subcommands_is_not_executable(self) -> None:
        result = get_guidance(self.registry, ["cpu"])
        self.assertFalse(result.is_executable)
        self.assertIsNotNone(result.matched_node)
        self.assertEqual(result.matched_node.name, "cpu")

    # Leaf node (no subcommands, has handler) — must be executable
    def test_leaf_node_is_executable(self) -> None:
        result = get_guidance(self.registry, ["cpu", "usage"])
        self.assertTrue(result.is_executable)
        self.assertEqual(result.matched_node.name, "usage")
        result = get_guidance(self.registry, ["cpu"])
        self.assertIn("usage", result.next_options)
        self.assertIn("core-count", result.next_options)

    # Subcommand navigation
    def test_subcommand_is_executable(self) -> None:
        result = get_guidance(self.registry, ["cpu", "usage"])
        self.assertTrue(result.is_executable)
        self.assertEqual(result.matched_node.name, "usage")

    def test_subcommand_depth_is_correct(self) -> None:
        result = get_guidance(self.registry, ["cpu", "usage"])
        self.assertEqual(result.depth, 2)

    def test_top_level_depth_is_one(self) -> None:
        result = get_guidance(self.registry, ["cpu"])
        self.assertEqual(result.depth, 1)

    # Unrecognised subcommand — stays at parent node
    def test_unknown_subcommand_stays_at_parent(self) -> None:
        result = get_guidance(self.registry, ["cpu", "bogus"])
        self.assertIsNotNone(result.matched_node)
        self.assertEqual(result.matched_node.name, "cpu")
        self.assertEqual(result.depth, 1)

    # Destructive flag propagation
    def test_destructive_flag_on_leaf(self) -> None:
        result = get_guidance(self.registry, ["delete", "temp"])
        self.assertTrue(result.destructive)

    def test_destructive_flag_not_on_safe_command(self) -> None:
        result = get_guidance(self.registry, ["cpu"])
        self.assertFalse(result.destructive)

    # requires_admin flag
    def test_requires_admin_flag(self) -> None:
        result = get_guidance(self.registry, ["disk", "health"])
        self.assertTrue(result.requires_admin)

    def test_requires_admin_not_set_normally(self) -> None:
        result = get_guidance(self.registry, ["cpu", "usage"])
        self.assertFalse(result.requires_admin)

    # arg_hint makes a node executable even without a subcommand match
    def test_arg_hint_node_is_executable(self) -> None:
        result = get_guidance(self.registry, ["copy"])
        self.assertTrue(result.is_executable)
        self.assertEqual(result.arg_hint, "<source> to <destination>")

    def test_delete_folder_arg_hint(self) -> None:
        result = get_guidance(self.registry, ["delete", "folder"])
        self.assertTrue(result.is_executable)
        self.assertIn("<path>", result.arg_hint)

    # remaining_args
    def test_remaining_args_captured(self) -> None:
        result = get_guidance(self.registry, ["copy", "report.pdf", "to", "desktop"])
        self.assertEqual(result.remaining_args, ["report.pdf", "to", "desktop"])

    def test_no_remaining_args_on_exact_leaf(self) -> None:
        result = get_guidance(self.registry, ["cpu", "usage"])
        self.assertEqual(result.remaining_args, [])

    # examples
    def test_examples_propagated(self) -> None:
        result = get_guidance(self.registry, ["cpu"])
        self.assertIn("cpu usage", result.examples)


# ---------------------------------------------------------------------------
# Tokeniser tests
# ---------------------------------------------------------------------------

class TestTokenize(unittest.TestCase):

    def test_simple_words(self) -> None:
        self.assertEqual(_tokenize("cpu usage"), ["cpu", "usage"])

    def test_leading_trailing_spaces(self) -> None:
        self.assertEqual(_tokenize("  disk health  "), ["disk", "health"])

    def test_quoted_string_kept_together(self) -> None:
        self.assertEqual(
            _tokenize('find file "my document.pdf"'),
            ["find", "file", "my document.pdf"],
        )

    def test_single_quoted_string(self) -> None:
        self.assertEqual(
            _tokenize("open 'my folder'"),
            ["open", "my folder"],
        )

    def test_empty_string(self) -> None:
        self.assertEqual(_tokenize(""), [])

    def test_single_word(self) -> None:
        self.assertEqual(_tokenize("cpu"), ["cpu"])

    def test_multiple_spaces_between_words(self) -> None:
        self.assertEqual(_tokenize("disk   health"), ["disk", "health"])


# ---------------------------------------------------------------------------
# Full stub registry smoke test
# ---------------------------------------------------------------------------

class TestFullRegistry(unittest.TestCase):
    """Sanity-check the registry built by the real stub commands."""

    def setUp(self) -> None:
        self.registry = _make_registry()

    def test_cpu_registered(self) -> None:
        self.assertIsNotNone(self.registry.get("cpu"))

    def test_disk_registered(self) -> None:
        self.assertIsNotNone(self.registry.get("disk"))

    def test_ip_registered(self) -> None:
        self.assertIsNotNone(self.registry.get("ip"))

    def test_delete_registered(self) -> None:
        self.assertIsNotNone(self.registry.get("delete"))

    def test_cpu_has_expected_subcommands(self) -> None:
        cpu = self.registry.get("cpu")
        for sub in ("usage", "core-count", "temperature", "speed", "info"):
            self.assertIn(sub, cpu.subcommands)

    def test_disk_has_expected_subcommands(self) -> None:
        disk = self.registry.get("disk")
        for sub in ("list", "health", "space", "partitions"):
            self.assertIn(sub, disk.subcommands)

    def test_ip_has_expected_subcommands(self) -> None:
        ip = self.registry.get("ip")
        for sub in ("all", "wifi", "ethernet", "public", "local"):
            self.assertIn(sub, ip.subcommands)

    def test_delete_subcommands_are_destructive(self) -> None:
        delete = self.registry.get("delete")
        for sub in delete.subcommands.values():
            self.assertTrue(sub.destructive, f"{sub.name} should be destructive")

    def test_disk_health_requires_admin(self) -> None:
        disk = self.registry.get("disk")
        self.assertTrue(disk.subcommands["health"].requires_admin)

    def test_stub_handlers_callable(self) -> None:
        """Stub handlers should be callable and not raise."""
        captured = io.StringIO()
        for node in self.registry.all_nodes():
            if node.handler:
                try:
                    with patch("sys.stdout", captured):
                        node.handler([])
                except Exception as exc:  # pragma: no cover
                    self.fail(f"handler for '{node.name}' raised: {exc}")

    def test_stub_handler_prints_not_implemented(self) -> None:
        cpu = self.registry.get("cpu")
        captured = io.StringIO()
        with patch("sys.stdout", captured):
            cpu.handler([])
        self.assertIn("not yet implemented", captured.getvalue())

    def test_guidance_on_full_registry_cpu(self) -> None:
        # cpu has subcommands — must show guidance, not execute
        result = get_guidance(self.registry, ["cpu"])
        self.assertFalse(result.is_executable)
        self.assertIn("usage", result.next_options)

    def test_guidance_on_full_registry_delete_shows_subcommands(self) -> None:
        result = get_guidance(self.registry, ["delete"])
        self.assertFalse(result.is_executable)
        self.assertIn("file", result.next_options)
        self.assertIn("folder", result.next_options)
        self.assertIn("temp", result.next_options)

    def test_guidance_delete_is_not_executable_alone(self) -> None:
        # delete node has no handler itself, only subcommands
        result = get_guidance(self.registry, ["delete"])
        self.assertFalse(result.is_executable)

    def test_total_root_commands_reasonable(self) -> None:
        # Sanity check: we have at least 10 commands registered
        self.assertGreaterEqual(len(self.registry.root_names()), 10)


if __name__ == "__main__":
    unittest.main()
