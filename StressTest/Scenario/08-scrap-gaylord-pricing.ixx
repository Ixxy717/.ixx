use "Modules/asserts.ixx"
use "Modules/inventory.ixx"
use "Modules/reports.ixx"

section "scenario 08 scrap gaylord pricing"

path = "StressTest/tmp/scenario-08-gaylord-pricing.txt"
report_start "Gaylord Pricing", path

gl1 = "GL-A100"
gl2 = "GL-B200"
gl3 = "GL-C300"

pounds1 = 820
pounds2 = 610
pounds3 = 450

rate_low = 0.10
rate_mid = 0.18
rate_high = 0.32

value1 = gaylord_value(pounds1, rate_low)
value2 = gaylord_value(pounds2, rate_mid)
value3 = gaylord_value(pounds3, rate_high)

total_value = round(value1 + value2 + value3, 2)
total_weight = pounds1 + pounds2 + pounds3
avg_rate = round(total_value / total_weight, 2)

label1 = container_label(gl1, "mixed telecom boxes", pounds1)
label2 = container_label(gl2, "adapter wire", pounds2)
label3 = container_label(gl3, "high grade boards", pounds3)

report_add path, gl1, value1
report_add path, gl2, value2
report_add path, gl3, value3
report_add path, "total_value", total_value
report_add path, "avg_rate", avg_rate
report_add path, "label1", label1
report_add path, "label2", label2
report_add path, "label3", label3
final = report_finish(path)

assert "value1", value1, 82
assert "value2", value2, 109.8
assert "value3", value3, 144
assert "total value", total_value, 335.8
assert "avg rate", avg_rate, 0.18
assert "label includes GL", contains_line(label1, "GL-A100"), YES
assert "report contains high grade", contains_line(final, "high grade boards"), YES

done "scenario 08 complete"
