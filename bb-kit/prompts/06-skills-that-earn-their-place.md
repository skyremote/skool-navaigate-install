# Module 6 · Skills that earn their place: prompts

Paste one prompt at a time into a new Claude chat in bb, opened on your AIOS folder. Run them in order. If a prompt has lines marked "edit", change them to your own details first. Each prompt sets something up, checks it, and shows you the result.

These prompts are instructions to Claude. They also work in Claude Code in a terminal, opened in the same folder.

## Prompt 6.1 · Make me a skill for my weekly job, with three tests

**What it does:** Turns one job you explain to Claude every week into a skill (a saved set of steps), with three test cases, and checks it.

**How you know it worked:** `aios-skill check` says PASS for the new skill and counts three cases.

~~~text
About my weekly job (edit these lines before you send):
- The job: turn rough meeting notes into a list of actions.
- What I type to ask for it: "actions from these notes".
- The check that proves it is done: every action has an owner and a due date, and nothing in the notes is missing.

Make me a skill for this weekly job, with three test cases, and check it passes.

Step 0, get the pack. These commands change Claude's own plugin folder in my home folder, outside this folder. I allow that for these commands only: if the sandbox blocks them, run them outside the sandbox. Run `claude plugin marketplace list`. If `navaigate-aios` is not listed, run `claude plugin marketplace add skyremote/skool-navaigate-install`. Then run `claude plugin install aios-skills@navaigate-aios` ("already installed" is fine; it also brings the start pack `aios`). Until I restart Claude, call the pack's command by its full path: `"$(ls -d "${CLAUDE_CONFIG_DIR:-$HOME/.claude}"/plugins/cache/navaigate-aios/aios-skills/*/bin | tail -1)/aios-skill"`. Below, `aios-skill` means that full path.

1. Pick a short name for the job, lower case with dashes (for example `meeting-actions`). If a skill with that name exists, pick another name.
2. Run `aios-skill new <name> --description "<what it does>. Use when <the words I type>."`. Show where it was created and the files it made.
3. Run `aios-skill check <the skill folder>`. It should fail with "still contains TODO" lines. That is expected.
4. Fill in SKILL.md: replace each `TODO:` line with the steps, the check above and the one mistake to avoid. The pack has a finished example at `examples/meeting-actions/SKILL.md` inside its plugin folder; read it for the style.
5. Fill in the three test cases under `evals/`: `should-fire` (a message I would type, without naming the skill), `should-not-fire` (a nearby job the skill must leave alone) and `edge-case`. Each `graders/result.md` gets one PASS line and one FAIL line.
6. Run `aios-skill check <the skill folder>` again. It must say PASS and count 3 cases.

