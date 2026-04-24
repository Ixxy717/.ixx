"""
IXX v0.3.0 Tests

Covers:
- Path alias resolution (paths.py)
- Format helpers: format_bytes, render_table (safety.py)
- Guidance model: executable_with_children (ip, cpu, disk, ram, network)
- Command handler behaviour (mocked platform adapter)
- ixx do CLI command
"""

from __future__ import annotations

import io
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def cli(*args: str, input_text: str | None = None) -> tuple[int, str]:
    """Run the ixx CLI in a subprocess and return (exit_code, combined_output)."""
    proc = subprocess.run(
        [sys.executable, "-m", "ixx"] + list(args),
        capture_output=True,
        text=True,
        timeout=20,
        input=input_text,
        stdin=subprocess.DEVNULL if input_text is None else None,
    )
    return proc.returncode, proc.stdout + proc.stderr


# ---------------------------------------------------------------------------
# Path alias tests
# ---------------------------------------------------------------------------

class TestPaths(unittest.TestCase):

    def setUp(self) -> None:
        from ixx.shell.paths import resolve, PathNotFoundError
        self.resolve = resolve
        self.PathNotFoundError = PathNotFoundError
        self.tmp = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()

    def tearDown(self) -> None:
        os.chdir(self.original_cwd)

    def test_resolve_here(self) -> None:
        os.chdir(self.tmp)
        p = self.resolve("here")
        self.assertEqual(p, Path(self.tmp).resolve())

    def test_resolve_dot(self) -> None:
        os.chdir(self.tmp)
        p = self.resolve(".")
        self.assertEqual(p, Path(self.tmp).resolve())

    def test_resolve_current(self) -> None:
        os.chdir(self.tmp)
        p = self.resolve("current")
        self.assertEqual(p, Path(self.tmp).resolve())

    def test_resolve_subpath(self) -> None:
        """desktop/subdir style paths resolve alias then append subpath."""
        sub = os.path.join(self.tmp, "subdir")
        os.makedirs(sub)
        # Patch _aliases so "here" points to tmp, then test here/subdir
        from ixx.shell import paths as paths_mod
        fake_aliases = {
            "here": Path(self.tmp),
            ".": Path(self.tmp),
            "current": Path(self.tmp),
        }
        with patch.object(paths_mod, "_aliases", return_value=fake_aliases):
            p = self.resolve("here/subdir")
        self.assertEqual(p, Path(sub).resolve())

    def test_resolve_absolute_path(self) -> None:
        """An absolute path that exists should pass straight through."""
        p = self.resolve(self.tmp)
        self.assertEqual(p, Path(self.tmp).resolve())

    def test_resolve_relative_path(self) -> None:
        """A relative path relative to cwd resolves correctly."""
        os.chdir(self.tmp)
        subdir = os.path.join(self.tmp, "reldir")
        os.makedirs(subdir)
        p = self.resolve("reldir")
        self.assertEqual(p, Path(subdir).resolve())

    def test_missing_path_raises(self) -> None:
        with self.assertRaises(self.PathNotFoundError) as ctx:
            self.resolve(os.path.join(self.tmp, "does_not_exist_xyz"))
        self.assertIn("does_not_exist_xyz", str(ctx.exception))

    def test_alias_with_missing_subpath_raises(self) -> None:
        from ixx.shell import paths as paths_mod
        fake_aliases = {"here": Path(self.tmp), ".": Path(self.tmp), "current": Path(self.tmp)}
        with patch.object(paths_mod, "_aliases", return_value=fake_aliases):
            with self.assertRaises(self.PathNotFoundError):
                self.resolve("here/no_such_folder_xyz")

    def test_path_not_found_error_carries_raw(self) -> None:
        try:
            self.resolve("/definitely/not/a/real/path/ever")
        except self.PathNotFoundError as e:
            self.assertIn("not/a/real/path", e.raw)

    def test_empty_raw_returns_cwd(self) -> None:
        os.chdir(self.tmp)
        p = self.resolve("")
        self.assertEqual(p, Path(self.tmp).resolve())


# ---------------------------------------------------------------------------
# format_bytes tests
# ---------------------------------------------------------------------------

