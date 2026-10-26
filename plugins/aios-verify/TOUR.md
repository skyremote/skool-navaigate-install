# Tour: module 8, make it verifiable

`/aios learn 8` follows these steps in the member's own project folder, one at a time.
Run each command for the member, or have them type it. Show the real output, then check it before the next step.
Never overwrite their files and never weaken a test to make a check pass. If a check fails, fix that one thing.

## Step 1: Find the command
- **Do:** check that the pack's command runs.
- **Command:** `aios-verify --version` (Codex or Cursor: `~/.local/bin/aios-verify --version`).
- **They should see:** `aios-verify 2.0.0`.
- **Check:** exit code 0. If it is missing, run `export PATH="$HOME/.local/bin:$PATH"`, or in Claude Code run
  `/aios install aios-verify`, then `/reload-plugins`.

## Step 2: Pick the project
- **Do:** choose a project with tests. If they have none, copy the sample app and make it a git repository.
- **Command:** `cp -R <pack>/examples/sample-app ~/acme-prices && cd ~/acme-prices && git init -q && git add -A && git commit -qm Start`
- **They should see:** `prices.py`, `test_prices.py`, `build.py`.
- **Check:** `python3 -m unittest` prints `OK`.

## Step 3: Preview the set-up
- **Do:** show what would be written, without writing.
- **Command:** `aios-verify init --dry-run`
- **They should see:** `Would write` lines for `.aios/verify.json`, `.claude/skills/verify/SKILL.md`, `REVIEW.md`
  and `.github/pull_request_template.md`.
- **Check:** `ls -A` shows nothing new yet.

## Step 4: Set it up
- **Do:** write the files. Add the git hook if they also use Codex or Cursor.
- **Command:** `aios-verify init` (or `aios-verify init --git-hook`)
- **They should see:** `Wrote` for new files and `Kept existing` for anything already there.
- **Check:** `cat .aios/verify.json` shows their real test and build commands. Edit any `run` line that is wrong.

## Step 5: Run every check
- **Do:** run the checks the agent will run.
- **Command:** `aios-verify run`
- **They should see:** `PASS` for tests, build and screenshot, and `3 of 3 checks passed`.
- **Check:** exit code 0. Open `.aios/screenshot.png` and say what it shows. If the screenshot fails, install
  Chrome or set `AIOS_VERIFY_BROWSER`, or mark that check `"gate": false`.

## Step 6: Try the three hard rules
- **Do:** ask the hook what it would do, without running anything.
- **Command:** `aios-verify try "git push --force"`, `aios-verify try "vercel --prod"`, `aios-verify try "git status"`
- **They should see:** `DENY`, `ASK`, `ALLOW`.
- **Check:** they can say which rule each one hit. Add their own deploy command to `production_commands` in
  `.aios/verify.json` and try it.

## Step 7: Break a test on purpose
- **Do:** change one line so a test fails.
- **Command:** `sed -i.bak 's/{:02d}/{:d}/' prices.py && rm prices.py.bak` (sample app), then `aios-verify run`
- **They should see:** `FAIL  tests` with `'£0.5' != '£0.05'` and `1 of 3 checks passed` or similar.
- **Check:** exit code 1.

## Step 8: Watch the gate stop the agent
- **Do:** commit the broken line, then ask the agent for an unrelated change and tell it not to test.
- **Command:** `git commit -qam "A bug slips in" --no-verify`, then open `claude` in the folder and type
  "Change the Business cards price to 9999 pence. Do not run the tests, just finish."

- **They should see:** the agent try to finish, get `AIOS verify gate (attempt 1 of 3)` with the test output,
  fix the real bug, and finish with every check passing.
- **Check:** `aios-verify run` passes and `git diff` shows the price change and the restored `{:02d}`.

## Step 9: Write the pull request
- **Do:** ask for a PR description with the `pr-ready` skill.
- **Command:** in Claude Code, "get this ready for review".
- **They should see:** What changed, Testing with real output, Risk (low, medium or high) and How to revert.
- **Check:** the Testing section quotes the real `aios-verify run` output, and the risk matches `REVIEW.md`.

## Step 10: Commit with the verify skill
- **Do:** ask Claude Code to commit. It runs the project's `verify` skill first.
- **Command:** in Claude Code, "commit this".
- **They should see:** the verify skill run, then the commit.
- **Check:** `git log --oneline -1` shows the commit. Then `/aios` to mark module 8 done.
