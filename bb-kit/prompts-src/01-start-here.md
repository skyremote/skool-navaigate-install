# 01 · Start here
pack: aios
cmd: aios-guide

## 1.1 · Install BB Overlay and walk me through Set up
what: Installs BB Overlay, NavAIgate's free front end for bb (Home, the run-sheet sidebar, Kanban, to-dos, voice and five mods), and tells you the Set up steps.
check: The installer's checklist ends with every line ticked, and Home shows the Set up wizard after you reload bb.
~~~
Install BB Overlay from github.com/skyremote/bb-overlay using its install script. Show me what it will do first, then run it, then walk me through Set up one step at a time.

Here is how:
1. Show me the plan without changing anything: run `curl -fsSL https://raw.githubusercontent.com/skyremote/bb-overlay/main/install.sh | bash -s -- --dry-run` and give me its list of steps in plain words.
2. Run the real install: `curl -fsSL https://raw.githubusercontent.com/skyremote/bb-overlay/main/install.sh | bash`. It installs bb plugins, which live outside this folder: I allow that for this one command, so if the sandbox blocks it, run it outside the sandbox. It can take a few minutes. If a step times out, run the same command again: it is safe to re-run and keeps what is already there.
3. Show me its final checklist. Run `bb plugin list` and confirm that `navaigate-workspace`, `kanban`, `helper-desk`, `cache-clock`, `reflect` and `screen-share` are running.
4. Tell me to reload bb (Cmd+R on a Mac), open Home and follow the Set up wizard. Explain its steps in plain words: my first name, two to five areas of my work, and optional keys for my own tools. Every key is optional; I can skip them all today.
5. Tell me that BB Overlay is free for my own business, and that I must not resell or repackage it.

<<RULES>>

<<FINISH m01-bb-overlay>>
~~~

## 1.2 · Add the AIOS course to bb and show me where I start
what: Adds the AIOS start pack for Claude Code (and Codex if you have it), the AIOS course page in your bb sidebar and every course prompt in bb's Prompt Library, then shows where you stand.
check: The report shows the installer's OK lines, `aios-guide next` naming module 1, and the AIOS course page listed in bb.
~~~
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

<<RULES>>

<<FINISH m01-start-here>>
~~~

## 1.3 · Install the whole AIOS in one go (optional)
what: Installs every core pack for modules 2 to 11 at once, then proves each one.
check: The report shows one `OK` line per core pack, and tells you to start a new chat so the new commands load.
~~~
Install the whole AIOS framework now, not one pack at a time, and prove each pack works.

<<INSTALL>>

1. Run `aios-guide install aios-complete`. It installs the start pack, the memory pack and every core pack for modules 2 to 11.
2. For each pack it installed, run `aios-guide verify <pack>` and keep the line it prints.
3. Run `aios-guide list` and show which packs are now installed.
4. Do not install the shelf packs (module 12). I will add those when I need them.

Tell me plainly that I must start a new chat (or type `/reload-plugins` in Claude Code) before the new commands load.

<<RULES>>

<<FINISH m01-install-everything>>
~~~
