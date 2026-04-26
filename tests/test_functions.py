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
        self.assertIn("not defined", err)

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
        """type() returns 'bool' for YES and NO — intentional, documented IXX behaviour."""
        self.assertEqual(run('say type(YES)'), "bool")
        self.assertEqual(run('say type(NO)'), "bool")

    def test_type_nothing_literal(self):
        """type() returns 'nothing' for the nothing literal."""
        self.assertEqual(run('say type(nothing)'), "nothing")

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
        """YES/NO on the right side of a numeric comparison should raise."""
        err = run_err("if 0 more than YES\n- say \"bad\"")
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


# ─────────────────────────────────────────────────────────────────────────────
# v0.4 regression — keyword-as-identifier-prefix bug (return_list, etc.)
# ─────────────────────────────────────────────────────────────────────────────

class TestKeywordIdentifierRegression(unittest.TestCase):
    """Functions whose names start with a keyword must parse and run correctly."""

    def test_return_literal(self):
        src = (
            "function simple\n"
            "- return 81\n"
            "\n"
            "value = simple()\n"
            "say value\n"
        )
        self.assertEqual(run(src), "81")

    def test_return_variable(self):
        src = (
            "function identity x\n"
            "- return x\n"
            "\n"
            "value = identity(42)\n"
            "say value\n"
        )
        self.assertEqual(run(src), "42")

    def test_return_arithmetic(self):
        src = (
            "function math x\n"
            "- y = x + 1\n"
            "- return y * 2\n"
            "\n"
            "value = math(5)\n"
            "say value\n"
        )
        self.assertEqual(run(src), "12")

    def test_return_function_call(self):
        src = (
            "function nested_call x\n"
            "- return add(x, 5)\n"
            "\n"
            "function add a, b\n"
            "- return a + b\n"
            "\n"
            "value = nested_call(10)\n"
            "say value\n"
        )
        self.assertEqual(run(src), "15")

    def test_two_functions_back_to_back_with_return(self):
        src = (
            "function one\n"
            "- return 1\n"
            "\n"
            "function two\n"
            "- return 2\n"
            "\n"
            "say one()\n"
            "say two()\n"
        )
        self.assertEqual(lines(src), ["1", "2"])

    def test_function_named_return_list(self):
        """Function name starting with keyword 'return' must not break lexer."""
        src = (
            'function return_list\n'
            '- items = "alpha", "beta", "ixx"\n'
            '- return items\n'
            '\n'
            'result = return_list()\n'
            'say count(result)\n'
        )
        self.assertEqual(run(src), "3")

    def test_function_named_is_valid(self):
        """Function name starting with keyword 'is' must not break lexer."""
        src = (
            "function is_valid x\n"
            "- return x more than 0\n"
            "\n"
            "say is_valid(5)\n"
            "say is_valid(-1)\n"
        )
        self.assertEqual(lines(src), ["YES", "NO"])

    def test_function_named_not_empty(self):
        """Function name starting with keyword 'not' must not break lexer."""
        src = (
            "function not_empty x\n"
            "- return x more than 0\n"
            "\n"
            "say not_empty(3)\n"
        )
        self.assertEqual(run(src), "YES")

    def test_function_named_contains_check(self):
        """Function name starting with keyword 'contains' must not break lexer."""
        src = (
            'function contains_check items\n'
            '- if items contains "x"\n'
            '-- return YES\n'
            '- return NO\n'
            '\n'
            'langs = "a", "x", "b"\n'
            'say contains_check(langs)\n'
        )
        self.assertEqual(run(src), "YES")


# ─────────────────────────────────────────────────────────────────────────────
# v0.4 regression — UTF-8 BOM at start of source
# ─────────────────────────────────────────────────────────────────────────────

class TestBOMHandling(unittest.TestCase):
    """UTF-8 BOM (U+FEFF / EF BB BF) must be silently stripped."""

    def test_bom_say_hello(self):
        """Source beginning with BOM runs correctly."""
        src = '\ufeffsay "Hello"'
        self.assertEqual(run(src), "Hello")

    def test_bom_with_variable(self):
        """BOM before assignment and say still works."""
        src = '\ufeffx = 42\nsay x'
        self.assertEqual(run(src), "42")

    def test_bom_with_function(self):
        """BOM before a function definition parses and runs correctly."""
        src = (
            '\ufefffunction greet name\n'
            '- say "Hi {name}"\n'
            '\n'
            'greet "World"\n'
        )
        self.assertEqual(run(src), "Hi World")


if __name__ == "__main__":
    unittest.main()


# ─────────────────────────────────────────────────────────────────────────────
# v0.5 built-ins — text
# ─────────────────────────────────────────────────────────────────────────────

