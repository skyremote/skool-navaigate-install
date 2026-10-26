# Module 11 · Ship it to others: prompts

Paste one prompt at a time into a new Claude chat in bb, opened on your AIOS folder. Run them in order. If a prompt has lines marked "edit", change them to your own details first. Each prompt sets something up, checks it, and shows you the result.

These prompts are instructions to Claude. They also work in Claude Code in a terminal, opened in the same folder.

## Prompt 11.1 · Turn my skill into a plugin someone else can install

**What it does:** Packages one of your skills as a plugin (a pack) with tests, three eval cases and an installer, then validates it.

**How you know it worked:** `ship-pack check` ends with `0 error(s)`, the tests print OK and `claude plugin validate` says `Validation passed`.

~~~text
Set up module 11: package one of my skills so someone else can install it.

My name for the pack's author line (edit this line): Sam Lee

Step 0, get the pack. These commands change Claude's own plugin folder in my home folder, outside this folder. I allow that for these commands only: if the sandbox blocks them, run them outside the sandbox. Run `claude plugin marketplace list`. If `navaigate-aios` is not listed, run `claude plugin marketplace add skyremote/skool-navaigate-install`. Then run `claude plugin install aios-ship@navaigate-aios` ("already installed" is fine; it also brings the start pack `aios`). Until I restart Claude, call the pack's command by its full path: `"$(ls -d "${CLAUDE_CONFIG_DIR:-$HOME/.claude}"/plugins/cache/navaigate-aios/aios-ship/*/bin | tail -1)/ship-pack"`. Below, `ship-pack` means that full path.

1. Find a skill to package: list the folders in `~/.claude/skills` (or `$CLAUDE_CONFIG_DIR/skills`) that hold a SKILL.md. Pick the smallest one. If I have none, create a small practice skill `meeting-actions` in `~/.claude/skills/meeting-actions/SKILL.md` that turns meeting notes into actions with an owner and a due date.
2. Make a home for my packs: `mkdir -p ~/my-tools && cd ~/my-tools && git init` (skip `git init` if it is already a repository). Work in `~/my-tools` from now on.
3. Run `ship-pack from-skill <the skill folder> --author "<my name>"`. If it stops because it found a key or a personal path, show me the file and line, and stop.
4. Run `ship-pack check <name>`. It lists placeholders. Fill them: the three cases in `evals/` (a real request, an edge case and one it must refuse; each grader pattern is a word the right answer always contains) and the README's names.
5. Run `ship-pack check <name>` until it ends with `0 error(s)`.
6. Run `python3 -m unittest discover <name>/tests` (it must print OK) and `claude plugin validate <name> --strict` (it must say `Validation passed`).

