# Tour: module 12, tools: WhatsApp

`/aios learn 12 tools-whatsapp` follows these steps, one at a time. Show the real output, then check it.
Never send a message during the tour. Never copy chat text anywhere outside the member's Mac.

## Step 1: Find the command
- **Command:** `tools-whatsapp --version`, then `tools-whatsapp doctor`
- **They should see:** macOS, the WhatsApp app and whatscribe, each found or with its install line.

## Step 2: Practise
- **Command:** `tools-whatsapp sample ~/WhatsApp-practice`, then `tools-whatsapp extract ~/WhatsApp-practice/transcript.jsonl`
- **They should see:** two amounts, the dates and times, each with its sender.

## Step 3: Install whatscribe
- **Command:** the clone and install lines, `whatscribe setup`, `whatscribe permissions`.
- **Check:** `whatscribe doctor` passes.

## Step 4: First sync
- **Command:** `whatscribe sync` (repeat until no voice notes are pending).
- **Check:** `ls ~/Documents/whatscribe/<chat>` shows `transcript.md` and `transcript.jsonl`.

## Step 5: Their own question
- **Do:** prompt 2 from prompts.md with a real chat.
- **Check:** every figure has a quote they can find in WhatsApp.

## Recap
Archive locally, sync, find, extract, quote. Sending is theirs, confirmed each time.
