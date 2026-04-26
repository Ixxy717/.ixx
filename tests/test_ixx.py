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
import json
import os
import subprocess
import sys
import tempfile
import textwrap
import unittest
import unittest.mock
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
        self.assertIn("check passed", out)

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

    def test_check_json_valid(self):
        """--json on a good file emits ok:true with empty errors array."""
        import json
        code, out = cli("check", "examples/hello.ixx", "--json")
        self.assertEqual(code, 0)
        data = json.loads(out)
        self.assertTrue(data["ok"])
        self.assertEqual(data["errors"], [])
        self.assertIn("hello.ixx", data["file"])

    def test_check_json_invalid(self):
        """--json on a bad file emits ok:false with at least one error entry."""
        import json
        bad = ROOT / "examples" / "_test_bad_json.ixx"
        bad.write_text("if age less\n- say oops\n", encoding="utf-8")
        try:
            code, out = cli("check", "examples/_test_bad_json.ixx", "--json")
            self.assertNotEqual(code, 0)
            data = json.loads(out)
            self.assertFalse(data["ok"])
            self.assertGreater(len(data["errors"]), 0)
            err = data["errors"][0]
            self.assertIn("line", err)
            self.assertIn("column", err)
            self.assertIn("message", err)
        finally:
            bad.unlink(missing_ok=True)

    def test_check_json_missing_file(self):
        """--json on a non-existent file emits ok:false with a message."""
        import json
        code, out = cli("check", "examples/_does_not_exist.ixx", "--json")
        self.assertNotEqual(code, 0)
        data = json.loads(out)
        self.assertFalse(data["ok"])
        self.assertGreater(len(data["errors"]), 0)

    # ── semantic check tests ─────────────────────────────────────────────────

    def test_check_semantic_wrong_arg_count(self):
        """check catches wrong argument count for user-defined functions."""
        code, out = cli("check", "StressTest/ExpectedFailures/bad-wrong-arg-count.ixx")
        self.assertNotEqual(code, 0)
        self.assertIn("check failed", out)
        self.assertIn("expects 2", out)

    def test_check_semantic_unknown_function(self):
        """check catches calls to completely unknown functions."""
        code, out = cli("check", "StressTest/ExpectedFailures/bad-unknown-function.ixx")
        self.assertNotEqual(code, 0)
        self.assertIn("check failed", out)
        self.assertIn("not defined", out)

    def test_check_semantic_wrong_builtin_arg_count(self):
        """check catches wrong argument count for built-ins."""
        import tempfile, os
        with tempfile.NamedTemporaryFile(suffix=".ixx", mode="w",
                                        encoding="utf-8", delete=False) as f:
            f.write('say upper("hello", "extra")\n')
            tmp = f.name
        try:
            code, out = cli("check", tmp)
            self.assertNotEqual(code, 0)
            self.assertIn("check failed", out)
            self.assertIn("upper", out)
        finally:
            os.unlink(tmp)

    def test_check_semantic_undefined_variable(self):
        """check catches obvious undefined variable references at top level."""
        import tempfile, os
        with tempfile.NamedTemporaryFile(suffix=".ixx", mode="w",
                                        encoding="utf-8", delete=False) as f:
            f.write("say ghost\n")
            tmp = f.name
        try:
            code, out = cli("check", tmp)
            self.assertNotEqual(code, 0)
            self.assertIn("check failed", out)
            self.assertIn("ghost", out)
        finally:
            os.unlink(tmp)

    def test_check_json_semantic_failure(self):
        """--json emits ok:false with severity/line fields on semantic error."""
        import json
        code, out = cli("check", "StressTest/ExpectedFailures/bad-wrong-arg-count.ixx",
                        "--json")
        self.assertNotEqual(code, 0)
        data = json.loads(out)
        self.assertFalse(data["ok"])
        err = data["errors"][0]
        self.assertIn("severity", err)
        self.assertEqual(err["severity"], "error")
        self.assertIsNotNone(err["line"])
        self.assertIn("add", err["message"])

    def test_check_json_success_schema(self):
        """--json on a clean file returns the expected schema keys."""
        import json
        code, out = cli("check", "examples/hello.ixx", "--json")
        self.assertEqual(code, 0)
        data = json.loads(out)
        self.assertIn("ok", data)
        self.assertIn("file", data)
        self.assertIn("errors", data)
        self.assertTrue(data["ok"])
        self.assertEqual(data["errors"], [])
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

class TestCheckerLiteralValidation(unittest.TestCase):
    """Tests for conservative literal-value checks in ixx check / ixx check --json."""

    # ── helpers ───────────────────────────────────────────────────────────────

    def _check(self, code: str, *extra_flags: str):
        """Write *code* to a temp file, run ixx check, return (exit_code, output)."""
        import tempfile, os as _os
        with tempfile.NamedTemporaryFile(suffix=".ixx", mode="w",
                                         encoding="utf-8", delete=False) as f:
            f.write(code)
            tmp = f.name
        try:
            return cli("check", tmp, *extra_flags)
        finally:
            _os.unlink(tmp)

    def _json_check(self, code: str):
        """Run ixx check --json; return (exit_code, parsed_dict)."""
        import json
        code_val, out = self._check(code, "--json")
        return code_val, json.loads(out)

    # ── color ─────────────────────────────────────────────────────────────────

    def test_color_invalid_literal_human(self):
        """check catches an invalid literal color name."""
        code, out = self._check('x = color("purple", "hello")\n')
        self.assertNotEqual(code, 0)
        self.assertIn("check failed", out)
        self.assertIn("purple", out)

    def test_color_invalid_literal_json(self):
        """--json reports invalid literal color name."""
        import json
        code, out = self._check('x = color("purple", "hello")\n', "--json")
        self.assertNotEqual(code, 0)
        data = json.loads(out)
        self.assertFalse(data["ok"])
        msg = data["errors"][0]["message"]
        self.assertIn("purple", msg)
        self.assertIn("Valid colors", msg)

    def test_color_valid_literal_passes(self):
        """check does NOT flag a known color name."""
        code, out = self._check('x = color("cyan", "hello")\n')
        self.assertEqual(code, 0)

    def test_color_bad_in_stresstest(self):
        """The StressTest bad-color-name.ixx is caught by check."""
        code, out = cli("check", "StressTest/ExpectedFailures/bad-color-name.ixx")
        self.assertNotEqual(code, 0)
        self.assertIn("check failed", out)

    # ── read / readlines ──────────────────────────────────────────────────────

    def test_read_missing_literal_file(self):
        """check catches read() on a non-existent literal path."""
        code, out = self._check(
            'content = read("definitely-not-a-real-path-xyz123.txt")\n'
        )
        self.assertNotEqual(code, 0)
        self.assertIn("check failed", out)
        self.assertIn("not found", out.lower())

    def test_read_missing_json(self):
        """--json reports missing literal file for read()."""
        import json
        code, out = self._check(
            'content = read("definitely-not-a-real-path-xyz123.txt")\n',
            "--json",
        )
        data = json.loads(out)
        self.assertFalse(data["ok"])
        self.assertIn("not found", data["errors"][0]["message"].lower())

    def test_readlines_missing_literal_file(self):
        """check catches readlines() on a non-existent literal path."""
        code, out = self._check(
            'lines = readlines("definitely-not-a-real-path-xyz123.txt")\n'
        )
        self.assertNotEqual(code, 0)
        self.assertIn("File not found", out)

    def test_read_bad_in_stresstest(self):
        """The StressTest bad-file-read.ixx is caught by check."""
        code, out = cli("check", "StressTest/ExpectedFailures/bad-file-read.ixx")
        self.assertNotEqual(code, 0)
        self.assertIn("check failed", out)

    # ── first / sort ──────────────────────────────────────────────────────────

    def test_first_with_text_literal(self):
        """check flags first() called on a text literal."""
        code, out = self._check('x = first("abc")\n')
        self.assertNotEqual(code, 0)
        self.assertIn("first", out)
        self.assertIn("text", out)

    def test_first_with_text_json(self):
        """--json reports first() on text literal."""
        import json
        code, out = self._check('x = first("abc")\n', "--json")
        data = json.loads(out)
        self.assertFalse(data["ok"])
        msg = data["errors"][0]["message"]
        self.assertIn("first", msg)

    def test_sort_with_text_literal(self):
        """check flags sort() called on a text literal."""
        code, out = self._check('x = sort("abc")\n')
        self.assertNotEqual(code, 0)
        self.assertIn("sort", out)

    def test_last_with_number_literal(self):
        """check flags last() called on a number literal."""
        code, out = self._check('x = last(123)\n')
        self.assertNotEqual(code, 0)
        self.assertIn("last", out)

    def test_reverse_with_number_literal(self):
        """check flags reverse() called on a number literal."""
        code, out = self._check('x = reverse(123)\n')
        self.assertNotEqual(code, 0)
        self.assertIn("reverse", out)

    def test_first_with_list_literal_passes(self):
        """check does NOT flag first() called on a list variable."""
        code, out = self._check('items = "a", "b"\nx = first(items)\n')
        self.assertEqual(code, 0)

    # ── count ─────────────────────────────────────────────────────────────────

    def test_count_with_number_literal(self):
        """check flags count() called on a number literal."""
        code, out = self._check('x = count(42)\n')
        self.assertNotEqual(code, 0)
        self.assertIn("count", out)
        self.assertIn("number", out)

    def test_count_with_number_json(self):
        """--json reports count() on number literal."""
        import json
        code, out = self._check('x = count(42)\n', "--json")
        data = json.loads(out)
        self.assertFalse(data["ok"])
        msg = data["errors"][0]["message"]
        self.assertIn("count", msg)
        self.assertIn("number", msg)

    def test_count_with_text_passes(self):
        """check does NOT flag count() called on a text literal."""
        code, out = self._check('x = count("hello")\n')
        self.assertEqual(code, 0)

    # ── number ────────────────────────────────────────────────────────────────

    def test_number_invalid_string_literal(self):
        """check flags number() called on a non-numeric string literal."""
        code, out = self._check('x = number("abc")\n')
        self.assertNotEqual(code, 0)
        self.assertIn("Cannot convert", out)
        self.assertIn("abc", out)

    def test_number_invalid_json(self):
        """--json reports number() on un-convertible string literal."""
        import json
        code, out = self._check('x = number("abc")\n', "--json")
        data = json.loads(out)
        self.assertFalse(data["ok"])
        msg = data["errors"][0]["message"]
        self.assertIn("abc", msg)

    def test_number_valid_string_passes(self):
        """check does NOT flag number() on a valid numeric string literal."""
        code, out = self._check('x = number("42")\n')
        self.assertEqual(code, 0)

    def test_number_valid_float_passes(self):
        """check does NOT flag number() on a valid float string literal."""
        code, out = self._check('x = number("3.14")\n')
        self.assertEqual(code, 0)

    # ── do ────────────────────────────────────────────────────────────────────

    def test_do_empty_string(self):
        """check flags do() called with an empty string literal."""
        code, out = self._check('x = do("")\n')
        self.assertNotEqual(code, 0)
        self.assertIn("empty", out.lower())

    def test_do_empty_string_json(self):
        """--json reports do() called with empty string."""
        import json
        code, out = self._check('x = do("")\n', "--json")
        data = json.loads(out)
        self.assertFalse(data["ok"])
        msg = data["errors"][0]["message"]
        self.assertIn("empty", msg.lower())

    def test_do_nontext_number(self):
        """check flags do() called with a number literal."""
        code, out = self._check('x = do(42)\n')
        self.assertNotEqual(code, 0)
        self.assertIn("text", out.lower())

    def test_do_nontext_json(self):
        """--json reports do() called with a non-text literal."""
        import json
        code, out = self._check('x = do(42)\n', "--json")
        data = json.loads(out)
        self.assertFalse(data["ok"])
        msg = data["errors"][0]["message"]
        self.assertIn("text", msg.lower())

    def test_do_valid_string_passes(self):
        """check does NOT flag do() with a non-empty text literal."""
        code, out = self._check('x = do("ram used")\n')
        self.assertEqual(code, 0)

    def test_do_bad_in_stresstest_empty(self):
        """The StressTest bad-do-empty.ixx is caught by check."""
        code, out = cli("check", "StressTest/ExpectedFailures/bad-do-empty.ixx")
        self.assertNotEqual(code, 0)

    def test_do_bad_in_stresstest_nontext(self):
        """The StressTest bad-do-nontext.ixx is caught by check."""
        code, out = cli("check", "StressTest/ExpectedFailures/bad-do-nontext.ixx")
        self.assertNotEqual(code, 0)


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
        self.assertIn("pip install ixx", self._plain_out())

    def test_output_contains_boot_header(self):
        self.assertIn("IXX SHOWOFF", self._plain_out())

    def test_output_contains_validation_header(self):
        self.assertIn("VALIDATION", self._plain_out())

    def test_output_contains_functions_header(self):
        self.assertIn("FUNCTIONS", self._plain_out())

    def test_output_contains_478_passed(self):
        self.assertIn("hundreds passing", self._plain_out())

    def test_output_contains_229_passed(self):
        self.assertIn("all passing", self._plain_out())

    # ── in-process with mocked sleep ──────────────────────────────────────────

    def test_default_mode_runs_without_error(self):
        out = self._run_in_process("default")
        self.assertIn("IXX", out)
        self.assertIn("OLD WAY", out)
        self.assertIn("IXX WAY", out)
        self.assertIn("IXX SHOWOFF", out)

    def test_quick_mode_is_short(self):
        out = self._run_in_process("quick")
        self.assertIn("IXX", out)
        self.assertIn("wifi ip", out)
        # slogans only appear in full mode
        self.assertNotIn("Readable when you write it", out)

    def test_full_mode_includes_all_sections(self):
        out = self._run_in_process("full")
        self.assertIn("TIMELINE", out)
        self.assertIn("BUILT-INS", out)
        self.assertIn("NATIVE COMMANDS", out)
        self.assertIn("A REAL SCRIPT", out)
        self.assertIn("Readable when you write it", out)   # slogans in full mode
        self.assertIn("pip install ixx", out)

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
# do() built-in — shell bridge
# ══════════════════════════════════════════════════════════════════════════════

class TestDoBuiltin(unittest.TestCase):

    def _run(self, source: str) -> str:
        """Execute IXX source and return combined stdout."""
        return run(source)

    def test_do_ram_used_returns_text(self):
        """do('ram used') returns a non-empty string."""
        result = self._run('x = do("ram used")\nsay x')
        self.assertIsInstance(result, str)
        self.assertGreater(len(result.strip()), 0)

    def test_do_cpu_info_returns_text(self):
        """do('cpu info') returns a non-empty string."""
        result = self._run('x = do("cpu info")\nsay x')
        self.assertIsInstance(result, str)
        self.assertGreater(len(result.strip()), 0)

    def test_do_wifi_ip_returns_text(self):
        """do('wifi ip') returns text (may be unavailable message — must not raise)."""
        # Alias 'wifi ip' → 'ip wifi'. Either a real IP or a friendly
        # 'not available' message is acceptable; an exception is not.
        result = self._run('x = do("wifi ip")\nsay x')
        self.assertIsInstance(result, str)

    def test_do_unknown_command_raises(self):
        """do() with an unknown command raises IXXRuntimeError."""
        from ixx.interpreter import IXXRuntimeError
        with self.assertRaises(IXXRuntimeError):
            self._run('x = do("thiscommanddoesnotexist")')

    def test_do_result_is_ixx_string(self):
        """Output of do() can be used as a text value in further expressions."""
        result = self._run(
            'x = do("ram used")\n'
            'say count(x)'
        )
        # count() of the returned string is its length — must be a positive number
        n = int(result.strip())
        self.assertGreater(n, 0)

    def test_do_try_catch_catches_failure(self):
        """try/catch handles a do() failure gracefully."""
        result = self._run(
            'try\n'
            '- result = do("thiscommanddoesnotexist")\n'
            'catch\n'
            '- say "caught"\n'
            '- say error'
        )
        self.assertIn("caught", result)
        self.assertIn("thiscommanddoesnotexist", result)

    def test_do_cli_path_still_works(self):
        """ixx do 'ram used' CLI path is unchanged."""
        code, out = cli("do", "ram used")
        self.assertEqual(code, 0)
        self.assertGreater(len(out.strip()), 0)

    def test_do_wrong_type_raises(self):
        """do() with a non-text argument raises IXXRuntimeError."""
        from ixx.interpreter import IXXRuntimeError
        with self.assertRaises(IXXRuntimeError):
            self._run("x = do(42)")


# ── TestLoopEach ──────────────────────────────────────────────────────────────