class TestFormatBytes(unittest.TestCase):

    def setUp(self) -> None:
        from ixx.shell.safety import format_bytes
        self.fmt = format_bytes

    def test_zero(self) -> None:
        self.assertEqual(self.fmt(0), "0 B")

    def test_bytes(self) -> None:
        self.assertEqual(self.fmt(512), "512 B")

    def test_kilobytes(self) -> None:
        result = self.fmt(1024)
        self.assertIn("KB", result)

    def test_megabytes(self) -> None:
        result = self.fmt(1024 * 1024)
        self.assertIn("MB", result)

    def test_gigabytes(self) -> None:
        result = self.fmt(1024 * 1024 * 1024)
        self.assertIn("GB", result)

    def test_terabytes(self) -> None:
        result = self.fmt(1024 ** 4)
        self.assertIn("TB", result)

    def test_negative(self) -> None:
        self.assertEqual(self.fmt(-1), "-")

    def test_large_gb(self) -> None:
        # 2 TB expressed in GB should come out as TB
        result = self.fmt(2 * 1024 ** 4)
        self.assertIn("TB", result)


# ---------------------------------------------------------------------------
# render_table tests
# ---------------------------------------------------------------------------

class TestRenderTable(unittest.TestCase):

    def setUp(self) -> None:
        from ixx.shell.safety import render_table
        self.tbl = render_table

    def test_basic_output(self) -> None:
        result = self.tbl(["Name", "Value"], [["foo", "bar"]])
        self.assertIn("Name", result)
        self.assertIn("Value", result)
        self.assertIn("foo", result)
        self.assertIn("bar", result)

    def test_separator_line(self) -> None:
        result = self.tbl(["A", "B"], [["x", "y"]])
        lines = result.splitlines()
        # Second line should be the separator (dashes)
        self.assertTrue(all(c in ("- ") for c in lines[1]))

    def test_empty_cell_becomes_dash(self) -> None:
        result = self.tbl(["A", "B"], [["hello", ""]])
        self.assertIn("-", result)

    def test_missing_cell_becomes_dash(self) -> None:
        result = self.tbl(["A", "B", "C"], [["only_one"]])
        self.assertIn("-", result)

    def test_column_alignment(self) -> None:
        result = self.tbl(
            ["Adapter", "IPv4"],
            [
                ["Wi-Fi",    "192.168.1.42"],
                ["Ethernet", "not connected"],
            ],
        )
        lines = result.splitlines()
        # All data lines should start at the same column
        data_lines = [l for l in lines if l.strip() and "-" * 5 not in l]
        starts = [len(l) - len(l.lstrip()) for l in data_lines]
        self.assertEqual(len(set(starts)), 1)

    def test_empty_headers(self) -> None:
        result = self.tbl([], [])
        self.assertEqual(result, "")


# ---------------------------------------------------------------------------
# Guidance tests — executable_with_children
# ---------------------------------------------------------------------------

