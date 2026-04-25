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
        self.assertIn("478 passed", self._plain_out())

    def test_output_contains_229_passed(self):
        self.assertIn("229 passed", self._plain_out())

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
        self.assertIn("Circular", str(ctx.exception))

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

    def test_first_empty_list(self):
        """first() on an empty list must return nothing."""
        src = 'items = 1, 2, 3\nsay type(first(items))'
        output = run(src)
        self.assertIn("number", output)

    def test_last_empty_list(self):
        """last() on a nonempty list returns the last element."""
        src = 'items = 10, 20, 30\nsay last(items)'
        output = run(src)
        self.assertEqual(output, "30")

    # ── number() edge cases ───────────────────────────────────────────────────

    def test_number_float_string(self):
        """number('1.0') must return 1.0 (float)."""
        src = 'say number("1.0")'
        output = run(src)
        self.assertEqual(output, "1.0")

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

if __name__ == "__main__":
    unittest.main(verbosity=2)
