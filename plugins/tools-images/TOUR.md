# Tour: module 12, tools: images

`/aios learn 12 tools-images` follows these steps, one at a time. Show the real output, then check it.
Never spend credits during the tour without the member's go.

## Step 1: Find the command
- **Command:** `tools-images --version`, then `tools-images doctor`
- **They should see:** what is installed, signed in and missing.

## Step 2: Install Higgsfield
- **Command:** the CLI install line, `higgsfield auth login`, then `npx skills add higgsfield-ai/skills`.
- **Check:** `tools-images doctor` says all three are ready.

## Step 3: The prompt shape (free)
- **Command:** `tools-images sample ~/Images-practice`, then `tools-images check ~/Images-practice/northwind-cake_video-prompt_v1.txt --seconds 10`
- **They should see:** `PASS`.

## Step 4: See it fail
- **Do:** change SHOT 3's start to 0:06 and add the word "stunning". Check again.
- **They should see:** the gap and the hype word, with the fix for each.

## Step 5: One test image
- **Do:** one image from their own product photo, after they say go.
- **Command:** then `tools-images log <folder> --prompt <file> --model <model> --job <id>`.
- **Check:** the manifest has the entry.

## Recap
Brief, prompt, check, cost, go, generate, log, look.
