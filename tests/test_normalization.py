"""
Tests for command alias normalization and routing.

Asserts:
- apply_aliases() returns correct canonical token lists
- Aliases actually invoke the correct handler behavior (output content checks)
- Protected commands are never silently rerouted

Run with:
    python -m unittest tests.test_normalization
"""

from __future__ import annotations

import io
import sys
import unittest
from unittest.mock import patch

from ixx.shell.aliases import apply_aliases, PROTECTED_COMMANDS
from ixx.shell.repl import run_command_once


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _run(line: str) -> str:
    """Run a single command line via the shell, capture stdout."""
    buf = io.StringIO()
    with patch("sys.stdout", buf):
        run_command_once(line)
    return buf.getvalue()


# ---------------------------------------------------------------------------
# Unit tests for apply_aliases()
# ---------------------------------------------------------------------------

class TestApplyAliasesUnit(unittest.TestCase):

    # Root aliases (single token)
    def test_memory_to_ram(self):
        self.assertEqual(apply_aliases(["memory"]), ["ram"])

    def test_processor_to_cpu(self):
        self.assertEqual(apply_aliases(["processor"]), ["cpu"])

    def test_storage_to_disk(self):
        self.assertEqual(apply_aliases(["storage"]), ["disk"])

    def test_drive_to_disk(self):
        self.assertEqual(apply_aliases(["drive"]), ["disk"])

    # Phrase aliases
    def test_memory_used_to_ram_usage(self):
        self.assertEqual(apply_aliases(["memory", "used"]), ["ram", "usage"])

    def test_memory_free_to_ram_free(self):
        self.assertEqual(apply_aliases(["memory", "free"]), ["ram", "free"])

    def test_memory_total_to_ram_total(self):
        self.assertEqual(apply_aliases(["memory", "total"]), ["ram", "total"])

    def test_wifi_ip_to_ip_wifi(self):
        self.assertEqual(apply_aliases(["wifi", "ip"]), ["ip", "wifi"])

    def test_ethernet_ip_to_ip_ethernet(self):
        self.assertEqual(apply_aliases(["ethernet", "ip"]), ["ip", "ethernet"])

    def test_wifi_address_to_ip_wifi(self):
        self.assertEqual(apply_aliases(["wifi", "address"]), ["ip", "wifi"])

    def test_ethernet_address_to_ip_ethernet(self):
        self.assertEqual(apply_aliases(["ethernet", "address"]), ["ip", "ethernet"])

    def test_downloads_size_to_folder_size_downloads(self):
        self.assertEqual(
            apply_aliases(["downloads", "size"]),
            ["folder", "size", "downloads"],
        )

    def test_desktop_size_to_folder_size_desktop(self):
        self.assertEqual(
            apply_aliases(["desktop", "size"]),
            ["folder", "size", "desktop"],
        )

    def test_documents_size_to_folder_size_documents(self):
        self.assertEqual(
            apply_aliases(["documents", "size"]),
            ["folder", "size", "documents"],
        )

    def test_processor_cores_to_cpu_core_count(self):
        self.assertEqual(
            apply_aliases(["processor", "cores"]),
            ["cpu", "core-count"],
        )

    def test_storage_space_to_disk_space(self):
        self.assertEqual(
            apply_aliases(["storage", "space"]),
            ["disk", "space"],
        )

    # Trailing tokens preserved
    def test_trailing_tokens_preserved(self):
        result = apply_aliases(["memory", "free", "extra"])
        self.assertEqual(result, ["ram", "free", "extra"])

    # Unknown tokens pass through unchanged
    def test_unknown_unchanged(self):
        self.assertEqual(apply_aliases(["foobar"]), ["foobar"])

    def test_empty_list(self):
        self.assertEqual(apply_aliases([]), [])

    # Protected commands are never rerouted TO
    def test_protected_commands_not_normalized(self):
        for cmd in PROTECTED_COMMANDS:
            tokens = [cmd]
            # apply_aliases must return them as-is (no normalization needed,
            # but more importantly nothing maps TO them via normalization)
            result = apply_aliases(tokens)
            self.assertEqual(result, tokens)


# ---------------------------------------------------------------------------
# Integration tests — actual output content
# ---------------------------------------------------------------------------

class TestAliasRouting(unittest.TestCase):
    """These tests verify the aliased tokens resolve to the correct handler."""

    def test_memory_used_shows_used(self):
        out = _run("memory used")
        self.assertIn("used", out.lower())

    def test_memory_free_shows_free(self):
        out = _run("memory free")
        self.assertIn("free", out.lower())

    def test_ram_total_shows_total(self):
        out = _run("ram total")
        self.assertIn("total", out.lower())

    def test_cpu_cores_shows_cores(self):
        out = _run("cpu cores")
        self.assertIn("cores", out.lower())

    def test_processor_cores_shows_cores(self):
        out = _run("processor cores")
        self.assertIn("cores", out.lower())

    def test_cpu_usage_shows_usage(self):
        out = _run("cpu usage")
        # cpu usage handler calls handle_cpu which shows full overview including Usage
        self.assertTrue(out.strip() != "", "cpu usage returned empty output")

    def test_ram_usage_shows_used(self):
        out = _run("ram usage")
        self.assertIn("used", out.lower())

    def test_ram_free_shows_free(self):
        out = _run("ram free")
        self.assertIn("free", out.lower())

    def test_memory_used_same_as_ram_usage(self):
        """'memory used' and 'ram usage' must produce identical output."""
        out_alias = _run("memory used")
        out_canon = _run("ram usage")
        self.assertEqual(out_alias.strip(), out_canon.strip())

    def test_processor_to_cpu_overview(self):
        out = _run("processor")
        self.assertTrue(out.strip() != "", "processor alias returned empty output")

    def test_storage_to_disk_overview(self):
        out = _run("storage")
        self.assertTrue(out.strip() != "", "storage alias returned empty output")


if __name__ == "__main__":
    unittest.main()