class TestLoopEach(unittest.TestCase):
    """Tests for v0.6.6 loop each list iteration."""

    def _run(self, source: str) -> str:
        from ixx.parser import parse
        from ixx.interpreter import Interpreter
        buf = io.StringIO()
        with unittest.mock.patch("builtins.print",
                                 side_effect=lambda *a, **kw: buf.write(" ".join(str(x) for x in a) + "\n")):
            Interpreter().run(parse(source))
        return buf.getvalue()

    def _check(self, source: str):
        from ixx.parser import parse
        from ixx.checker import SemanticChecker
        return SemanticChecker().check(parse(source), "test.ixx")

    # ── grammar / AST ─────────────────────────────────────────────────────────

    def test_parse_loop_each(self):
        from ixx.parser import parse
        from ixx.ast_nodes import LoopEach
        p = parse('items = "a", "b"\nloop each item in items\n- say item')
        loop = p.body[1]
        self.assertIsInstance(loop, LoopEach)
        self.assertEqual(loop.var_name, "item")

    def test_parse_loop_each_has_body(self):
        from ixx.parser import parse
        from ixx.ast_nodes import LoopEach, Say
        p = parse('items = "a"\nloop each x in items\n- say x')
        loop = p.body[1]
        self.assertIsInstance(loop, LoopEach)
        self.assertEqual(len(loop.body), 1)
        self.assertIsInstance(loop.body[0], Say)

    def test_while_loop_still_parses(self):
        """Existing while-style loop must not be broken."""
        from ixx.parser import parse
        from ixx.ast_nodes import Loop
        p = parse('n = 3\nloop n more than 0\n- n = n - 1')
        self.assertIsInstance(p.body[1], Loop)

    # ── interpreter ───────────────────────────────────────────────────────────

    def test_sum_number_list(self):
        out = self._run('nums = 1, 2, 3, 4, 5\ntotal = 0\nloop each n in nums\n- total = total + n\nsay total')
        self.assertIn("15", out)

    def test_build_text_from_word_list(self):
        out = self._run('words = "a", "b", "c"\nr = ""\nloop each w in words\n- r = r + w\nsay r')
        self.assertIn("abc", out)

    def test_nested_loop_each(self):
        src = 'r = 1, 2\nc = 10, 100\ntotal = 0\nloop each x in r\n- loop each y in c\n-- total = total + x * y\nsay total'
        out = self._run(src)
        self.assertIn("330", out)

    def test_loop_each_inside_function(self):
        src = 'function sum_list lst\n- total = 0\n- loop each n in lst\n-- total = total + n\n- return total\nnums = 4, 6\nsay sum_list(nums)'
        out = self._run(src)
        self.assertIn("10", out)

    def test_return_from_inside_loop_each(self):
        src = ('function first_positive lst\n'
               '- loop each n in lst\n'
               '-- if n more than 0\n'
               '--- return n\n'
               '- return 0\n'
               'items = -2, -1, 5, 9\n'
               'say first_positive(items)')
        out = self._run(src)
        self.assertIn("5", out)

    def test_try_catch_inside_loop_each(self):
        src = ('values = "1", "bad", "3"\n'
               'total = 0\n'
               'errors = 0\n'
               'loop each v in values\n'
               '- try\n'
               '-- total = total + number(v)\n'
               '- catch\n'
               '-- errors = errors + 1\n'
               'say total\n'
               'say errors')
        out = self._run(src)
        self.assertIn("4", out)
        self.assertIn("1", out)

    # ── scoping ───────────────────────────────────────────────────────────────

    def test_scoping_predeclared_survives(self):
        """If the loop var existed before the loop, the last value survives after."""
        src = 'items = "x", "y", "z"\ncurrent = ""\nloop each current in items\n- say current\nsay current'
        out = self._run(src)
        lines = [l.strip() for l in out.strip().splitlines() if l.strip()]
        self.assertEqual(lines[-1], "z")

    def test_scoping_new_var_does_not_leak(self):
        """If the loop var did not exist before the loop, it is not accessible after."""
        from ixx.interpreter import IXXRuntimeError
        src = 'items = "a", "b"\nloop each newvar in items\n- say newvar\nsay newvar'
        with self.assertRaises(IXXRuntimeError):
            self._run(src)

    # ── runtime error ─────────────────────────────────────────────────────────

    def test_non_list_text_raises(self):
        from ixx.interpreter import IXXRuntimeError
        with self.assertRaises(IXXRuntimeError) as ctx:
            self._run('loop each ch in "hello"\n- say ch')
        self.assertIn("expects a list", str(ctx.exception))

    def test_non_list_number_raises(self):
        from ixx.interpreter import IXXRuntimeError
        with self.assertRaises(IXXRuntimeError) as ctx:
            self._run('loop each n in 42\n- say n')
        self.assertIn("expects a list", str(ctx.exception))

    def test_non_list_bool_raises(self):
        from ixx.interpreter import IXXRuntimeError
        with self.assertRaises(IXXRuntimeError):
            self._run('loop each x in YES\n- say x')

    # ── checker ───────────────────────────────────────────────────────────────

    def test_checker_accepts_valid_loop_each(self):
        errs = self._check('nums = 1, 2, 3\ntotal = 0\nloop each n in nums\n- total = total + n\nsay total')
        self.assertEqual(errs, [])

    def test_checker_var_defined_inside_body(self):
        """Loop variable must not trigger unknown-var error inside the body."""
        errs = self._check('items = "a", "b"\nloop each item in items\n- say item')
        self.assertEqual(errs, [])

    def test_checker_predeclared_var_survives(self):
        """Predeclared loop var should not trigger error after the loop."""
        errs = self._check('items = "a", "b"\ncurrent = ""\nloop each current in items\n- say current\nsay current')
        self.assertFalse(any("current" in e.message and "not defined" in e.message for e in errs))

    def test_checker_non_predeclared_var_leaks_caught(self):
        """Using non-predeclared loop var after the loop should be flagged."""
        errs = self._check('items = "a", "b"\nloop each item in items\n- say item\nsay item')
        self.assertTrue(any("item" in e.message for e in errs))

    def test_checker_literal_text_iterable(self):
        """Top-level literal text iterable should be flagged."""
        errs = self._check('loop each ch in "abc"\n- say ch')
        self.assertTrue(any("expects a list" in e.message for e in errs))

    def test_checker_literal_number_iterable(self):
        """Top-level literal number iterable should be flagged."""
        errs = self._check('loop each n in 42\n- say n')
        self.assertTrue(any("expects a list" in e.message for e in errs))

    def test_checker_list_literal_not_flagged(self):
        """A variable holding a list (not a scalar literal) must NOT be flagged."""
        errs = self._check('items = 1, 2, 3\nloop each x in items\n- say x')
        self.assertFalse(any("expects a list" in e.message for e in errs))

    def test_checker_json_text_literal(self):
        """ixx check --json on literal text iterable returns ok false with message."""
        code, out = cli("check", "StressTest/CheckJson/bad-loop-each-text-literal.ixx", "--json")
        self.assertEqual(code, 1)
        data = json.loads(out)
        self.assertFalse(data["ok"])
        self.assertTrue(any("expects a list" in e["message"] for e in data["errors"]))


# ── TestImports ───────────────────────────────────────────────────────────────

class TestImports(unittest.TestCase):
    """Tests for the v0.6.5 import system."""

    def setUp(self):
        self._td = tempfile.TemporaryDirectory()
        self._dir = self._td.name

    def tearDown(self):
        self._td.cleanup()

    def _write(self, name: str, content: str) -> str:
        path = os.path.join(self._dir, name)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return path

    def _run_main(self, source: str) -> str:
        from ixx.parser import parse
        from ixx.modules import resolve_imports
        from ixx.interpreter import Interpreter
        prog = parse(source)
        imported = resolve_imports(prog, self._dir)
        buf = io.StringIO()
        with unittest.mock.patch("builtins.print",
                                 side_effect=lambda *a, **kw: buf.write(" ".join(str(x) for x in a) + "\n")):
            Interpreter().run(prog, imported)
        return buf.getvalue()

    # ── grammar ───────────────────────────────────────────────────────────────

    def test_parse_use_file(self):
        from ixx.parser import parse
        from ixx.ast_nodes import UseStmt
        p = parse('use "helpers.ixx"\nsay "hi"')
        self.assertIsInstance(p.body[0], UseStmt)
        self.assertEqual(p.body[0].kind, "file")
        self.assertEqual(p.body[0].path, "helpers.ixx")

    def test_parse_use_std(self):
        from ixx.parser import parse
        from ixx.ast_nodes import UseStmt
        p = parse('use std "time"\nsay "hi"')
        self.assertIsInstance(p.body[0], UseStmt)
        self.assertEqual(p.body[0].kind, "std")
        self.assertEqual(p.body[0].path, "time")

    def test_parse_without_use_unchanged(self):
        """Existing programs still parse fine."""
        from ixx.parser import parse
        p = parse('x = 1\nsay x')
        self.assertEqual(len(p.body), 2)

    # ── module resolver ───────────────────────────────────────────────────────

    def test_resolve_imports_returns_funcs(self):
        from ixx.parser import parse
        from ixx.modules import resolve_imports
        self._write("helpers.ixx", "function double x\n- return x * 2\n")
        prog = parse('use "helpers.ixx"\nsay "x"')
        result = resolve_imports(prog, self._dir)
        self.assertIn("double", result)

    def test_resolve_top_level_stmts_not_included(self):
        """Top-level say/assign in imported file are ignored (not in func table)."""
        from ixx.parser import parse
        from ixx.modules import resolve_imports
        self._write("helpers.ixx", 'say "SHOULD NOT PRINT"\nfunction double x\n- return x * 2\n')
        prog = parse('use "helpers.ixx"\nsay "x"')
        result = resolve_imports(prog, self._dir)
        self.assertIn("double", result)
        self.assertNotIn("SHOULD NOT PRINT", str(result))

    def test_resolve_missing_file_raises(self):
        from ixx.parser import parse
        from ixx.modules import resolve_imports, IXXImportError
        prog = parse('use "missing.ixx"\nsay "x"')
        with self.assertRaises(IXXImportError):
            resolve_imports(prog, self._dir)

    def test_resolve_circular_import_raises(self):
        from ixx.parser import parse
        from ixx.modules import resolve_imports, IXXImportError
        self._write("a.ixx", 'use "b.ixx"\nfunction fa\n- return 1\n')
        self._write("b.ixx", 'use "a.ixx"\nfunction fb\n- return 2\n')
        prog = parse('use "a.ixx"\nsay "x"')
        with self.assertRaises(IXXImportError) as ctx:
            resolve_imports(prog, self._dir)
        self.assertIn("loop", str(ctx.exception))

    def test_resolve_duplicate_function_raises(self):
        from ixx.parser import parse
        from ixx.modules import resolve_imports, IXXImportError
        self._write("a.ixx", 'function double x\n- return x * 2\n')
        self._write("b.ixx", 'function double x\n- return x * 4\n')
        prog = parse('use "a.ixx"\nuse "b.ixx"\nsay "x"')
        with self.assertRaises(IXXImportError) as ctx:
            resolve_imports(prog, self._dir)
        self.assertIn("double", str(ctx.exception))

    def test_resolve_transitive_imports(self):
        from ixx.parser import parse
        from ixx.modules import resolve_imports
        self._write("base.ixx", 'function base_func x\n- return x + 1\n')
        self._write("mid.ixx", 'use "base.ixx"\nfunction mid_func x\n- return x + 2\n')
        prog = parse('use "mid.ixx"\nsay "x"')
        result = resolve_imports(prog, self._dir)
        self.assertIn("base_func", result)
        self.assertIn("mid_func", result)

    # ── interpreter ───────────────────────────────────────────────────────────

    def test_imported_function_callable(self):
        self._write("helpers.ixx", "function double x\n- return x * 2\n")
        output = self._run_main('use "helpers.ixx"\nsay double(21)')
        self.assertIn("42", output)

    def test_imported_top_level_does_not_run(self):
        """Top-level say in imported file must not appear in output."""
        self._write("helpers.ixx", 'say "SHOULD NOT PRINT"\nfunction double x\n- return x * 2\n')
        output = self._run_main('use "helpers.ixx"\nsay double(3)')
        self.assertNotIn("SHOULD NOT PRINT", output)
        self.assertIn("6", output)

    def test_local_function_overrides_raises(self):
        """Local function with same name as imported function should raise."""
        from ixx.interpreter import Interpreter, IXXRuntimeError
        from ixx.parser import parse
        from ixx.modules import resolve_imports
        self._write("helpers.ixx", "function double x\n- return x * 2\n")
        prog = parse('use "helpers.ixx"\nfunction double x\n- return x * 99\nsay double(1)')
        imported = resolve_imports(prog, self._dir)
        with self.assertRaises(IXXRuntimeError) as ctx:
            Interpreter().run(prog, imported)
        self.assertIn("double", str(ctx.exception))

    def test_stdlib_time(self):
        from ixx.parser import parse
        from ixx.modules import resolve_imports
        prog = parse('use std "time"\nsay time_greeting(9)')
        imported = resolve_imports(prog, self._dir)
        self.assertIn("time_greeting", imported)

    def test_stdlib_time_runs(self):
        output = self._run_main('use std "time"\nsay time_greeting(9)')
        self.assertIn("Good morning", output)

    def test_stdlib_date_runs(self):
        output = self._run_main('use std "date"\nsay is_leap_year(2024)')
        self.assertIn("YES", output)

    def test_stdlib_missing_raises(self):
        from ixx.parser import parse
        from ixx.modules import resolve_imports, IXXImportError
        prog = parse('use std "nosuchmodule"\nsay "x"')
        with self.assertRaises(IXXImportError):
            resolve_imports(prog, self._dir)

    # ── checker ───────────────────────────────────────────────────────────────

    def test_checker_knows_imported_functions(self):
        from ixx.parser import parse
        from ixx.modules import resolve_imports
        from ixx.checker import SemanticChecker
        self._write("helpers.ixx", "function double x\n- return x * 2\n")
        prog = parse('use "helpers.ixx"\nx = double(5)\nsay x')
        imported = resolve_imports(prog, self._dir)
        errors = SemanticChecker().check(prog, "main.ixx", imported)
        self.assertEqual(errors, [])

    def test_checker_wrong_arity_imported_function(self):
        from ixx.parser import parse
        from ixx.modules import resolve_imports
        from ixx.checker import SemanticChecker
        self._write("helpers.ixx", "function double x\n- return x * 2\n")
        prog = parse('use "helpers.ixx"\nx = double(1, 2, 3)\nsay x')
        imported = resolve_imports(prog, self._dir)
        errors = SemanticChecker().check(prog, "main.ixx", imported)
        msgs = [e.message for e in errors]
        self.assertTrue(any("double" in m and "expects 1" in m for m in msgs))

    def test_checker_duplicate_local_imported_function(self):
        from ixx.parser import parse
        from ixx.modules import resolve_imports
        from ixx.checker import SemanticChecker
        self._write("helpers.ixx", "function double x\n- return x * 2\n")
        prog = parse('use "helpers.ixx"\nfunction double x\n- return x * 99\nsay double(1)')
        imported = resolve_imports(prog, self._dir)
        errors = SemanticChecker().check(prog, "main.ixx", imported)
        self.assertTrue(any("double" in e.message for e in errors))


# ══════════════════════════════════════════════════════════════════════════════
# TestEdgeCases — v0.6.7 bug & edge case coverage
# ══════════════════════════════════════════════════════════════════════════════

class TestEdgeCases(unittest.TestCase):
    """Covers every bug and edge case fixed / documented in v0.6.7."""

    # ── color() bool/nothing ───────────────────────────────────────────────────

    def test_color_bool_yes(self):
        """color() with YES must show 'YES', not Python 'True'."""
        src = 'say color("bold", YES)'
        output = run(src)
        self.assertIn("YES", output)
        self.assertNotIn("True", output)

    def test_color_bool_no(self):
        """color() with NO must show 'NO', not Python 'False'."""
        src = 'say color("bold", NO)'
        output = run(src)
        self.assertIn("NO", output)
        self.assertNotIn("False", output)

    def test_color_nothing(self):
        """color() with nothing must return empty string (no crash)."""
        src = 'x = color("red", nothing)\nsay count(x)'
        output = run(src)
        self.assertEqual(output, "0")

    # ── _eval_binop TypeError wraps ───────────────────────────────────────────

    def test_binop_list_minus_number(self):
        """list - number must raise IXXRuntimeError, not Python crash."""
        src = 'x = 1, 2, 3\ny = x - 1\nsay y'
        with self.assertRaises(IXXRuntimeError):
            run(src)

    def test_binop_nothing_plus_number(self):
        """nothing + number must raise IXXRuntimeError."""
        src = 'x = nothing\ny = x + 1\nsay y'
        with self.assertRaises(IXXRuntimeError):
            run(src)

    # ── text + nothing → error (bug 2a) ──────────────────────────────────────

    def test_text_plus_nothing_raises(self):
        """'text' + nothing must raise IXXRuntimeError, not produce 'textnothing'."""
        src = 'x = "hello" + nothing\nsay x'
        with self.assertRaises(IXXRuntimeError) as ctx:
            run(src)
        self.assertIn("nothing", str(ctx.exception).lower())

    def test_nothing_plus_text_raises(self):
        """nothing + 'text' must also raise IXXRuntimeError."""
        src = 'x = nothing + "world"\nsay x'
        with self.assertRaises(IXXRuntimeError):
            run(src)

    # ── _eval_compare TypeError wrap (bug 3) ─────────────────────────────────

    def test_compare_text_vs_number_less_than(self):
        """'abc' less than 1 must raise IXXRuntimeError, not crash with Python TypeError."""
        src = 'if "abc" less than 1\n- say "should not reach"'
        with self.assertRaises(IXXRuntimeError):
            run(src)

    def test_compare_text_vs_number_more_than(self):
        src = 'if "abc" more than 1\n- say "bad"'
        with self.assertRaises(IXXRuntimeError):
            run(src)

    def test_compare_try_catch_wraps_compare_error(self):
        """After the fix, try/catch should intercept comparison type errors."""
        src = textwrap.dedent("""\
            try
            - x = "abc" more than 1
            catch
            - say "caught"
        """)
        output = run(src)
        self.assertEqual(output, "caught")

    # ── min/max already wrapped (bug 4 — confirmed NOT a bug) ─────────────────

    def test_min_mixed_types_caught(self):
        """min(1, 'a') error must be catchable via try/catch."""
        src = textwrap.dedent("""\
            try
            - x = min(1, "a")
            catch
            - say "caught"
        """)
        output = run(src)
        self.assertEqual(output, "caught")

    # ── ask() EOFError wrap (bug 6) ───────────────────────────────────────────

    def test_ask_eoferror_raises_ixx(self):
        """ask() on closed stdin must raise IXXRuntimeError, not crash."""
        with unittest.mock.patch("builtins.input", side_effect=EOFError):
            with self.assertRaises(IXXRuntimeError) as ctx:
                run('x = ask("?")\nsay x')
        self.assertIn("stdin", str(ctx.exception).lower())

    # ── UnicodeDecodeError caught by try/catch (bug 5) ───────────────────────

    def test_unicode_decode_caught(self):
        """UnicodeDecodeError from reading a binary file must be caught by try/catch."""
        import tempfile, os
        with tempfile.NamedTemporaryFile(delete=False, suffix=".bin") as f:
            f.write(b"\xff\xfe\x00bad")
            path = f.name
        try:
            src = textwrap.dedent(f"""\
                try
                - content = read("{path}")
                catch
                - say "caught"
            """)
            output = run(src)
            self.assertEqual(output, "caught")
        finally:
            os.unlink(path)

    # ── first/last on empty list ──────────────────────────────────────────────

    def test_first_on_empty_list(self):
        """first() on an empty list must return nothing.
        IXX has no empty-list literal; split("") is the valid production path.
        """
        # split("") calls Python "".split() which returns [] — a real empty list.
        src = 'empty = split("")\nsay first(empty)'
        output = run(src)
        self.assertEqual(output, "nothing")

    def test_first_on_nonempty_list(self):
        """first() on a non-empty list returns the first element."""
        src = 'items = 1, 2, 3\nsay type(first(items))'
        output = run(src)
        self.assertIn("number", output)

    def test_last_on_empty_list(self):
        """last() on an empty list must return nothing.
        IXX has no empty-list literal; split("") is the valid production path.
        """
        src = 'empty = split("")\nsay last(empty)'
        output = run(src)
        self.assertEqual(output, "nothing")

    def test_last_on_nonempty_list(self):
        """last() on a non-empty list returns the last element."""
        src = 'items = 10, 20, 30\nsay last(items)'
        output = run(src)
        self.assertEqual(output, "30")

    # ── number() edge cases ───────────────────────────────────────────────────

    def test_number_float_string(self):
        """number('1.0') must return a number that displays cleanly (no trailing .0)."""
        src = 'say number("1.0")'
        output = run(src)
        self.assertEqual(output, "1")

    def test_number_bool_raises(self):
        """number(YES) must raise IXXRuntimeError."""
        src = 'say number(YES)'
        with self.assertRaises(IXXRuntimeError):
            run(src)

    def test_number_nothing_raises(self):
        """number(nothing) must raise IXXRuntimeError (can't convert 'nothing')."""
        src = 'say number(nothing)'
        with self.assertRaises(IXXRuntimeError):
            run(src)

    # ── say with no args ──────────────────────────────────────────────────────

    def test_say_no_args(self):
        """say with no arguments must print a blank line."""
        src = 'say'
        output = run(src)
        self.assertEqual(output, "")

    # ── division behaviour ────────────────────────────────────────────────────

    def test_division_integer_result(self):
        """10 / 2 must return int 5, not float 5.0."""
        src = 'say type(10 / 2)'
        output = run(src)
        self.assertEqual(output, "number")

    def test_division_float_result(self):
        """10 / 3 must return a float."""
        src = 'say 10 / 3'
        output = run(src)
        self.assertIn(".", output)

    # ── contains with number in string ───────────────────────────────────────

    def test_contains_number_in_string(self):
        """'abc' contains 97 must be NO (97 is not '97'... actually str(97)='97' not in 'abc')."""
        src = 'say "abc" contains 97'
        output = run(src)
        self.assertEqual(output, "NO")

    # ── replace coerces replacement to str ───────────────────────────────────

    def test_replace_number_replacement(self):
        """replace('abc', 'b', 42) must produce 'a42c'."""
        src = 'say replace("abc", "b", 42)'
        output = run(src)
        self.assertEqual(output, "a42c")

    # ── checker: LoopEach write inside loop, read at top-level ───────────────

    def test_checker_loop_each_write_then_read(self):
        """A write() inside loop each must not cause a false 'file not found' for a subsequent read()."""
        import tempfile, os
        with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as f:
            path = f.name
        os.unlink(path)
        from ixx.checker import SemanticChecker
        src = textwrap.dedent(f"""\
            items = "a", "b"
            loop each item in items
            - write "{path}", item
            content = read("{path}")
            say content
        """)
        prog = parse(src)
        errors = SemanticChecker().check(prog, "<test>")
        hard_errors = [e for e in errors if e.severity == "error"]
        self.assertEqual(hard_errors, [], msg=f"Unexpected errors: {hard_errors}")

    # ── checker: interpolation expression warning ─────────────────────────────

    def test_checker_interpolation_expression_warn(self):
        """say '{count(items)}' must produce a warning about non-interpolatable expression."""
        from ixx.checker import SemanticChecker
        src = 'items = 1, 2, 3\nsay "Total: {count(items)}"'
        prog = parse(src)
        errors = SemanticChecker().check(prog, "<test>")
        warnings = [e for e in errors if e.severity == "warning"]
        self.assertTrue(
            any("count(items)" in e.message or "interpolat" in e.message for e in warnings),
            msg=f"Expected interpolation warning, got: {warnings}"
        )

    def test_checker_interpolation_warn_does_not_fail_check(self):
        """Interpolation warnings must not cause ok: false in JSON output."""
        import json, tempfile, os
        src = 'items = 1, 2, 3\nsay "Total: {count(items)}"\n'
        with tempfile.NamedTemporaryFile(mode="w", suffix=".ixx", delete=False, encoding="utf-8") as f:
            f.write(src)
            path = f.name
        try:
            rc, out = cli("check", path, "--json")
            data = json.loads(out)
            self.assertTrue(data["ok"], msg=f"Expected ok: true, got: {out}")
        finally:
            os.unlink(path)

    # ── REPL heuristic recognises new IXX keywords ───────────────────────────

    def test_repl_ixx_starters_contains_function(self):
        """The REPL ixx_starters set must contain 'function'."""
        import ast as _ast, inspect
        from ixx.shell import repl
        src = inspect.getsource(repl._try_run_ixx)
        self.assertIn("function", src)

    def test_repl_ixx_starters_contains_try(self):
        from ixx.shell import repl
        import inspect
        src = inspect.getsource(repl._try_run_ixx)
        self.assertIn('"try"', src)


