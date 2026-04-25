"""
IXX automated test suite — v0.1.0

Covers all current language features plus CLI commands.

Run with:
    python -m pytest tests/test_ixx.py -v
    python -m unittest tests.test_ixx -v
"""

from __future__ import annotations
import contextlib
import io
import os
import subprocess
import sys
import textwrap
import unittest
from pathlib import Path

# Make sure the ixx package is importable when running from any directory
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from ixx.parser import parse
from ixx.interpreter import Interpreter, IXXRuntimeError


# ── helpers ────────────────────────────────────────────────────────────────────

def run(source: str) -> str:
    """Run IXX source and return stdout as a string."""
    source = textwrap.dedent(source).strip()
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        Interpreter().run(parse(source))
    return buf.getvalue().rstrip("\n")


def lines(source: str) -> list[str]:
    """Run source and return each output line as a list."""
    return run(source).splitlines()


def cli(*args: str) -> tuple[int, str]:
    """Run `ixx <args>` in a subprocess, return (exit_code, combined_output)."""
    result = subprocess.run(
        [sys.executable, "-m", "ixx", *args],
        capture_output=True,
        text=True,
        stdin=subprocess.DEVNULL,
        timeout=30,
        cwd=str(ROOT),
    )
    combined = (result.stdout + result.stderr).strip()
    return result.returncode, combined


# ══════════════════════════════════════════════════════════════════════════════
# 1. BASICS
# ══════════════════════════════════════════════════════════════════════════════

class TestBasics(unittest.TestCase):

    def test_hello_world(self):
        self.assertEqual(run('say "Hello World"'), "Hello World")

    def test_say_multiple_args(self):
        self.assertEqual(run('say "a", "b", "c"'), "a b c")

    def test_say_empty(self):
        self.assertEqual(run("say"), "")

    def test_variable_assignment_and_ref(self):
        self.assertEqual(run('x = 42\nsay x'), "42")

    def test_reassignment(self):
        self.assertEqual(run('x = 1\nx = 2\nsay x'), "2")


# ══════════════════════════════════════════════════════════════════════════════
# 2. STRINGS
# ══════════════════════════════════════════════════════════════════════════════

class TestStrings(unittest.TestCase):

    def test_plain_string(self):
        self.assertEqual(run('say "hello"'), "hello")

    def test_string_concat(self):
        self.assertEqual(run('say "Hello, " + "World"'), "Hello, World")

    def test_string_concat_via_variable(self):
        self.assertEqual(run('a = "Hello"\nb = " World"\nsay a + b'), "Hello World")

    def test_string_interpolation_basic(self):
        self.assertEqual(run('name = "Ixxy"\nsay "Hello, {name}"'), "Hello, Ixxy")

    def test_string_interpolation_number(self):
        self.assertEqual(run('score = 99\nsay "Score: {score}"'), "Score: 99")

    def test_string_interpolation_undefined_left_as_is(self):
        # {undefined} becomes {?name} with a warning to stderr (v0.4 behavior)
        buf_err = io.StringIO()
        buf_out = io.StringIO()
        with contextlib.redirect_stderr(buf_err), contextlib.redirect_stdout(buf_out):
            prog = parse('say "Hello {ghost}"')
            from ixx.interpreter import Interpreter as _I
            _I().run(prog)
        self.assertIn("{?ghost}", buf_out.getvalue())
        self.assertIn("ghost", buf_err.getvalue())

    def test_string_interpolation_multiple(self):
        self.assertEqual(
            run('a = "one"\nb = "two"\nsay "{a} and {b}"'),
            "one and two",
        )


# ══════════════════════════════════════════════════════════════════════════════
# 3. NUMBERS
# ══════════════════════════════════════════════════════════════════════════════

