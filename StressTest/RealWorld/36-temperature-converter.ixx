# Temperature converter: Celsius list to Fahrenheit and back

function c_to_f celsius
- return celsius * 9 / 5 + 32

function f_to_c fahrenheit
- return (fahrenheit - 32) * 5 / 9

function temp_label temp_f
- if temp_f at least 100
-- return "Very Hot"
- if temp_f at least 80
-- return "Hot"
- if temp_f at least 60
-- return "Warm"
- if temp_f at least 40
-- return "Cool"
- if temp_f at least 32
-- return "Freezing"
- return "Below Freezing"

celsius_temps = -40, -10, 0, 15, 20, 25, 37, 100

say "Celsius -> Fahrenheit:"
loop each c in celsius_temps
- f = round(c_to_f(c), 1)
- label = temp_label(f)
- say "  " + c + "C = " + f + "F  (" + label + ")"

say "---"
say "Roundtrip checks:"
say "  Boiling: " + round(f_to_c(212), 1) + "C"
say "  Freezing: " + round(f_to_c(32), 1) + "C"
say "  Body temp: " + round(f_to_c(98.6), 1) + "C"

if round(c_to_f(100)) is 212
- say "PASS: boiling point"
if round(c_to_f(0)) is 32
- say "PASS: freezing point"