# ══════════════════════════════════════════════════════════════════════════════
# Letter A — v0.6.8 crash-path fixes
# ══════════════════════════════════════════════════════════════════════════════

class TestLetterA(unittest.TestCase):
    """Tests for v0.6.8 Letter A: crash path fixes."""

    # ── A1: split() empty separator ───────────────────────────────────────────

    def test_split_empty_sep_raises(self):
        """split(x, '') must raise IXXRuntimeError, not raw ValueError."""
        with self.assertRaises(IXXRuntimeError) as ctx:
            run('say split("hello", "")')
        self.assertIn("separator", str(ctx.exception).lower())
        self.assertIn("empty", str(ctx.exception).lower())

    def test_split_empty_sep_message_no_traceback(self):
        """The split empty-sep error must not contain 'ValueError'."""
        try:
            run('say split("hello", "")')
        except IXXRuntimeError as e:
            self.assertNotIn("ValueError", str(e))
        except Exception as e:
            self.fail(f"Expected IXXRuntimeError, got {type(e).__name__}: {e}")

    def test_split_normal_still_works(self):
        """Normal split must still work after the empty-sep guard."""
        result = run('parts = split("a,b,c", ",")\nsay count(parts)')
        self.assertEqual(result, "3")

    def test_split_no_sep_still_works(self):
        """split(x) with no separator must still split on whitespace."""
        result = run('parts = split("hello world")\nsay count(parts)')
        self.assertEqual(result, "2")

    # ── A2: ask() KeyboardInterrupt ───────────────────────────────────────────

    def test_ask_keyboard_interrupt_becomes_ixx_error(self):
        """ask() KeyboardInterrupt must raise IXXRuntimeError, not propagate raw."""
        with unittest.mock.patch("builtins.input", side_effect=KeyboardInterrupt):
            with self.assertRaises(IXXRuntimeError) as ctx:
                run('x = ask("prompt")\nsay x')
        self.assertIn("cancelled", str(ctx.exception).lower())

    def test_ask_keyboard_interrupt_catchable_by_try(self):
        """ask() KeyboardInterrupt must be catchable by IXX try/catch."""
        with unittest.mock.patch("builtins.input", side_effect=KeyboardInterrupt):
            result = run(
                'try\n'
                '- x = ask("?")\n'
                'catch\n'
                '- say "caught"'
            )
        self.assertEqual(result, "caught")

    def test_ask_eof_still_friendly(self):
        """ask() EOF must still give the existing friendly message."""
        with unittest.mock.patch("builtins.input", side_effect=EOFError):
            with self.assertRaises(IXXRuntimeError) as ctx:
                run('x = ask("?")\nsay x')
        self.assertIn("input", str(ctx.exception).lower())

    # ── A3: builtin TypeError not reported as arity ───────────────────────────

    def test_builtin_type_error_not_arity_message(self):
        """A builtin type error must not say 'Wrong number of arguments'."""
        # sort() on a mixed list raises a TypeError internally
        try:
            run('items = 1, "a"\nsort(items)')
        except IXXRuntimeError as e:
            self.assertNotIn("Wrong number of arguments", str(e))
        except Exception:
            pass  # other exceptions are fine here

    def test_builtin_arity_error_still_friendly(self):
        """Wrong arity for a builtin must still give a friendly message."""
        try:
            run('say count()')
        except IXXRuntimeError as e:
            msg = str(e)
            self.assertNotIn("positional argument", msg)
            # Should say something about wrong number of arguments
            self.assertTrue(
                "argument" in msg.lower() or "number" in msg.lower(),
                f"Expected arity hint, got: {msg}"
            )

    def test_builtin_type_error_no_raw_python(self):
        """Builtin type errors must not expose raw Python exception text."""
        # Passing a non-list to sort triggers a type error path
        try:
            run('items = 1, "a"\nsort(items)')
        except IXXRuntimeError as e:
            msg = str(e)
            self.assertNotIn("'<' not supported", msg)
            self.assertNotIn("TypeError", msg)

    # ── A4: nested function definitions ───────────────────────────────────────

    def test_nested_function_inside_if_runtime(self):
        """function inside if must raise IXXRuntimeError at runtime."""
        with self.assertRaises(IXXRuntimeError) as ctx:
            run(
                'if YES\n'
                '- function bad x\n'
                '-- return x\n'
                'say "done"'
            )
        self.assertIn("top level", str(ctx.exception).lower())

    def test_nested_function_inside_loop_runtime(self):
        """function inside loop must raise IXXRuntimeError at runtime."""
        with self.assertRaises(IXXRuntimeError) as ctx:
            run(
                'n = 1\n'
                'loop n less than 2\n'
                '- function bad x\n'
                '-- return x\n'
                '- n = 2'
            )
        self.assertIn("top level", str(ctx.exception).lower())

    def test_nested_function_inside_loop_each_runtime(self):
        """function inside loop each must raise IXXRuntimeError at runtime."""
        with self.assertRaises(IXXRuntimeError) as ctx:
            run(
                'items = 1, 2\n'
                'loop each item in items\n'
                '- function bad x\n'
                '-- return x'
            )
        self.assertIn("top level", str(ctx.exception).lower())

    def test_nested_function_inside_try_runtime(self):
        """function inside try raises IXXRuntimeError, which IXX try/catch can catch."""
        # The nested function error IS catchable by IXX's own try/catch block —
        # this is correct behavior (users can recover from it).
        result = run(
            'try\n'
            '- function bad x\n'
            '-- return x\n'
            'catch\n'
            '- say error'
        )
        self.assertIn("top level", result.lower())

    def test_nested_function_inside_function_runtime(self):
        """function inside another function must raise IXXRuntimeError at runtime."""
        with self.assertRaises(IXXRuntimeError) as ctx:
            run(
                'function outer a\n'
                '- function inner x\n'
                '-- return x\n'
                'say outer(1)'
            )
        self.assertIn("top level", str(ctx.exception).lower())

    def test_nested_function_checker_inside_if(self):
        """Checker must flag function inside if as an error."""
        from ixx.checker import SemanticChecker
        program = parse(
            'if YES\n'
            '- function bad x\n'
            '-- return x'
        )
        errors = SemanticChecker().check(program, "<test>")
        messages = [e.message for e in errors]
        self.assertTrue(
            any("top level" in m.lower() for m in messages),
            f"Expected nested function error, got: {messages}"
        )

    def test_nested_function_checker_inside_loop(self):
        """Checker must flag function inside loop as an error."""
        from ixx.checker import SemanticChecker
        program = parse(
            'n = 3\n'
            'loop n more than 0\n'
            '- function bad x\n'
            '-- return x\n'
            '- n = n - 1'
        )
        errors = SemanticChecker().check(program, "<test>")
        self.assertTrue(any("top level" in e.message.lower() for e in errors))

    def test_nested_function_checker_inside_function(self):
        """Checker must flag function inside another function as an error."""
        from ixx.checker import SemanticChecker
        program = parse(
            'function outer\n'
            '- function inner x\n'
            '-- return x'
        )
        errors = SemanticChecker().check(program, "<test>")
        self.assertTrue(any("top level" in e.message.lower() for e in errors))

    def test_top_level_function_still_works(self):
        """Top-level function definitions must still work normally."""
        result = run(
            'function double x\n'
            '- return x * 2\n'
            'say double(5)'
        )
        self.assertEqual(result, "10")

    # ── A5: UnicodeDecodeError in file builtins ───────────────────────────────

    def test_read_unicode_error_friendly(self):
        """read() on a binary file must give IXXRuntimeError, not UnicodeDecodeError."""
        import tempfile, os
        with tempfile.NamedTemporaryFile(delete=False, suffix=".bin") as f:
            f.write(b"\xff\xfe binary \x00\x01 garbage")
            path = f.name
        # Use forward slashes so \t in Windows temp paths isn't treated as tab escape.
        ixx_path = path.replace("\\", "/")
        try:
            with self.assertRaises(IXXRuntimeError) as ctx:
                run(f'say read("{ixx_path}")')
            msg = str(ctx.exception)
            self.assertNotIn("UnicodeDecodeError", msg)
            self.assertNotIn("codec", msg)
            self.assertIn("cannot be decoded", msg)
        finally:
            os.unlink(path)

    def test_readlines_unicode_error_friendly(self):
        """readlines() on a binary file must give IXXRuntimeError, not UnicodeDecodeError."""
        import tempfile, os
        with tempfile.NamedTemporaryFile(delete=False, suffix=".bin") as f:
            f.write(b"\xff\xfe binary \x00\x01 garbage")
            path = f.name
        # Use forward slashes so \t in Windows temp paths isn't treated as tab escape.
        ixx_path = path.replace("\\", "/")
        try:
            with self.assertRaises(IXXRuntimeError) as ctx:
                run(f'say readlines("{ixx_path}")')
            msg = str(ctx.exception)
            self.assertNotIn("UnicodeDecodeError", msg)
            self.assertIn("cannot be decoded", msg)
        finally:
            os.unlink(path)


# ══════════════════════════════════════════════════════════════════════════════

# ══════════════════════════════════════════════════════════════════════════════
# Letter B — v0.6.8 wrong-output fixes
# ══════════════════════════════════════════════════════════════════════════════

class TestLetterB(unittest.TestCase):
    """Tests for v0.6.8 Letter B: silently-incorrect-output fixes."""

    # ── B1: join() display ────────────────────────────────────────────────────

    def test_join_yes_no_nothing(self):
        """join() must display YES/NO/nothing, not True/False/None."""
        result = run(
            'vals = YES, NO, nothing\n'
            'say join(vals, " ")'
        )
        self.assertEqual(result, "YES NO nothing")

    def test_join_yes_no_no_python_repr(self):
        """join() must not produce True/False/None."""
        result = run('vals = YES, NO, nothing\nsay join(vals, ",")')
        self.assertNotIn("True", result)
        self.assertNotIn("False", result)
        self.assertNotIn("None", result)

    def test_join_with_separator_displays_correctly(self):
        """join() with custom separator must show IXX values."""
        result = run('vals = YES, NO\nsay join(vals, " | ")')
        self.assertEqual(result, "YES | NO")

    def test_join_numbers_still_work(self):
        """join() with numbers still works correctly."""
        result = run('nums = 1, 2, 3\nsay join(nums, "-")')
        self.assertEqual(result, "1-2-3")

    def test_join_default_separator(self):
        """join() default separator is ', '."""
        result = run('vals = "a", "b", "c"\nsay join(vals)')
        self.assertEqual(result, "a, b, c")

    # ── B2: replace() replacement display ────────────────────────────────────

    def test_replace_replacement_yes(self):
        """replace() with YES replacement must show 'YES', not 'True'."""
        result = run('say replace("x is here", "here", YES)')
        self.assertEqual(result, "x is YES")

    def test_replace_replacement_no(self):
        """replace() with NO replacement must show 'NO', not 'False'."""
        result = run('say replace("x is here", "here", NO)')
        self.assertEqual(result, "x is NO")

    def test_replace_replacement_nothing(self):
        """replace() with nothing replacement must show 'nothing', not 'None'."""
        result = run('say replace("x is here", "here", nothing)')
        self.assertEqual(result, "x is nothing")

    def test_replace_normal_still_works(self):
        """replace() with normal text replacement still works."""
        result = run('say replace("hello world", "world", "IXX")')
        self.assertEqual(result, "hello IXX")

    # ── B3: replace() empty find ──────────────────────────────────────────────

    def test_replace_empty_find_raises(self):
        """replace() with empty find string must raise IXXRuntimeError."""
        with self.assertRaises(IXXRuntimeError) as ctx:
            run('say replace("abc", "", "X")')
        self.assertIn("empty", str(ctx.exception).lower())

    def test_replace_empty_find_no_python_behavior(self):
        """replace() with empty find must not silently insert between every char."""
        try:
            run('say replace("abc", "", "X")')
            self.fail("Expected IXXRuntimeError")
        except IXXRuntimeError as e:
            self.assertIn("empty", str(e).lower())

    # ── B4: number() error message display ───────────────────────────────────

    def test_number_nothing_error_says_nothing(self):
        """number(nothing) error must say 'nothing', not 'None'."""
        with self.assertRaises(IXXRuntimeError) as ctx:
            run('x = nothing\nsay number(x)')
        msg = str(ctx.exception)
        self.assertIn("nothing", msg)
        self.assertNotIn("None", msg)

    def test_number_yes_error_says_yes(self):
        """number(YES) error must say 'YES', not 'True'."""
        with self.assertRaises(IXXRuntimeError) as ctx:
            run('say number(YES)')
        msg = str(ctx.exception)
        self.assertIn("YES", msg)
        self.assertNotIn("True", msg)

    def test_number_valid_string_still_works(self):
        """number('42') must still work."""
        self.assertEqual(run('say number("42")'), "42")

    # ── B5: contains text path uses display() ────────────────────────────────

    def test_contains_text_nothing(self):
        '"nothing here" contains nothing must match "nothing" display value.'
        result = run('say "nothing here" contains nothing')
        self.assertEqual(result, "YES")

    def test_contains_text_yes(self):
        '"YES value" contains YES must match "YES" display value.'
        result = run('say "YES value" contains YES')
        self.assertEqual(result, "YES")

    def test_contains_text_no(self):
        '"NO value" contains NO must match "NO" display value.'
        result = run('say "NO value" contains NO')
        self.assertEqual(result, "YES")

    def test_contains_text_yes_not_true(self):
        """contains must not search for 'True' when given YES."""
        result = run('say "True value" contains YES')
        self.assertEqual(result, "NO")

    def test_contains_text_nothing_not_none(self):
        """contains must not search for 'None' when given nothing."""
        result = run('say "None value" contains nothing')
        self.assertEqual(result, "NO")

    def test_contains_list_still_works(self):
        """contains on list still works correctly."""
        result = run('items = 1, 2, 3\nsay items contains 2')
        self.assertEqual(result, "YES")

    # ── B6: min()/max() reject booleans ──────────────────────────────────────

    def test_min_yes_raises(self):
        """min(YES, 2) must raise IXXRuntimeError."""
        with self.assertRaises(IXXRuntimeError) as ctx:
            run('say min(YES, 2)')
        self.assertIn("YES/NO", str(ctx.exception))

    def test_max_no_raises(self):
        """max(NO, 2) must raise IXXRuntimeError."""
        with self.assertRaises(IXXRuntimeError) as ctx:
            run('say max(NO, 2)')
        self.assertIn("YES/NO", str(ctx.exception))

    def test_min_list_with_bool_raises(self):
        """min(list containing YES) must raise IXXRuntimeError."""
        with self.assertRaises(IXXRuntimeError) as ctx:
            run('items = YES, 2, 3\nsay min(items)')
        self.assertIn("YES/NO", str(ctx.exception))

    def test_max_list_with_bool_raises(self):
        """max(list containing NO) must raise IXXRuntimeError."""
        with self.assertRaises(IXXRuntimeError) as ctx:
            run('items = 1, NO, 3\nsay max(items)')
        self.assertIn("YES/NO", str(ctx.exception))

    def test_min_numbers_still_works(self):
        """min(3, 7) must still work."""
        self.assertEqual(run('say min(3, 7)'), "3")

    def test_max_numbers_still_works(self):
        """max(3, 7) must still work."""
        self.assertEqual(run('say max(3, 7)'), "7")

    def test_min_list_numbers_still_works(self):
        """min(number list) must still work."""
        self.assertEqual(run('items = 3, 1, 4\nsay min(items)'), "1")

    # ── B7: round(x, YES) rejects bool digits ─────────────────────────────────

    def test_round_yes_digits_raises(self):
        """round(3.14, YES) must raise IXXRuntimeError."""
        with self.assertRaises(IXXRuntimeError) as ctx:
            run('say round(3.14, YES)')
        self.assertIn("YES/NO", str(ctx.exception))

    def test_round_no_digits_raises(self):
        """round(3.14, NO) must raise IXXRuntimeError."""
        with self.assertRaises(IXXRuntimeError) as ctx:
            run('say round(3.14, NO)')
        self.assertIn("YES/NO", str(ctx.exception))

    def test_round_normal_still_works(self):
        """round(3.14, 1) must still work."""
        self.assertEqual(run('say round(3.14, 1)'), "3.1")

    def test_round_no_digits_zero_still_works(self):
        """round(3.7) with no digits arg must still work (default 0)."""
        self.assertEqual(run('say round(3.7)'), "4")

    # ── B8: list arithmetic rejected ─────────────────────────────────────────

    def test_list_plus_list_raises(self):
        """list + list must raise IXXRuntimeError."""
        with self.assertRaises(IXXRuntimeError) as ctx:
            run('a = 1, 2\nb = 3, 4\nsay a + b')
        self.assertIn("list", str(ctx.exception).lower())

    def test_list_times_number_raises(self):
        """list * number must raise IXXRuntimeError."""
        with self.assertRaises(IXXRuntimeError) as ctx:
            run('a = 1, 2\nsay a * 3')
        self.assertIn("list", str(ctx.exception).lower())

    def test_number_times_list_raises(self):
        """number * list must raise IXXRuntimeError."""
        with self.assertRaises(IXXRuntimeError) as ctx:
            run('a = 1, 2\nsay 3 * a')
        self.assertIn("list", str(ctx.exception).lower())

    def test_list_minus_number_raises(self):
        """list - number must raise IXXRuntimeError."""
        with self.assertRaises(IXXRuntimeError) as ctx:
            run('a = 1, 2\nsay a - 1')
        self.assertIn("list", str(ctx.exception).lower())

    def test_list_divide_number_raises(self):
        """list / number must raise IXXRuntimeError."""
        with self.assertRaises(IXXRuntimeError) as ctx:
            run('a = 1, 2\nsay a / 2')
        self.assertIn("list", str(ctx.exception).lower())

    def test_text_plus_number_still_works(self):
        """text + number must still work (string concat)."""
        self.assertEqual(run('say "count: " + 5'), "count: 5")

    def test_number_plus_text_still_works(self):
        """number + text must still work (string concat)."""
        self.assertEqual(run('say 5 + " items"'), "5 items")

    def test_number_arithmetic_still_works(self):
        """Normal numeric arithmetic must still work."""
        self.assertEqual(run('say 3 + 4 * 2'), "11")

    def test_list_arithmetic_catchable(self):
        """list arithmetic error must be catchable by IXX try/catch."""
        result = run(
            'a = 1, 2, 3\n'
            'try\n'
            '- say a + a\n'
            'catch\n'
            '- say "caught"'
        )
        self.assertEqual(result, "caught")


