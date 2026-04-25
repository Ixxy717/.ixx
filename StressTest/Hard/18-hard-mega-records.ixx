use "Modules/asserts.ixx"
use "Modules/Mega/records.ixx"

say color("cyan", "hard 18 mega records")
assert "make record clamp high", make_record("Ixxy Buckles", 999), "ixxy-buckles:100"
assert "make record clamp low", make_record("Ixxy Buckles", -1), "ixxy-buckles:0"
assert "status excellent", record_status(95), "excellent"
assert "status good", record_status(75), "good"
assert "status ok", record_status(55), "ok"
assert "status low", record_status(30), "low"
say color("green", "hard 18 complete")
