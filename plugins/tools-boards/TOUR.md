# Tour: module 12, tools: boards

`/aios learn 12 tools-boards` follows these steps, one at a time. Show the real output, then check it.
Never ask for a token. BluPlai signs the member in through the browser.

## Step 1: Find the command
- **Command:** `tools-boards --version`
- **They should see:** `tools-boards 2.0.0`.

## Step 2: Validate a practice scene
- **Command:** `tools-boards sample ~/Boards-practice`, then the `validate` line it prints with `--strict`.
- **They should see:** `"ready": true` and no warnings.

## Step 3: See a warning
- **Do:** change one card's height to 50 in the JSON and validate again.
- **They should see:** an error about the minimum height. Change it back.

## Step 4: Connect BluPlai
- **Do:** ask "list my BluPlai boards". The browser opens BluPlai's sign-in once.
- **Check:** the agent lists their boards (or says there are none yet).

## Step 5: Build the practice board
- **Do:** prompt 1 from prompts.md.
- **Check:** they open the link, press Shift+1 to fit, and drag one card.

## Step 6: A real one
- **Do:** prompt 2 with a transcript from their own call.
- **Check:** quotes are real, owners are named in the call, there is room to write back.

## Recap
Plan, validate, write, read back, look at it zoomed to fit.