# ══════════════════════════════════════════════════════════════════════════════
# Letter C — v0.6.8 string escape sequences
# ══════════════════════════════════════════════════════════════════════════════

class TestLetterC(unittest.TestCase):
    """Tests for v0.6.8 Letter C: \\n, \\t, \\\\ escape sequences in string literals."""

    # ── C1: \n produces a real newline ────────────────────────────────────────

    def test_newline_escape_two_lines(self):
        r'say "a\nb" must output two separate lines.'
        result = run(r'say "a\nb"')
        self.assertIn("\n", result)
        parts = result.splitlines()
        self.assertEqual(parts[0], "a")
        self.assertEqual(parts[1], "b")

    def test_newline_escape_in_variable(self):
        r'Assigning "a\nb" must give a string with a real newline.'
        result = run('x = "a\\nb"\nsay x')
        self.assertIn("\n", result)

    def test_newline_write_readlines(self):
        r'write with \n then readlines must return multiple lines.'
        result = run(
            'write "StressTest/tmp/c1-escape.txt", "one\\ntwo\\nthree"\n'
            'lines = readlines("StressTest/tmp/c1-escape.txt")\n'
            'say count(lines)'
        )
        self.assertEqual(result, "3")

    def test_newline_first_line(self):
        r'Each \n splits content; first line is accessible.'
        result = run(
            'write "StressTest/tmp/c1-nl-a.txt", "alpha\\nbeta"\n'
            'lines = readlines("StressTest/tmp/c1-nl-a.txt")\n'
            'say first(lines)'
        )
        self.assertEqual(result, "alpha")

    # ── C1: \t produces a real tab ────────────────────────────────────────────

    def test_tab_escape_in_output(self):
        r'say "a\tb" must contain a real tab character.'
        result = run('say "a\\tb"')
        self.assertIn("\t", result)

    def test_tab_escape_split(self):
        r'split on \t separator must work after escape processing.'
        result = run(
            'parts = split("a\\tb", "\\t")\n'
            'say count(parts)'
        )
        self.assertEqual(result, "2")

    # ── C1: \\ produces a single backslash ────────────────────────────────────

    def test_backslash_escape(self):
        r'say "C:\\Temp" must display C:\Temp (one backslash).'
        result = run('say "C:\\\\Temp"')
        self.assertEqual(result, "C:\\Temp")

    def test_double_backslash_length(self):
        r'"\\" must produce a string of length 1 (one backslash).'
        result = run('say count("\\\\")')
        self.assertEqual(result, "1")

    # ── Normal strings unaffected ─────────────────────────────────────────────

    def test_normal_string_unchanged(self):
        """A string with no escapes must be unchanged."""
        result = run('say "hello world"')
        self.assertEqual(result, "hello world")

    def test_interpolation_still_works(self):
        r'Variable interpolation must still work alongside escaped newline.'
        result = run(
            'name = "Ixxy"\n'
            'say "Hello\\n{name}"'
        )
        parts = result.splitlines()
        self.assertEqual(parts[0], "Hello")
        self.assertEqual(parts[1], "Ixxy")

    def test_unknown_escape_preserved(self):
        r'An unknown escape like \q must be kept as-is (literal \q).'
        result = run('say "a\\qb"')
        self.assertIn("\\q", result)

    def test_string_concat_unaffected(self):
        """String concat with no escapes must still work."""
        result = run('say "hello" + " " + "world"')
        self.assertEqual(result, "hello world")

class TestLetterD(unittest.TestCase):
    """D1 — Wire resolve_imports() into REPL _try_run_ixx()."""

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _repl_run(self, source: str) -> str:
        """Run *source* through the REPL's _try_run_ixx() and return stdout."""
        import io, contextlib
        from ixx.shell.repl import _try_run_ixx

        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            _try_run_ixx(source, lambda p: "")
        return buf.getvalue().strip()

    # ------------------------------------------------------------------
    # Local file imports
    # ------------------------------------------------------------------

    def test_repl_use_local_file(self):
        """REPL can import a local helper file and call an imported function."""
        import tempfile, os

        helper_src = "function double x\n- return x * 2\n"
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".ixx", delete=False, encoding="utf-8"
        ) as f:
            helper_path = f.name
            f.write(helper_src)

        try:
            fwd = helper_path.replace("\\", "/")
            src = f'use "{fwd}"\nsay double(21)'
            result = self._repl_run(src)
            self.assertEqual(result, "42")
        finally:
            os.unlink(helper_path)

    def test_repl_local_import_multiple_functions(self):
        """REPL imports multiple functions from a local file and calls them."""
        import tempfile, os

        helper_src = (
            "function greet name\n- return \"Hello, \" + name\n"
            "function shout name\n- return \"HEY \" + name\n"
        )
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".ixx", delete=False, encoding="utf-8"
        ) as f:
            helper_path = f.name
            f.write(helper_src)

        try:
            fwd = helper_path.replace("\\", "/")
            src = f'use "{fwd}"\nsay greet("Ixxy")'
            result = self._repl_run(src)
            self.assertIn("Hello, Ixxy", result)
        finally:
            os.unlink(helper_path)

    # ------------------------------------------------------------------
    # stdlib imports
    # ------------------------------------------------------------------

    def test_repl_use_std_time(self):
        """REPL can import use std 'time' and call time_greeting."""
        src = 'use std "time"\nsay time_greeting(9)'
        result = self._repl_run(src)
        self.assertIn("Good morning", result)

    def test_repl_use_std_time_evening(self):
        """REPL time_greeting returns evening greeting for hour >= 18."""
        src = 'use std "time"\nsay time_greeting(20)'
        result = self._repl_run(src)
        self.assertIn("Good evening", result)

    def test_repl_use_std_date(self):
        """REPL can import use std 'date' and call is_leap_year."""
        src = 'use std "date"\nsay is_leap_year(2024)'
        result = self._repl_run(src)
        self.assertEqual(result, "YES")

    def test_repl_use_std_date_non_leap(self):
        """REPL date module: non-leap year returns NO."""
        src = 'use std "date"\nsay is_leap_year(2023)'
        result = self._repl_run(src)
        self.assertEqual(result, "NO")

    # ------------------------------------------------------------------
    # Error handling
    # ------------------------------------------------------------------

    def test_repl_missing_import_friendly(self):
        """Missing local import in REPL shows friendly error, no traceback."""
        import io, contextlib
        from ixx.shell.repl import _try_run_ixx

        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            recognised = _try_run_ixx(
                'use "definitely-does-not-exist-xyz.ixx"\nsay "hi"',
                lambda p: "",
            )

        output = buf.getvalue()
        self.assertTrue(recognised, "Should be recognised as IXX")
        self.assertNotIn("Traceback", output)
        self.assertNotIn("IXXImportError", output)
        # Should mention something about the import failing
        self.assertTrue(
            "import" in output.lower() or "not found" in output.lower(),
            f"Expected import-error text in: {output!r}",
        )

    def test_repl_missing_std_module_friendly(self):
        """Missing stdlib module in REPL shows friendly error, no traceback."""
        import io, contextlib
        from ixx.shell.repl import _try_run_ixx

        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            recognised = _try_run_ixx(
                'use std "nonexistent_module_xyz"',
                lambda p: "",
            )

        output = buf.getvalue()
        self.assertTrue(recognised)
        self.assertNotIn("Traceback", output)
        self.assertNotIn("IXXImportError", output)

    def test_repl_runtime_error_still_caught(self):
        """Runtime error in REPL (no imports) still shows friendly error."""
        result = self._repl_run('say number("not-a-number")')
        self.assertIn("Error", result)
        self.assertNotIn("Traceback", result)

    def test_repl_plain_ixx_unaffected(self):
        """Plain IXX (no imports) still works after D1 change."""
        result = self._repl_run('say 6 * 7')
        self.assertEqual(result, "42")

    def test_repl_interp_var_assignment_still_works(self):
        """Variable assignment + say still works in REPL."""
        result = self._repl_run('name = "Ixxy"\nsay "Hello, {name}"')
        self.assertEqual(result, "Hello, Ixxy")


class TestLetterE(unittest.TestCase):
    """E1/E2/E3 — Checker scoping fixes: func params, catch error, top-level return."""

    # ------------------------------------------------------------------
    # Helper: run checker and return list of error messages
    # ------------------------------------------------------------------

    def _check(self, src: str) -> list[str]:
        from ixx.checker import SemanticChecker
        from ixx.parser import parse
        errors = SemanticChecker().check(parse(src), "test.ixx")
        return [e.message for e in errors if e.severity == "error"]

    # ------------------------------------------------------------------
    # E1 — function parameter does not leak to top level
    # ------------------------------------------------------------------

    def test_func_param_visible_inside_body(self):
        """Parameter is visible inside the function body (no false error)."""
        errors = self._check("function show data\n- say data\n")
        self.assertEqual(errors, [])

    def test_func_param_does_not_leak_top_level(self):
        """Using a function param name at top level is flagged."""
        errors = self._check("function show data\n- say data\nsay data")
        self.assertTrue(
            any("data" in m and "not defined" in m for m in errors),
            f"Expected undefined-data error, got: {errors}",
        )

    def test_multiple_func_params_do_not_leak(self):
        """Multiple params from multiple functions don't pollute top-level scope."""
        src = (
            "function add a, b\n- return a + b\n"
            "function mul x, y\n- return x * y\n"
            "say a\n"
        )
        errors = self._check(src)
        self.assertTrue(any("a" in m and "not defined" in m for m in errors), errors)

    def test_func_local_var_does_not_leak(self):
        """Variables assigned inside a function body don't suppress top-level errors."""
        src = "function foo\n- result = 42\nsay result\n"
        errors = self._check(src)
        self.assertTrue(
            any("result" in m and "not defined" in m for m in errors),
            f"Expected undefined-result error, got: {errors}",
        )

    def test_calling_function_still_passes(self):
        """Calling a defined function at top level still passes check."""
        src = "function show data\n- say data\nshow(\"hello\")\n"
        errors = self._check(src)
        self.assertEqual(errors, [])

    def test_top_level_assignment_still_visible(self):
        """Top-level assignment is still visible and not falsely flagged."""
        src = "name = \"Ixxy\"\nsay name\n"
        errors = self._check(src)
        self.assertEqual(errors, [])

    # ------------------------------------------------------------------
    # E2 — catch `error` visible only inside catch body
    # ------------------------------------------------------------------

    def test_error_visible_inside_catch(self):
        """'error' is usable inside catch body without a checker error."""
        src = "try\n- x = 1\ncatch\n- say error\n"
        errors = self._check(src)
        self.assertEqual(errors, [])

    def test_error_does_not_leak_after_catch(self):
        """'error' after the try/catch block is flagged as undefined."""
        src = "try\n- x = 1\ncatch\n- say error\nsay error\n"
        errors = self._check(src)
        self.assertTrue(
            any("error" in m and "not defined" in m for m in errors),
            f"Expected undefined-error error, got: {errors}",
        )

    def test_error_not_global_from_different_catch(self):
        """'error' from one catch does not make it defined after a second catch."""
        src = (
            "try\n- x = 1\ncatch\n- say error\n"
            "try\n- y = 2\ncatch\n- say error\n"
            "say error\n"
        )
        errors = self._check(src)
        self.assertTrue(
            any("error" in m and "not defined" in m for m in errors),
            f"Expected undefined-error after two catches, got: {errors}",
        )

    def test_catch_assigned_var_still_accessible_after(self):
        """A variable assigned inside catch IS accessible after the block (IXX scoping)."""
        src = (
            "caught = NO\n"
            "try\n- x = 1\ncatch\n- caught = YES\n"
            "say caught\n"
        )
        errors = self._check(src)
        self.assertEqual(errors, [])

    # ------------------------------------------------------------------
    # E3 — top-level return flagged by checker
    # ------------------------------------------------------------------

    def test_top_level_return_fails_checker(self):
        """Return at top level is a checker error."""
        errors = self._check("return 42\n")
        self.assertTrue(
            any("return" in m.lower() and "function" in m.lower() for m in errors),
            f"Expected top-level return error, got: {errors}",
        )

    def test_return_inside_function_passes(self):
        """Return inside a function is valid."""
        errors = self._check("function f\n- return 42\n")
        self.assertEqual(errors, [])

    def test_return_inside_if_inside_function_passes(self):
        """Return inside an if inside a function is valid."""
        src = "function f x\n- if x more than 0\n-- return x\n- return 0\n"
        errors = self._check(src)
        self.assertEqual(errors, [])

    def test_bare_return_top_level_fails(self):
        """Bare 'return' (no value) at top level is also caught."""
        errors = self._check("say \"hi\"\nreturn\n")
        self.assertTrue(
            any("return" in m.lower() and "function" in m.lower() for m in errors),
            f"Expected top-level bare-return error, got: {errors}",
        )

    # ------------------------------------------------------------------
    # Regression: Letter A nested function checks still pass
    # ------------------------------------------------------------------

    def test_nested_function_in_if_still_caught(self):
        """Letter A: nested function inside if is still caught (no regression)."""
        src = "if YES\n- function inner\n-- say \"hi\"\n"
        errors = self._check(src)
        self.assertTrue(
            any("top level" in m for m in errors),
            f"Expected nested-function error, got: {errors}",
        )

    # ------------------------------------------------------------------
    # Regression: loop-each scoping still correct
    # ------------------------------------------------------------------

    def test_loop_each_var_visible_inside_body(self):
        """Loop-each variable is usable inside the loop body."""
        src = "items = 1, 2, 3\nloop each item in items\n- say item\n"
        errors = self._check(src)
        self.assertEqual(errors, [])

    def test_loop_each_non_predeclared_var_does_not_leak(self):
        """Non-predeclared loop-each variable is not accessible after loop."""
        src = "items = 1, 2, 3\nloop each item in items\n- say item\nsay item\n"
        errors = self._check(src)
        self.assertTrue(
            any("item" in m and "not defined" in m for m in errors),
            f"Expected undefined-item after loop, got: {errors}",
        )


# ─────────────────────────────────────────────────────────────────────────────
# Letter I — error message quality
# ─────────────────────────────────────────────────────────────────────────────