class TestBuiltinText(unittest.TestCase):

    def test_upper_basic(self):
        self.assertEqual(run('say upper("hello")'), "HELLO")

    def test_upper_already_upper(self):
        self.assertEqual(run('say upper("WORLD")'), "WORLD")

    def test_lower_basic(self):
        self.assertEqual(run('say lower("HELLO")'), "hello")

    def test_lower_mixed(self):
        self.assertEqual(run('say lower("Hello World")'), "hello world")

    def test_trim_spaces(self):
        self.assertEqual(run('say trim("  hi  ")'), "hi")

    def test_trim_no_spaces(self):
        self.assertEqual(run('say trim("clean")'), "clean")

    def test_replace_word(self):
        self.assertEqual(
            run('say replace("hello world", "world", "there")'), "hello there"
        )

    def test_replace_all_occurrences(self):
        self.assertEqual(run('say replace("aaa", "a", "b")'), "bbb")

    def test_replace_not_found(self):
        self.assertEqual(run('say replace("hello", "xyz", "abc")'), "hello")

    def test_split_by_comma(self):
        self.assertEqual(
            run('parts = split("a,b,c", ",")\nsay count(parts)'), "3"
        )

    def test_split_by_default_whitespace(self):
        self.assertEqual(
            run('words = split("hello world")\nsay count(words)'), "2"
        )

    def test_split_result_is_list(self):
        self.assertEqual(
            run('parts = split("x,y", ",")\nsay type(parts)'), "list"
        )

    def test_join_with_separator(self):
        self.assertEqual(
            run('items = "a", "b", "c"\nsay join(items, " - ")'), "a - b - c"
        )

    def test_join_default_separator(self):
        self.assertEqual(run('items = "x", "y"\nsay join(items)'), "x, y")

    def test_upper_type_error(self):
        err = run_err('say upper(42)')
        self.assertIn("upper", err)
        self.assertIn("number", err)

    def test_replace_type_error(self):
        err = run_err('say replace(42, "x", "y")')
        self.assertIn("replace", err)


# ─────────────────────────────────────────────────────────────────────────────
# v0.5 built-ins — math
# ─────────────────────────────────────────────────────────────────────────────

class TestBuiltinMath(unittest.TestCase):

    def test_round_up(self):
        self.assertEqual(run('say round(3.7)'), "4")

    def test_round_down(self):
        self.assertEqual(run('say round(3.2)'), "3")

    def test_round_with_digits(self):
        self.assertEqual(run('say round(3.14159, 2)'), "3.14")

    def test_round_already_whole(self):
        self.assertEqual(run('say round(5)'), "5")

    def test_abs_negative(self):
        self.assertEqual(run('say abs(-10)'), "10")

    def test_abs_positive(self):
        self.assertEqual(run('say abs(10)'), "10")

    def test_abs_zero(self):
        self.assertEqual(run('say abs(0)'), "0")

    def test_min_two_values(self):
        self.assertEqual(run('say min(3, 7)'), "3")

    def test_min_list(self):
        self.assertEqual(run('nums = 5, 2, 9, 1\nsay min(nums)'), "1")

    def test_max_two_values(self):
        self.assertEqual(run('say max(3, 7)'), "7")

    def test_max_list(self):
        self.assertEqual(run('nums = 5, 2, 9, 1\nsay max(nums)'), "9")

    def test_abs_type_error(self):
        err = run_err('say abs("text")')
        self.assertIn("abs", err)

    def test_round_type_error(self):
        err = run_err('say round("text")')
        self.assertIn("round", err)


# ─────────────────────────────────────────────────────────────────────────────
# v0.5 built-ins — lists
# ─────────────────────────────────────────────────────────────────────────────

class TestBuiltinLists(unittest.TestCase):

    def test_first_basic(self):
        self.assertEqual(run('items = "a", "b", "c"\nsay first(items)'), "a")

    def test_last_basic(self):
        self.assertEqual(run('items = "a", "b", "c"\nsay last(items)'), "c")

    def test_first_single_item(self):
        self.assertEqual(run('items = "only", "other"\nsay first(items)'), "only")

    def test_sort_strings(self):
        src = 'items = "banana", "apple", "cherry"\nresult = sort(items)\nsay first(result)'
        self.assertEqual(run(src), "apple")

    def test_sort_numbers(self):
        self.assertEqual(run('nums = 5, 2, 9, 1\nresult = sort(nums)\nsay first(result)'), "1")

    def test_reverse_list(self):
        self.assertEqual(run('items = "a", "b", "c"\nrev = reverse(items)\nsay first(rev)'), "c")

    def test_reverse_does_not_modify_original(self):
        src = 'items = "a", "b", "c"\nrev = reverse(items)\nsay first(items)\n'
        self.assertEqual(run(src), "a")

    def test_sort_type_error(self):
        err = run_err('say sort("not a list")')
        self.assertIn("sort", err)

    def test_first_type_error(self):
        err = run_err('say first("not a list")')
        self.assertIn("first", err)


