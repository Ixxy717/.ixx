"""
v0.4 function system tests — user-defined functions, built-ins, and all related
error cases.

v0.5 items (records, try/error, extended built-in library) are skipped below.
"""

from __future__ import annotations
import io
import sys
import unittest
from contextlib import redirect_stdout, redirect_stderr
from ixx.parser import parse
from ixx.interpreter import Interpreter, IXXRuntimeError


def run(source: str) -> str:
    """Run IXX source and return captured stdout."""
    buf = io.StringIO()
    with redirect_stdout(buf):
        prog = parse(source)
        interp = Interpreter()
        interp.run(prog)
    return buf.getvalue().strip()


def run_err(source: str) -> str:
    """Run source and return the IXXRuntimeError message."""
    with redirect_stdout(io.StringIO()):
        try:
            prog = parse(source)
            interp = Interpreter()
            interp.run(prog)
        except IXXRuntimeError as e:
            return str(e)
    return ""


def lines(source: str) -> list[str]:
    """Run source and return output as a list of stripped lines."""
    return [l for l in run(source).split("\n") if l]


# ─────────────────────────────────────────────────────────────────────────────
# Basic function definitions and calls
# ─────────────────────────────────────────────────────────────────────────────

class TestFuncBasic(unittest.TestCase):

    def test_no_arg_function(self):
        src = """
function divider
- say "--------"

divider
"""
        self.assertEqual(run(src), "--------")

    def test_one_arg_function(self):
        src = """
function greet name
- say "Hello, {name}"

greet "World"
"""
        self.assertEqual(run(src), "Hello, World")

    def test_two_arg_function_call_stmt(self):
        src = """
function add a, b
- say a + b

add 3, 4
"""
        self.assertEqual(run(src), "7")

    def test_function_defined_after_use(self):
        """Two-pass: function defined later in file is callable from earlier."""
        src = """
greet "Ixxy"

function greet name
- say "Hi {name}"
"""
        self.assertEqual(run(src), "Hi Ixxy")

    def test_call_multiple_times(self):
        src = """
function line
- say "---"

line
line
line
"""
        self.assertEqual(lines(src), ["---", "---", "---"])


# ─────────────────────────────────────────────────────────────────────────────
# Return values — expression-position calls must use parentheses
# ─────────────────────────────────────────────────────────────────────────────

class TestFuncReturn(unittest.TestCase):

    def test_return_value_assigned(self):
        src = """
function add a, b
- return a + b

sum = add(5, 3)
say sum
"""
        self.assertEqual(run(src), "8")

    def test_return_string(self):
        src = """
function greet name
- return "Hello, " + name

msg = greet("Ixxy")
say msg
"""
        self.assertEqual(run(src), "Hello, Ixxy")

    def test_early_return(self):
        src = """
function check age
- if age less than 18
-- return "minor"
- return "adult"

say check(15)
say check(21)
"""
        self.assertEqual(lines(src), ["minor", "adult"])

    def test_return_nothing(self):
        src = """
function noop
- return

result = noop()
say type(result)
"""
        self.assertEqual(run(src), "nothing")

    def test_no_explicit_return_gives_nothing(self):
        src = """
function dowork
- x = 1

r = dowork()
say type(r)
"""
        self.assertEqual(run(src), "nothing")


# ─────────────────────────────────────────────────────────────────────────────
# Scoping
# ─────────────────────────────────────────────────────────────────────────────

class TestFuncScope(unittest.TestCase):

    def test_local_variable_does_not_leak(self):
        src = """
name = "Outside"

function test
- name = "Inside"
- say name

test
say name
"""
        out = lines(src)
        self.assertEqual(out[0], "Inside")
        self.assertEqual(out[1], "Outside")

    def test_function_reads_global(self):
        src = """
greeting = "Howdy"

function wave
- say greeting

wave
"""
        self.assertEqual(run(src), "Howdy")

    def test_param_shadows_global(self):
        src = """
x = 100

function show x
- say x

show 42
say x
"""
        out = lines(src)
        self.assertEqual(out[0], "42")
        self.assertEqual(out[1], "100")


# ─────────────────────────────────────────────────────────────────────────────
# Recursion
# ─────────────────────────────────────────────────────────────────────────────

class TestFuncRecursion(unittest.TestCase):

    def test_countdown(self):
        src = """
function countdown n
- if n at most 0
-- return
- say n
- countdown n - 1

countdown 3
"""
        self.assertEqual(lines(src), ["3", "2", "1"])

    def test_factorial(self):
        src = """
function factorial n
- if n at most 1
-- return 1
- sub = factorial(n - 1)
- return n * sub

say factorial(5)
"""
        self.assertEqual(run(src), "120")

    def test_deep_recursion_raises(self):
        src = """
function infinite n
- infinite (n + 1)

infinite 0
"""
        err = run_err(src)
        self.assertIn("Recursion too deep", err)


# ─────────────────────────────────────────────────────────────────────────────
# Error cases
# ─────────────────────────────────────────────────────────────────────────────

