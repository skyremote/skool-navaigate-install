# Module 3 · The harnesses: prompts

Paste one prompt at a time into a new Claude chat in bb, opened on your AIOS folder. Run them in order. If a prompt has lines marked "edit", change them to your own details first. Each prompt sets something up, checks it, and shows you the result.

These prompts are instructions to Claude. They also work in Claude Code in a terminal, opened in the same folder.

## Prompt 3.1 · Check my harnesses and set them all up on this folder

**What it does:** Makes Claude Code, Codex and Cursor read the same rules and skills in this folder, then checks they match.

**How you know it worked:** The report shows the check table before and after, and the last line reads `Result: all harnesses match.` (or names what still differs and why).

~~~text
Check which of Claude Code, Codex and Cursor I have installed and signed in, tell me how to add the missing ones to bb, then set this folder up so they all read the same rules and skills.

Step 0, get the pack. These commands change Claude's own plugin folder in my home folder, outside this folder. I allow that for these commands only: if the sandbox blocks them, run them outside the sandbox. Run `claude plugin marketplace list`. If `navaigate-aios` is not listed, run `claude plugin marketplace add skyremote/skool-navaigate-install`. Then run `claude plugin install aios-harnesses@navaigate-aios` ("already installed" is fine; it also brings the start pack `aios`). Until I restart Claude, call the pack's command by its full path: `"$(ls -d "${CLAUDE_CONFIG_DIR:-$HOME/.claude}"/plugins/cache/navaigate-aios/aios-harnesses/*/bin | tail -1)/harness"`. Below, `harness` means that full path.

1. Make a three-row table: Claude Code, Codex, Cursor. For each, check whether it is installed (`claude --version`, `codex --version`, `cursor-agent --version`) and signed in (`codex login status`; for Claude, this chat proves it). Where one is missing, give me the one next step to add it, and say that bb lists it in its model picker once it is installed and signed in.
2. Run `harness check` before you change anything. Show me the table and the `Result:` line. Differences now are normal.
3. Preview: `harness setup --dry-run`. Show me the "Would create" and "Would write" lines, and check with `ls -A` that nothing new exists yet.
4. Run `harness setup`.
5. Check: `cat CLAUDE.md` prints `@AGENTS.md`, and `tail -1 AGENTS.md` prints a line that starts with `Rules check phrase:`. Do not touch that line.
6. Run `harness check` again. Show me the table and the `Result:` line. If a harness is not installed on this computer, say so in one line; that is fine.

