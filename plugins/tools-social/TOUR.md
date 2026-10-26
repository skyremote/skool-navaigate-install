# Tour: module 12, tools: social

`/aios learn 12 tools-social` follows these steps, one at a time. Show the real output, then check it.
Never post or schedule during the tour unless the member gives a release time.

## Step 1: Find the command
- **Command:** `tools-social --version`
- **They should see:** `tools-social 2.0.0`.

## Step 2: A checked practice pack
- **Command:** `tools-social sample ~/Social-practice`, then `tools-social check ~/Social-practice/northwind_posts_v1.json`
- **They should see:** `PASS`.

## Step 3: The gate says no
- **Command:** `echo '{"tool_name":"mcp__blotato__blotato_create_post","tool_input":{}}' | tools-social gate`
- **They should see:** `deny` and "When should this go live?".

## Step 4: "Approved" is not a time
- **Command:** `tools-social release now --words "I love it, go ahead"`
- **They should see:** `READY, not released`.

## Step 5: Connect Blotato
- **Do:** Blotato account, social accounts connected, key in the plugin settings (or Codex/Cursor MCP entry).
- **Check:** the agent lists their accounts with the Blotato tools.

## Step 6: Their first scheduled post
- **Do:** prompt 2 from prompts.md with a real source.
- **They should see:** both posts, a `PASS`, then after their time: local and UTC time, and Blotato's receipt.
- **Check:** the post shows in Blotato's calendar at that time.

## Recap
Check the copy, give a time, then post. Approval is never a time.