class TestFuncErrors(unittest.TestCase):

    def test_wrong_arg_count_too_few(self):
        src = """
function add a, b
- return a + b

add 5
"""
        err = run_err(src)
        self.assertIn("expects 2", err)

    def test_wrong_arg_count_too_many(self):
        src = """
function greet name
- say name

greet "a", "b"
"""
        err = run_err(src)
        self.assertIn("expects 1", err)

    def test_unknown_function(self):
        src = """
foo "bar"
"""
        err = run_err(src)
        self.assertIn("foo", err)
        self.assertIn("not a function", err)

    def test_return_outside_function_is_parse_error(self):
        """return at top level should raise a parse or runtime error."""
        try:
            prog = parse("return 5")
        except Exception:
            return   # parse error is fine
        # If it parsed, running it should raise
        err = run_err("return 5")
        self.assertNotEqual(err, "")


# ─────────────────────────────────────────────────────────────────────────────
# Built-in functions (v0.4: count, text, number, type, ask)
# v0.5 built-ins (upper/lower/trim/round/etc.) are skipped below
# ─────────────────────────────────────────────────────────────────────────────

class TestBuiltins(unittest.TestCase):

    # count
    def test_count_list(self):
        self.assertEqual(run('items = 1, 2, 3\nsay count(items)'), "3")

    def test_count_string(self):
        self.assertEqual(run('say count("hello")'), "5")

    # text / number
    def test_text_converts_int(self):
        self.assertEqual(run('say text(42)'), "42")

    def test_number_converts_string(self):
        self.assertEqual(run('say number("7")'), "7")

    def test_number_converts_float_string(self):
        self.assertEqual(run('say number("3.5")'), "3.5")

    def test_number_bad_input_raises(self):
        err = run_err('say number("abc")')
        self.assertIn("Cannot convert", err)
        self.assertIn("abc", err)

    # type
    def test_type_int(self):
        self.assertEqual(run('say type(42)'), "number")

    def test_type_string(self):
        self.assertEqual(run('say type("hello")'), "text")

    def test_type_bool(self):
        self.assertEqual(run('say type(YES)'), "bool")

    def test_type_list(self):
        self.assertEqual(run('items = 1, 2\nsay type(items)'), "list")

    def test_type_nothing(self):
        src = """
function noop
- return

r = noop()
say type(r)
"""
        self.assertEqual(run(src), "nothing")

    # ── v0.5 built-ins: skipped ────────────────────────────────────────────────

    @unittest.skip("v0.5 built-in")
    def test_upper(self):
        self.assertEqual(run('say upper("hello")'), "HELLO")

    @unittest.skip("v0.5 built-in")
    def test_lower(self):
        self.assertEqual(run('say lower("WORLD")'), "world")

    @unittest.skip("v0.5 built-in")
    def test_trim(self):
        self.assertEqual(run('say trim("  hi  ")'), "hi")

    @unittest.skip("v0.5 built-in")
    def test_length_string(self):
        self.assertEqual(run('say length("abc")'), "3")

    @unittest.skip("v0.5 built-in")
    def test_length_list(self):
        self.assertEqual(run('items = 1, 2, 3\nsay length(items)'), "3")

    @unittest.skip("v0.5 built-in")
    def test_round_up(self):
        self.assertEqual(run('say round(3.7)'), "4")

    @unittest.skip("v0.5 built-in")
    def test_floor(self):
        self.assertEqual(run('say floor(3.9)'), "3")

    @unittest.skip("v0.5 built-in")
    def test_ceil(self):
        self.assertEqual(run('say ceil(3.1)'), "4")

    @unittest.skip("v0.5 built-in")
    def test_abs_negative(self):
        self.assertEqual(run('x = -5\nsay abs(x)'), "5")

    @unittest.skip("v0.5 built-in")
    def test_min(self):
        self.assertEqual(run('result = min(3, 1, 4)\nsay result'), "1")

    @unittest.skip("v0.5 built-in")
    def test_max(self):
        self.assertEqual(run('result = max(3, 1, 4)\nsay result'), "4")

    @unittest.skip("v0.5 built-in")
    def test_sqrt(self):
        self.assertEqual(run('say sqrt(16)'), "4")

    @unittest.skip("v0.5 built-in")
    def test_power(self):
        self.assertEqual(run('result = power(2, 10)\nsay result'), "1024")

    @unittest.skip("v0.5 built-in")
    def test_first(self):
        self.assertEqual(run('items = 10, 20, 30\nsay first(items)'), "10")

    @unittest.skip("v0.5 built-in")
    def test_last(self):
        self.assertEqual(run('items = 10, 20, 30\nsay last(items)'), "30")

    @unittest.skip("v0.5 built-in")
    def test_sort(self):
        self.assertEqual(run('items = 3, 1, 2\nsay sort(items)'), "1, 2, 3")

    @unittest.skip("v0.5 built-in")
    def test_reverse(self):
        self.assertEqual(run('items = 1, 2, 3\nsay reverse(items)'), "3, 2, 1")

    @unittest.skip("v0.5 built-in")
    def test_unique(self):
        self.assertEqual(run('items = 1, 2, 1, 3\nsay unique(items)'), "1, 2, 3")

    @unittest.skip("v0.5 built-in")
    def test_split(self):
        self.assertEqual(run('parts = split("a,b,c", ",")\nsay count(parts)'), "3")

    @unittest.skip("v0.5 built-in")
    def test_join(self):
        self.assertEqual(run('items = "a", "b", "c"\nresult = join(items, "-")\nsay result'), "a-b-c")

    @unittest.skip("v0.5 built-in")
    def test_replace(self):
        self.assertEqual(run('result = replace("hello world", "world", "IXX")\nsay result'), "hello IXX")


