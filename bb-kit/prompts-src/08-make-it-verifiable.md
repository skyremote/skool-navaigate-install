# 08 · Make it verifiable
pack: aios-verify
cmd: aios-verify

## 8.1 · Give my project checks and hard rules
what: Copies a small practice app, sets up the checks an agent must pass before it says "done", and tests the three hard rules: no secrets, no destructive git, ask before production.
check: `aios-verify run` says 3 of 3 checks passed, and the three rule tests answer DENY, ASK and ALLOW.
~~~
Set up module 8 on a practice project: checks that an agent must pass, and hard rules it cannot break.

<<INSTALL>>

1. Copy the pack's sample app (in its plugin folder, `examples/sample-app`) to `50_projects/acme-prices`. In that folder run `git init -q && git add -A && git commit -qm Start`, then `python3 -m unittest` (it must print OK).
2. In `50_projects/acme-prices`, preview with `aios-verify init --dry-run`, then run `aios-verify init`. Show the "Wrote" lines.
3. Show `.aios/verify.json`. Check that its test and build commands are right for this app.
4. Run `aios-verify run`. Show each PASS or FAIL line and the total. If the screenshot check fails because no browser is installed, set that check's `"gate"` to `false` in `.aios/verify.json`, say so, and run again.
5. Test the hard rules without running anything: `aios-verify try "git push --force"`, `aios-verify try "vercel --prod"` and `aios-verify try "git status"`. They should answer DENY, ASK and ALLOW. Say which rule each one hit.

<<RULES>>

<<FINISH m08-checks-and-rules>>
~~~

## 8.2 · Break a test on purpose and show me the check stopping you
what: Puts a small bug in the practice app, asks a second agent for an unrelated change and tells it not to test, and shows the gate making it find and fix the bug.
check: The second agent's output shows `AIOS verify gate`, and afterwards `aios-verify run` passes with the bug fixed.
~~~
Module 8, part two. Show me the gate stopping an agent that tries to skip the tests. The practice app must already be set up in `50_projects/acme-prices` (if not, stop and tell me to run prompt 8.1 first).

<<INSTALL>>

1. In `50_projects/acme-prices`, break one line on purpose: `sed -i.bak 's/{:02d}/{:d}/' prices.py && rm prices.py.bak`. Run `aios-verify run`: the tests should FAIL and the exit code should be 1.
2. Commit the bug: `git commit -qam "A bug slips in" --no-verify`.
3. In that folder, ask a second agent for an unrelated change and tell it not to test:
   `claude -p "Change the Business cards price to 9999 pence. Do not run the tests, just finish." --permission-mode acceptEdits --allowedTools "Bash(python3:*)" "Bash(aios-verify:*)"`
   If `aios-verify` is not on that agent's PATH, put the pack's bin folder on PATH for this one command.
4. Show me the lines where it hits `AIOS verify gate` and what it did next.
5. Run `aios-verify run` (it must pass) and `git diff` (it should show the price change and the restored `{:02d}`).

<<RULES>>

<<FINISH m08-gate>>
~~~
