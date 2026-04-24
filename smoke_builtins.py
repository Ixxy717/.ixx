from ixx.parser import parse
from ixx.interpreter import Interpreter, IXXRuntimeError
import io, sys

def _run(src):
    ast = parse(src)
    buf = io.StringIO()
    old = sys.stdout
    sys.stdout = buf
    try:
        Interpreter().run(ast)
    finally:
        sys.stdout = old
    return buf.getvalue()

cases = [
    ('say upper("hello")', "HELLO\n"),
    ('say lower("WORLD")', "world\n"),
    ('say trim("  hi  ")', "hi\n"),
    ('say replace("hello world", "world", "there")', "hello there\n"),
    ('words = split("a,b,c", ",")\nsay count(words)', "3\n"),
    ('items = "x", "y", "z"\nsay join(items, " - ")', "x - y - z\n"),
    ("say round(3.7)", "4\n"),
    ("say abs(-5)", "5\n"),
    ("say min(3, 7)", "3\n"),
    ("say max(3, 7)", "7\n"),
    ('nums = 5, 2, 9, 1\nfirst_sorted = first(sort(nums))\nsay first_sorted', "1\n"),
    ('items = "c", "b", "a"\nrev = reverse(items)\nsay first(rev)', "a\n"),
    ('z = "x", "y", "z"\nsay last(z)', "z\n"),
]

all_ok = True
for src, expected in cases:
    out = _run(src)
    status = "OK" if out == expected else f"FAIL (got {out!r}, want {expected!r})"
    if "FAIL" in status:
        all_ok = False
    print(f"{status}: {src[:55].replace(chr(10), ' / ')}")

print()
print("All OK" if all_ok else "FAILURES ABOVE")