class TestNumbers(unittest.TestCase):

    def test_integer(self):
        self.assertEqual(run("say 42"), "42")

    def test_float(self):
        self.assertEqual(run("say 3.14"), "3.14")

    def test_negative(self):
        self.assertEqual(run("say -10"), "-10")

    def test_negative_variable(self):
        self.assertEqual(run("x = -5\nsay x"), "-5")

    def test_addition(self):
        self.assertEqual(run("say 2 + 3"), "5")

    def test_subtraction(self):
        self.assertEqual(run("say 10 - 4"), "6")

    def test_multiplication(self):
        self.assertEqual(run("say 3 * 4"), "12")

    def test_division_whole(self):
        self.assertEqual(run("say 10 / 2"), "5")

    def test_division_float(self):
        self.assertEqual(run("say 7 / 2"), "3.5")

    def test_division_by_zero(self):
        with self.assertRaises(IXXRuntimeError):
            run("say 1 / 0")

    def test_operator_precedence(self):
        # 2 + 3 * 4 = 14, not 20
        self.assertEqual(run("say 2 + 3 * 4"), "14")

    def test_parentheses(self):
        self.assertEqual(run("say (2 + 3) * 4"), "20")


# ══════════════════════════════════════════════════════════════════════════════
# 4. BOOLEANS
# ══════════════════════════════════════════════════════════════════════════════

class TestBooleans(unittest.TestCase):

    def test_yes(self):
        self.assertEqual(run("say YES"), "YES")

    def test_no(self):
        self.assertEqual(run("say NO"), "NO")

    def test_yes_lowercase(self):
        self.assertEqual(run("say yes"), "YES")

    def test_no_uppercase(self):
        self.assertEqual(run("say No"), "NO")

    def test_yes_is_truthy(self):
        self.assertEqual(run("if YES\n- say \"true\""), "true")

    def test_no_is_falsy(self):
        self.assertEqual(run("if NO\n- say \"true\"\nelse\n- say \"false\""), "false")

    def test_nonzero_is_truthy(self):
        self.assertEqual(run("if 1\n- say \"yes\""), "yes")

    def test_zero_is_falsy(self):
        self.assertEqual(run("if 0\n- say \"yes\"\nelse\n- say \"no\""), "no")

    def test_nonempty_string_is_truthy(self):
        self.assertEqual(run('if "hello"\n- say "yes"'), "yes")

    def test_empty_string_is_falsy(self):
        self.assertEqual(run('if ""\n- say "yes"\nelse\n- say "no"'), "no")


# ══════════════════════════════════════════════════════════════════════════════
# 5. CONDITIONS
# ══════════════════════════════════════════════════════════════════════════════

class TestConditions(unittest.TestCase):

    def test_if_true(self):
        self.assertEqual(run('if YES\n- say "hit"'), "hit")

    def test_if_false_no_output(self):
        self.assertEqual(run('if NO\n- say "hit"'), "")

    def test_if_else_true_branch(self):
        self.assertEqual(
            run('if YES\n- say "yes"\nelse\n- say "no"'), "yes"
        )

    def test_if_else_false_branch(self):
        self.assertEqual(
            run('if NO\n- say "yes"\nelse\n- say "no"'), "no"
        )

    def test_multiple_statements_in_block(self):
        out = lines('if YES\n- say "a"\n- say "b"\n- say "c"')
        self.assertEqual(out, ["a", "b", "c"])

    def test_if_does_not_run_else_when_true(self):
        self.assertEqual(
            run('x = YES\nif x\n- say "if"\nelse\n- say "else"'), "if"
        )


# ══════════════════════════════════════════════════════════════════════════════
# 6. DASH BLOCKS
# ══════════════════════════════════════════════════════════════════════════════

class TestDashBlocks(unittest.TestCase):

    def test_single_dash(self):
        self.assertEqual(run('if YES\n- say "inside"'), "inside")

    def test_double_dash_nesting(self):
        out = lines('if YES\n- if YES\n-- say "deep"')
        self.assertEqual(out, ["deep"])

    def test_nested_if_else(self):
        src = 'if YES\n- if NO\n-- say "inner-if"\n- else\n-- say "inner-else"'
        self.assertEqual(run(src), "inner-else")

    def test_triple_dash(self):
        src = 'if YES\n- if YES\n-- if YES\n--- say "triple"'
        self.assertEqual(run(src), "triple")

    def test_outer_else_not_affected_by_inner(self):
        src = 'if YES\n- say "outer"\nelse\n- say "never"'
        self.assertEqual(run(src), "outer")