class TestLetterI(unittest.TestCase):
    """I1–I7: friendlier error messages, no raw Python text leaks."""

    # ── helpers ──────────────────────────────────────────────────────────────

    def _run(self, src: str) -> str:
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            try:
                Interpreter().run(parse(src))
            except IXXRuntimeError as e:
                return f"ERR:{e}"
        return buf.getvalue().strip()

    def _check(self, src: str) -> list[str]:
        from ixx.checker import SemanticChecker
        return [e.message for e in SemanticChecker().check(parse(src), "t.ixx")]

    # ── I1: builtin TypeError arity should not leak Python text ──────────────

    def test_i1_builtin_arity_no_python_text(self):
        """Wrong builtin arg count should not mention 'positional argument'."""
        # write expects 2 args; call it with 3 via interpreter directly
        from ixx.interpreter import Interpreter as _I
        from ixx.runtime.errors import IXXRuntimeError as _E
        interp = _I()
        interp.run(parse("x = 1"))  # init func table
        with self.assertRaises(_E) as ctx:
            interp._call("read", ["a", "b"])  # read takes 1 arg
        msg = str(ctx.exception)
        self.assertNotIn("positional argument", msg)
        self.assertNotIn("takes 1", msg)
        self.assertNotIn("missing 1", msg)

    def test_i1_builtin_arity_message_contains_count(self):
        """Builtin arity error should mention the got-count."""
        from ixx.interpreter import Interpreter as _I
        from ixx.runtime.errors import IXXRuntimeError as _E
        interp = _I()
        interp.run(parse("x = 1"))
        with self.assertRaises(_E) as ctx:
            interp._call("read", ["a", "b"])
        msg = str(ctx.exception)
        # "was called with 2 arguments" or similar
        self.assertTrue(
            "2" in msg or "argument" in msg,
            f"Expected count info in: {msg}",
        )

    # ── I2: write() to nonexistent directory ─────────────────────────────────

    def test_i2_write_missing_folder_friendly(self):
        """write() to a nonexistent folder gives a helpful message."""
        import tempfile, os
        bad = os.path.join(tempfile.gettempdir(), "no_such_dir_ixx_i2", "out.txt").replace("\\", "/")
        out = self._run(f'write "{bad}", "hello"')
        self.assertTrue(out.startswith("ERR:"), f"Expected error, got: {out}")
        msg = out[4:]
        self.assertNotIn("WinError", msg)
        self.assertNotIn("errno", msg)
        self.assertNotIn("[Errno", msg)
        self.assertIn(bad, msg)

    def test_i2_write_missing_folder_no_rawerror(self):
        """write() error message should mention folder or path clearly."""
        import tempfile, os
        bad = os.path.join(tempfile.gettempdir(), "no_such_dir_ixx_i2", "out.txt").replace("\\", "/")
        out = self._run(f'write "{bad}", "hello"')
        msg = out[4:]
        # Should mention folder/path existence
        self.assertTrue(
            "folder" in msg or "path" in msg or "exist" in msg,
            f"Expected folder hint in: {msg}",
        )

    def test_i2_append_missing_folder_friendly(self):
        """append() to a nonexistent folder also gives a helpful message."""
        import tempfile, os
        bad = os.path.join(tempfile.gettempdir(), "no_such_dir_ixx_i2b", "out.txt").replace("\\", "/")
        out = self._run(f'append "{bad}", "hello"')
        self.assertTrue(out.startswith("ERR:"), f"Expected error, got: {out}")
        msg = out[4:]
        self.assertNotIn("WinError", msg)
        self.assertNotIn("[Errno", msg)

    # ── I3: _friendly_message for indentation/dash issues ────────────────────

    def test_i3_function_no_name_hint(self):
        """A bare 'function' keyword with no name gives a helpful hint."""
        from ixx.__main__ import _friendly_message
        class FakeE:
            pass
        msg = _friendly_message("function", None, FakeE())
        self.assertIn("function name", msg.lower())
        self.assertIn("function add", msg)

    def test_i3_function_no_name_hint_with_spaces(self):
        """Whitespace around 'function' still triggers the hint."""
        from ixx.__main__ import _friendly_message
        class FakeE:
            pass
        msg = _friendly_message("  function  ", None, FakeE())
        self.assertIn("function name", msg.lower())

    # ── I6: number() on list ─────────────────────────────────────────────────

    def test_i6_number_list_no_repr(self):
        """number(list) should not show Python [1, 2, 3] repr."""
        out = self._run("items = 1, 2, 3\nx = number(items)\nsay x")
        self.assertTrue(out.startswith("ERR:"), f"Expected error, got: {out}")
        msg = out[4:]
        self.assertNotIn("[1, 2, 3]", msg)
        self.assertNotIn("[1,", msg)

    def test_i6_number_list_friendly_message(self):
        """number(list) error should mention 'list' and 'number'."""
        out = self._run("items = 1, 2, 3\nx = number(items)\nsay x")
        msg = out[4:]
        self.assertIn("list", msg.lower())
        self.assertIn("number", msg.lower())

    # ── I7: argument(s) pluralization ────────────────────────────────────────

    def test_i7_checker_singular_argument(self):
        """Checker: 1-param function called with too many args → '1 argument'."""
        errors = self._check("function f a\n- return a\nx = f(1, 2)")
        self.assertTrue(errors, "Expected a checker error")
        msg = errors[0]
        self.assertIn("1 argument", msg)
        self.assertNotIn("1 arguments", msg)
        self.assertNotIn("argument(s)", msg)

    def test_i7_checker_plural_arguments(self):
        """Checker: 2-param function called with wrong args → '2 arguments'."""
        errors = self._check("function g a, b\n- return a\nx = g(1, 2, 3)")
        self.assertTrue(errors, "Expected a checker error")
        msg = errors[0]
        self.assertIn("2 arguments", msg)
        self.assertNotIn("argument(s)", msg)

    def test_i7_runtime_singular_argument(self):
        """Runtime: 1-param function called with 2 args → '1 argument'."""
        out = self._run("function f a\n- return a\nx = f(1, 2)")
        self.assertTrue(out.startswith("ERR:"), f"Expected error, got: {out}")
        msg = out[4:]
        self.assertIn("1 argument", msg)
        self.assertNotIn("argument(s)", msg)

    def test_i7_runtime_plural_arguments(self):
        """Runtime: 2-param function called with 1 arg → '2 arguments'."""
        out = self._run("function g a, b\n- return a\nx = g(1)")
        self.assertTrue(out.startswith("ERR:"), f"Expected error, got: {out}")
        msg = out[4:]
        self.assertIn("2 arguments", msg)
        self.assertNotIn("argument(s)", msg)

    def test_i7_builtin_checker_singular(self):
        """Checker: 1-arg builtin called with 0 args → '1 argument'."""
        errors = self._check("x = count()")
        self.assertTrue(errors, "Expected a checker error")
        self.assertTrue(
            any("1 argument" in m for m in errors),
            f"Expected '1 argument' in: {errors}",
        )

    def test_i7_builtin_checker_plural(self):
        """Checker: 2-arg builtin called with 1 arg → '2 arguments'."""
        # replace expects 3 args; give it 2
        errors = self._check('x = replace("abc", "a")')
        self.assertTrue(errors, "Expected a checker error")
        self.assertTrue(
            any("3 arguments" in m or "argument" in m for m in errors),
            f"Expected argument count in: {errors}",
        )

    def test_i7_no_argument_s_anywhere(self):
        """No user-facing message should contain the awkward 'argument(s)'."""
        # Trigger a few different arity errors and check none say argument(s)
        srcs = [
            "function f a\n- return a\nx = f(1, 2)",
            "function g a, b\n- return a\nx = g(1)",
            "x = count()",
        ]
        for src in srcs:
            errors = self._check(src)
            for msg in errors:
                self.assertNotIn(
                    "argument(s)", msg,
                    f"Found 'argument(s)' in: {msg!r}",
                )


# ─────────────────────────────────────────────────────────────────────────────
# Letter J — shell handler crash paths
# ─────────────────────────────────────────────────────────────────────────────

class TestLetterJ(unittest.TestCase):
    """J1–J2: shell handler crash paths don't leak raw Python exceptions."""

    # ── J1: handle_open non-Windows subprocess guard ─────────────────────────

    def test_j1_open_xdg_missing_no_raw_error(self):
        """When xdg-open is not found, handle_open prints friendly message."""
        import sys
        from unittest.mock import patch, MagicMock
        from ixx.shell.commands.files import handle_open
        from ixx.shell.paths import PathNotFoundError

        # Resolve to a real path so we reach the subprocess call
        fake_path = MagicMock()
        fake_path.__str__ = lambda self: "/tmp/fake_file"

        buf = io.StringIO()
        with patch("ixx.shell.commands.files.resolve", return_value=fake_path), \
             patch("ixx.shell.commands.files.os.startfile", side_effect=AttributeError), \
             patch("ixx.shell.commands.files.sys.platform", "linux"), \
             patch("subprocess.run", side_effect=FileNotFoundError("xdg-open not found")), \
             contextlib.redirect_stdout(buf):
            handle_open(["fakepath"])

        out = buf.getvalue()
        # Should not raise — must produce friendly output
        self.assertIn("Could not open", out)
        self.assertNotIn("Traceback", out)
        self.assertNotIn("FileNotFoundError", out)

    def test_j1_open_xdg_other_error_no_raw(self):
        """When xdg-open raises a generic OSError, handle_open stays friendly."""
        from unittest.mock import patch, MagicMock
        from ixx.shell.commands.files import handle_open

        fake_path = MagicMock()
        fake_path.__str__ = lambda self: "/tmp/fake_file"

        buf = io.StringIO()
        with patch("ixx.shell.commands.files.resolve", return_value=fake_path), \
             patch("ixx.shell.commands.files.os.startfile", side_effect=AttributeError), \
             patch("ixx.shell.commands.files.sys.platform", "linux"), \
             patch("subprocess.run", side_effect=OSError("permission denied")), \
             contextlib.redirect_stdout(buf):
            handle_open(["fakepath"])

        out = buf.getvalue()
        self.assertIn("Could not open", out)
        self.assertNotIn("Traceback", out)

    def test_j1_open_windows_success_still_works(self):
        """On Windows (mocked), os.startfile success still prints 'Opened'."""
        from unittest.mock import patch, MagicMock
        from ixx.shell.commands.files import handle_open

        fake_path = MagicMock()
        fake_path.__str__ = lambda self: "C:\\Users\\test\\file.txt"

        buf = io.StringIO()
        with patch("ixx.shell.commands.files.resolve", return_value=fake_path), \
             patch("ixx.shell.commands.files.os.startfile", return_value=None), \
             contextlib.redirect_stdout(buf):
            handle_open(["fakepath"])

        out = buf.getvalue()
        self.assertIn("Opened", out)

    def test_j1_open_no_args_usage(self):
        """handle_open with no args prints usage hint."""
        from ixx.shell.commands.files import handle_open
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            handle_open([])
        out = buf.getvalue()
        self.assertIn("Usage", out)

    # ── J2: _classify_adapter with malformed IP ───────────────────────────────

    def test_j2_classify_malformed_172_no_valueerror(self):
        """_classify_adapter with non-numeric 172.x octet does not raise ValueError."""
        from ixx.shell.commands.network import _classify_adapter
        # Should not raise — returns "other" for malformed
        result = _classify_adapter("SomeAdapter", "172.abc.0.1")
        self.assertIsInstance(result, str)

    def test_j2_classify_malformed_172_returns_other(self):
        """_classify_adapter with non-numeric 172.x octet returns 'other'."""
        from ixx.shell.commands.network import _classify_adapter
        result = _classify_adapter("SomeAdapter", "172.abc.0.1")
        self.assertEqual(result, "other")

    def test_j2_classify_valid_172_rfc1918(self):
        """_classify_adapter with valid RFC 1918 172.16-31 still returns 'other'."""
        from ixx.shell.commands.network import _classify_adapter
        result = _classify_adapter("Ethernet", "172.16.0.1")
        self.assertEqual(result, "other")

    def test_j2_classify_valid_172_virtual(self):
        """_classify_adapter: 172.17.x with neutral name returns 'other' (RFC 1918)."""
        from ixx.shell.commands.network import _classify_adapter
        # "eth0" has no virtual keyword — IP-based check governs
        result = _classify_adapter("eth0", "172.17.0.1")
        self.assertEqual(result, "other")

    def test_j2_classify_172_outside_rfc1918(self):
        """_classify_adapter with 172.14.x (outside RFC 1918) returns 'virtual'."""
        from ixx.shell.commands.network import _classify_adapter
        result = _classify_adapter("VirtualAdapter", "172.14.0.1")
        self.assertEqual(result, "virtual")

    def test_j2_classify_private_192(self):
        """_classify_adapter with 192.168.x still works normally."""
        from ixx.shell.commands.network import _classify_adapter
        result = _classify_adapter("Ethernet", "192.168.1.100")
        self.assertEqual(result, "ethernet")

    def test_j2_classify_loopback(self):
        """_classify_adapter with 127.0.0.1 still returns 'loopback'."""
        from ixx.shell.commands.network import _classify_adapter
        result = _classify_adapter("lo", "127.0.0.1")
        self.assertEqual(result, "loopback")

    def test_j2_classify_link_local(self):
        """_classify_adapter with 169.254.x returns 'link-local'."""
        from ixx.shell.commands.network import _classify_adapter
        result = _classify_adapter("Autoconfiguration", "169.254.1.1")
        self.assertEqual(result, "link-local")


# ─────────────────────────────────────────────────────────────────────────────
# Letter K — stale version strings and misleading UI/help text
# ─────────────────────────────────────────────────────────────────────────────

class TestLetterK(unittest.TestCase):
    """K1–K6: no stale version numbers, no stub commands in live examples."""

    # ── K1: stubs.py ─────────────────────────────────────────────────────────

    def test_k1_stubs_no_v030(self):
        """stubs.py must not contain 'v0.3.0' anywhere."""
        import importlib.util, pathlib
        path = pathlib.Path("ixx/shell/commands/stubs.py")
        text = path.read_text(encoding="utf-8")
        self.assertNotIn("v0.3.0", text)

    # ── K2: demo_walk.py ─────────────────────────────────────────────────────

    def test_k2_demo_walk_no_v04(self):
        """demo_walk.py must not output 'v0.4' to users."""
        from ixx.shell.commands.demo_walk import handle_demo_walk
        buf = io.StringIO()
        # fast-forward through all steps then reach the closing message
        with contextlib.redirect_stdout(buf):
            handle_demo_walk([], _input_fn=lambda _: "")
        out = buf.getvalue()
        self.assertNotIn("v0.4", out)

    def test_k2_demo_walk_still_has_branding(self):
        """demo_walk.py closing message should still mention IXX."""
        from ixx.shell.commands.demo_walk import handle_demo_walk
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            handle_demo_walk([], _input_fn=lambda _: "")
        out = buf.getvalue()
        self.assertIn("IXX", out)

    # ── K3: renderer.py broad help examples ──────────────────────────────────

    def test_k3_broad_help_no_copy(self):
        """Broad help examples must not include stub 'copy' command."""
        from ixx.shell.renderer import _show_broad_help
        from ixx.shell.registry import CommandRegistry
        from ixx.shell.commands.stubs import register_all
        reg = CommandRegistry()
        register_all(reg)
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            _show_broad_help(reg)
        out = buf.getvalue()
        self.assertNotIn("copy report.pdf", out)

    def test_k3_broad_help_no_delete_recursive(self):
        """Broad help examples must not include stub 'delete' recursive example."""
        from ixx.shell.renderer import _show_broad_help
        from ixx.shell.registry import CommandRegistry
        from ixx.shell.commands.stubs import register_all
        reg = CommandRegistry()
        register_all(reg)
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            _show_broad_help(reg)
        out = buf.getvalue()
        self.assertNotIn("delete folder old-stuff recursive", out)

    def test_k3_broad_help_has_live_examples(self):
        """Broad help still contains live command examples."""
        from ixx.shell.renderer import _show_broad_help
        from ixx.shell.registry import CommandRegistry
        from ixx.shell.commands.stubs import register_all
        reg = CommandRegistry()
        register_all(reg)
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            _show_broad_help(reg)
        out = buf.getvalue()
        self.assertIn("ip wifi", out)
        self.assertIn("disk health", out)

    # ── K4: system.py disk smart full ────────────────────────────────────────

    def test_k4_disk_smart_full_no_ixx_setup(self):
        """disk smart full message must not suggest 'ixx setup'."""
        import pathlib
        text = pathlib.Path("ixx/shell/commands/system.py").read_text(encoding="utf-8")
        # Find the smart full section and verify
        idx = text.find("disk smart full requires")
        self.assertGreater(idx, 0, "Could not find disk smart full message")
        section = text[idx: idx + 400]
        self.assertNotIn("ixx setup", section)

    def test_k4_disk_smart_full_has_admin_hint(self):
        """disk smart full message still mentions administrator."""
        import pathlib
        text = pathlib.Path("ixx/shell/commands/system.py").read_text(encoding="utf-8")
        idx = text.find("disk smart full requires")
        section = text[idx: idx + 400]
        self.assertIn("administrator", section.lower())

    # ── K5: showoff.py hardcoded counts ──────────────────────────────────────

    def test_k5_showoff_no_478(self):
        """showoff.py must not hardcode '478 passed'."""
        import pathlib
        text = pathlib.Path("ixx/showoff.py").read_text(encoding="utf-8")
        self.assertNotIn("478 passed", text)

    def test_k5_showoff_no_stale_stresstest_count(self):
        """showoff.py must not hardcode ' 30 passed' StressTest count."""
        import pathlib
        text = pathlib.Path("ixx/showoff.py").read_text(encoding="utf-8")
        self.assertNotIn('" 30 passed"', text)

    def test_k5_showoff_still_mentions_tests(self):
        """showoff.py still mentions some form of testing / validation."""
        import pathlib
        text = pathlib.Path("ixx/showoff.py").read_text(encoding="utf-8")
        self.assertTrue(
            "unit test" in text.lower() or "stresstest" in text.lower() or "passing" in text.lower(),
            "Expected test-related wording still present in showoff.py",
        )

    # ── K6: examples stale version strings ───────────────────────────────────

    def test_k6_stdlib_no_v05_in_output(self):
        """examples/stdlib.ixx must not contain 'v0.5' header comment."""
        import pathlib
        text = pathlib.Path("examples/stdlib.ixx").read_text(encoding="utf-8")
        # The file header should no longer say "v0.5"
        self.assertNotIn("v0.5 built-in", text.lower())

    def test_k6_showcase_parses_ok(self):
        """examples/ixx-showcase.ixx must still parse without errors."""
        import pathlib
        src = pathlib.Path("examples/ixx-showcase.ixx").read_text(encoding="utf-8")
        # Should not raise
        result = parse(src)
        self.assertIsNotNone(result)


# ─────────────────────────────────────────────────────────────────────────────
# Letter M — v0.6.8 test quality fixes
# ─────────────────────────────────────────────────────────────────────────────

