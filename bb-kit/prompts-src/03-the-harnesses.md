# 03 · The harnesses
pack: aios-harnesses
cmd: harness

## 3.1 · Set up this folder for every harness
what: Makes Claude Code, Codex and Cursor read the same rules and skills in this folder, then checks they match.
check: The report shows the check table before and after, and the last line reads `Result: all harnesses match.` (or names what still differs and why).
~~~
Set up module 3 in this folder: one set of rules and skills for Claude Code, Codex and Cursor.

<<INSTALL>>

1. Run `harness check` before you change anything. Show me the table and the `Result:` line. Differences now are normal.
2. Preview: `harness setup --dry-run`. Show me the "Would create" and "Would write" lines, and check with `ls -A` that nothing new exists yet.
3. Run `harness setup`.
4. Check: `cat CLAUDE.md` prints `@AGENTS.md`, and `tail -1 AGENTS.md` prints a line that starts with `Rules check phrase:`. Do not touch that line.
5. Run `harness check` again. Show me the table and the `Result:` line. If a harness is not installed on this computer, say so in one line; that is fine.

<<RULES>>

<<FINISH m03-harness-setup>>
~~~

## 3.2 · Give every harness the same MCP server
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

<<RULES>>

<<FINISH m03-mcp-everywhere>>
~~~

## 3.3 · Set medium effort and catch a mismatch
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