Ground rules: work only in this folder unless a step names another one. Never delete or overwrite my files: if a file already exists, keep it and tell me. Never print or ask for a key, token or password. Show real command output, never a guess. If a step fails, show the error, fix that one cause if you can, and run the check again. If a step below must write outside this folder (for example to Claude's settings, `~/.local` or a folder the step names), I allow exactly that command: if the sandbox blocks it, run it outside the sandbox. Do not stop to ask me anything unless a step needs my decision.

When you are done, show me the result:
1. Write a one-page HTML report to `80_aios/reports/m06-new-skill_v1.html` (create the folder if needed; if that file exists, use the next free `_vN` and use that name below). Put in it: what you set up, a table of every check (the command, a short piece of its real output, PASS or FAIL) and my one next step. Keep it simple: no web fonts, scripts or internet links.
2. If the `BB_THREAD_ID` environment variable is set, you are in bb. Then put `::inline-vis{file="80_aios/reports/m06-new-skill_v1.html"}` on its own line in your final reply, outside any code block. Then move this chat to the Review lane: run `bb thread section list --json`, create a section called Review with `bb thread section create Review` if there is none, and run `bb thread update --self --section <the Review id>`.
3. End with at most five plain lines: what works, what failed, and the one thing I do next.
~~~

## Prompt 6.2 · Show me my skill beats no skill

**What it does:** Runs your skill's three test cases with and without the skill, so you see whether it really helps. It uses your own Claude plan for six short runs.

**How you know it worked:** The report shows WITH, WITHOUT and the difference for each case, and whether the skill fired.

~~~text
Show me the skill I made does better than no skill. If there is no skill with three filled test cases, stop and tell me to run prompt 6.1 first.

Step 0, get the pack. These commands change Claude's own plugin folder in my home folder, outside this folder. I allow that for these commands only: if the sandbox blocks them, run them outside the sandbox. Run `claude plugin marketplace list`. If `navaigate-aios` is not listed, run `claude plugin marketplace add skyremote/skool-navaigate-install`. Then run `claude plugin install aios-skills@navaigate-aios` ("already installed" is fine; it also brings the start pack `aios`). Until I restart Claude, call the pack's command by its full path: `"$(ls -d "${CLAUDE_CONFIG_DIR:-$HOME/.claude}"/plugins/cache/navaigate-aios/aios-skills/*/bin | tail -1)/aios-skill"`. Below, `aios-skill` means that full path.

1. Find the skill folder I made (run `aios-skill audit` if you need the path) and run `aios-skill check <folder>`. It must pass first.
2. Run `claude plugin eval <folder> --runs 1 --no-publish`. If it asks whether to trust the folder, answer yes. It makes six short runs on my plan.
3. Show me, for each case, the WITH score, the WITHOUT score, the difference, and whether the skill fired.
4. If the skill did not fire, rewrite the "Use when" words in its description and run the eval once more. If the difference is zero or below, tell me the model already does this job well without the skill.

Ground rules: work only in this folder unless a step names another one. Never delete or overwrite my files: if a file already exists, keep it and tell me. Never print or ask for a key, token or password. Show real command output, never a guess. If a step fails, show the error, fix that one cause if you can, and run the check again. If a step below must write outside this folder (for example to Claude's settings, `~/.local` or a folder the step names), I allow exactly that command: if the sandbox blocks it, run it outside the sandbox. Do not stop to ask me anything unless a step needs my decision.

When you are done, show me the result:
1. Write a one-page HTML report to `80_aios/reports/m06-skill-eval_v1.html` (create the folder if needed; if that file exists, use the next free `_vN` and use that name below). Put in it: what you set up, a table of every check (the command, a short piece of its real output, PASS or FAIL) and my one next step. Keep it simple: no web fonts, scripts or internet links.
2. If the `BB_THREAD_ID` environment variable is set, you are in bb. Then put `::inline-vis{file="80_aios/reports/m06-skill-eval_v1.html"}` on its own line in your final reply, outside any code block. Then move this chat to the Review lane: run `bb thread section list --json`, create a section called Review with `bb thread section create Review` if there is none, and run `bb thread update --self --section <the Review id>`.
3. End with at most five plain lines: what works, what failed, and the one thing I do next.
~~~

## Prompt 6.3 · Find a bb plugin that shows what fills my context

**What it does:** Searches the bb plugin store, picks the best plugin for seeing what fills a chat's context, and installs it after showing you what it is.

**How you know it worked:** The report shows the search results and why one was picked, and `bb plugin list` shows it running.

~~~text
Search the bb plugin store for something that shows what is filling my context, and install the best one.

Here is how:
1. Run `bb plugin search context` and show me the results as a short table: name, what it does, installs.
2. Pick the best match for "see what is filling my chat's context" and say why in one line. Expect "Context Health".
3. Show me its source before you install it: `bb plugin search "<its name>" --json` or the store page. Plugins run with full trust, so tell me who made it.
4. Install it: `bb plugin install <its id> --yes`. It changes bb's settings, outside this folder: I allow that for this one command, so if the sandbox blocks it, run it outside the sandbox.
5. Run `bb plugin list` and show it running. Tell me where to find it in bb.

Ground rules: work only in this folder unless a step names another one. Never delete or overwrite my files: if a file already exists, keep it and tell me. Never print or ask for a key, token or password. Show real command output, never a guess. If a step fails, show the error, fix that one cause if you can, and run the check again. If a step below must write outside this folder (for example to Claude's settings, `~/.local` or a folder the step names), I allow exactly that command: if the sandbox blocks it, run it outside the sandbox. Do not stop to ask me anything unless a step needs my decision.

When you are done, show me the result:
1. Write a one-page HTML report to `80_aios/reports/m06-store-plugin_v1.html` (create the folder if needed; if that file exists, use the next free `_vN` and use that name below). Put in it: what you set up, a table of every check (the command, a short piece of its real output, PASS or FAIL) and my one next step. Keep it simple: no web fonts, scripts or internet links.
2. If the `BB_THREAD_ID` environment variable is set, you are in bb. Then put `::inline-vis{file="80_aios/reports/m06-store-plugin_v1.html"}` on its own line in your final reply, outside any code block. Then move this chat to the Review lane: run `bb thread section list --json`, create a section called Review with `bb thread section create Review` if there is none, and run `bb thread update --self --section <the Review id>`.
3. End with at most five plain lines: what works, what failed, and the one thing I do next.
~~~

## Prompt 6.4 · Show me what my skills cost (optional)

**What it does:** Lists every skill you have with the tokens it costs on every turn, and previews hiding one you never use. Nothing is hidden yet.

**How you know it worked:** The report lists your skills sorted by cost, and shows the dry run for one skill you could hide.

~~~text
Show me what my skills cost me, and which one I could hide.

Step 0, get the pack. These commands change Claude's own plugin folder in my home folder, outside this folder. I allow that for these commands only: if the sandbox blocks them, run them outside the sandbox. Run `claude plugin marketplace list`. If `navaigate-aios` is not listed, run `claude plugin marketplace add skyremote/skool-navaigate-install`. Then run `claude plugin install aios-skills@navaigate-aios` ("already installed" is fine; it also brings the start pack `aios`). Until I restart Claude, call the pack's command by its full path: `"$(ls -d "${CLAUDE_CONFIG_DIR:-$HOME/.claude}"/plugins/cache/navaigate-aios/aios-skills/*/bin | tail -1)/aios-skill"`. Below, `aios-skill` means that full path.

1. Run `aios-skill audit`. Show me the skills sorted by tokens per turn, and mark which ones come from plugins.
2. Pick the one skill that costs the most tokens per turn and is not from a plugin. If every skill comes from a plugin, say so, and tell me that plugin skills are switched off with `/plugin` instead.
3. Preview hiding it: `aios-skill hide <skill> off --dry-run`. Show me the result. Do not hide it for real.
4. Give me the exact command to hide it for real, and the one to undo it, so I can decide.
5. Tell me that `/skill-doctor` in Claude Code shows which skills were never used.

Ground rules: work only in this folder unless a step names another one. Never delete or overwrite my files: if a file already exists, keep it and tell me. Never print or ask for a key, token or password. Show real command output, never a guess. If a step fails, show the error, fix that one cause if you can, and run the check again. If a step below must write outside this folder (for example to Claude's settings, `~/.local` or a folder the step names), I allow exactly that command: if the sandbox blocks it, run it outside the sandbox. Do not stop to ask me anything unless a step needs my decision.

When you are done, show me the result:
1. Write a one-page HTML report to `80_aios/reports/m06-skill-costs_v1.html` (create the folder if needed; if that file exists, use the next free `_vN` and use that name below). Put in it: what you set up, a table of every check (the command, a short piece of its real output, PASS or FAIL) and my one next step. Keep it simple: no web fonts, scripts or internet links.
2. If the `BB_THREAD_ID` environment variable is set, you are in bb. Then put `::inline-vis{file="80_aios/reports/m06-skill-costs_v1.html"}` on its own line in your final reply, outside any code block. Then move this chat to the Review lane: run `bb thread section list --json`, create a section called Review with `bb thread section create Review` if there is none, and run `bb thread update --self --section <the Review id>`.
3. End with at most five plain lines: what works, what failed, and the one thing I do next.
~~~