# ─────────────────────────────────────────────────────────────────────────────
# Records — v0.5, skipped
# ─────────────────────────────────────────────────────────────────────────────

@unittest.skip("v0.5 — records not yet implemented")
class TestRecords(unittest.TestCase):

    def test_record_field_access(self):
        src = """
person = record
- name = "Ixxy"
- age = 19

say person.name
say person.age
"""
        out = lines(src)
        self.assertEqual(out[0], "Ixxy")
        self.assertEqual(out[1], "19")

    def test_record_interpolation(self):
        src = """
person = record
- name = "Ixxy"

say "Hello, {person.name}"
"""
        self.assertEqual(run(src), "Hello, Ixxy")

    def test_record_in_function(self):
        src = """
function greet_person p
- say "Hi, " + p.name

person = record
- name = "Ixxy"

greet_person person
"""
        self.assertEqual(run(src), "Hi, Ixxy")

    def test_record_bad_field(self):
        src = """
person = record
- name = "Ixxy"

say person.missing
"""
        err = run_err(src)
        self.assertIn("missing", err)


# ─────────────────────────────────────────────────────────────────────────────
# try / if error — v0.5, skipped
# ─────────────────────────────────────────────────────────────────────────────

@unittest.skip("v0.5 — try/error not yet implemented")
class TestTryError(unittest.TestCase):

    def test_try_no_error(self):
        src = """
try
- x = 10
- say x
"""
        self.assertEqual(run(src), "10")

    def test_try_catches_runtime_error(self):
        src = """
try
- say undefined_var
if error
- say "caught"
"""
        out = run(src)
        self.assertIn("caught", out)

    def test_try_error_as_variable(self):
        src = """
try
- say undefined_var
if error as e
- say "error occurred"
"""
        out = run(src)
        self.assertIn("error occurred", out)

    def test_no_error_skips_handler(self):
        src = """
try
- x = 1
if error
- say "should not see this"
say "ok"
"""
        self.assertNotIn("should not see this", run(src))
        self.assertIn("ok", run(src))


# ─────────────────────────────────────────────────────────────────────────────
# v0.3.8 regression tests
# ─────────────────────────────────────────────────────────────────────────────

class TestBugfixes(unittest.TestCase):

    def test_blank_lines_in_block_ok(self):
        """Blank lines inside dash-blocks should be silently stripped."""
        src = "if YES\n- say \"yes\"\n\n- say \"still yes\"\n"
        self.assertEqual(lines(src), ["yes", "still yes"])

    def test_loop_iteration_limit(self):
        """Infinite loop should raise a friendly error."""
        src = "x = 1\nloop x more than 0\n- say x"
        err = run_err(src)
        self.assertIn("10,000", err)

    def test_bool_int_guard_arithmetic(self):
        """YES + 1 should raise instead of silently returning 2."""
        err = run_err("x = YES + 1")
        self.assertIn("YES/NO in arithmetic", err)

    def test_bool_int_guard_comparison(self):
        """YES more than 0 should raise, not silently return True."""
        err = run_err("if YES more than 0\n- say \"bad\"")
        self.assertIn("YES/NO", err)

    def test_silent_interpolation_warning(self):
        """Undefined variable in interpolation writes warning to stderr."""
        buf_err = io.StringIO()
        buf_out = io.StringIO()
        with redirect_stderr(buf_err), redirect_stdout(buf_out):
            prog = parse('say "Hello {undefined_var}"')
            Interpreter().run(prog)
        self.assertIn("undefined_var", buf_err.getvalue())

    def test_contains_type_mismatch_warns(self):
        """Checking for string in list-of-ints warns on stderr."""
        buf_err = io.StringIO()
        buf_out = io.StringIO()
        with redirect_stderr(buf_err), redirect_stdout(buf_out):
            prog = parse('ids = 1, 2, 3\nif ids contains "2"\n- say "found"')
            Interpreter().run(prog)
        self.assertIn("types don", buf_err.getvalue())

    def test_if_scope_variable_warn(self):
        """Variable created inside if block doesn't exist outside."""
        src = 'if YES\n- inner = "x"\nsay "{inner}"'
        buf_err = io.StringIO()
        buf_out = io.StringIO()
        with redirect_stderr(buf_err), redirect_stdout(buf_out):
            prog = parse(src)
            Interpreter().run(prog)
        # Should warn about inner not being defined in the outer scope
        self.assertIn("inner", buf_err.getvalue())


if __name__ == "__main__":
    unittest.main()