Ground rules: work only in this folder unless a step names another one. Never delete or overwrite my files: if a file already exists, keep it and tell me. Never print or ask for a key, token or password. Show real command output, never a guess. If a step fails, show the error, fix that one cause if you can, and run the check again. If a step below must write outside this folder (for example to Claude's settings, `~/.local` or a folder the step names), I allow exactly that command: if the sandbox blocks it, run it outside the sandbox. Do not stop to ask me anything unless a step needs my decision.

When you are done, show me the result:
1. Write a one-page HTML report to `80_aios/reports/m03-harness-setup_v1.html` (create the folder if needed; if that file exists, use the next free `_vN` and use that name below). Put in it: what you set up, a table of every check (the command, a short piece of its real output, PASS or FAIL) and my one next step. Keep it simple: no web fonts, scripts or internet links.
2. If the `BB_THREAD_ID` environment variable is set, you are in bb. Then put `::inline-vis{file="80_aios/reports/m03-harness-setup_v1.html"}` on its own line in your final reply, outside any code block. Then move this chat to the Review lane: run `bb thread section list --json`, create a section called Review with `bb thread section create Review` if there is none, and run `bb thread update --self --section <the Review id>`.
3. End with at most five plain lines: what works, what failed, and the one thing I do next.
~~~

## Prompt 3.2 · Ask Claude, Codex and Cursor the same question

**What it does:** Starts three bb threads in this folder, one per harness, asks each the same question, and compares their answers in one table.

**How you know it worked:** Three new threads appear in the bb sidebar, and the report holds one table with an answer from each harness that is signed in.

~~~text
Ask Claude, Codex and Cursor the same question in three threads: what are the three biggest risks in this folder? Then compare their answers in one table.

Here is how:
1. Run `bb provider list` and note which of `claude-code`, `codex` and `acp-cursor` are listed. Use only those. If one is not signed in, its thread will fail; then say so and carry on with the others.
2. Write the question to `80_aios/ask/risks_v1.md`: "Read this folder and list the three biggest risks you see, one line each. Do not change any file."
3. For each harness, start a thread in this bb project: `bb thread spawn --project "$BB_PROJECT_ID" --provider <id> --title "Risks: <harness>" --prompt-file 80_aios/ask/risks_v1.md --json`. Keep each thread id.
4. Wait for each one with `bb thread wait <id> --timeout 10m`, then read its answer with `bb thread output <id>`.
5. Compare the answers in one table: harness, risk 1, risk 2, risk 3. Then add one line on where they agree and one on where they differ.

Ground rules: work only in this folder unless a step names another one. Never delete or overwrite my files: if a file already exists, keep it and tell me. Never print or ask for a key, token or password. Show real command output, never a guess. If a step fails, show the error, fix that one cause if you can, and run the check again. If a step below must write outside this folder (for example to Claude's settings, `~/.local` or a folder the step names), I allow exactly that command: if the sandbox blocks it, run it outside the sandbox. Do not stop to ask me anything unless a step needs my decision.

When you are done, show me the result:
1. Write a one-page HTML report to `80_aios/reports/m03-same-question_v1.html` (create the folder if needed; if that file exists, use the next free `_vN` and use that name below). Put in it: what you set up, a table of every check (the command, a short piece of its real output, PASS or FAIL) and my one next step. Keep it simple: no web fonts, scripts or internet links.
2. If the `BB_THREAD_ID` environment variable is set, you are in bb. Then put `::inline-vis{file="80_aios/reports/m03-same-question_v1.html"}` on its own line in your final reply, outside any code block. Then move this chat to the Review lane: run `bb thread section list --json`, create a section called Review with `bb thread section create Review` if there is none, and run `bb thread update --self --section <the Review id>`.
3. End with at most five plain lines: what works, what failed, and the one thing I do next.
~~~

## Prompt 3.3 · Give every harness the same tool connection

**What it does:** Adds one MCP server (a tool connection for the agents) to Claude Code, Codex and Cursor at once, from one list.

**How you know it worked:** `harness mcp list` shows the server, and the report shows the three files it wrote, one per harness.

~~~text
Add one MCP server to every harness in this folder. Use the free "memory" example server; I can swap it for my own later.

Step 0, get the pack. These commands change Claude's own plugin folder in my home folder, outside this folder. I allow that for these commands only: if the sandbox blocks them, run them outside the sandbox. Run `claude plugin marketplace list`. If `navaigate-aios` is not listed, run `claude plugin marketplace add skyremote/skool-navaigate-install`. Then run `claude plugin install aios-harnesses@navaigate-aios` ("already installed" is fine; it also brings the start pack `aios`). Until I restart Claude, call the pack's command by its full path: `"$(ls -d "${CLAUDE_CONFIG_DIR:-$HOME/.claude}"/plugins/cache/navaigate-aios/aios-harnesses/*/bin | tail -1)/harness"`. Below, `harness` means that full path.

1. Run `harness mcp add memory -- npx -y @modelcontextprotocol/server-memory`.
2. Show me the "Added" line and the three "Wrote" lines (`.mcp.json`, `.cursor/mcp.json`, `.codex/config.toml`).
3. Run `harness mcp list` and show that `memory` is there.
4. Run `harness check` and show the MCP row.
5. Tell me exactly what I do myself to approve it, because an agent cannot do this for me: in Claude Code type `/mcp` and approve `memory`; open Codex in this folder and trust the folder.
6. Tell me in one line how to add a server that needs a key, without putting the key in a file: `harness mcp add <name> --env 'MY_TOKEN=${MY_TOKEN}' -- <command>`.
7. Explain in plain words how I would connect Grok Bot to my own tools with a custom MCP server (`harness grok` prints its steps), and list what it should and should not be allowed to touch. Keep it to five short lines.

Ground rules: work only in this folder unless a step names another one. Never delete or overwrite my files: if a file already exists, keep it and tell me. Never print or ask for a key, token or password. Show real command output, never a guess. If a step fails, show the error, fix that one cause if you can, and run the check again. If a step below must write outside this folder (for example to Claude's settings, `~/.local` or a folder the step names), I allow exactly that command: if the sandbox blocks it, run it outside the sandbox. Do not stop to ask me anything unless a step needs my decision.

When you are done, show me the result:
1. Write a one-page HTML report to `80_aios/reports/m03-mcp-everywhere_v1.html` (create the folder if needed; if that file exists, use the next free `_vN` and use that name below). Put in it: what you set up, a table of every check (the command, a short piece of its real output, PASS or FAIL) and my one next step. Keep it simple: no web fonts, scripts or internet links.
2. If the `BB_THREAD_ID` environment variable is set, you are in bb. Then put `::inline-vis{file="80_aios/reports/m03-mcp-everywhere_v1.html"}` on its own line in your final reply, outside any code block. Then move this chat to the Review lane: run `bb thread section list --json`, create a section called Review with `bb thread section create Review` if there is none, and run `bb thread update --self --section <the Review id>`.
3. End with at most five plain lines: what works, what failed, and the one thing I do next.
~~~

## Prompt 3.4 · Set medium effort and catch a mismatch (optional)

**What it does:** Sets medium effort as the default for this folder, then breaks and repairs the match on purpose so you see the check work.

**How you know it worked:** `harness defaults` shows medium, the check fails while the stray file exists, and passes again after it is removed.

~~~text
Finish module 3 in this folder: set sensible defaults, then show me that the check catches a mismatch.

Step 0, get the pack. These commands change Claude's own plugin folder in my home folder, outside this folder. I allow that for these commands only: if the sandbox blocks them, run them outside the sandbox. Run `claude plugin marketplace list`. If `navaigate-aios` is not listed, run `claude plugin marketplace add skyremote/skool-navaigate-install`. Then run `claude plugin install aios-harnesses@navaigate-aios` ("already installed" is fine; it also brings the start pack `aios`). Until I restart Claude, call the pack's command by its full path: `"$(ls -d "${CLAUDE_CONFIG_DIR:-$HOME/.claude}"/plugins/cache/navaigate-aios/aios-harnesses/*/bin | tail -1)/harness"`. Below, `harness` means that full path.

1. Run `harness defaults` and show me the model and effort for each harness.
2. Run `harness defaults --apply`. Show the "Set ..." lines, then run `harness defaults` again: Claude Code and Codex should show medium.
3. Show me the check catching a mismatch. Create a Cursor-only rule with `echo "- Use American spelling." > .cursorrules`. Run `harness check` and show the DIFF line and the exit code (`echo $?`, it should be 1).
4. Remove only that file you just created: `rm .cursorrules`. Run `harness check` again and show the exit code (it should be 0).

Ground rules: work only in this folder unless a step names another one. Never delete or overwrite my files: if a file already exists, keep it and tell me. Never print or ask for a key, token or password. Show real command output, never a guess. If a step fails, show the error, fix that one cause if you can, and run the check again. If a step below must write outside this folder (for example to Claude's settings, `~/.local` or a folder the step names), I allow exactly that command: if the sandbox blocks it, run it outside the sandbox. Do not stop to ask me anything unless a step needs my decision.

When you are done, show me the result:
1. Write a one-page HTML report to `80_aios/reports/m03-defaults-and-drill_v1.html` (create the folder if needed; if that file exists, use the next free `_vN` and use that name below). Put in it: what you set up, a table of every check (the command, a short piece of its real output, PASS or FAIL) and my one next step. Keep it simple: no web fonts, scripts or internet links.
2. If the `BB_THREAD_ID` environment variable is set, you are in bb. Then put `::inline-vis{file="80_aios/reports/m03-defaults-and-drill_v1.html"}` on its own line in your final reply, outside any code block. Then move this chat to the Review lane: run `bb thread section list --json`, create a section called Review with `bb thread section create Review` if there is none, and run `bb thread update --self --section <the Review id>`.
3. End with at most five plain lines: what works, what failed, and the one thing I do next.
~~~