class TestGuidanceExecutableWithChildren(unittest.TestCase):

    def setUp(self) -> None:
        from ixx.shell.commands.stubs import register_all
        from ixx.shell.registry import CommandRegistry
        from ixx.shell.guidance import get_guidance
        self.reg = CommandRegistry()
        register_all(self.reg)
        self.get_guidance = get_guidance

    def test_ip_is_executable_alone(self) -> None:
        result = self.get_guidance(self.reg, ["ip"])
        self.assertTrue(result.is_executable)

    def test_ip_still_has_subcommands(self) -> None:
        result = self.get_guidance(self.reg, ["ip"])
        self.assertIn("wifi", result.next_options)
        self.assertIn("ethernet", result.next_options)

    def test_ip_wifi_is_executable(self) -> None:
        result = self.get_guidance(self.reg, ["ip", "wifi"])
        self.assertTrue(result.is_executable)

    def test_cpu_is_executable_alone(self) -> None:
        result = self.get_guidance(self.reg, ["cpu"])
        self.assertTrue(result.is_executable)

    def test_cpu_shows_subcommands(self) -> None:
        result = self.get_guidance(self.reg, ["cpu"])
        self.assertIn("core-count", result.next_options)

    def test_cpu_core_count_is_executable(self) -> None:
        result = self.get_guidance(self.reg, ["cpu", "core-count"])
        self.assertTrue(result.is_executable)

    def test_ram_is_executable_alone(self) -> None:
        result = self.get_guidance(self.reg, ["ram"])
        self.assertTrue(result.is_executable)

    def test_disk_is_executable_alone(self) -> None:
        result = self.get_guidance(self.reg, ["disk"])
        self.assertTrue(result.is_executable)

    def test_disk_space_is_executable(self) -> None:
        result = self.get_guidance(self.reg, ["disk", "space"])
        self.assertTrue(result.is_executable)

    def test_network_is_executable_alone(self) -> None:
        result = self.get_guidance(self.reg, ["network"])
        self.assertTrue(result.is_executable)

    def test_folder_size_requires_path(self) -> None:
        # folder is not executable — only folder size (leaf with arg_hint) is
        result = self.get_guidance(self.reg, ["folder"])
        self.assertFalse(result.is_executable)

    def test_folder_size_is_executable(self) -> None:
        result = self.get_guidance(self.reg, ["folder", "size"])
        self.assertTrue(result.is_executable)

    def test_open_accepts_path(self) -> None:
        result = self.get_guidance(self.reg, ["open"])
        self.assertTrue(result.is_executable)

    def test_list_accepts_optional_path(self) -> None:
        result = self.get_guidance(self.reg, ["list"])
        self.assertTrue(result.is_executable)

    def test_ssh_is_registered(self) -> None:
        node = self.reg.get("ssh")
        self.assertIsNotNone(node)

    def test_servers_is_registered(self) -> None:
        node = self.reg.get("servers")
        self.assertIsNotNone(node)

    def test_server_add_is_registered(self) -> None:
        server = self.reg.get("server")
        self.assertIn("add", server.subcommands)


# ---------------------------------------------------------------------------
# Command handler tests (mocked platform)
# ---------------------------------------------------------------------------

class TestAdapterClassification(unittest.TestCase):

    def setUp(self) -> None:
        from ixx.shell.commands.network import _classify_adapter
        self.classify = _classify_adapter

    def test_loopback(self) -> None:
        self.assertEqual(self.classify("Loopback", "127.0.0.1"), "loopback")

    def test_link_local(self) -> None:
        self.assertEqual(self.classify("Local Area Connection", "169.254.16.80"), "link-local")

    def test_vpn_by_name(self) -> None:
        self.assertEqual(self.classify("NordLynx", "10.5.0.2"), "vpn")
        self.assertEqual(self.classify("OpenVPN Data Channel Offload", "10.100.0.2"), "vpn")
        self.assertEqual(self.classify("Tailscale", "100.127.28.64"), "vpn")

    def test_virtual_by_name(self) -> None:
        self.assertEqual(self.classify("vEthernet (WSL)", "172.27.64.1"), "virtual")
        self.assertEqual(self.classify("VMware Network Adapter VMnet8", "192.168.168.1"), "virtual")

    def test_virtual_by_ip(self) -> None:
        # VirtualBox host-only range
        self.assertEqual(self.classify("Ethernet", "192.168.56.1"), "virtual")

    def test_wifi_by_name(self) -> None:
        self.assertEqual(self.classify("Wi-Fi", "192.168.1.10"), "wifi")
        self.assertEqual(self.classify("Wireless Network Connection", "192.168.1.11"), "wifi")

    def test_ethernet_by_name(self) -> None:
        self.assertEqual(self.classify("Ethernet 4", "192.168.1.46"), "ethernet")

    def test_other(self) -> None:
        self.assertEqual(self.classify("Some Unknown Adapter", "10.0.0.1"), "other")


