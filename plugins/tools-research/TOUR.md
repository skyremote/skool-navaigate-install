# Tour: module 12, tools: research

`/aios learn 12 tools-research` follows these steps, one at a time. Show the real output, then check it.

## Step 1: Find the command
- **Command:** `tools-research --version` then `tools-research doctor`
- **They should see:** papers and Substack ready; Reddit needs their app.

## Step 2: Papers (free)
- **Command:** `tools-research papers "<a topic from their work>" --n 3`
- **They should see:** three papers with DOI links.

## Step 3: A newsletter (free)
- **Command:** `tools-research substack archive <a newsletter they read> --n 3`
- **They should see:** three posts with dates, paid ones marked.

## Step 4: Their Reddit app
- **Do:** reddit.com/prefs/apps, "create another app", type script. Save the id and secret in the plugin settings
  (or the two shell variables).
- **Command:** `tools-research reddit search "<topic>" --n 3`
- **They should see:** three threads with scores.

## Step 5: The ledger
- **Command:** `tools-research sample ~/Research-practice`, then `tools-research check ~/Research-practice/bakery-ordering_ledger_practice_v1.md`
- **They should see:** `PASS`. Change one confidence to "certain" and check again: `FAIL`.

## Step 6: A real question
- **Do:** prompt 1 from prompts.md with their own question.
- **Check:** the ledger passes, and they open two links to confirm they say what the ledger says.

## Recap
Papers, newsletters, Reddit on your own app, one ledger, honest labels, checked.