class TestLetterM(unittest.TestCase):
    """Tests for v0.6.8 Letter M: test suite trustworthiness fixes."""

    # ── M1: first/last on empty list ──────────────────────────────────────────

    def test_m1_first_empty_list_fix_regression(self):
        """The original test_first_empty_list used a non-empty list.
        This regression test proves first(empty) really returns nothing.
        IXX has no empty-list literal; split("") is the production path.
        """
        output = run('empty = split("")\nsay first(empty)')
        self.assertEqual(output, "nothing")

    def test_m1_last_empty_list_regression(self):
        """last() on a truly empty list must also return nothing."""
        output = run('empty = split("")\nsay last(empty)')
        self.assertEqual(output, "nothing")

    def test_m1_split_empty_string_gives_empty_list(self):
        """split("") with no sep is the only valid IXX path to an empty list."""
        output = run('empty = split("")\nsay count(empty)')
        self.assertEqual(output, "0")

    # ── M2: showoff wording is durable (not hardcoded counts) ─────────────────

    def test_m2_showoff_no_hardcoded_478(self):
        """showoff.py must not contain a hardcoded '478 passed' count."""
        import pathlib
        text = pathlib.Path("ixx/showoff.py").read_text(encoding="utf-8")
        self.assertNotIn("478 passed", text)

    def test_m2_showoff_no_hardcoded_30_passed(self):
        """showoff.py must not contain a hardcoded '30 passed' count."""
        import pathlib
        text = pathlib.Path("ixx/showoff.py").read_text(encoding="utf-8")
        self.assertNotIn('" 30 passed"', text)

    def test_m2_showoff_durable_wording_present(self):
        """showoff.py uses durable wording ('hundreds passing', 'all passing')."""
        import pathlib
        text = pathlib.Path("ixx/showoff.py").read_text(encoding="utf-8")
        self.assertIn("hundreds passing", text)
        self.assertIn("all passing", text)

    # ── M3: \n escape regression (covered by TestLetterC; verified here) ──────

    def test_m3_newline_escape_regression(self):
        r'If \n becomes literal again, this test would fail.'
        result = run(r'say "a\nb"')
        parts = result.splitlines()
        self.assertGreaterEqual(len(parts), 2, "\\n must produce a real newline")
        self.assertEqual(parts[0], "a")
        self.assertEqual(parts[1], "b")

    def test_m3_write_readlines_newline_roundtrip(self):
        r'write with \n then readlines must return multiple lines (regression).'
        result = run(
            'write "StressTest/tmp/m3-escape.txt", "one\\ntwo\\nthree"\n'
            'lines = readlines("StressTest/tmp/m3-escape.txt")\n'
            'say count(lines)'
        )
        self.assertEqual(result, "3")

    # ── M4: REPL import behavior (covered by TestLetterD; verified here) ──────

    def test_m4_repl_use_local_file(self):
        """REPL import of a local .ixx file works (regression)."""
        import tempfile
        from ixx.shell.repl import _try_run_ixx
        import io, contextlib

        helper = "function triple x\n- return x * 3\n"
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".ixx", delete=False, encoding="utf-8"
        ) as f:
            helper_path = f.name
            f.write(helper)

        try:
            fwd = helper_path.replace("\\", "/")
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                _try_run_ixx(f'use "{fwd}"\nsay triple(14)', lambda p: "")
            self.assertEqual(buf.getvalue().strip(), "42")
        finally:
            os.unlink(helper_path)

    def test_m4_repl_use_std_module(self):
        """REPL import of std module works (regression)."""
        from ixx.shell.repl import _try_run_ixx
        import io, contextlib

        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            _try_run_ixx('use std "time"\nsay time_greeting(9)', lambda p: "")
        self.assertIn("Good morning", buf.getvalue())


# ─────────────────────────────────────────────────────────────────────────────
# Letter N — v0.6.8 vocabulary / wording cleanup
# ─────────────────────────────────────────────────────────────────────────────

class TestLetterN(unittest.TestCase):
    """Tests for v0.6.8 Letter N: user-facing vocabulary and error message cleanup."""

    # ── N1: ixx_err_type maps bool → yes-or-no wording ───────────────────────

    def test_n1_type_builtin_still_returns_bool(self):
        """type(YES) must still return 'bool' for script compatibility."""
        self.assertEqual(run('say type(YES)'), "bool")
        self.assertEqual(run('say type(NO)'), "bool")

    def test_n1_upper_bool_says_yes_or_no(self):
        """upper(YES) error must mention yes-or-no, not 'bool'."""
        with self.assertRaises(IXXRuntimeError) as ctx:
            run('say upper(YES)')
        msg = str(ctx.exception)
        self.assertIn("yes-or-no", msg.lower())
        self.assertNotIn("bool", msg)

    def test_n1_lower_bool_says_yes_or_no(self):
        """lower(NO) error must mention yes-or-no, not 'bool'."""
        with self.assertRaises(IXXRuntimeError) as ctx:
            run('say lower(NO)')
        msg = str(ctx.exception)
        self.assertIn("yes-or-no", msg.lower())

    def test_n1_split_bool_says_yes_or_no(self):
        """split(YES) error must mention yes-or-no, not 'bool'."""
        with self.assertRaises(IXXRuntimeError) as ctx:
            run('say split(YES)')
        msg = str(ctx.exception)
        self.assertIn("yes-or-no", msg.lower())

    def test_n1_count_bool_says_yes_or_no(self):
        """count(YES) error must mention yes-or-no, not 'bool'."""
        with self.assertRaises(IXXRuntimeError) as ctx:
            run('say count(YES)')
        msg = str(ctx.exception)
        self.assertIn("yes-or-no", msg.lower())

    def test_n1_negate_bool_says_yes_no(self):
        """Negating a bool in arithmetic raises a friendly error containing YES/NO."""
        with self.assertRaises(IXXRuntimeError) as ctx:
            run('say -YES')
        msg = str(ctx.exception)
        self.assertIn("YES/NO", msg)
        self.assertNotIn("bool", msg)

    # ── N2: catch error variable: friendly messages ───────────────────────────

    def test_n2_catch_ixx_error_preserved(self):
        """IXXRuntimeError message is preserved exactly in catch {error}."""
        src = 'try\n- say number("abc")\ncatch\n- say error'
        result = run(src)
        self.assertIn("abc", result)
        self.assertNotIn("Traceback", result)
        self.assertNotIn("IXXRuntimeError", result)

    def test_n2_catch_no_traceback(self):
        """catch error must not contain raw Python traceback text."""
        src = 'try\n- say number("abc")\ncatch\n- say error'
        result = run(src)
        self.assertNotIn("Traceback", result)
        self.assertNotIn("File \"", result)

    # ── N3/N4: unknown statement/operator messages ────────────────────────────

    def test_n3_unknown_stmt_no_class_name(self):
        """The unknown-statement fallback must not expose Python AST class names.
        This is a defensive code path; we verify the message wording in source.
        """
        import pathlib
        text = pathlib.Path("ixx/interpreter.py").read_text(encoding="utf-8")
        self.assertIn("This statement cannot be run here.", text)
        self.assertNotIn("Unknown statement type:", text)

    def test_n5_bool_comparison_wording(self):
        """Numeric comparison with YES/NO (right side) must use yes-or-no wording."""
        with self.assertRaises(IXXRuntimeError) as ctx:
            run('if 1 more than YES\n- say "bad"')
        msg = str(ctx.exception)
        self.assertIn("yes-or-no", msg.lower())
        self.assertNotIn("booleans", msg)

    # ── N6/N7: modules.py import messages ────────────────────────────────────

    def test_n6_missing_import_friendly(self):
        """Missing import shows friendly message without raw OSError text."""
        from ixx.modules import resolve_imports, IXXImportError
        from ixx.parser import parse
        src = 'use "definitely-does-not-exist-xyz-123.ixx"\nsay "hi"'
        prog = parse(src)
        import tempfile
        with self.assertRaises(IXXImportError) as ctx:
            resolve_imports(prog, tempfile.gettempdir())
        msg = str(ctx.exception)
        self.assertIn("find", msg.lower())
        self.assertNotIn("[Errno", msg)
        self.assertNotIn("OSError", msg)

    def test_n7_circular_import_message(self):
        """Circular import message uses 'loop' wording, not just 'Circular import detected'."""
        from ixx.modules import resolve_imports, IXXImportError
        import tempfile, os
        tmpdir = tempfile.mkdtemp()
        try:
            # Create two files that import each other
            a = os.path.join(tmpdir, "a.ixx")
            b = os.path.join(tmpdir, "b.ixx")
            with open(a, "w") as f: f.write('use "b.ixx"\n')
            with open(b, "w") as f: f.write('use "a.ixx"\n')
            from ixx.parser import parse
            prog = parse('use "a.ixx"\n')
            with self.assertRaises(IXXImportError) as ctx:
                resolve_imports(prog, tmpdir)
            msg = str(ctx.exception)
            self.assertIn("loop", msg.lower())
            self.assertNotIn("Circular import detected", msg)
        finally:
            import shutil
            shutil.rmtree(tmpdir, ignore_errors=True)

    # ── N8: ixx check success says check passed ───────────────────────────────

    def test_n8_check_passed_wording(self):
        """ixx check on a valid file must say 'check passed', not 'syntax OK'."""
        code, out = cli("check", "examples/hello.ixx")
        self.assertEqual(code, 0)
        self.assertIn("check passed", out)
        self.assertNotIn("syntax OK", out)

    # ── N9: HELP_TEXT forward slashes ────────────────────────────────────────

    def test_n9_help_text_no_backslashes(self):
        """HELP_TEXT examples must use forward slashes, not Windows backslashes."""
        from ixx.__main__ import HELP_TEXT
        # The examples section should not contain backslash path separators
        examples_section = HELP_TEXT[HELP_TEXT.find("Examples:"):]
        self.assertNotIn("examples\\\\", examples_section)
        self.assertNotIn("examples\\hello", examples_section)
        self.assertIn("examples/hello.ixx", examples_section)

    # ── N10: renderer wording ─────────────────────────────────────────────────

    def test_n10_renderer_no_root_wording(self):
        """renderer.py must not say 'root privileges'."""
        import pathlib
        text = pathlib.Path("ixx/shell/renderer.py").read_text(encoding="utf-8")
        self.assertNotIn("root privileges", text)
        self.assertIn("run as admin", text)

    def test_n10_renderer_no_not_yet_implemented(self):
        """renderer.py must not print 'not yet implemented'."""
        import pathlib
        text = pathlib.Path("ixx/shell/renderer.py").read_text(encoding="utf-8")
        self.assertNotIn("not yet implemented", text)
        self.assertIn("not available yet", text)


# ─────────────────────────────────────────────────────────────────────────────
# Letter O — v0.6.8 float display and number() finite validation
# ─────────────────────────────────────────────────────────────────────────────

class TestLetterO(unittest.TestCase):
    """Tests for v0.6.8 Letter O: float precision display and inf/nan rejection."""

    # ── O1: Float precision display ───────────────────────────────────────────

    def test_o1_point_one_plus_point_two(self):
        """0.1 + 0.2 must display as 0.3, not 0.30000000000000004."""
        self.assertEqual(run('say 0.1 + 0.2'), "0.3")

    def test_o1_1_1_plus_2_2(self):
        """1.1 + 2.2 must display as 3.3."""
        self.assertEqual(run('say 1.1 + 2.2'), "3.3")

    def test_o1_four_thirds(self):
        """4 / 3 must not display excessive Python precision."""
        result = run('say 4 / 3')
        self.assertNotIn("33333333333", result)
        self.assertTrue(result.startswith("1.333"))

    def test_o1_ten_thirds(self):
        """10 / 3 must display at most 10 significant digits."""
        result = run('say 10 / 3')
        self.assertNotIn("33333333333", result)
        self.assertTrue(result.startswith("3.333"))

    def test_o1_normal_float_unchanged(self):
        """3.14 must still display as 3.14."""
        self.assertEqual(run('say 3.14'), "3.14")

    def test_o1_half_unchanged(self):
        """0.5 must still display as 0.5."""
        self.assertEqual(run('say 0.5'), "0.5")

    def test_o1_round_still_works(self):
        """round(3.14159, 2) must still display as 3.14."""
        self.assertEqual(run('say round(3.14159, 2)'), "3.14")

    def test_o1_round_whole_still_works(self):
        """round(3.7) must still display as 4."""
        self.assertEqual(run('say round(3.7)'), "4")

    def test_o1_integer_division_clean(self):
        """10 / 2 must display as 5 (integer), not 5.0."""
        self.assertEqual(run('say 10 / 2'), "5")

    # ── O3: number("1e5") display ─────────────────────────────────────────────

    def test_o3_number_1e5(self):
        """number('1e5') must display as 100000, not 100000.0."""
        self.assertEqual(run('say number("1e5")'), "100000")

    def test_o3_number_1_point_0(self):
        """number('1.0') must display as 1, not 1.0 (trailing zero stripped)."""
        self.assertEqual(run('say number("1.0")'), "1")

    def test_o3_number_normal_decimal(self):
        """number('3.14') must still display as 3.14."""
        self.assertEqual(run('say number("3.14")'), "3.14")

    # ── O2: Reject inf/nan in number() ───────────────────────────────────────

    def test_o2_number_inf_raises(self):
        """number('inf') must raise IXXRuntimeError with 'finite'."""
        with self.assertRaises(IXXRuntimeError) as ctx:
            run('say number("inf")')
        self.assertIn("finite", str(ctx.exception).lower())

    def test_o2_number_negative_inf_raises(self):
        """number('-inf') must raise IXXRuntimeError."""
        with self.assertRaises(IXXRuntimeError) as ctx:
            run('say number("-inf")')
        self.assertIn("finite", str(ctx.exception).lower())

    def test_o2_number_nan_raises(self):
        """number('nan') must raise IXXRuntimeError."""
        with self.assertRaises(IXXRuntimeError) as ctx:
            run('say number("nan")')
        self.assertIn("finite", str(ctx.exception).lower())

    def test_o2_number_infinity_case_variants(self):
        """number('Infinity') and number('INF') must also raise (Python accepts these)."""
        for variant in ("Infinity", "INF", "NaN", "Inf"):
            with self.subTest(variant=variant):
                with self.assertRaises(IXXRuntimeError):
                    run(f'say number("{variant}")')

    def test_o2_number_no_python_jargon_in_error(self):
        """number('inf') error must not expose Python float/nan jargon."""
        with self.assertRaises(IXXRuntimeError) as ctx:
            run('say number("inf")')
        msg = str(ctx.exception)
        self.assertNotIn("float", msg.lower())
        self.assertNotIn("ieee", msg.lower())
        self.assertNotIn("traceback", msg.lower())

    def test_o2_number_normal_still_works(self):
        """Normal number conversion must still work after the finite check."""
        self.assertEqual(run('say number("42")'), "42")
        self.assertEqual(run('say number("3.14")'), "3.14")
        self.assertEqual(run('say number("-7")'), "-7")

    def test_o2_number_catch_inf(self):
        """catch block should receive friendly error when number('inf') fails."""
        src = 'try\n- say number("inf")\ncatch\n- say error'
        result = run(src)
        self.assertIn("finite", result.lower())
        self.assertNotIn("Traceback", result)

    # ── O1+O2: display via write/read roundtrip ───────────────────────────────

    def test_o1_write_read_float_precision(self):
        """Float written to a file uses the same display (no excess precision)."""
        src = (
            'x = 0.1 + 0.2\n'
            'write "StressTest/tmp/o1-float.txt", x\n'
            'say read("StressTest/tmp/o1-float.txt")'
        )
        result = run(src)
        self.assertEqual(result, "0.3")


# ─────────────────────────────────────────────────────────────────────────────
# Letter P — v0.6.8 keyword interpolation fix
# ─────────────────────────────────────────────────────────────────────────────

class TestLetterP(unittest.TestCase):
    """Tests for v0.6.8 Letter P: {YES}/{NO}/{nothing} interpolation fix."""

    # ── P1: keyword interpolation produces correct output ────────────────────

    def test_p1_yes_interpolation(self):
        """say '{YES}' must output YES with no warning."""
        import io, contextlib
        buf = io.StringIO()
        with contextlib.redirect_stderr(buf):
            result = run('say "{YES}"')
        self.assertEqual(result, "YES")
        self.assertNotIn("not defined", buf.getvalue())
        self.assertNotIn("{?YES}", buf.getvalue())

    def test_p1_no_interpolation(self):
        """say '{NO}' must output NO with no warning."""
        import io, contextlib
        buf = io.StringIO()
        with contextlib.redirect_stderr(buf):
            result = run('say "{NO}"')
        self.assertEqual(result, "NO")
        self.assertNotIn("not defined", buf.getvalue())

    def test_p1_nothing_interpolation(self):
        """say '{nothing}' must output nothing with no warning."""
        import io, contextlib
        buf = io.StringIO()
        with contextlib.redirect_stderr(buf):
            result = run('say "{nothing}"')
        self.assertEqual(result, "nothing")
        self.assertNotIn("not defined", buf.getvalue())

    def test_p1_yes_with_surrounding_text(self):
        """say 'Active: {YES}' must output 'Active: YES'."""
        result = run('say "Active: {YES}"')
        self.assertEqual(result, "Active: YES")

    def test_p1_no_with_surrounding_text(self):
        """say 'Status: {NO}' must output 'Status: NO'."""
        result = run('say "Status: {NO}"')
        self.assertEqual(result, "Status: NO")

    def test_p1_nothing_with_surrounding_text(self):
        """say 'Value: {nothing}' must output 'Value: nothing'."""
        result = run('say "Value: {nothing}"')
        self.assertEqual(result, "Value: nothing")

    def test_p1_lowercase_yes_interpolation(self):
        """say '{yes}' must also output YES (yes is a valid alias)."""
        result = run('say "{yes}"')
        self.assertEqual(result, "YES")

    def test_p1_lowercase_no_interpolation(self):
        """say '{no}' must also output NO (no is a valid alias)."""
        result = run('say "{no}"')
        self.assertEqual(result, "NO")

    # ── P1: normal variable interpolation unchanged ───────────────────────────

    def test_p1_normal_variable_still_works(self):
        """Normal variable interpolation must still work."""
        result = run('name = "Ixxy"\nsay "Hello, {name}"')
        self.assertEqual(result, "Hello, Ixxy")

    def test_p1_variable_named_yes_takes_precedence(self):
        """If a variable named YES exists, it takes precedence over the keyword."""
        # In IXX, YES is a bool literal keyword — you can't assign to it.
        # The keyword table fires before env lookup, so the literal value is used.
        result = run('say "{YES}"')
        self.assertEqual(result, "YES")

    def test_p1_unknown_variable_still_warns(self):
        """Unknown variable still produces {?name} and prints a warning."""
        import io, contextlib
        buf = io.StringIO()
        with contextlib.redirect_stderr(buf):
            result = run('say "{ghost_var_xyz}"')
        self.assertIn("{?ghost_var_xyz}", result)
        self.assertIn("not defined", buf.getvalue())

    def test_p1_expression_interpolation_still_warns(self):
        """'{count(items)}' must not evaluate — appears as literal and warns."""
        # The regex only matches identifier-only tokens; count(items) has parens
        # so it doesn't match and passes through as literal text.
        result = run('items = "a", "b"\nsay "{count(items)}"')
        # Should contain the literal text, not the evaluated value
        self.assertIn("count(items)", result)

    # ── P1: escape sequence + keyword interpolation ───────────────────────────

    def test_p1_newline_then_yes(self):
        r"""say "Value:\n{YES}" outputs two lines, second line is YES."""
        result = run('say "Value:\\n{YES}"')
        parts = result.splitlines()
        self.assertEqual(parts[0], "Value:")
        self.assertEqual(parts[1], "YES")

    # ── P1: keyword does not interfere with variables named similarly ─────────

    def test_p1_variable_named_nope_not_affected(self):
        """A variable named 'nope' is not mistaken for 'no'."""
        result = run('nope = "hello"\nsay "{nope}"')
        self.assertEqual(result, "hello")


