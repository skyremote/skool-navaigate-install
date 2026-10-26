# Tour: module 3, the harnesses

Run this inside your own AIOS folder. Each step says what to do, the command, what you should see, and how to check it.
Use `harness` in a terminal, Codex or Cursor. In Claude Code, the same tool is `"${CLAUDE_PLUGIN_ROOT}/bin/harness"`.

## Step 1. See where you start
- Do: run the check before you change anything.
- Command: `harness check`
- You should see: a table with rows for rules, skills and MCP servers, one column per harness, and a "What differs" list.
- Check: the last line starts with `Result:`. Differences now are normal.

## Step 2. Look at the plan
- Do: preview the setup. Nothing is written yet.
- Command: `harness setup --dry-run`
- You should see: lines that start with "Would create" or "Would write".
- Check: `ls` shows no new files yet.

## Step 3. Set up the folder
- Do: create the rules bridge, the MCP list and the skill links.
- Command: `harness setup`
- You should see: "Created AGENTS.md" (only if you had none), "Created CLAUDE.md with the one line @AGENTS.md", "Created .aios/mcp.json".
- Check: `cat CLAUDE.md` prints `@AGENTS.md`, and `tail -1 AGENTS.md` prints a line starting `Rules check phrase:`.

## Step 4. Fill in AGENTS.md
- Do: open AGENTS.md and replace the text in brackets with your business, your folders and your never rules.
- Command: `open AGENTS.md` (or open it in your editor)
- You should see: four short sections and the check phrase at the end. Leave the phrase line alone.
- Check: `wc -l AGENTS.md` is well under 200.

## Step 5. Add one MCP server to every harness
- Do: add a server you already use. Keep any key in your shell, never in the file.
- Command: `harness mcp add <name> -- <command> [args]` or, with a key, `harness mcp add <name> --env 'MY_TOKEN=${MY_TOKEN}' -- <command> [args]`
- You should see: "Added ... to .aios/mcp.json" and three "Wrote" lines (`.mcp.json`, `.cursor/mcp.json`, `.codex/config.toml`).
- Check: `harness mcp list` shows the server.

## Step 6. Approve it in each harness
- Do: open Claude Code in the folder and approve the server; open Codex in the folder and trust it.
- Command: `claude` then `/mcp`, and `codex`
- You should see: the server listed as connected (Claude Code) and the folder trusted (Codex).
- Check: `claude mcp list`, `codex mcp list` and `cursor-agent mcp list` each show the server.

## Step 7. Set up Grok Bot by hand
- Do: print the Grok Bot steps, follow them in the app, and save its answer to the probe.
- Command: `harness grok`
- You should see: the rules step, each server's name and command (or URL), and a probe question.
- Check: `.aios/grok-bot.txt` exists and holds Grok Bot's whole answer.

## Step 8. Prove they match
- Do: run the check again.
- Command: `harness check`
- You should see: OK in every rules, skills and MCP cell (WARN is fine), and Grok Bot's column filled in.
- Check: the last line reads `Result: all harnesses match.` and `echo $?` prints 0.

## Step 9. Fix one deliberate mismatch
- Do: give Cursor a rule the others never see, check, then fix it.
- Command: `echo "- Use American spelling." > .cursorrules`, then `harness check`, then `rm .cursorrules`, then `harness check`
- You should see: DIFF under Cursor naming `.cursorrules` the first time, and "all harnesses match" the second time.
- Check: the first check exits 1, the second exits 0.

## Step 10. Set your defaults
- Do: see each harness's model and effort, then set medium effort for this folder.
- Command: `harness defaults`, then `harness defaults --apply`
- You should see: one row per harness, then "Set effortLevel = medium" and "Set model_reasoning_effort = medium".
- Check: `harness defaults` now shows medium for Claude Code and Codex.

## Keep it true
After any change to AGENTS.md, a skill or an MCP server, run `harness check`. Then type `/aios` for module 4.
