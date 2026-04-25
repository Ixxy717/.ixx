# Every builtin called inside functions

function text_pipeline input
- u = upper(input)
- l = lower(input)
- t = trim("  " + input + "  ")
- r = replace(input, "o", "0")
- parts = split(input)
- rejoined = join(parts, "-")
- say u + " | " + l + " | " + r + " | " + rejoined
- return count(parts)

function number_pipeline x
- r = round(x, 2)
- a = abs(x)
- n = number(text(x))
- say "round=" + r + " abs=" + a + " roundtrip=" + n
- return r

function list_pipeline lst
- f = first(lst)
- la = last(lst)
- s = sort(lst)
- rv = reverse(lst)
- c = count(lst)
- say "first=" + f + " last=" + la + " count=" + c
- say "sorted: " + join(s, ",") + "  reversed: " + join(rv, ",")
- return c

function math_pipeline a, b
- mn = min(a, b)
- mx = max(a, b)
- say "min=" + mn + " max=" + mx + " abs_diff=" + abs(a - b)
- return mx

function type_pipeline x
- t = type(x)
- disp = text(x)
- say t + ": " + disp
- return t

wc = text_pipeline("Hello World foo bar")
say "Word count: " + wc

nr = number_pipeline(-3.7)
say "Number result: " + nr

data = 5, 2, 8, 1, 9, 3
lc = list_pipeline(data)
say "List size: " + lc

mp = math_pipeline(10, 3)
say "Math max: " + mp

type_pipeline(42)
type_pipeline("hello")
type_pipeline(YES)
type_pipeline(nothing)
