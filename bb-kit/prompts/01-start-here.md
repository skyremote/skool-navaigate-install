# Module 1 · Start here: prompts

Paste one prompt at a time into a new Claude chat in bb, opened on your AIOS folder. Run them in order. If a prompt has lines marked "edit", change them to your own details first. Each prompt sets something up, checks it, and shows you the result.

These prompts are instructions to Claude. They also work in Claude Code in a terminal, opened in the same folder.

## Prompt 1.1 · Install BB Overlay and walk me through Set up

**What it does:** Installs BB Overlay, NavAIgate's free front end for bb (Home, the run-sheet sidebar, Kanban, to-dos, voice and five mods), and tells you the Set up steps.

**How you know it worked:** The installer's checklist ends with every line ticked, and Home shows the Set up wizard after you reload bb.

~~~text
Install BB Overlay from github.com/skyremote/bb-overlay using its install script. Show me what it will do first, then run it, then walk me through Set up one step at a time.

Here is how:
1. Show me the plan without changing anything: run `curl -fsSL https://raw.githubusercontent.com/skyremote/bb-overlay/main/install.sh | bash -s -- --dry-run` and give me its list of steps in plain words.
2. Run the real install: `curl -fsSL https://raw.githubusercontent.com/skyremote/bb-overlay/main/install.sh | bash`. It installs bb plugins, which live outside this folder: I allow that for this one command, so if the sandbox blocks it, run it outside the sandbox. It can take a few minutes. If a step times out, run the same command again: it is safe to re-run and keeps what is already there.
3. Show me its final checklist. Run `bb plugin list` and confirm that `navaigate-workspace`, `kanban`, `helper-desk`, `cache-clock`, `reflect` and `screen-share` are running.
4. Tell me to reload bb (Cmd+R on a Mac), open Home and follow the Set up wizard. Explain its steps in plain words: my first name, two to five areas of my work, and optional keys for my own tools. Every key is optional; I can skip them all today.
5. Tell me that BB Overlay is free for my own business, and that I must not resell or repackage it.

Ground rules: work only in this folder unless a step names another one. Never delete or overwrite my files: if a file already exists, keep it and tell me. Never print or ask for a key, token or password. Show real command output, never a guess. If a step fails, show the error, fix that one cause if you can, and run the check again. If a step below must write outside this folder (for example to Claude's settings, `~/.local` or a folder the step names), I allow exactly that command: if the sandbox blocks it, run it outside the sandbox. Do not stop to ask me anything unless a step needs my decision.

When you are done, show me the result:
1. Write a one-page HTML report to `80_aios/reports/m01-bb-overlay_v1.html` (create the folder if needed; if that file exists, use the next free `_vN` and use that name below). Put in it: what you set up, a table of every check (the command, a short piece of its real output, PASS or FAIL) and my one next step. Keep it simple: no web fonts, scripts or internet links.
2. If the `BB_THREAD_ID` environment variable is set, you are in bb. Then put `::inline-vis{file="80_aios/reports/m01-bb-overlay_v1.html"}` on its own line in your final reply, outside any code block. Then move this chat to the Review lane: run `bb thread section list --json`, create a section called Review with `bb thread section create Review` if there is none, and run `bb thread update --self --section <the Review id>`.
3. End with at most five plain lines: what works, what failed, and the one thing I do next.
~~~

## Prompt 1.2 · Add the AIOS course to bb and show me where I start

**What it does:** Adds the AIOS start pack for Claude Code (and Codex if you have it), the AIOS course page in your bb sidebar and every course prompt in bb's Prompt Library, then shows where you stand.

**How you know it worked:** The report shows the installer's OK lines, `aios-guide next` naming module 1, and the AIOS course page listed in bb.

~~~text
Add the YOUR AIOS course to my bb, for this folder, and tell me where I am.

Here is how:
1. Run the AIOS step of the starter kit for this folder: `curl -fsSL https://raw.githubusercontent.com/skyremote/skool-navaigate-install/main/bb-kit/install.sh | bash -s -- --folder "$PWD"`. It adds the `navaigate-aios` marketplace, installs the start pack `aios`, keeps the bb project this chat is in, adds the "AIOS course" page to the bb sidebar and saves every course prompt in bb's Prompt Library. It writes outside this folder: I allow that for this one command, so if the sandbox blocks it, run it outside the sandbox. Show me its OK, SKIP and FAIL lines.
2. Until I restart Claude, call the start pack's command by its full path: `"$(ls -d "${CLAUDE_CONFIG_DIR:-$HOME/.claude}"/plugins/cache/navaigate-aios/aios/*/bin | tail -1)/aios-guide"`. Below, `aios-guide` means that full path.
3. Run `aios-guide next`. Tell me which harness I am in, which packs are installed and my next module.
4. Run `aios-guide list`. Show the modules as a short table: module, pack, installed yes or no.
5. Run `ls -A` in this folder. Tell me whether it is empty, halfway (it already has an AGENTS.md, a CLAUDE.md or project files) or already running. Change nothing.
6. Run `aios-guide verify aios`. It must print a line that starts with `OK aios`.
7. Tell me where to find the prompts from now on: "AIOS course" in the bb sidebar, or Ctrl+R in any chat box and type AIOS.

Do not record module 1 as complete. I will do that myself once I am happy.

Ground rules: work only in this folder unless a step names another one. Never delete or overwrite my files: if a file already exists, keep it and tell me. Never print or ask for a key, token or password. Show real command output, never a guess. If a step fails, show the error, fix that one cause if you can, and run the check again. If a step below must write outside this folder (for example to Claude's settings, `~/.local` or a folder the step names), I allow exactly that command: if the sandbox blocks it, run it outside the sandbox. Do not stop to ask me anything unless a step needs my decision.

When you are done, show me the result:
1. Write a one-page HTML report to `80_aios/reports/m01-start-here_v1.html` (create the folder if needed; if that file exists, use the next free `_vN` and use that name below). Put in it: what you set up, a table of every check (the command, a short piece of its real output, PASS or FAIL) and my one next step. Keep it simple: no web fonts, scripts or internet links.
2. If the `BB_THREAD_ID` environment variable is set, you are in bb. Then put `::inline-vis{file="80_aios/reports/m01-start-here_v1.html"}` on its own line in your final reply, outside any code block. Then move this chat to the Review lane: run `bb thread section list --json`, create a section called Review with `bb thread section create Review` if there is none, and run `bb thread update --self --section <the Review id>`.
3. End with at most five plain lines: what works, what failed, and the one thing I do next.
~~~

## Prompt 1.3 · Install the whole AIOS in one go (optional)

**What it does:** Installs every core pack for modules 2 to 11 at once, then proves each one.

**How you know it worked:** The report shows one `OK` line per core pack, and tells you to start a new chat so the new commands load.

~~~text
Install the whole AIOS framework now, not one pack at a time, and prove each pack works.

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