For this task only: work only in this folder unless a step names another one. Never delete or overwrite my files: if a file already exists, keep it and tell me. Never print or ask for a key, token or password. Show real command output, never a guess. If a step fails, show the error, fix that one cause if you can, and run the check again. If a step below must write outside this folder (for example to Claude's settings, `~/.local` or a folder the step names), I allow exactly that command: if the sandbox blocks it, run it outside the sandbox. Do not stop to ask me anything unless a step needs my decision.

When you are done, show me the result:
1. Write a one-page HTML report to `80_aios/reports/m11-make-pack_v1.html` (create the folder if needed; if that file exists, use the next free `_vN` and use that name below). Put in it: what you set up, a table of every check (the command, a short piece of its real output, PASS or FAIL) and my one next step. Keep it simple: no web fonts, scripts or internet links.
2. If the `BB_THREAD_ID` environment variable is set, you are in bb. Then put `::inline-vis{file="80_aios/reports/m11-make-pack_v1.html"}` on its own line in your final reply, outside any code block. Then move this chat to the Review lane: run `bb thread section list --json`, create a section called Review with `bb thread section create Review` if there is none, and run `bb thread update --self --section <the Review id>`.
3. End with at most five plain lines: what works, what failed, and the one thing I do next.
~~~

## Prompt 11.2 · Install my plugin as a stranger would

**What it does:** Lists your pack in your own marketplace, installs it into an empty test home folder as a new user would, and checks it is enabled.

**How you know it worked:** The test install says `Successfully installed`, the pack shows as enabled at 0.1.0, and the test home is removed afterwards.

~~~text
Module 11, part two. Prove my pack installs for a stranger. The pack must already exist in `~/my-tools` (if not, stop and tell me to run prompt 11.1 first).

Step 0, get the pack. These commands change Claude's own plugin folder in my home folder, outside this folder. I allow that for these commands only: if the sandbox blocks them, run them outside the sandbox. Run `claude plugin marketplace list`. If `navaigate-aios` is not listed, run `claude plugin marketplace add skyremote/skool-navaigate-install`. Then run `claude plugin install aios-ship@navaigate-aios` ("already installed" is fine; it also brings the start pack `aios`). Until I restart Claude, call the pack's command by its full path: `"$(ls -d "${CLAUDE_CONFIG_DIR:-$HOME/.claude}"/plugins/cache/navaigate-aios/aios-ship/*/bin | tail -1)/ship-pack"`. Below, `ship-pack` means that full path.

1. In `~/my-tools`, run `ship-pack marketplace <name> --file .claude-plugin/marketplace.json --name my-tools --owner "<the author name in the pack>"`, then `claude plugin validate .`, then `git add . && git commit -m "<name> 0.1.0"`.
2. Make an empty test home: `mkdir -p /tmp/new-member`. Run the next commands with `env -u CLAUDE_CONFIG_DIR HOME=/tmp/new-member` in front, so they use that empty home:
   `claude plugin marketplace add ~/my-tools`, then `claude plugin install <name>@my-tools`, then `claude plugin list`.
3. Show me `Successfully installed` and the pack listed as enabled at 0.1.0.
4. Remove only the test home you just made: `rm -rf /tmp/new-member`.
5. Tell me how others install it once I push `~/my-tools` to GitHub: `/plugin marketplace add <github-name>/my-tools`.

For this task only: work only in this folder unless a step names another one. Never delete or overwrite my files: if a file already exists, keep it and tell me. Never print or ask for a key, token or password. Show real command output, never a guess. If a step fails, show the error, fix that one cause if you can, and run the check again. If a step below must write outside this folder (for example to Claude's settings, `~/.local` or a folder the step names), I allow exactly that command: if the sandbox blocks it, run it outside the sandbox. Do not stop to ask me anything unless a step needs my decision.

When you are done, show me the result:
1. Write a one-page HTML report to `80_aios/reports/m11-stranger-install_v1.html` (create the folder if needed; if that file exists, use the next free `_vN` and use that name below). Put in it: what you set up, a table of every check (the command, a short piece of its real output, PASS or FAIL) and my one next step. Keep it simple: no web fonts, scripts or internet links.
2. If the `BB_THREAD_ID` environment variable is set, you are in bb. Then put `::inline-vis{file="80_aios/reports/m11-stranger-install_v1.html"}` on its own line in your final reply, outside any code block. Then move this chat to the Review lane: run `bb thread section list --json`, create a section called Review with `bb thread section create Review` if there is none, and run `bb thread update --self --section <the Review id>`.
3. End with at most five plain lines: what works, what failed, and the one thing I do next.
~~~

## Prompt 11.3 · Make me a small bb mod (stretch)

**What it does:** Asks Claude to write a tiny bb plugin of your own that shows a line above the chat box, then builds and installs it in your bb.

**How you know it worked:** `bb plugin list` shows your mod running, and its line shows above the chat box after a reload.

~~~text
Make me a small bb mod that shows today's date and the days left in this month above the chat box.

Here is how:
1. Read bb's plugin guide first: run `bb guide plugins`, and use the `bb-plugin-authoring` skill if you have it.
2. Work in `50_projects/bb-mods/`. Run `bb plugin new date-line` there, and keep only what the mod needs: one small banner above the chat box, no server code if none is needed.
3. Build it with `bb plugin build` and fix any error it shows.
4. Install it into my bb: `bb plugin install 50_projects/bb-mods/bb-plugin-date-line --yes`. It changes bb's settings: I allow that for this command, so if the sandbox blocks it, run it outside the sandbox.
5. Run `bb plugin list` and show it running. Tell me to reload bb (Cmd+R) to see the line, and how to switch it off: `bb plugin disable date-line`.

For this task only: work only in this folder unless a step names another one. Never delete or overwrite my files: if a file already exists, keep it and tell me. Never print or ask for a key, token or password. Show real command output, never a guess. If a step fails, show the error, fix that one cause if you can, and run the check again. If a step below must write outside this folder (for example to Claude's settings, `~/.local` or a folder the step names), I allow exactly that command: if the sandbox blocks it, run it outside the sandbox. Do not stop to ask me anything unless a step needs my decision.

When you are done, show me the result:
1. Write a one-page HTML report to `80_aios/reports/m11-bb-mod_v1.html` (create the folder if needed; if that file exists, use the next free `_vN` and use that name below). Put in it: what you set up, a table of every check (the command, a short piece of its real output, PASS or FAIL) and my one next step. Keep it simple: no web fonts, scripts or internet links.
2. If the `BB_THREAD_ID` environment variable is set, you are in bb. Then put `::inline-vis{file="80_aios/reports/m11-bb-mod_v1.html"}` on its own line in your final reply, outside any code block. Then move this chat to the Review lane: run `bb thread section list --json`, create a section called Review with `bb thread section create Review` if there is none, and run `bb thread update --self --section <the Review id>`.
3. End with at most five plain lines: what works, what failed, and the one thing I do next.
~~~
