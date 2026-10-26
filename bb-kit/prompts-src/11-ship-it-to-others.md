# 11 · Ship it to others
pack: aios-ship
cmd: ship-pack

## 11.1 · Turn my skill into a plugin someone else can install
what: Packages one of your skills as a plugin (a pack) with tests, three eval cases and an installer, then validates it.
check: `ship-pack check` ends with `0 error(s)`, the tests print OK and `claude plugin validate` says `Validation passed`.
~~~
Set up module 11: package one of my skills so someone else can install it.

My name for the pack's author line (edit this line): Sam Lee

<<INSTALL>>

1. Find a skill to package: list the folders in `~/.claude/skills` (or `$CLAUDE_CONFIG_DIR/skills`) that hold a SKILL.md. Pick the smallest one. If I have none, create a small practice skill `meeting-actions` in `~/.claude/skills/meeting-actions/SKILL.md` that turns meeting notes into actions with an owner and a due date.
2. Make a home for my packs: `mkdir -p ~/my-tools && cd ~/my-tools && git init` (skip `git init` if it is already a repository). Work in `~/my-tools` from now on.
3. Run `ship-pack from-skill <the skill folder> --author "<my name>"`. If it stops because it found a key or a personal path, show me the file and line, and stop.
4. Run `ship-pack check <name>`. It lists placeholders. Fill them: the three cases in `evals/` (a real request, an edge case and one it must refuse; each grader pattern is a word the right answer always contains) and the README's names.
5. Run `ship-pack check <name>` until it ends with `0 error(s)`.
6. Run `python3 -m unittest discover <name>/tests` (it must print OK) and `claude plugin validate <name> --strict` (it must say `Validation passed`).

<<RULES>>

<<FINISH m11-make-pack>>
~~~

## 11.2 · Install my plugin as a stranger would
what: Lists your pack in your own marketplace, installs it into an empty test home folder as a new user would, and checks it is enabled.
check: The test install says `Successfully installed`, the pack shows as enabled at 0.1.0, and the test home is removed afterwards.
~~~
Module 11, part two. Prove my pack installs for a stranger. The pack must already exist in `~/my-tools` (if not, stop and tell me to run prompt 11.1 first).

<<INSTALL>>

1. In `~/my-tools`, run `ship-pack marketplace <name> --file .claude-plugin/marketplace.json --name my-tools --owner "<the author name in the pack>"`, then `claude plugin validate .`, then `git add . && git commit -m "<name> 0.1.0"`.
2. Make an empty test home: `mkdir -p /tmp/new-member`. Run the next commands with `env -u CLAUDE_CONFIG_DIR HOME=/tmp/new-member` in front, so they use that empty home:
   `claude plugin marketplace add ~/my-tools`, then `claude plugin install <name>@my-tools`, then `claude plugin list`.
3. Show me `Successfully installed` and the pack listed as enabled at 0.1.0.
4. Remove only the test home you just made: `rm -rf /tmp/new-member`.
5. Tell me how others install it once I push `~/my-tools` to GitHub: `/plugin marketplace add <github-name>/my-tools`.

<<RULES>>

<<FINISH m11-stranger-install>>
~~~

## 11.3 · Make me a small bb mod (stretch)
what: Asks Claude to write a tiny bb plugin of your own that shows a line above the chat box, then builds and installs it in your bb.
check: `bb plugin list` shows your mod running, and its line shows above the chat box after a reload.
~~~
Make me a small bb mod that shows today's date and the days left in this month above the chat box.

Here is how:
1. Read bb's plugin guide first: run `bb guide plugins`, and use the `bb-plugin-authoring` skill if you have it.
2. Work in `50_projects/bb-mods/`. Run `bb plugin new date-line` there, and keep only what the mod needs: one small banner above the chat box, no server code if none is needed.
3. Build it with `bb plugin build` and fix any error it shows.
4. Install it into my bb: `bb plugin install 50_projects/bb-mods/bb-plugin-date-line --yes`. It changes bb's settings: I allow that for this command, so if the sandbox blocks it, run it outside the sandbox.
5. Run `bb plugin list` and show it running. Tell me to reload bb (Cmd+R) to see the line, and how to switch it off: `bb plugin disable date-line`.

<<RULES>>

<<FINISH m11-bb-mod>>
~~~