# ══════════════════════════════════════════════════════════════════════════════
# 7. LOOP
# ══════════════════════════════════════════════════════════════════════════════

class TestLoop(unittest.TestCase):

    def test_basic_loop(self):
        out = lines('n = 3\nloop n more than 0\n- say n\n- n = n - 1')
        self.assertEqual(out, ["3", "2", "1"])

    def test_loop_zero_iterations(self):
        self.assertEqual(run('loop NO\n- say "never"'), "")

    def test_loop_accumulates(self):
        src = 'total = 0\ni = 3\nloop i more than 0\n- total = total + i\n- i = i - 1\nsay total'
        self.assertEqual(run(src), "6")

    def test_loop_modifies_outer_var(self):
        src = 'x = 5\nloop x more than 3\n- x = x - 1\nsay x'
        self.assertEqual(run(src), "3")


# ══════════════════════════════════════════════════════════════════════════════
# 8. LISTS
# ══════════════════════════════════════════════════════════════════════════════

class TestLists(unittest.TestCase):

    def test_list_literal(self):
        self.assertEqual(
            run('items = "a", "b", "c"\nsay items'),
            "a, b, c",
        )

    def test_list_two_items(self):
        self.assertEqual(run('x = 1, 2\nsay x'), "1, 2")

    def test_list_numbers(self):
        self.assertEqual(run('nums = 10, 20, 30\nsay nums'), "10, 20, 30")

    def test_list_mixed(self):
        self.assertEqual(
            run('m = "hello", 42, YES\nsay m'),
            "hello, 42, YES",
        )


# ══════════════════════════════════════════════════════════════════════════════
# 9. COMPARISONS
# ══════════════════════════════════════════════════════════════════════════════

class TestComparisons(unittest.TestCase):

    def _assert_comparison(self, expr: str, expected: str) -> None:
        src = f'if {expr}\n- say "yes"\nelse\n- say "no"'
        self.assertEqual(run(src), expected)

    def test_is_equal(self):
        self._assert_comparison('5 is 5', "yes")

    def test_is_not_equal(self):
        self._assert_comparison('5 is 4', "no")

    def test_is_not(self):
        self._assert_comparison('5 is not 4', "yes")

    def test_is_not_false(self):
        self._assert_comparison('5 is not 5', "no")

    def test_less_than_true(self):
        self._assert_comparison('3 less than 5', "yes")

    def test_less_than_false(self):
        self._assert_comparison('5 less than 3', "no")

    def test_more_than_true(self):
        self._assert_comparison('5 more than 3', "yes")

    def test_more_than_false(self):
        self._assert_comparison('3 more than 5', "no")

    def test_at_least_equal(self):
        self._assert_comparison('5 at least 5', "yes")

    def test_at_least_greater(self):
        self._assert_comparison('6 at least 5', "yes")

    def test_at_least_less(self):
        self._assert_comparison('4 at least 5', "no")

    def test_at_most_equal(self):
        self._assert_comparison('5 at most 5', "yes")

    def test_at_most_less(self):
        self._assert_comparison('4 at most 5', "yes")

    def test_at_most_greater(self):
        self._assert_comparison('6 at most 5', "no")

    def test_is_string(self):
        self._assert_comparison('"hello" is "hello"', "yes")

    def test_is_not_string(self):
        self._assert_comparison('"hello" is not "world"', "yes")


# ══════════════════════════════════════════════════════════════════════════════
# 10. CONTAINS
# ══════════════════════════════════════════════════════════════════════════════