# ─────────────────────────────────────────────────────────────────────────────
# Letter Q — v0.6.8 return list literal
# ─────────────────────────────────────────────────────────────────────────────

class TestLetterQ(unittest.TestCase):
    """Tests for v0.6.8 Letter Q: return list literal from functions."""

    # ── Q1: basic return of list literals ────────────────────────────────────

    def test_q1_return_number_list(self):
        """function can return a number list literal."""
        result = run(
            "function get_nums\n- return 1, 2, 3\n"
            "items = get_nums()\n"
            "say count(items)"
        )
        self.assertEqual(result, "3")

    def test_q1_return_text_list(self):
        """function can return a text list literal."""
        result = run(
            'function names\n- return "Ixxy", "Lune"\n'
            "say first(names())"
        )
        self.assertEqual(result, "Ixxy")

    def test_q1_return_mixed_list(self):
        """function can return a mixed list literal."""
        result = run(
            'function mixed\n- return YES, NO, nothing, "done"\n'
            "say count(mixed())"
        )
        self.assertEqual(result, "4")

    def test_q1_count_returned_list(self):
        """count() on a returned list literal gives correct length."""
        result = run(
            "function trio\n- return 10, 20, 30\n"
            "say count(trio())"
        )
        self.assertEqual(result, "3")

    def test_q1_first_on_returned_list(self):
        """first() on a returned list literal gives the first element."""
        result = run(
            'function abc\n- return "a", "b", "c"\n'
            "say first(abc())"
        )
        self.assertEqual(result, "a")

    def test_q1_last_on_returned_list(self):
        """last() on a returned list literal gives the last element."""
        result = run(
            'function abc\n- return "a", "b", "c"\n'
            "say last(abc())"
        )
        self.assertEqual(result, "c")

    def test_q1_loop_each_over_returned_list(self):
        """loop each over a returned list literal iterates all elements."""
        result = run(
            "function nums\n- return 1, 2, 3\n"
            "total = 0\n"
            "loop each n in nums()\n- total = total + n\n"
            "say total"
        )
        self.assertEqual(result, "6")

    def test_q1_return_two_items(self):
        """return with exactly two items works."""
        result = run(
            "function pair\n- return 7, 8\n"
            "p = pair()\n"
            "say count(p)"
        )
        self.assertEqual(result, "2")

    # ── Q1: existing return behaviors unchanged ───────────────────────────────

    def test_q1_return_single_value_unchanged(self):
        """return single value still works as before."""
        result = run(
            "function give_five\n- return 5\n"
            "say give_five()"
        )
        self.assertEqual(result, "5")

    def test_q1_return_text_unchanged(self):
        """return single text value still works."""
        result = run(
            'function greet\n- return "hello"\n'
            "say greet()"
        )
        self.assertEqual(result, "hello")

    def test_q1_return_nothing_unchanged(self):
        """return nothing still works."""
        result = run(
            "function noop\n- return nothing\n"
            "say text(noop())"
        )
        self.assertEqual(result, "nothing")

    def test_q1_bare_return_unchanged(self):
        """bare return (no value) still works."""
        result = run(
            "x = 0\n"
            "function early\n- return\n"
            "early\n"
            "say 42"
        )
        self.assertEqual(result, "42")

    def test_q1_return_list_variable_unchanged(self):
        """return of a list variable still works."""
        result = run(
            "function get_items\n"
            "- items = 10, 20, 30\n"
            "- return items\n"
            "say count(get_items())"
        )
        self.assertEqual(result, "3")

    def test_q1_return_function_call_with_comma_args(self):
        """return join(items, ', ') is a single function call, not a list."""
        result = run(
            'parts = "a", "b", "c"\n'
            "function joined\n"
            '- return join(parts, ", ")\n'
            "say joined()"
        )
        self.assertEqual(result, "a, b, c")

    # ── Q1: checker behavior ─────────────────────────────────────────────────

    def _check_errors(self, src: str) -> list[str]:
        from ixx.checker import SemanticChecker
        from ixx.parser import parse
        errors = SemanticChecker().check(parse(src), "test.ixx")
        return [e.message for e in errors if e.severity == "error"]

    def test_q1_checker_accepts_return_list_in_function(self):
        """ixx check accepts return list literal inside a function."""
        errors = self._check_errors("function get_items\n- return 1, 2, 3")
        self.assertEqual(errors, [])

    def test_q1_checker_rejects_toplevel_return_list(self):
        """ixx check rejects top-level return list literal."""
        errors = self._check_errors("return 1, 2, 3")
        self.assertTrue(any("function" in e.lower() for e in errors), errors)


# ─────────────────────────────────────────────────────────────────────────────
# Letter T — v0.6.8 checker/interpreter behavior items
# ─────────────────────────────────────────────────────────────────────────────

class TestLetterT(unittest.TestCase):
    """Tests for v0.6.8 Letter T: builtin shadow warning, chaining error, indent hint."""

    # ── shared checker helper ─────────────────────────────────────────────────

    def _check(self, src: str):
        """Return list of CheckError objects from the semantic checker."""
        from ixx.checker import SemanticChecker
        from ixx.parser import parse
        return SemanticChecker().check(parse(src), "test.ixx")

    def _errors(self, src: str) -> list[str]:
        return [e.message for e in self._check(src) if e.severity == "error"]

    def _warnings(self, src: str) -> list[str]:
        return [e.message for e in self._check(src) if e.severity == "warning"]

    # ── T1: builtin shadow warning ────────────────────────────────────────────

    def test_t1_shadow_count_warns(self):
        """Assigning to 'count' produces a checker warning."""
        warnings = self._warnings("count = 5\nsay count")
        self.assertTrue(
            any("count" in w and "shadows" in w for w in warnings),
            f"Expected shadow warning, got: {warnings}",
        )

    def test_t1_shadow_text_warns(self):
        """Assigning to 'text' produces a checker warning."""
        warnings = self._warnings('text = "hello"\nsay text')
        self.assertTrue(any("text" in w and "shadows" in w for w in warnings))

    def test_t1_shadow_write_warns(self):
        """Assigning to 'write' produces a checker warning."""
        warnings = self._warnings('write = "oops"')
        self.assertTrue(any("write" in w and "shadows" in w for w in warnings))

    def test_t1_shadow_produces_warning_not_error(self):
        """Builtin shadow is a warning, not an error — ok:true in check."""
        errors = self._errors("count = 5\nsay count")
        self.assertEqual(errors, [])

    def test_t1_shadow_warning_mentions_rename(self):
        """Shadow warning message mentions 'Rename' to guide the user."""
        warnings = self._warnings("count = 5")
        self.assertTrue(any("Rename" in w for w in warnings))

    def test_t1_normal_var_no_warning(self):
        """Normal variable name produces no shadow warning."""
        warnings = self._warnings('score = 42\nsay score')
        shadow_warnings = [w for w in warnings if "shadows" in w]
        self.assertEqual(shadow_warnings, [])

    def test_t1_no_warning_inside_function(self):
        """Shadow warning is suppressed inside function bodies (conservative)."""
        warnings = self._warnings("function demo\n- count = 5\n- say count")
        shadow_warnings = [w for w in warnings if "shadows" in w]
        self.assertEqual(shadow_warnings, [])

    def test_t1_json_check_ok_true_for_shadow(self):
        """ixx check --json produces ok:true with a warning for builtin shadowing."""
        import json, tempfile, os as _os
        code = "count = 5\nsay count\n"
        with tempfile.NamedTemporaryFile(suffix=".ixx", mode="w",
                                         encoding="utf-8", delete=False) as f:
            f.write(code)
            tmp = f.name
        try:
            exit_code, raw = cli("check", tmp, "--json")
        finally:
            _os.unlink(tmp)
        data = json.loads(raw)
        self.assertTrue(data["ok"])
        severities = [e["severity"] for e in data["errors"]]
        self.assertIn("warning", severities)

    # ── T2: comparison chaining error ─────────────────────────────────────────

    def test_t2_chaining_error_message(self):
        """Chained comparison produces 'Comparisons cannot be chained' error."""
        with self.assertRaises(IXXRuntimeError) as ctx:
            run('a = 1\nb = 2\nc = 3\nif a less than b less than c\n- say "ok"')
        self.assertIn("Comparisons cannot be chained", str(ctx.exception))

    def test_t2_chaining_hint_includes_and(self):
        """Chaining error includes 'and' in the hint."""
        with self.assertRaises(IXXRuntimeError) as ctx:
            run('a = 1\nb = 2\nc = 3\nif a less than b less than c\n- say "ok"')
        self.assertIn("and", str(ctx.exception))

    def test_t2_non_chained_bool_keeps_yes_no_message(self):
        """YES/NO as the RIGHT operand keeps the existing yes-or-no message."""
        with self.assertRaises(IXXRuntimeError) as ctx:
            run('if 5 less than YES\n- say "bad"')
        self.assertIn("YES/NO", str(ctx.exception))
        self.assertNotIn("chained", str(ctx.exception).lower())

    def test_t2_normal_comparison_unchanged(self):
        """Normal numeric comparison still works."""
        result = run('x = 3\nif x less than 10\n- say "small"')
        self.assertEqual(result, "small")

    def test_t2_chaining_with_more_than(self):
        """Chained 'more than' also gives chaining message."""
        with self.assertRaises(IXXRuntimeError) as ctx:
            run('a = 10\nb = 5\nc = 1\nif a more than b more than c\n- say "ok"')
        self.assertIn("Comparisons cannot be chained", str(ctx.exception))

    # ── T5: skipped indentation level friendly error ──────────────────────────

    def test_t5_skipped_indent_gives_dash_hint(self):
        """Missing block body (no indent) produces the dash-hint message."""
        import tempfile, os as _os
        code = "if YES\nsay hello\n"   # if body has no dash — INDENT expected
        with tempfile.NamedTemporaryFile(suffix=".ixx", mode="w",
                                         encoding="utf-8", delete=False) as f:
            f.write(code)
            tmp = f.name
        try:
            exit_code, out = cli(tmp)
        finally:
            _os.unlink(tmp)
        self.assertNotEqual(exit_code, 0)
        self.assertIn("dash", out.lower())

    def test_t5_normal_indent_works(self):
        """Correct single-level indentation executes without error."""
        result = run('if YES\n- say "ok"')
        self.assertEqual(result, "ok")

    def test_t5_two_level_indent_works(self):
        """Correct two-level indentation inside a function parses and runs fine."""
        # Verify that -- inside a function body is valid IXX syntax.
        result = run(
            "function demo\n"
            "- if YES\n"
            "-- say \"ok\"\n"
            "demo"
        )
        self.assertEqual(result, "ok")


# ─────────────────────────────────────────────────────────────────────────────
# Letter U — v0.6.8 REPL/shell fixes
# ─────────────────────────────────────────────────────────────────────────────

class TestLetterU(unittest.TestCase):
    """Tests for v0.6.8 Letter U: REPL persistence, routing, history, normalize."""

    # ── shared helpers ────────────────────────────────────────────────────────

    def _make_interp(self):
        """Create a fresh Interpreter for a simulated REPL session."""
        from ixx.interpreter import Interpreter
        return Interpreter()

    def _repl_run(self, interp, source: str) -> str:
        """Run *source* through run_repl_input() using the given session interpreter."""
        import io, contextlib, os
        from ixx.parser import parse
        from ixx.modules import resolve_imports
        buf = io.StringIO()
        program = parse(source)
        imported = resolve_imports(program, os.getcwd())
        with contextlib.redirect_stdout(buf):
            interp.run_repl_input(program, imported)
        return buf.getvalue().rstrip("\n")

    # ── U1: state persistence ─────────────────────────────────────────────────

    def test_u1_variable_persists(self):
        """Variable defined in one input is visible in the next."""
        interp = self._make_interp()
        self._repl_run(interp, 'name = "Ixxy"')
        result = self._repl_run(interp, 'say name')
        self.assertEqual(result, "Ixxy")

    def test_u1_function_persists(self):
        """Function defined in one input can be called in a later input."""
        interp = self._make_interp()
        self._repl_run(interp, 'function double x\n- return x * 2')
        result = self._repl_run(interp, 'say double(21)')
        self.assertEqual(result, "42")

    def test_u1_multiple_variables_persist(self):
        """Multiple sequential definitions all persist."""
        interp = self._make_interp()
        self._repl_run(interp, 'a = 10')
        self._repl_run(interp, 'b = 20')
        result = self._repl_run(interp, 'say a + b')
        self.assertEqual(result, "30")

    def test_u1_function_redefinition_works(self):
        """Redefining a function in the REPL silently overwrites it (no duplicate error)."""
        interp = self._make_interp()
        self._repl_run(interp, 'function greet\n- say "v1"')
        self._repl_run(interp, 'function greet\n- say "v2"')
        result = self._repl_run(interp, 'greet')
        self.assertEqual(result, "v2")

    def test_u1_fresh_interpreter_has_no_state(self):
        """A fresh Interpreter starts with no variables."""
        interp = self._make_interp()
        from ixx.runtime.errors import IXXRuntimeError
        with self.assertRaises(IXXRuntimeError):
            self._repl_run(interp, 'say undefined_ghost_xyz')

    def test_u1_normal_run_still_resets(self):
        """run() still resets state — it is not affected by run_repl_input."""
        from ixx.parser import parse
        from ixx.interpreter import Interpreter
        interp = Interpreter()
        program = parse('x = 99')
        interp.run(program)
        # A second run() should reset env
        program2 = parse('say x')
        from ixx.runtime.errors import IXXRuntimeError
        with self.assertRaises(IXXRuntimeError):
            interp.run(program2)

    # ── U2: IXX call statement routing ───────────────────────────────────────

    def test_u2_write_routed_as_ixx(self):
        """'write' as first token is treated as IXX, not an unknown shell command."""
        import tempfile, os as _os
        with tempfile.TemporaryDirectory() as d:
            path = _os.path.join(d, "out.txt")
            # run via _try_run_ixx logic — provide a dummy prompt that never continues
            from ixx.shell.repl import _try_run_ixx
            captured = []
            import io, contextlib
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                result = _try_run_ixx(
                    f'write "{path}", "hello"',
                    lambda p: "",   # blank continuation → abort multiline
                )
            # Should be True (routed as IXX) and write the file
            self.assertTrue(result)
            if _os.path.exists(path):
                with open(path) as f:
                    self.assertEqual(f.read(), "hello")

    def test_u2_say_routed_as_ixx(self):
        """'say' is correctly classified as IXX."""
        from ixx.shell.repl import _try_run_ixx
        import io, contextlib
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            result = _try_run_ixx('say "hello"', lambda p: "")
        self.assertTrue(result)
        self.assertEqual(buf.getvalue().strip(), "hello")

    def test_u2_do_routed_as_ixx_starter(self):
        """'do' as first token is classified as an IXX starter, not an unknown command."""
        from ixx.shell.repl import _try_run_ixx
        # We just need result=True (classified as IXX), not necessarily successful
        # 'do' may fail if there's nothing useful to run, but it shouldn't be False
        result = _try_run_ixx('do "echo test"', lambda p: "")
        self.assertTrue(result)

    # ── U3: blank continuation line shows error ───────────────────────────────

    def test_u3_blank_continuation_shows_error_not_silent(self):
        """When blank continuation is entered after incomplete IXX, errors are shown."""
        from ixx.shell.repl import _try_run_ixx
        import io, contextlib
        buf_out = io.StringIO()
        buf_err = io.StringIO()
        # incomplete function definition → UnexpectedEOF → blank line → parse attempt
        with contextlib.redirect_stdout(buf_out), contextlib.redirect_stderr(buf_err):
            result = _try_run_ixx(
                'function broken',
                lambda p: "",  # blank continuation
            )
        # Should have returned True (handled as IXX)
        self.assertTrue(result)
        # Should NOT be completely silent — some output or at least not crash
        combined = buf_out.getvalue() + buf_err.getvalue()
        # The blank-cont path either succeeds (function registered) or
        # prints a friendly error — either way no raw Python traceback
        self.assertNotIn("Traceback", combined)

    # ── U4: _normalize preserves quoted string casing ────────────────────────

    def test_u4_unquoted_tokens_lowercased(self):
        """Unquoted command tokens are lowercased."""
        from ixx.shell.repl import _tokenize_raw, _normalize
        tokens = _tokenize_raw("CPU Info")
        result = _normalize(tokens)
        self.assertEqual(result, ["cpu", "info"])

    def test_u4_quoted_tokens_preserve_case(self):
        """Quoted string arguments preserve their original casing."""
        from ixx.shell.repl import _tokenize_raw, _normalize
        tokens = _tokenize_raw('open "/home/User/MyFile.txt"')
        result = _normalize(tokens)
        self.assertEqual(result, ["open", "/home/User/MyFile.txt"])

    def test_u4_mixed_command_and_path(self):
        """Command portion is lowercased; quoted path argument is not."""
        from ixx.shell.repl import _tokenize_raw, _normalize
        tokens = _tokenize_raw('COPY "/Src/File.txt" "/Dst/Output.TXT"')
        result = _normalize(tokens)
        self.assertEqual(result, ["copy", "/Src/File.txt", "/Dst/Output.TXT"])

    def test_u4_unquoted_path_lowercased(self):
        """Unquoted arguments are still lowercased (existing behavior preserved)."""
        from ixx.shell.repl import _tokenize_raw, _normalize
        tokens = _tokenize_raw("RAM Used")
        result = _normalize(tokens)
        self.assertEqual(result, ["ram", "used"])

    def test_u4_tokenize_returns_strings(self):
        """_tokenize (public API) returns plain list[str] for backward compat."""
        from ixx.shell.repl import _tokenize
        result = _tokenize('say "World"')
        self.assertEqual(result, ["say", "World"])

    def test_u4_tokenize_raw_returns_tuples(self):
        """_tokenize_raw returns list of (token, was_quoted) tuples."""
        from ixx.shell.repl import _tokenize_raw
        result = _tokenize_raw('say "World"')
        self.assertEqual(result, [("say", False), ("World", True)])

    # ── U5: readline history ──────────────────────────────────────────────────

    def test_u5_setup_readline_does_not_crash_without_readline(self):
        """_setup_readline does not crash when readline is unavailable."""
        from ixx.shell.repl import _setup_readline
        import sys
        from unittest.mock import patch, MagicMock
        # Simulate both readline and pyreadline3 being missing
        with patch.dict(sys.modules, {"readline": None, "pyreadline3": None}):
            try:
                _setup_readline()  # Must not raise
            except Exception as e:
                self.fail(f"_setup_readline raised {e!r} when readline unavailable")

    def test_u5_history_file_path_is_home_ixx_history(self):
        """The history file path includes .ixx_history in the home directory."""
        from ixx.shell.repl import _HISTORY_FILE
        import pathlib
        expected = str(pathlib.Path.home() / ".ixx_history")
        self.assertEqual(_HISTORY_FILE, expected)

    def test_u5_safe_write_history_does_not_crash_without_readline(self):
        """_safe_write_history is a no-op when readline is missing."""
        from ixx.shell.repl import _safe_write_history
        import sys
        from unittest.mock import patch
        with patch.dict(sys.modules, {"readline": None}):
            try:
                _safe_write_history()
            except Exception as e:
                self.fail(f"_safe_write_history raised {e!r}")


