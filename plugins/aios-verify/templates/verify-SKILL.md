---
name: verify
description: Prove a change works before it is called done or committed, by running this project's tests, build and screenshot. Use before every commit and whenever someone asks to verify, check or test a change.
---

# Verify this project

Claude Code runs a project skill named `verify` right before each commit (docs and
test-only changes excepted). Keep the steps exact and the evidence real.

1. Run every check from `.aios/verify.json`:
   ```
   aios-verify run
   ```
   It prints PASS or FAIL for each check (tests, build, screenshot) and the last lines of any failure.
2. If a check fails, read the output, fix the cause (never the test's expectation unless the
   requirement changed), and run `aios-verify run` again.
3. If the project has a page or screen, open the screenshot the run saved
   (`.aios/screenshot.png`) and look at it. Say what you see.
4. Report in this shape, with the real output:
   - Tests: <PASS/FAIL, count>
   - Build: <PASS/FAIL>
   - Screenshot: <path, and one line on what it shows, or "not applicable">
5. Never say "done", "fixed" or "working" while a check fails. Say which check fails and why.