class TestContains(unittest.TestCase):

    def test_list_contains_true(self):
        src = 'items = "apple", "banana", "grape"\nif items contains "banana"\n- say "found"'
        self.assertEqual(run(src), "found")

    def test_list_contains_false(self):
        src = 'items = "apple", "banana"\nif items contains "mango"\n- say "found"\nelse\n- say "not found"'
        self.assertEqual(run(src), "not found")

    def test_list_contains_number(self):
        src = 'nums = 1, 2, 3\nif nums contains 2\n- say "yes"'
        self.assertEqual(run(src), "yes")

    def test_string_contains_true(self):
        src = 'msg = "Hello World"\nif msg contains "World"\n- say "yes"'
        self.assertEqual(run(src), "yes")

    def test_string_contains_false(self):
        src = 'msg = "Hello"\nif msg contains "World"\n- say "yes"\nelse\n- say "no"'
        self.assertEqual(run(src), "no")

    def test_string_contains_substring(self):
        src = 'if "abcdef" contains "cde"\n- say "yes"'
        self.assertEqual(run(src), "yes")


# ══════════════════════════════════════════════════════════════════════════════
# 11. LOGIC
# ══════════════════════════════════════════════════════════════════════════════

class TestLogic(unittest.TestCase):

    def test_and_both_true(self):
        self.assertEqual(run('if YES and YES\n- say "yes"'), "yes")

    def test_and_one_false(self):
        self.assertEqual(
            run('if YES and NO\n- say "yes"\nelse\n- say "no"'), "no"
        )

    def test_or_both_false(self):
        self.assertEqual(
            run('if NO or NO\n- say "yes"\nelse\n- say "no"'), "no"
        )

    def test_or_one_true(self):
        self.assertEqual(run('if NO or YES\n- say "yes"'), "yes")

    def test_not_true(self):
        self.assertEqual(
            run('if not YES\n- say "yes"\nelse\n- say "no"'), "no"
        )

    def test_not_false(self):
        self.assertEqual(run('if not NO\n- say "yes"'), "yes")

    def test_combined_logic(self):
        src = 'a = YES\nb = NO\nif a and not b\n- say "ok"'
        self.assertEqual(run(src), "ok")


# ══════════════════════════════════════════════════════════════════════════════
# 12. ERRORS
# ══════════════════════════════════════════════════════════════════════════════

class TestErrors(unittest.TestCase):

    def test_undefined_variable_raises(self):
        with self.assertRaises(IXXRuntimeError) as ctx:
            run("say undefined_var")
        self.assertIn("undefined_var", str(ctx.exception))

    def test_undefined_variable_message_has_tip(self):
        with self.assertRaises(IXXRuntimeError) as ctx:
            run("say ghost")
        msg = str(ctx.exception)
        self.assertIn("Tip:", msg)

    def test_division_by_zero_raises(self):
        with self.assertRaises(IXXRuntimeError):
            run("say 5 / 0")

    def test_negate_non_number_raises(self):
        with self.assertRaises(IXXRuntimeError):
            run('x = "hello"\nsay -x')


# ══════════════════════════════════════════════════════════════════════════════
# 13. CLI
# ══════════════════════════════════════════════════════════════════════════════