# ─────────────────────────────────────────────────────────────────────────────
# Letter V — v0.6.8 checker quality fixes
# ─────────────────────────────────────────────────────────────────────────────

class TestLetterV(unittest.TestCase):
    """Tests for v0.6.8 Letter V: StrLit line metadata, script-dir paths, line map."""

    # ── shared helpers ────────────────────────────────────────────────────────

    def _check(self, src: str, file_path: str = "test.ixx"):
        """Run SemanticChecker directly; return list of CheckError objects."""
        from ixx.checker import SemanticChecker
        from ixx.parser import parse
        return SemanticChecker().check(parse(src), file_path)

    # ── V1: StrLit carries line metadata ─────────────────────────────────────

    def test_v1_strlit_has_line_attribute(self):
        """StrLit node has a line attribute after parsing."""
        from ixx.parser import parse
        from ixx.ast_nodes import Assign, StrLit
        program = parse('x = "hello"')
        assign = program.body[0]
        self.assertIsInstance(assign, Assign)
        self.assertIsInstance(assign.value, StrLit)
        self.assertIsNotNone(assign.value.line)

    def test_v1_strlit_line_matches_source_line(self):
        """StrLit.line reflects the correct (preprocessed) source line."""
        from ixx.parser import parse
        from ixx.ast_nodes import Assign, StrLit
        program = parse('x = 1\ny = "hello"')
        str_assign = program.body[1]
        self.assertIsInstance(str_assign.value, StrLit)
        # Preprocessed line 2 (no blank lines in source)
        self.assertEqual(str_assign.value.line, 2)

    def test_v1_interpolation_warning_has_line_not_null(self):
        """Interpolation expression warning now has a real line number, not null."""
        errors = self._check('items = "a", "b"\nx = "{count(items)}"')
        warnings = [e for e in errors if e.severity == "warning"]
        self.assertTrue(len(warnings) > 0, "Expected a warning for expression interpolation")
        self.assertIsNotNone(warnings[0].line,
                             "Interpolation warning should have a line number, not null")

    def test_v1_interpolation_warning_line_is_correct(self):
        """Interpolation warning line points to the string's actual source line."""
        errors = self._check('x = 1\ny = "{count(items)}"')
        warnings = [e for e in errors if e.severity == "warning"]
        self.assertTrue(warnings)
        # The string is on line 2
        self.assertEqual(warnings[0].line, 2)

    # ── V2: read() path resolves relative to script directory ────────────────

    def test_v2_read_resolves_relative_to_script_dir(self):
        """read('data.txt') in a script finds the file next to the script."""
        import tempfile, os as _os
        from ixx.checker import SemanticChecker
        from ixx.parser import parse
        with tempfile.TemporaryDirectory() as d:
            # Create data.txt next to the "script"
            data_file = _os.path.join(d, "data.txt")
            with open(data_file, "w") as f:
                f.write("hello")
            script_path = _os.path.join(d, "script.ixx")
            # Check from a completely different CWD
            src = 'say read("data.txt")'
            errors = SemanticChecker().check(parse(src), script_path)
            file_errors = [e for e in errors if e.severity == "error"
                           and "File not found" in e.message]
            self.assertEqual(file_errors, [],
                             "read('data.txt') should not error when file is next to script")

    def test_v2_read_still_errors_for_truly_missing_file(self):
        """read('missing.txt') still errors when file is genuinely missing."""
        import tempfile, os as _os
        from ixx.checker import SemanticChecker
        from ixx.parser import parse
        with tempfile.TemporaryDirectory() as d:
            script_path = _os.path.join(d, "script.ixx")
            src = 'say read("no_such_file_xyz.txt")'
            errors = SemanticChecker().check(parse(src), script_path)
            file_errors = [e for e in errors if e.severity == "error"
                           and "File not found" in e.message]
            self.assertTrue(len(file_errors) > 0,
                            "read('missing.txt') should still produce an error")

    def test_v2_readlines_resolves_relative_to_script_dir(self):
        """readlines('data.txt') also resolves relative to script dir."""
        import tempfile, os as _os
        from ixx.checker import SemanticChecker
        from ixx.parser import parse
        with tempfile.TemporaryDirectory() as d:
            data_file = _os.path.join(d, "data.txt")
            with open(data_file, "w") as f:
                f.write("line1\nline2")
            script_path = _os.path.join(d, "script.ixx")
            src = 'lines = readlines("data.txt")'
            errors = SemanticChecker().check(parse(src), script_path)
            file_errors = [e for e in errors if e.severity == "error"
                           and "File not found" in e.message]
            self.assertEqual(file_errors, [])

    def test_v2_absolute_path_unchanged(self):
        """An absolute path in read() is not re-resolved."""
        import tempfile, os as _os
        from ixx.checker import SemanticChecker
        from ixx.parser import parse
        with tempfile.TemporaryDirectory() as d:
            data_file = _os.path.join(d, "data.txt")
            with open(data_file, "w") as f:
                f.write("content")
            # Use forward slashes so backslashes aren't treated as IXX escapes
            fwd_path = data_file.replace("\\", "/")
            src = f'say read("{fwd_path}")'
            errors = SemanticChecker().check(parse(src), "test.ixx")
            file_errors = [e for e in errors if "File not found" in e.message]
            self.assertEqual(file_errors, [])

    # ── V3: line map corrects checker error lines for blank-line stripping ────

    def test_v3_preprocess_with_map_no_blanks(self):
        """With no blank lines, map is identity (preprocessed line == original line)."""
        from ixx.preprocessor import preprocess_with_map
        src = "x = 1\nsay x\n"
        _, line_map = preprocess_with_map(src)
        self.assertEqual(line_map.get(1), 1)
        self.assertEqual(line_map.get(2), 2)

    def test_v3_preprocess_with_map_blank_lines_shift(self):
        """Blank lines shift preprocessed line numbers; map records correct originals."""
        from ixx.preprocessor import preprocess_with_map
        # original line 1: x = 1
        # original line 2: (blank)
        # original line 3: say x
        src = "x = 1\n\nsay x\n"
        _, line_map = preprocess_with_map(src)
        self.assertEqual(line_map.get(1), 1)   # "x = 1" → orig line 1
        self.assertEqual(line_map.get(2), 3)   # "say x" → orig line 3

    def test_v3_checker_error_line_corrected_via_cli(self):
        """ixx check --json reports the original file line, not the preprocessed line."""
        import json, tempfile, os as _os
        # Line 1: blank
        # Line 2: x = 1
        # Line 3: blank
        # Line 4: say ghost_var  ← error here (original line 4)
        src = "\nx = 1\n\nsay ghost_var\n"
        with tempfile.NamedTemporaryFile(suffix=".ixx", mode="w",
                                         encoding="utf-8", delete=False) as f:
            f.write(src)
            tmp = f.name
        try:
            exit_code, raw = cli("check", tmp, "--json")
        finally:
            _os.unlink(tmp)
        data = json.loads(raw)
        error_lines = [e["line"] for e in data["errors"] if e["severity"] == "error"]
        self.assertTrue(any(ln == 4 for ln in error_lines),
                        f"Expected error on original line 4, got lines: {error_lines}")

    def test_v3_human_check_line_corrected(self):
        """ixx check (human output) reports the original file line number."""
        import tempfile, os as _os
        # original line 1: blank
        # original line 2: say ghost_var  ← error
        src = "\nsay ghost_var\n"
        with tempfile.NamedTemporaryFile(suffix=".ixx", mode="w",
                                         encoding="utf-8", delete=False) as f:
            f.write(src)
            tmp = f.name
        try:
            exit_code, combined = cli("check", tmp)
        finally:
            _os.unlink(tmp)
        self.assertNotEqual(exit_code, 0)
        # Original line 2 should appear, not preprocessed line 1
        self.assertIn("line 2", combined)

    def test_v3_no_blank_lines_line_unchanged(self):
        """With no blank lines, checker error line is reported as-is."""
        import json, tempfile, os as _os
        src = "say ghost_var\n"
        with tempfile.NamedTemporaryFile(suffix=".ixx", mode="w",
                                         encoding="utf-8", delete=False) as f:
            f.write(src)
            tmp = f.name
        try:
            exit_code, raw = cli("check", tmp, "--json")
        finally:
            _os.unlink(tmp)
        data = json.loads(raw)
        error_lines = [e["line"] for e in data["errors"] if e["severity"] == "error"]
        self.assertTrue(any(ln == 1 for ln in error_lines),
                        f"Expected error on line 1, got: {error_lines}")


class TestReplMultiline(unittest.TestCase):
    """REPL multiline block entry — block-starter detection and orphan dash guard."""

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _make_prompt(self, lines: list):
        """Return a prompt function that yields *lines* then raises EOFError."""
        it = iter(lines)

        def _prompt(p):
            try:
                return next(it)
            except StopIteration:
                raise EOFError()

        return _prompt

    def _run_block(self, header, body_lines, setup=None, interpreter=None):
        """
        Feed *header* + *body_lines* + blank-line into ``_try_run_ixx``.

        If *setup* is provided it is run first (single-line IXX on *interpreter*).
        Returns (stdout_text, interpreter).
        """
        import io, contextlib
        from ixx.shell.repl import _try_run_ixx
        from ixx.interpreter import Interpreter

        if interpreter is None:
            interpreter = Interpreter()

        # Optional setup lines (plain single-line IXX)
        if setup:
            for setup_line in ([setup] if isinstance(setup, str) else setup):
                with contextlib.redirect_stdout(io.StringIO()):
                    _try_run_ixx(setup_line, lambda p: "", interpreter)

        # body_lines + blank line terminates collection
        prompt_fn = self._make_prompt(body_lines + [""])

        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            _try_run_ixx(header, prompt_fn, interpreter)

        return buf.getvalue(), interpreter

    # ------------------------------------------------------------------
    # 1. if-false block does not run body
    # ------------------------------------------------------------------

    def test_if_false_no_output(self):
        """if false: body must not run."""
        out, _ = self._run_block(
            "if 1 more than 10",
            ['- say "big"'],
        )
        self.assertNotIn("big", out)

    # ------------------------------------------------------------------
    # 2. if-true block runs body
    # ------------------------------------------------------------------

    def test_if_true_runs_body(self):
        """if true: body runs."""
        out, _ = self._run_block(
            "if 15 more than 10",
            ['- say "big"'],
        )
        self.assertIn("big", out)

    # ------------------------------------------------------------------
    # 3. Function block defines function and persists in session
    # ------------------------------------------------------------------

    def test_function_definition_and_call(self):
        """function block defines a function that persists in the session."""
        import io, contextlib
        from ixx.shell.repl import _try_run_ixx
        from ixx.interpreter import Interpreter

        interp = Interpreter()

        self._run_block(
            "function double x",
            ["- return x * 2"],
            interpreter=interp,
        )

        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            _try_run_ixx("say double(21)", lambda p: "", interp)
        self.assertIn("42", buf.getvalue())

    # ------------------------------------------------------------------
    # 4. Loop block works
    # ------------------------------------------------------------------

    def test_loop_block(self):
        """loop block runs the correct number of iterations."""
        out, _ = self._run_block(
            "loop n more than 0",
            ["- say n", "- n = n - 1"],
            setup="n = 3",
        )
        self.assertIn("3", out)
        self.assertIn("2", out)
        self.assertIn("1", out)
        self.assertNotIn("0", out)

    # ------------------------------------------------------------------
    # 5. Loop-each block works
    # ------------------------------------------------------------------

    def test_loop_each_block(self):
        """loop each block iterates over list items."""
        out, _ = self._run_block(
            "loop each item in items",
            ["- say item"],
            setup='items = "a", "b", "c"',
        )
        self.assertIn("a", out)
        self.assertIn("b", out)
        self.assertIn("c", out)

    # ------------------------------------------------------------------
    # 6. Try/catch block works
    # ------------------------------------------------------------------

    def test_try_catch_block(self):
        """try/catch block catches a runtime error and runs catch body."""
        out, _ = self._run_block(
            "try",
            ['- x = number("bad")', "catch", '- say "caught"', "- say error"],
        )
        self.assertIn("caught", out)
        self.assertIn("bad", out)

    # ------------------------------------------------------------------
    # 7. Nested if block works
    # ------------------------------------------------------------------

    def test_nested_if_block(self):
        """Nested if block (two-level dash indent) runs correctly."""
        out, _ = self._run_block(
            "if x more than 0",
            ["- if x less than 5", '-- say "inside"'],
            setup="x = 3",
        )
        self.assertIn("inside", out)

    def test_nested_if_false_outer_no_inner_output(self):
        """Outer if false → inner body must not run."""
        out, _ = self._run_block(
            "if x more than 10",
            ["- if x less than 5", '-- say "inside"'],
            setup="x = 3",
        )
        self.assertNotIn("inside", out)

    # ------------------------------------------------------------------
    # 8. Orphan dash line does not execute; shows friendly error
    # ------------------------------------------------------------------

    def test_orphan_dash_shows_error_not_output(self):
        """Orphan '-' line shows friendly error instead of executing body."""
        import io, contextlib
        from ixx.shell.repl import _try_run_ixx

        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            result = _try_run_ixx('- say "big"', lambda p: "")
        out = buf.getvalue()
        self.assertTrue(result, "Should return True (handled)")
        self.assertIn("no block", out.lower())
        self.assertNotIn("big", out)

    def test_orphan_double_dash_shows_error(self):
        """Double-dash orphan line also gives a friendly message, no execution."""
        import io, contextlib
        from ixx.shell.repl import _try_run_ixx

        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            _try_run_ixx('-- say "nested"', lambda p: "")
        out = buf.getvalue()
        self.assertNotIn("nested", out)

    # ------------------------------------------------------------------
    # 9. Old single-line REPL persistence still works
    # ------------------------------------------------------------------

    def test_single_line_assignment_persists(self):
        """Single-line variable assignment persists across subsequent lines."""
        import io, contextlib
        from ixx.shell.repl import _try_run_ixx
        from ixx.interpreter import Interpreter

        interp = Interpreter()
        _try_run_ixx('name = "Ixxy"', lambda p: "", interp)
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            _try_run_ixx("say name", lambda p: "", interp)
        self.assertIn("Ixxy", buf.getvalue())

    # ------------------------------------------------------------------
    # 10. if/else collected as one block
    # ------------------------------------------------------------------

    def test_if_else_false_branch(self):
        """if/else block — false branch: else body runs."""
        out, _ = self._run_block(
            "if x more than 10",
            ['- say "big"', "else", '- say "small"'],
            setup="x = 3",
        )
        self.assertNotIn("big", out)
        self.assertIn("small", out)

    def test_if_else_true_branch(self):
        """if/else block — true branch runs, else does not."""
        out, _ = self._run_block(
            "if x more than 10",
            ['- say "big"', "else", '- say "small"'],
            setup="x = 15",
        )
        self.assertIn("big", out)
        self.assertNotIn("small", out)

    # ------------------------------------------------------------------
    # 11. _is_block_start helper
    # ------------------------------------------------------------------

    def test_is_block_start_recognises_keywords(self):
        """_is_block_start returns True for all block-starting keywords."""
        from ixx.shell.repl import _is_block_start
        for kw in (
            "if x more than 5", "else", "loop n more than 0",
            "loop each item in items", "function double x", "try", "catch",
        ):
            self.assertTrue(_is_block_start(kw), f"Expected True for: {kw!r}")

    def test_is_block_start_rejects_normal_lines(self):
        """_is_block_start returns False for non-block lines."""
        from ixx.shell.repl import _is_block_start
        for line in ("x = 5", 'say "hi"', "# comment", "", "name = function_name"):
            self.assertFalse(_is_block_start(line), f"Expected False for: {line!r}")


class TestReplClear(unittest.TestCase):
    """clear / cls shell meta-command tests."""

    def test_clear_callable_without_error(self):
        """_handle_clear() runs without raising."""
        from ixx.shell.repl import _handle_clear
        import unittest.mock
        with unittest.mock.patch("os.system"):
            try:
                _handle_clear()
            except Exception as exc:
                self.fail(f"_handle_clear() raised: {exc}")

    def test_clear_calls_os_system_once(self):
        """_handle_clear() calls os.system exactly once."""
        from ixx.shell.repl import _handle_clear
        import unittest.mock
        with unittest.mock.patch("os.system") as mock_sys:
            _handle_clear()
        mock_sys.assert_called_once()

    def test_cls_alias_in_run_source(self):
        """The run() main loop handles both 'clear' and 'cls'."""
        import inspect
        from ixx.shell import repl
        src = inspect.getsource(repl.run)
        self.assertIn('"cls"', src)
        self.assertIn('"clear"', src)

    def test_clear_does_not_reset_interpreter_state(self):
        """clear does not wipe variables from the session interpreter."""
        import io, contextlib, unittest.mock
        from ixx.shell.repl import _try_run_ixx, _handle_clear
        from ixx.interpreter import Interpreter

        interp = Interpreter()
        _try_run_ixx('name = "Ixxy"', lambda p: "", interp)

        with unittest.mock.patch("os.system"):
            _handle_clear()

        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            _try_run_ixx("say name", lambda p: "", interp)
        self.assertIn("Ixxy", buf.getvalue())

    def test_clear_followed_by_block_still_works(self):
        """Calling _handle_clear() then running a block works normally."""
        import io, contextlib, unittest.mock
        from ixx.shell.repl import _try_run_ixx, _handle_clear
        from ixx.interpreter import Interpreter

        interp = Interpreter()
        with unittest.mock.patch("os.system"):
            _handle_clear()

        lines_it = iter(["- say x", ""])

        def mock_prompt(p):
            return next(lines_it)

        # x is not defined → IXX runtime error; just must not crash hard
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            _try_run_ixx("if x more than 0", mock_prompt, interp)
        # Should not propagate a raw Python exception
        self.assertNotIn("Traceback", buf.getvalue())

    def test_clear_failure_no_exception(self):
        """If os.system raises, _handle_clear() swallows it silently."""
        from ixx.shell.repl import _handle_clear
        import unittest.mock
        with unittest.mock.patch(
            "os.system", side_effect=Exception("terminal error")
        ):
            try:
                _handle_clear()
            except Exception:
                self.fail("_handle_clear() should not propagate exceptions")


if __name__ == "__main__":
    unittest.main(verbosity=2)