class TestCommandHandlers(unittest.TestCase):
    """Test command handlers with the platform adapter mocked out."""

    def _mock_adapter(self, **overrides) -> MagicMock:
        adapter = MagicMock()
        adapter.get_ip_info.return_value = [
            {"adapter": "Wi-Fi", "ipv4": "192.168.1.42"},
        ]
        adapter.get_wifi_ip.return_value = "192.168.1.42"
        adapter.get_ethernet_ip.return_value = None
        adapter.get_network_info.return_value = [
            {"adapter": "Wi-Fi", "status": "connected",
             "ipv4": "192.168.1.42", "gateway": "192.168.1.1"},
        ]
        adapter.get_cpu_info.return_value = {
            "name": "Test CPU", "cores": "4", "threads": "8", "usage_pct": "12%"
        }
        adapter.get_cpu_core_count.return_value = {
            "name": "Test CPU", "cores": "4", "threads": "8"
        }
        adapter.get_ram_info.return_value = {
            "total_bytes": 8 * 1024 ** 3,
            "used_bytes":  3 * 1024 ** 3,
            "free_bytes":  5 * 1024 ** 3,
        }
        adapter.get_disk_info.return_value = [
            {"drive": "C:", "label": "System", "total_bytes": 500 * 1024 ** 3,
             "free_bytes": 200 * 1024 ** 3, "used_bytes": 300 * 1024 ** 3},
        ]
        for k, v in overrides.items():
            setattr(adapter, k, MagicMock(return_value=v))
        return adapter

    def _capture(self, func, *args):
        buf = io.StringIO()
        with patch("sys.stdout", buf):
            func(*args)
        return buf.getvalue()

    # --- ip ---

    def test_ip_no_crash(self) -> None:
        from ixx.shell.commands.network import handle_ip
        adapter = self._mock_adapter()
        with patch("ixx.shell.platform.current", return_value=adapter):
            out = self._capture(handle_ip, [])
        self.assertIn("192.168.1.42", out)
        self.assertIn("Wi-Fi", out)

    def test_ip_shows_primary_section(self) -> None:
        """handle_ip should show 'Primary IP' for ethernet/wifi adapters."""
        from ixx.shell.commands.network import handle_ip
        adapter = self._mock_adapter()
        with patch("ixx.shell.platform.current", return_value=adapter):
            out = self._capture(handle_ip, [])
        self.assertIn("Primary IP", out)

    def test_ip_filters_link_local(self) -> None:
        """handle_ip should not show 169.254.x.x in primary when a real IP exists."""
        from ixx.shell.commands.network import handle_ip
        from unittest.mock import MagicMock
        adapter = MagicMock()
        adapter.get_ip_info.return_value = [
            {"adapter": "Ethernet 4",            "ipv4": "192.168.1.46"},
            {"adapter": "Local Area Connection", "ipv4": "169.254.16.80"},
        ]
        with patch("ixx.shell.platform.current", return_value=adapter):
            out = self._capture(handle_ip, [])
        self.assertIn("192.168.1.46", out)
        # The link-local address should not appear in the filtered default view
        self.assertNotIn("169.254.16.80", out)

    def test_ip_all_shows_everything(self) -> None:
        """handle_ip_all shows unfiltered table including link-local."""
        from ixx.shell.commands.network import handle_ip_all
        from unittest.mock import MagicMock
        adapter = MagicMock()
        adapter.get_ip_info.return_value = [
            {"adapter": "Wi-Fi",                "ipv4": "192.168.1.42"},
            {"adapter": "Local Area Connection", "ipv4": "169.254.16.80"},
            {"adapter": "NordLynx",              "ipv4": "10.5.0.2"},
        ]
        with patch("ixx.shell.platform.current", return_value=adapter):
            out = self._capture(handle_ip_all, [])
        self.assertIn("192.168.1.42", out)
        self.assertIn("169.254.16.80", out)
        self.assertIn("10.5.0.2", out)

    def test_ip_local_skips_link_local(self) -> None:
        """handle_ip_local should exclude 169.254.x.x addresses."""
        from ixx.shell.commands.network import handle_ip_local
        from unittest.mock import MagicMock
        adapter = MagicMock()
        adapter.get_ip_info.return_value = [
            {"adapter": "Ethernet 4",            "ipv4": "192.168.1.46"},
            {"adapter": "Local Area Connection", "ipv4": "169.254.16.80"},
        ]
        with patch("ixx.shell.platform.current", return_value=adapter):
            out = self._capture(handle_ip_local, [])
        self.assertIn("192.168.1.46", out)
        self.assertNotIn("169.254.16.80", out)

    def test_ip_wifi_found(self) -> None:
        from ixx.shell.commands.network import handle_ip_wifi
        adapter = self._mock_adapter()
        with patch("ixx.shell.platform.current", return_value=adapter):
            out = self._capture(handle_ip_wifi, [])
        self.assertIn("192.168.1.42", out)

    def test_ip_wifi_not_found(self) -> None:
        from ixx.shell.commands.network import handle_ip_wifi
        adapter = self._mock_adapter(get_wifi_ip=None)
        with patch("ixx.shell.platform.current", return_value=adapter):
            out = self._capture(handle_ip_wifi, [])
        self.assertIn("No connected Wi-Fi adapter found", out)

    def test_ip_ethernet_not_found(self) -> None:
        from ixx.shell.commands.network import handle_ip_ethernet
        adapter = self._mock_adapter()  # ethernet returns None by default
        with patch("ixx.shell.platform.current", return_value=adapter):
            out = self._capture(handle_ip_ethernet, [])
        self.assertIn("No connected Ethernet adapter found", out)

    def test_network_no_crash(self) -> None:
        from ixx.shell.commands.network import handle_network
        adapter = self._mock_adapter()
        with patch("ixx.shell.platform.current", return_value=adapter):
            out = self._capture(handle_network, [])
        self.assertIn("Wi-Fi", out)

    # --- cpu ---

    def test_cpu_no_crash(self) -> None:
        from ixx.shell.commands.hardware import handle_cpu
        adapter = self._mock_adapter()
        with patch("ixx.shell.platform.current", return_value=adapter):
            out = self._capture(handle_cpu, [])
        self.assertIn("Test CPU", out)
        self.assertIn("12%", out)

    def test_cpu_core_count_no_crash(self) -> None:
        from ixx.shell.commands.hardware import handle_cpu_cores
        adapter = self._mock_adapter()
        with patch("ixx.shell.platform.current", return_value=adapter):
            out = self._capture(handle_cpu_cores, [])
        self.assertIn("Test CPU", out)
        self.assertIn("4", out)

    # --- ram ---

    def test_ram_no_crash(self) -> None:
        from ixx.shell.commands.hardware import handle_ram
        adapter = self._mock_adapter()
        with patch("ixx.shell.platform.current", return_value=adapter):
            out = self._capture(handle_ram, [])
        self.assertIn("RAM", out)
        self.assertIn("GB", out)

    # --- disk ---

    def test_disk_no_crash(self) -> None:
        from ixx.shell.commands.system import handle_disk
        adapter = self._mock_adapter()
        with patch("ixx.shell.platform.current", return_value=adapter):
            out = self._capture(handle_disk, [])
        self.assertIn("C:", out)

    def test_disk_space_no_crash(self) -> None:
        from ixx.shell.commands.system import handle_disk_space
        adapter = self._mock_adapter()
        with patch("ixx.shell.platform.current", return_value=adapter):
            out = self._capture(handle_disk_space, [])
        self.assertIn("C:", out)
        self.assertIn("%", out)

    # --- folder size ---

    def test_folder_size_on_tempdir(self) -> None:
        from ixx.shell.commands.files import handle_folder_size
        from ixx.shell import paths as paths_mod
        tmp = tempfile.mkdtemp()
        # Write a small file so the folder is non-zero
        with open(os.path.join(tmp, "test.txt"), "w") as f:
            f.write("hello world")
        fake_aliases = {"here": Path(tmp), ".": Path(tmp), "current": Path(tmp)}
        with patch.object(paths_mod, "_aliases", return_value=fake_aliases):
            out = self._capture(handle_folder_size, ["here"])
        # Should print folder name and a size
        self.assertIn("B", out)  # any byte unit

    def test_folder_size_missing_path(self) -> None:
        from ixx.shell.commands.files import handle_folder_size
        out = self._capture(handle_folder_size, ["/this/path/does/not/exist/xyz"])
        self.assertIn("path not found", out)

    def test_folder_size_no_args(self) -> None:
        from ixx.shell.commands.files import handle_folder_size
        out = self._capture(handle_folder_size, [])
        self.assertIn("Usage", out)

    # --- list ---

    def test_list_on_tempdir(self) -> None:
        from ixx.shell.commands.files import handle_list
        from ixx.shell import paths as paths_mod
        tmp = tempfile.mkdtemp()
        # Create a file and a subdirectory
        with open(os.path.join(tmp, "file.txt"), "w") as f:
            f.write("content")
        os.makedirs(os.path.join(tmp, "subdir"))
        fake_aliases = {"here": Path(tmp), ".": Path(tmp), "current": Path(tmp)}
        with patch.object(paths_mod, "_aliases", return_value=fake_aliases):
            out = self._capture(handle_list, ["here"])
        self.assertIn("file.txt", out)
        self.assertIn("subdir", out)

    def test_list_missing_path(self) -> None:
        from ixx.shell.commands.files import handle_list
        out = self._capture(handle_list, ["/no/such/path/ever/xyz"])
        self.assertIn("path not found", out)

    # --- open (mocked so Explorer doesn't actually open) ---

    def test_open_mocked(self) -> None:
        from ixx.shell.commands.files import handle_open
        from ixx.shell import paths as paths_mod
        tmp = tempfile.mkdtemp()
        fake_aliases = {"here": Path(tmp), ".": Path(tmp), "current": Path(tmp)}
        with patch.object(paths_mod, "_aliases", return_value=fake_aliases):
            with patch("os.startfile"):
                out = self._capture(handle_open, ["here"])
        self.assertIn("Opened", out)

    def test_open_missing_path(self) -> None:
        from ixx.shell.commands.files import handle_open
        out = self._capture(handle_open, ["/no/such/path/ever/xyz"])
        self.assertIn("path not found", out)

    def test_open_no_args(self) -> None:
        from ixx.shell.commands.files import handle_open
        out = self._capture(handle_open, [])
        self.assertIn("Usage", out)

    # --- platform unavailable (NotImplementedError) ---

    def test_cpu_platform_unavailable(self) -> None:
        from ixx.shell.commands.hardware import handle_cpu
        bad_adapter = MagicMock()
        bad_adapter.get_cpu_info.side_effect = NotImplementedError
        with patch("ixx.shell.platform.current", return_value=bad_adapter):
            out = self._capture(handle_cpu, [])
        self.assertIn("not yet available", out)


