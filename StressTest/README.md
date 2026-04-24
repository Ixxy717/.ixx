# IXX StressTest

Run:

StressTest\run-all.cmd

What this does:

- Runs each positive `.ixx` stress test separately.
- Runs `ixx check` before running each positive test.
- Continues after failures.
- Runs `ExpectedFailures` and counts them as passing only if they fail.
- Creates temporary files under `StressTest/tmp`.

This is not a replacement for Python unit tests. It is an end-to-end CLI stress suite for the installed `ixx` command.
