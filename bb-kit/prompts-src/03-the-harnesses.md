# 03 · The harnesses
pack: aios-harnesses
cmd: harness

## 3.1 · Check my harnesses and set them all up on this folder
what: Makes Claude Code, Codex and Cursor read the same rules and skills in this folder, then checks they match.
check: The report shows the check table before and after, and the last line reads `Result: all harnesses match.` (or names what still differs and why).
~~~
Check which of Claude Code, Codex and Cursor I have installed and signed in, tell me how to add the missing ones to bb, then set this folder up so they all read the same rules and skills.

<<INSTALL>>

1. Make a three-row table: Claude Code, Codex, Cursor. For each, check whether it is installed (`claude --version`, `codex --version`, `cursor-agent --version`) and signed in (`codex login status`; for Claude, this chat proves it). Where one is missing, give me the one next step to add it, and say that bb lists it in its model picker once it is installed and signed in.
2. Run `harness check` before you change anything. Show me the table and the `Result:` line. Differences now are normal.
3. Preview: `harness setup --dry-run`. Show me the "Would create" and "Would write" lines, and check with `ls -A` that nothing new exists yet.
4. Run `harness setup`.
5. Check: `cat CLAUDE.md` prints `@AGENTS.md`, and `tail -1 AGENTS.md` prints a line that starts with `Rules check phrase:`. Do not touch that line.
6. Run `harness check` again. Show me the table and the `Result:` line. If a harness is not installed on this computer, say so in one line; that is fine.

<<RULES>>

<<FINISH m03-harness-setup>>
~~~

## 3.2 · Ask Claude, Codex and Cursor the same question
what: Starts three bb threads in this folder, one per harness, asks each the same question, and compares their answers in one table.
check: Three new threads appear in the bb sidebar, and the report holds one table with an answer from each harness that is signed in.
~~~
Ask Claude, Codex and Cursor the same question in three threads: what are the three biggest risks in this folder? Then compare their answers in one table.

Here is how:
1. Run `bb provider list` and note which of `claude-code`, `codex` and `acp-cursor` are listed. Use only those. If one is not signed in, its thread will fail; then say so and carry on with the others.
2. Write the question to `80_aios/ask/risks_v1.md`: "Read this folder and list the three biggest risks you see, one line each. Do not change any file."
3. For each harness, start a thread in this bb project: `bb thread spawn --project "$BB_PROJECT_ID" --provider <id> --title "Risks: <harness>" --prompt-file 80_aios/ask/risks_v1.md --json`. Keep each thread id.
4. Wait for each one with `bb thread wait <id> --timeout 10m`, then read its answer with `bb thread output <id>`.
5. Compare the answers in one table: harness, risk 1, risk 2, risk 3. Then add one line on where they agree and one on where they differ.

<<RULES>>

<<FINISH m03-same-question>>
~~~

## 3.3 · Give every harness the same tool connection
what: Adds one MCP server (a tool connection for the agents) to Claude Code, Codex and Cursor at once, from one list.
check: `harness mcp list` shows the server, and the report shows the three files it wrote, one per harness.
~~~
Add one MCP server to every harness in this folder. Use the free "memory" example server; I can swap it for my own later.

<<INSTALL>>

1. Run `harness mcp add memory -- npx -y @modelcontextprotocol/server-memory`.
2. Show me the "Added" line and the three "Wrote" lines (`.mcp.json`, `.cursor/mcp.json`, `.codex/config.toml`).
3. Run `harness mcp list` and show that `memory` is there.
4. Run `harness check` and show the MCP row.
5. Tell me exactly what I do myself to approve it, because an agent cannot do this for me: in Claude Code type `/mcp` and approve `memory`; open Codex in this folder and trust the folder.
6. Tell me in one line how to add a server that needs a key, without putting the key in a file: `harness mcp add <name> --env 'MY_TOKEN=${MY_TOKEN}' -- <command>`.
7. Explain in plain words how I would connect Grok Bot to my own tools with a custom MCP server (`harness grok` prints its steps), and list what it should and should not be allowed to touch. Keep it to five short lines.

<<RULES>>

<<FINISH m03-mcp-everywhere>>
~~~

## 3.4 · Set medium effort and catch a mismatch (optional)
what: Sets medium effort as the default for this folder, then breaks and repairs the match on purpose so you see the check work.
check: `harness defaults` shows medium, the check fails while the stray file exists, and passes again after it is removed.
~~~
Finish module 3 in this folder: set sensible defaults, then show me that the check catches a mismatch.

<<INSTALL>>

1. Run `harness defaults` and show me the model and effort for each harness.
2. Run `harness defaults --apply`. Show the "Set ..." lines, then run `harness defaults` again: Claude Code and Codex should show medium.
3. Show me the check catching a mismatch. Create a Cursor-only rule with `echo "- Use American spelling." > .cursorrules`. Run `harness check` and show the DIFF line and the exit code (`echo $?`, it should be 1).
4. Remove only that file you just created: `rm .cursorrules`. Run `harness check` again and show the exit code (it should be 0).

<<RULES>>

<<FINISH m03-defaults-and-drill>>
~~~
