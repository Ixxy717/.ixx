say color("cyan", "IXX Tough Showcase")
say color("dim", "Same file. Bigger stress.")
say "--------------------------------"

project = "IXX"
version = "0.6.8"
owner = "Ixxy"

function line
- say color("dim", "--------------------------------")

function section name
- line
- say color("bold", name)
- line

function add a, b
- return a + b

function sub a, b
- return a - b

function mul a, b
- return a * b

function makewords
- words = "alpha", "bravo", "charlie", "delta", "echo", "ixx"
- return words

function describelist items
- amount = count(items)
- sorteditems = sort(items)
- sortedtext = join(sorteditems, " / ")
- reverseditems = reverse(sorteditems)
- reversedtext = join(reverseditems, " / ")
- firstitem = first(sorteditems)
- lastitem = last(sorteditems)
- say "Count: {amount}"
- say "Sorted: {sortedtext}"
- say "Reversed: {reversedtext}"
- say "First: {firstitem}"
- say "Last: {lastitem}"
- if items contains "ixx"
-- say color("green", "contains check passed")

function triangular n
- total = 0
- loop n more than 0
-- total = total + n
-- n = n - 1
- return total

function factorial n
- if n at most 1
-- return 1
- previous = factorial(n - 1)
- return n * previous

function fib n
- if n at most 0
-- return 0
- a = 0
- b = 1
- loop n more than 1
-- temp = a + b
-- a = b
-- b = temp
-- n = n - 1
- return b

function scorelabel score
- if score at least 95
-- return color("green", "elite")
- if score at least 85
-- return color("cyan", "strong")
- if score at least 70
-- return color("yellow", "usable")
- return color("red", "rough")

function calculatescore base, bonus, penalty
- boosted = add(base, bonus)
- final = sub(boosted, penalty)
- return final

function shadowtest input
- project = "LOCAL PROJECT"
- version = "LOCAL VERSION"
- say "Inside project: {project}"
- say "Inside version: {version}"
- return input

function noreturn
- say "No-return function executed"

function nothinggate
- empty = noreturn()
- if not empty
-- return color("green", "good: nothing acted falsy")
- return color("red", "bad fallback")

function makereport ownername, projectname
- cleanowner = trim(ownername)
- cleanproject = trim(projectname)
- ownertext = upper(cleanowner)
- projecttext = upper(cleanproject)
- parts = ownertext, projecttext, "REPORT"
- result = join(parts, "-")
- return result

function pipeline textvalue
- cleaned = trim(textvalue)
- lowered = lower(cleaned)
- swapped = replace(lowered, "computer", "machine")
- loud = upper(swapped)
- return loud

function listmath nums
- smallest = min(nums)
- biggest = max(nums)
- ordered = sort(nums)
- orderedtext = join(ordered, ", ")
- flipped = reverse(ordered)
- flippedtext = join(flipped, ", ")
- say "Smallest: {smallest}"
- say "Biggest: {biggest}"
- say "Ordered: {orderedtext}"
- say "Flipped: {flippedtext}"

function runcountdown n
- loop n more than 0
-- say "T-minus {n}"
-- n = n - 1
- return "launch"

function repeatedtext word, times
- output = ""
- loop times more than 0
-- output = output + word
-- times = times - 1
- return output

section "Identity"

say "Project: {project}"
say "Version: {version}"
say "Owner: {owner}"

report = makereport(owner, project)
say "Report name: {report}"

section "Text pipeline"

raw = "  the computer should learn the user  "
processed = pipeline(raw)
say "Raw: {raw}"
say "Processed: {processed}"

section "Lists"

words = makewords()
describelist words

splititems = split("red,green,blue,yellow", ",")
splitjoined = join(splititems, " -> ")
say "Split joined: {splitjoined}"

section "Math"

nums = 42, 7, 13, 99, 1, 7
listmath nums

tri = triangular(10)
say "Triangular 10: {tri}"

fact = factorial(7)
say "Factorial 7: {fact}"

fibbed = fib(9)
say "Fib 9: {fibbed}"

score = calculatescore(80, 12, 5)
label = scorelabel(score)
say "Score: {score}"
say "Label: {label}"

rounded = round(3.14159265, 3)
positive = abs(-123)
say "Rounded pi-ish: {rounded}"
say "Absolute: {positive}"

section "Scope"

shadowresult = shadowtest("shadow returned cleanly")
say "Shadow result: {shadowresult}"
say "Outside project: {project}"
say "Outside version: {version}"

section "Nothing"

nothingresult = nothinggate()
say "Nothing gate: {nothingresult}"

empty = noreturn()
emptytype = type(empty)
say "Empty value: {empty}"
say "Empty type: {emptytype}"

section "Countdown"

launch = runcountdown(3)
say "Countdown result: {launch}"

section "Types"

wordstype = type(words)
scoretype = type(score)
reporttype = type(report)
say "Words type: {wordstype}"
say "Score type: {scoretype}"
say "Report type: {reporttype}"

section "String building"

repeated = repeatedtext("IXX ", 3)
cleanrepeated = trim(repeated)
say "Repeated: {cleanrepeated}"

section "Final"

if words contains "ixx"
- say color("green", "IXX survived the tougher showcase.")

say color("cyan", "Done.")