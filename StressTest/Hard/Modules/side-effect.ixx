write "StressTest/tmp/hard-import-side-effect-should-not-exist.txt", "BAD"

function side_effect_safe
- return "SAFE"