# ---------------------------------------------------------------------------
# CLI ixx do tests
# ---------------------------------------------------------------------------

class TestTrailingHelp(unittest.TestCase):
    """<cmd> help should behave identically to help <cmd>."""

    def _run_once(self, line: str) -> str:
        from ixx.shell.repl import run_command_once
        buf = io.StringIO()
        with patch("sys.stdout", buf):
            run_command_once(line)
        return buf.getvalue()

    def test_cmd_help_same_as_help_cmd(self) -> None:
        out_trailing = self._run_once("cpu help")
        out_leading  = self._run_once("help cpu")
        self.assertEqual(out_trailing, out_leading)

    def test_cpu_help_shows_subcommands(self) -> None:
        out = self._run_once("cpu help")
        self.assertIn("core-count", out)

    def test_ip_help_shows_subcommands(self) -> None:
        out = self._run_once("ip help")
        self.assertIn("wifi", out)
        self.assertIn("ethernet", out)

    def test_disk_help_shows_subcommands(self) -> None:
        out = self._run_once("disk help")
        self.assertIn("space", out)
        self.assertIn("health", out)

    def test_folder_help_shows_size(self) -> None:
        out = self._run_once("folder help")
        self.assertIn("size", out)

    def test_ixx_do_cpu_help(self) -> None:
        code, out = cli("do", "cpu", "help")
        self.assertEqual(code, 0)
        self.assertIn("core-count", out)


class TestReplDo(unittest.TestCase):

    def test_ixx_do_ip_runs(self) -> None:
        """ixx do ip should not crash and return exit code 0."""
        code, out = cli("do", "ip")
        self.assertEqual(code, 0)

    def test_ixx_do_cpu_runs(self) -> None:
        code, out = cli("do", "cpu")
        self.assertEqual(code, 0)

    def test_ixx_do_quoted_runs(self) -> None:
        """ixx do 'ip wifi' (joined from two args) should work."""
        code, out = cli("do", "ip", "wifi")
        self.assertEqual(code, 0)

    def test_ixx_do_no_arg_exits_nonzero(self) -> None:
        code, out = cli("do")
        self.assertNotEqual(code, 0)
        self.assertIn("do", out)

    def test_ixx_do_unknown_command(self) -> None:
        code, out = cli("do", "xyzzy_not_a_command")
        self.assertEqual(code, 0)  # exits clean but prints unknown message
        self.assertIn("Unknown", out)

    def test_ixx_do_gpu_stub(self) -> None:
        """A stub command should print not-implemented, not crash."""
        code, out = cli("do", "gpu")
        self.assertEqual(code, 0)
        self.assertIn("not yet implemented", out)


if __name__ == "__main__":
    unittest.main()
