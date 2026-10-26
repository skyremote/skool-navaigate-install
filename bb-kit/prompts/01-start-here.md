# Module 1 · Start here: prompts

Paste one prompt at a time into a new Claude chat in bb, opened on your AIOS folder. Run them in order. If a prompt has lines marked "edit", change them to your own details first. Each prompt sets something up, checks it, and shows you the result.

These prompts are instructions to Claude. They also work in Claude Code in a terminal, opened in the same folder.

## Prompt 1.1 · Install the AIOS and see where you start

**What it does:** Installs the start pack, reads what this computer already has, and shows the twelve modules with your next step.

**How you know it worked:** The report lists the modules, says `aios` is installed, and names module 1 as your next module.

~~~text
I am starting YOUR AIOS 2.0 in this folder. Set up the start pack and show me where I stand.

Step 0, get the pack. These commands change Claude's own plugin folder in my home folder, outside this folder. I allow that for these commands only: if the sandbox blocks them, run them outside the sandbox. Run `claude plugin marketplace list`. If `navaigate-aios` is not listed, run `claude plugin marketplace add skyremote/skool-navaigate-install`. Then run `claude plugin install aios@navaigate-aios` ("already installed" is fine; it also brings the start pack `aios`). Until I restart Claude, call the pack's command by its full path: `"$(ls -d "${CLAUDE_CONFIG_DIR:-$HOME/.claude}"/plugins/cache/navaigate-aios/aios/*/bin | tail -1)/aios-guide"`. Below, `aios-guide` means that full path.

1. Run `aios-guide next`. Tell me which harness I am in, which packs are installed and my next module.
2. Run `aios-guide list`. Show the modules as a short table: module, pack, installed yes or no.
3. Run `aios-guide find set up my brain`. Check that the first line names `aios-brain`.
4. Run `ls -A` in this folder. Tell me whether it is empty, halfway (it already has an AGENTS.md, a CLAUDE.md or project files) or already running. Change nothing.
5. Run `aios-guide verify aios`. It must print a line that starts with `OK aios`.

Do not record module 1 as complete. I will do that myself once I am happy.

Ground rules: work only in this folder unless a step names another one. Never delete or overwrite my files: if a file already exists, keep it and tell me. Never print or ask for a key, token or password. Show real command output, never a guess. If a step fails, show the error, fix that one cause if you can, and run the check again. If a step below must write outside this folder (for example to Claude's settings, `~/.local` or a folder the step names), I allow exactly that command: if the sandbox blocks it, run it outside the sandbox. Do not stop to ask me anything unless a step needs my decision.

When you are done, show me the result:
1. Write a one-page HTML report to `80_aios/reports/m01-start-here_v1.html` (create the folder if needed; if that file exists, use the next free `_vN` and use that name below). Put in it: what you set up, a table of every check (the command, a short piece of its real output, PASS or FAIL) and my one next step. Keep it simple: no web fonts, scripts or internet links.
2. If the `BB_THREAD_ID` environment variable is set, you are in bb. Then put `::inline-vis{file="80_aios/reports/m01-start-here_v1.html"}` on its own line in your final reply, outside any code block. Then move this chat to the Review lane: run `bb thread section list --json`, create a section called Review with `bb thread section create Review` if there is none, and run `bb thread update --self --section <the Review id>`.
3. End with at most five plain lines: what works, what failed, and the one thing I do next.
~~~

## Prompt 1.2 · Install the whole AIOS in one go (optional)

**What it does:** Installs every core pack for modules 2 to 11 at once, then proves each one.

**How you know it worked:** The report shows one `OK` line per core pack, and tells you to restart Claude so the new commands load.

~~~text
I want the whole AIOS framework installed now, not one pack at a time.

Step 0, get the pack. These commands change Claude's own plugin folder in my home folder, outside this folder. I allow that for these commands only: if the sandbox blocks them, run them outside the sandbox. Run `claude plugin marketplace list`. If `navaigate-aios` is not listed, run `claude plugin marketplace add skyremote/skool-navaigate-install`. Then run `claude plugin install aios@navaigate-aios` ("already installed" is fine; it also brings the start pack `aios`). Until I restart Claude, call the pack's command by its full path: `"$(ls -d "${CLAUDE_CONFIG_DIR:-$HOME/.claude}"/plugins/cache/navaigate-aios/aios/*/bin | tail -1)/aios-guide"`. Below, `aios-guide` means that full path.

1. Run `aios-guide install aios-complete`. It installs the start pack, the memory pack and every core pack for modules 2 to 11.
2. For each pack it installed, run `aios-guide verify <pack>` and keep the line it prints.
3. Run `aios-guide list` and show which packs are now installed.
4. Do not install the shelf packs (module 12). I will add those when I need them.

Tell me plainly that I must start a new chat (or type `/reload-plugins` in Claude Code) before the new commands load.

Ground rules: work only in this folder unless a step names another one. Never delete or overwrite my files: if a file already exists, keep it and tell me. Never print or ask for a key, token or password. Show real command output, never a guess. If a step fails, show the error, fix that one cause if you can, and run the check again. If a step below must write outside this folder (for example to Claude's settings, `~/.local` or a folder the step names), I allow exactly that command: if the sandbox blocks it, run it outside the sandbox. Do not stop to ask me anything unless a step needs my decision.

When you are done, show me the result:
1. Write a one-page HTML report to `80_aios/reports/m01-install-everything_v1.html` (create the folder if needed; if that file exists, use the next free `_vN` and use that name below). Put in it: what you set up, a table of every check (the command, a short piece of its real output, PASS or FAIL) and my one next step. Keep it simple: no web fonts, scripts or internet links.
2. If the `BB_THREAD_ID` environment variable is set, you are in bb. Then put `::inline-vis{file="80_aios/reports/m01-install-everything_v1.html"}` on its own line in your final reply, outside any code block. Then move this chat to the Review lane: run `bb thread section list --json`, create a section called Review with `bb thread section create Review` if there is none, and run `bb thread update --self --section <the Review id>`.
3. End with at most five plain lines: what works, what failed, and the one thing I do next.
~~~