class TestCLI(unittest.TestCase):

    def test_version(self):
        code, out = cli("version")
        self.assertEqual(code, 0)
        self.assertIn("0.6.", out)

    def test_help_contains_usage(self):
        code, out = cli("help")
        self.assertEqual(code, 0)
        self.assertIn("Usage:", out)

    def test_help_contains_examples(self):
        code, out = cli("help")
        self.assertEqual(code, 0)
        self.assertIn("Examples:", out)

    def test_check_valid_file(self):
        code, out = cli("check", "examples/hello.ixx")
        self.assertEqual(code, 0)
        self.assertIn("syntax OK", out)

    def test_check_bad_file(self):
        # Write a temp bad file, check it, then remove it
        bad = ROOT / "examples" / "_test_bad.ixx"
        bad.write_text("if age less\n- say oops\n", encoding="utf-8")
        try:
            code, out = cli("check", "examples/_test_bad.ixx")
            self.assertNotEqual(code, 0)
            self.assertIn("syntax error", out)
        finally:
            bad.unlink(missing_ok=True)

    def test_run_hello(self):
        code, out = cli("run", "examples/hello.ixx")
        self.assertEqual(code, 0)
        self.assertIn("Hello World", out)

    def test_run_condition(self):
        code, out = cli("run", "examples/condition.ixx")
        self.assertEqual(code, 0)
        self.assertIn("Adult", out)

    def test_run_lists(self):
        code, out = cli("run", "examples/lists.ixx")
        self.assertEqual(code, 0)
        self.assertIn("Found it", out)

    def test_run_advanced(self):
        code, out = cli("run", "examples/advanced.ixx")
        self.assertEqual(code, 0)
        self.assertIn("Hello, Ixxy", out)

    def test_unknown_command_exits_nonzero(self):
        code, out = cli("notacommand")
        self.assertNotEqual(code, 0)
        self.assertIn("unknown command", out)

    def test_file_not_found_exits_nonzero(self):
        code, out = cli("run", "does_not_exist.ixx")
        self.assertNotEqual(code, 0)
        self.assertIn("not found", out)

    def test_shell_opens_repl(self):
        # Send "exit" so the REPL closes immediately
        result = subprocess.run(
            [sys.executable, "-m", "ixx", "shell"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            input="exit\n",
            cwd=str(ROOT),
            timeout=30,
        )
        self.assertEqual(result.returncode, 0)
        combined = (result.stdout + result.stderr).strip()
        self.assertIn("IXX Shell", combined)


# ══════════════════════════════════════════════════════════════════════════════

# ══════════════════════════════════════════════════════════════════════════════

class TestShowoff(unittest.TestCase):
    """Tests for ixx showoff — exit codes, content, pacing, plain/NO_COLOR."""

    # ── helpers ───────────────────────────────────────────────────────────────

    def _run_showoff(self, *extra_args: str) -> subprocess.CompletedProcess:
        """Run ixx showoff via subprocess (piped stdout = no animation delays)."""
        env = {**os.environ, "PYTHONIOENCODING": "utf-8"}
        return subprocess.run(
            [sys.executable, "-m", "ixx", "showoff"] + list(extra_args),
            capture_output=True, text=True, encoding="utf-8",
            errors="replace", timeout=20, env=env,
        )

    def _run_in_process(self, mode: str) -> str:
        """Run showoff in-process with _sleep mocked; return captured stdout."""
        from unittest.mock import patch
        buf = io.StringIO()
        with patch("ixx.showoff._sleep", return_value=None):
            with contextlib.redirect_stdout(buf):
                from ixx.showoff import run
                run(mode)
        return buf.getvalue()

    # ── exit codes ────────────────────────────────────────────────────────────

    def test_showoff_exits_0(self):
        self.assertEqual(self._run_showoff().returncode, 0)

    def test_showoff_quick_exits_0(self):
        self.assertEqual(self._run_showoff("quick").returncode, 0)

    def test_showoff_plain_exits_0(self):
        self.assertEqual(self._run_showoff("plain").returncode, 0)

    def test_showoff_full_exits_0(self):
        self.assertEqual(self._run_showoff("full").returncode, 0)

    def test_unknown_subcommand_falls_back_to_default(self):
        r = self._run_showoff("garbage")
        self.assertEqual(r.returncode, 0)
        self.assertIn("IXX", r.stdout)

    # ── plain mode: OLD WAY → IXX WAY comparisons ────────────────────────────

    def _plain_out(self) -> str:
        r = self._run_showoff("plain")
        self.assertEqual(r.returncode, 0)
        return r.stdout

    def test_old_way_label(self):
        self.assertIn("OLD WAY", self._plain_out())

    def test_ixx_way_label(self):
        self.assertIn("IXX WAY", self._plain_out())

    def test_powershell_shown(self):
        self.assertIn("PowerShell", self._plain_out())

    def test_wifi_ip_shown(self):
        self.assertIn("wifi ip", self._plain_out())

    def test_ram_used_shown(self):
        self.assertIn("ram used", self._plain_out())

    def test_cpu_info_shown(self):
        self.assertIn("cpu info", self._plain_out())

    def test_read_file_shown(self):
        self.assertIn('read("notes.txt")', self._plain_out())

    def test_try_shown(self):
        self.assertIn("try", self._plain_out().lower())

    def test_catch_shown(self):
        self.assertIn("catch", self._plain_out().lower())

    # ── plain mode: core content ───────────────────────────────────────────────

    def test_output_contains_ixx(self):
        self.assertIn("IXX", self._plain_out())

    def test_output_contains_tagline(self):
        self.assertIn("The language for the user", self._plain_out())

    def test_output_contains_final_line(self):
        self.assertIn("The computer, translated", self._plain_out())

    def test_output_contains_boot_header(self):
        self.assertIn("BOOT", self._plain_out())

    def test_output_contains_validation_header(self):
        self.assertIn("VALIDATION", self._plain_out())

    def test_output_contains_functions_header(self):
        self.assertIn("FUNCTIONS", self._plain_out())

    def test_output_contains_478_passed(self):
        self.assertIn("478 passed", self._plain_out())

    def test_output_contains_229_passed(self):
        self.assertIn("229 passed", self._plain_out())

    # ── in-process with mocked sleep ──────────────────────────────────────────

    def test_default_mode_runs_without_error(self):
        out = self._run_in_process("default")
        self.assertIn("IXX", out)
        self.assertIn("OLD WAY", out)
        self.assertIn("IXX WAY", out)
        self.assertIn("BOOT", out)

    def test_quick_mode_is_short(self):
        out = self._run_in_process("quick")
        self.assertIn("IXX", out)
        self.assertIn("wifi ip", out)
        # slogans ("No braces") should NOT appear in quick mode
        self.assertNotIn("No braces", out)

    def test_full_mode_includes_all_sections(self):
        out = self._run_in_process("full")
        self.assertIn("TIMELINE", out)
        self.assertIn("BUILT-INS", out)
        self.assertIn("NATIVE COMMANDS", out)
        self.assertIn("A REAL SCRIPT", out)
        self.assertIn("No braces", out)          # slogans in full mode
        self.assertIn("The computer, translated", out)

    def test_full_mode_has_all_comparisons(self):
        out = self._run_in_process("full")
        self.assertIn("PowerShell", out)
        self.assertIn("wifi ip", out)
        self.assertIn("ram used", out)
        self.assertIn("cpu info", out)
        self.assertIn('read("notes.txt")', out)
        self.assertIn("try", out)

    def test_full_mode_real_script_uses_readlines_correctly(self):
        """readlines() takes a path, not file contents — verify the demo is correct."""
        out = self._run_in_process("full")
        self.assertIn('readlines("session.log")', out)

    # ── plain mode: no ANSI escapes ────────────────────────────────────────────

    def test_no_color_disables_ansi(self):
        env = {**os.environ, "NO_COLOR": "1", "PYTHONIOENCODING": "utf-8"}
        env.pop("IXX_COLOR", None)
        r = subprocess.run(
            [sys.executable, "-m", "ixx", "showoff", "plain"],
            capture_output=True, text=True, encoding="utf-8",
            errors="replace", timeout=20, env=env,
        )
        self.assertEqual(r.returncode, 0)
        self.assertNotIn("\033[", r.stdout)

    def test_plain_mode_no_ansi_even_with_forced_color(self):
        """plain mode must suppress ANSI even when IXX_COLOR=1."""
        env = {**os.environ, "IXX_COLOR": "1", "PYTHONIOENCODING": "utf-8"}
        env.pop("NO_COLOR", None)
        r = subprocess.run(
            [sys.executable, "-m", "ixx", "showoff", "plain"],
            capture_output=True, text=True, encoding="utf-8",
            errors="replace", timeout=20, env=env,
        )
        self.assertEqual(r.returncode, 0)
        self.assertNotIn("\033[", r.stdout)


# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    unittest.main(verbosity=2)


    def _run_in_process(self, mode: str) -> str:
        """Run showoff in-process with _sleep mocked out; return stdout."""
        from unittest.mock import patch
        buf = io.StringIO()
        with patch("ixx.showoff._sleep", return_value=None):
            with contextlib.redirect_stdout(buf):
                from ixx.showoff import run
                run(mode)
        return buf.getvalue()

    # ── exit codes ────────────────────────────────────────────────────────────

    def test_showoff_exits_0(self):
        self.assertEqual(self._run_showoff().returncode, 0)

    def test_showoff_quick_exits_0(self):
        self.assertEqual(self._run_showoff("quick").returncode, 0)

    def test_showoff_plain_exits_0(self):
        self.assertEqual(self._run_showoff("plain").returncode, 0)

    def test_showoff_full_exits_0(self):
        self.assertEqual(self._run_showoff("full").returncode, 0)

    # ── required content in plain output ─────────────────────────────────────

    def _plain_out(self) -> str:
        r = self._run_showoff("plain")
        self.assertEqual(r.returncode, 0)
        return r.stdout

    def test_output_contains_ixx(self):
        self.assertIn("IXX", self._plain_out())

    def test_output_contains_tagline(self):
        self.assertIn("The language for the user", self._plain_out())

    def test_output_contains_final_line(self):
        self.assertIn("The computer, translated", self._plain_out())

    def test_output_contains_boot_header(self):
        self.assertIn("BOOT", self._plain_out())

    def test_output_contains_validation_header(self):
        self.assertIn("VALIDATION", self._plain_out())

    def test_output_contains_functions(self):
        self.assertIn("FUNCTIONS", self._plain_out())

    def test_output_contains_file_io(self):
        out = self._plain_out()
        # Section header "FILES + ERRORS" or code using read/readlines
        self.assertTrue("FILES" in out or "read" in out)

    def test_output_contains_try_catch(self):
        out = self._plain_out().lower()
        self.assertIn("try", out)
        self.assertIn("catch", out)

    def test_output_contains_validation_numbers(self):
        out = self._plain_out()
        self.assertIn("478", out)
        self.assertIn("229", out)

    def test_output_contains_478_passed(self):
        self.assertIn("478 passed", self._plain_out())

    def test_output_contains_229_passed(self):
        self.assertIn("229 passed", self._plain_out())

    # ── in-process tests with mocked sleep ────────────────────────────────────

    def test_default_mode_runs_without_error(self):
        out = self._run_in_process("default")
        self.assertIn("IXX", out)
        self.assertIn("The language for the user", out)
        self.assertIn("BOOT", out)

    def test_full_mode_includes_timeline(self):
        out = self._run_in_process("full")
        self.assertIn("The computer, translated", out)
        self.assertIn("TIMELINE", out)
        self.assertIn("v0.4", out)

    def test_quick_mode_is_shorter(self):
        out = self._run_in_process("quick")
        self.assertIn("IXX", out)
        self.assertIn("double", out)  # Functions code example present in quick
        # Slogans section should be absent
        self.assertNotIn("No braces", out)

    def test_unknown_subcommand_falls_back_to_default(self):
        r = self._run_showoff("garbage")
        self.assertEqual(r.returncode, 0)
        self.assertIn("IXX", r.stdout)

    # ── plain mode produces no ANSI even when IXX_COLOR=1 ────────────────────

    def test_no_color_disables_ansi(self):
        env = {**os.environ, "NO_COLOR": "1", "IXX_COLOR": "",
               "PYTHONIOENCODING": "utf-8"}
        r = subprocess.run(
            [sys.executable, "-m", "ixx", "showoff", "plain"],
            capture_output=True, text=True, encoding="utf-8",
            errors="replace", timeout=15, env=env,
        )
        self.assertEqual(r.returncode, 0)
        self.assertNotIn("\033[", r.stdout)

    def test_plain_mode_no_ansi_even_with_forced_color(self):
        """plain mode must suppress ANSI even if IXX_COLOR=1."""
        env = {**os.environ, "IXX_COLOR": "1", "NO_COLOR": "",
               "PYTHONIOENCODING": "utf-8"}
        # Remove NO_COLOR so IXX_COLOR=1 can activate colors
        env.pop("NO_COLOR", None)
        r = subprocess.run(
            [sys.executable, "-m", "ixx", "showoff", "plain"],
            capture_output=True, text=True, encoding="utf-8",
            errors="replace", timeout=15, env=env,
        )
        self.assertEqual(r.returncode, 0)
        self.assertNotIn("\033[", r.stdout)


# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    unittest.main(verbosity=2)