# ─────────────────────────────────────────────────────────────────────────────
# v0.5 built-ins — color
# ─────────────────────────────────────────────────────────────────────────────

class TestBuiltinColor(unittest.TestCase):

    def test_color_returns_plain_text_when_no_color(self):
        """With NO_COLOR set, color() returns the text unchanged."""
        import os
        old = os.environ.get("NO_COLOR")
        os.environ["NO_COLOR"] = "1"
        try:
            self.assertEqual(run('say color("red", "hello")'), "hello")
        finally:
            if old is None:
                os.environ.pop("NO_COLOR", None)
            else:
                os.environ["NO_COLOR"] = old

    def test_color_unknown_name_raises(self):
        err = run_err('say color("purple", "hi")')
        self.assertIn("purple", err)

    def test_color_bad_first_arg_raises(self):
        err = run_err('say color(42, "hi")')
        self.assertIn("color", err.lower())

    def test_color_valid_names_no_error(self):
        """All documented color names work without raising (plain text in NO_COLOR mode)."""
        import os
        old = os.environ.get("NO_COLOR")
        os.environ["NO_COLOR"] = "1"
        try:
            for name in ("red", "green", "yellow", "cyan", "bold", "dim"):
                out = run(f'say color("{name}", "test")')
                self.assertEqual(out, "test", f"color({name!r}) should return plain text")
        finally:
            if old is None:
                os.environ.pop("NO_COLOR", None)
            else:
                os.environ["NO_COLOR"] = old


# ─────────────────────────────────────────────────────────────────────────────

class TestBareVariableAssignment(unittest.TestCase):
    """Regression suite for bare variable assignment (a = b).
    These all work correctly — tests lock in the behaviour."""

    def test_global_bare_var_assign(self):
        self.assertEqual(run("x = 5\ny = x\nsay y"), "5")

    def test_assign_from_parameter(self):
        src = """
function test value
- copy = value
- return copy

say test(42)
"""
        self.assertEqual(run(src), "42")

    def test_assign_from_local_var(self):
        src = """
function f
- a = 1
- b = a
- return b

say f()
"""
        self.assertEqual(run(src), "1")

    def test_assign_inside_loop_in_function(self):
        src = """
function loopcopy
- a = 1
- b = 2
- loop b more than 0
-- a = b
-- b = b - 1
- return a

say loopcopy()
"""
        self.assertEqual(run(src), "1")

    def test_iterative_fib(self):
        """Iterative Fibonacci -- the exact case the user reported."""
        src = """
function fib n
- a = 0
- b = 1
- loop n more than 1
-- temp = a + b
-- a = b
-- b = temp
-- n = n - 1
- return b

say fib(7)
"""
        self.assertEqual(run(src), "13")


# ─────────────────────────────────────────────────────────────────────────────

class TestNothingLiteral(unittest.TestCase):

    def test_nothing_type(self):
        self.assertEqual(run("x = nothing\nsay type(x)"), "nothing")

    def test_nothing_is_falsy(self):
        self.assertEqual(run('x = nothing\nif x\n- say "yes"\nelse\n- say "no"'), "no")

    def test_nothing_display(self):
        self.assertEqual(run("x = nothing\nsay x"), "nothing")

    def test_nothing_is_not_nothing(self):
        self.assertEqual(run('x = nothing\nif x is not nothing\n- say "yes"\nelse\n- say "no"'), "no")

    def test_assign_nothing_then_update(self):
        self.assertEqual(run("x = nothing\nx = 42\nsay x"), "42")


# ─────────────────────────────────────────────────────────────────────────────

class TestFileIO(unittest.TestCase):

    def setUp(self):
        import tempfile, os
        self._tmpdir = tempfile.mkdtemp()
        self._tmp = os.path.join(self._tmpdir, "ixx_test.txt").replace("\\", "/")

    def tearDown(self):
        import shutil
        shutil.rmtree(self._tmpdir, ignore_errors=True)

    def test_write_and_read(self):
        src = f'write "{self._tmp}", "hello ixx"\ncontent = read("{self._tmp}")\nsay content'
        self.assertEqual(run(src), "hello ixx")

    def test_append(self):
        src = f'write "{self._tmp}", "hello"\nappend "{self._tmp}", " world"\ncontent = read("{self._tmp}")\nsay content'
        self.assertEqual(run(src), "hello world")

    def test_readlines_single_line(self):
        src = f'write "{self._tmp}", "one line"\nlines = readlines("{self._tmp}")\nsay count(lines)'
        self.assertEqual(run(src), "1")

    def test_exists_true(self):
        src = f'write "{self._tmp}", "x"\nsay exists("{self._tmp}")'
        self.assertEqual(run(src), "YES")

    def test_exists_false(self):
        path = self._tmp + "_missing.txt"
        self.assertEqual(run(f'say exists("{path}")'), "NO")

    def test_read_missing_raises(self):
        path = self._tmp + "_missing.txt"
        err = run_err(f'content = read("{path}")')
        self.assertIn("not found", err.lower())

    def test_write_bad_path_type_raises(self):
        err = run_err('write 99, "content"')
        self.assertIn("write", err.lower())

    def test_read_bad_path_type_raises(self):
        err = run_err("content = read(42)")
        self.assertIn("read", err.lower())

    def test_exists_bad_path_type_raises(self):
        err = run_err("say exists(42)")
        self.assertIn("exists", err.lower())

    def test_append_creates_file(self):
        """append creates the file if it does not exist."""
        path = self._tmp + "_new.txt"
        src = f'append "{path}", "created"\ncontent = read("{path}")\nsay content'
        self.assertEqual(run(src), "created")

    def test_write_bool_true_displays_YES(self):
        src = f'write "{self._tmp}", YES\ncontent = read("{self._tmp}")\nsay content'
        self.assertEqual(run(src), "YES")

    def test_write_bool_false_displays_NO(self):
        src = f'write "{self._tmp}", NO\ncontent = read("{self._tmp}")\nsay content'
        self.assertEqual(run(src), "NO")

    def test_write_nothing_displays_nothing(self):
        src = f'write "{self._tmp}", nothing\ncontent = read("{self._tmp}")\nsay content'
        self.assertEqual(run(src), "nothing")

    def test_append_bool_displays_YES(self):
        src = f'write "{self._tmp}", "start:"\nappend "{self._tmp}", YES\ncontent = read("{self._tmp}")\nsay content'
        self.assertEqual(run(src), "start:YES")

    def test_append_nothing_displays_nothing(self):
        src = f'write "{self._tmp}", "val="\nappend "{self._tmp}", nothing\ncontent = read("{self._tmp}")\nsay content'
        self.assertEqual(run(src), "val=nothing")


# ─────────────────────────────────────────────────────────────────────────────

class TestTryCatch(unittest.TestCase):

    def test_catch_receives_error_variable(self):
        src = 'try\n- x = number("abc")\ncatch\n- say error'
        out = run(src)
        self.assertIn("abc", out)

    def test_no_error_catch_not_executed(self):
        src = 'try\n- x = 1\ncatch\n- say "should not print"'
        self.assertEqual(run(src), "")

    def test_try_without_catch_swallows_error(self):
        src = 'try\n- x = number("abc")\nsay "after"'
        self.assertEqual(run(src), "after")

    def test_execution_continues_after_catch(self):
        src = 'try\n- x = number("abc")\ncatch\n- say "caught"\nsay "done"'
        self.assertEqual(run(src), "caught\ndone")

    def test_execution_continues_after_silent_try(self):
        src = 'try\n- x = number("abc")\nsay "done"'
        self.assertEqual(run(src), "done")

    def test_predeclared_var_updated_in_try(self):
        src = 'result = 0\ntry\n- result = 42\ncatch\n- say "error"\nsay result'
        self.assertEqual(run(src), "42")

    def test_predeclared_nothing_updated_in_try(self):
        src = 'result = nothing\ntry\n- result = 42\ncatch\n- say "error"\nsay result'
        self.assertEqual(run(src), "42")

    def test_catch_file_not_found(self):
        src = 'try\n- x = read("no_file_ixx_test_99.txt")\ncatch\n- say "missing"'
        self.assertEqual(run(src), "missing")

    def test_error_interpolation_in_catch(self):
        src = 'try\n- x = number("bad")\ncatch\n- say "err: {error}"'
        out = run(src)
        self.assertTrue(out.startswith("err:"))
        self.assertIn("bad", out)

    def test_nested_try(self):
        src = (
            'outer = "ok"\n'
            'try\n'
            '- try\n'
            '-- x = number("abc")\n'
            '- catch\n'
            '-- outer = "inner caught"\n'
            'say outer'
        )
        self.assertEqual(run(src), "inner caught")


if __name__ == "__main__":
    unittest.main()
