---
title: "Start here: one loop, small context, checks it can run"
module: 1
pack: aios
video: aios2-m01-start-here_v1.mp4
narration: aios2-m01_v1.mp3
---

# Start here: one loop, small context, checks it can run

[VIDEO: aios2-m01-start-here_v1.mp4]

**By the end of this lesson you'll have the `aios` start plugin installed in Claude Code, Codex and Cursor, and you'll have typed `/aios` and got back the one next step for your setup, whether your folder is empty, halfway there or already running.**

## What you get

So before we install anything, it's worth being clear on what an AIOS actually is, because it isn't a chatbot with a folder next to it, and it isn't a pile of skills you installed on a Sunday afternoon. It's the setup that lets an agent do real work in your business without you explaining everything again every morning, and in 2026 it comes down to three things:

- **One main loop.** One agent, in one session, doing the job from start to finish. We add helpers later, and only when they've earned it, which is module 7.
- **A small always-on context.** The rules the agent reads before every job stay short, and everything else loads when the job needs it. That's module 2.
- **Checks the agent can run.** Before it starts, the agent says how it'll prove the job is done, and then it runs that check itself, for example the build passes, the file exists or the totals match the sheet. That's module 8, and we use it from today.

That's also what Anthropic recommend for the new models: load less, load it when the job needs it, give the agent a check it can run, and look at your setup again every time a new model comes out.

The `aios` plugin is the start of all of this. It's one skill, `/aios`, and it looks at what you've got on your machine, which packs are installed in which harness, and tells you the next module to do. Then you add one pack at a time, when you get to the module that needs it.

### The 12 modules

| Module | What we do | Pack |
|---|---|---|
| 1. Start here | Install `aios` and find your next step | `aios` |
| 2. Your folders and your rules | A folder map, one short AGENTS.md, a size check | `aios-rules` |
| 3. The harnesses | Claude Code, Codex and Cursor, and what each is best at | `aios-harnesses` |
| 4. bb as the cockpit | Threads, the kanban and inline results | `aios-bb` |
| 5. Memory you own | A private brain of your past work, on your own Mac | `aios-brain` |
| 6. Skills that earn their place | Small skills, short descriptions, three tests each | `aios-skills-kit` |
| 7. Agents without sprawl | One loop first, helpers only when they're needed | `aios-agents` |
| 8. Make it verifiable | Tests, a verify step, review and hard rules as hooks | `aios-verify` |
| 9. Working methods | Interview first, loops, worktrees, GSD and compound engineering | `aios-methods` |
| 10. Models, effort and cost | Which model does what, and what it costs | `aios-models` |
| 11. Ship it to others | Package your own pipeline as a plugin | `aios-ship-it` |
| 12. The shelf | Optional tools: video, decks, invoices, voice, design, research | one pack per tool |

Modules 1 to 5 get it working, 6 to 10 make it good, and 11 and 12 are for sharing it and for the extras. You don't need to do them all in one week, and the `/aios` skill always knows where you are.

## What you need

- A Mac, or Linux. Windows works through WSL.
- At least one harness: [Claude Code](https://code.claude.com/docs/en/overview), [Codex](https://developers.openai.com/codex) or [Cursor](https://cursor.com). You don't need all three, so start with the one you've got.
- Python 3.9 or newer for the checks. Type `python3 --version`, and a Mac already has it.
- Git, for Codex and Cursor. Type `git --version`. If it isn't there, macOS offers to install it.

## Install

### Claude Code

Open Claude Code in any folder and type these two lines, one at a time:

```text
/plugin marketplace add skyremote/skool-navaigate-install
/plugin install aios@navaigate-aios
```

The first line adds the YOUR AIOS marketplace, which is the list of packs, and the second installs the start plugin. You should see `Successfully installed plugin: aios@navaigate-aios`. Restart Claude Code, so it loads the new skill.

If you'd rather do it from the terminal, it's the same two steps:

```sh
claude plugin marketplace add skyremote/skool-navaigate-install
claude plugin install aios@navaigate-aios
```

[SCREENSHOT: m01_01_install-claude-code.png]

### Codex and Cursor

Codex and Cursor install from a copy of the repository on your Mac. The installer links the skill into both of them, so keep the folder where it is afterwards. In your terminal:

```sh
git clone https://github.com/skyremote/skool-navaigate-install.git ~/aios-install
cd ~/aios-install
./install.sh aios
```

You should see three `Linked` lines, for `.codex/skills/aios`, `.cursor/skills/aios` and `.agents/skills/aios`, and then `Installed aios 2.0.0`. It never replaces a skill you already have with the same name: if there's one there, it stops and tells you, and you move yours aside first. Then restart Codex and Cursor.

[SCREENSHOT: m01_02_install-codex-cursor.png]

## First use

### 1. Make a folder, or open the one you've got

If you're starting from nothing:

```sh
mkdir -p ~/my-aios
cd ~/my-aios
```

If you've already got a business folder with notes in it, use that, and don't tidy it first. We keep what's there.

### 2. Type /aios

In Claude Code, type `/aios`. If it shows up as `/aios:aios`, that's the same skill, and you can use either. In Cursor, type `/aios` in the Agent chat. In Codex, type `$aios`, or just ask "use the aios skill".

It asks you one question first: **is this machine empty, halfway, or already running?**

- **Empty.** A new folder with nothing in it.
- **Halfway.** Some notes, a half-written CLAUDE.md, a few folders you made and stopped using.
- **Already running.** You've got agents, skills or a daily routine working.

### 3. Read what it found

It then checks your machine, and it tells you three things: which packs are installed in which harness, whether there's a rules file in this folder, and the module to do next. Installed and enabled are reported separately, because a pack can be installed and still need a restart before the harness loads it.

[SCREENSHOT: m01_03_aios-empty-folder.png]

On an empty folder, the next step is module 2, and the one action is to set up your folders and your rules. On a halfway folder, it tells you what it found first, for example a CLAUDE.md with no AGENTS.md, and then it gives you the next step without wiping anything.

[SCREENSHOT: m01_04_aios-halfway-folder.png]

### 4. Do one job with a check

Before you move on, run one real job you do every week, in one session, with no helpers. Paste this in, with your job in the brackets:

```text
The job is: [your weekly job]. Before you start, tell me the check you will run to prove it is done. Then do the job, run the check, and show me the result. Do not use sub-agents.
```

If the check fails, give the agent the failure and let it fix that one thing, rather than asking for another big change.

## Daily use

Every time you come back to the course, open your folder and type `/aios`. It tells you where you are and the next action. When you finish a module, tell it, for example "I've finished module 2", and it can save that in `~/.local/share/aios/progress.json`, so next time it starts from module 3. Installing a pack never counts as finishing a module, because only you know whether you've done the lesson.

When you get to a module that has a pack, install that one pack, and nothing else:

```text
/plugin install aios-rules@navaigate-aios
```

or, for Codex and Cursor:

```sh
cd ~/aios-install && git pull && ./install.sh aios-rules
```

## How to check it works

- In Claude Code, type `/plugin` and look for `aios@navaigate-aios` on the **Installed** tab, or run `claude plugin list` in the terminal.
- For Codex and Cursor, run `ls -l ~/.codex/skills ~/.cursor/skills`. You should see `aios` pointing into `~/aios-install`.
- Type `/aios`. It should ask you the empty, halfway or already running question, and then list the packs it found in each harness.

> **Proof:** Anthropic cut over 80% of Claude Code's own system prompt with no measurable loss on its coding tests ("The new rules of context engineering", 24 July 2026), which is why we start small and add things when the numbers say so.

## Common problems

| What you see | What it means | The fix |
|---|---|---|
| `/aios` isn't in the list | Claude Code hasn't loaded the plugin yet | Restart Claude Code, then type `/aios` or `/aios:aios` |
| `Plugin "aios" not found in marketplace "navaigate-aios"` | The marketplace isn't added, or your copy of it is old | Run `/plugin marketplace add skyremote/skool-navaigate-install`, or `claude plugin marketplace update navaigate-aios` if you added it before |
| `Install stopped: Existing skill preserved` | You already have a skill called `aios` in Codex or Cursor | Move your own folder aside, for example rename it `aios-old`, then run `./install.sh aios` again |
| `/aios` says a pack is installed but not loaded | The harness was open during the install | Restart that harness |
| `./install.sh: Permission denied` | The file lost its run permission | Run `chmod +x install.sh`, then try again |
| Codex doesn't see the skill | Codex was open, or it needs the skill named | Restart Codex, then type `$aios` or "use the aios skill" |
| `/aios` says the check is unverified | Python couldn't run the status script | Run `python3 --version`. If it's below 3.9, update Python |

## Next module

Module 2 is your folders and your rules: a folder map, one short AGENTS.md that every harness reads, and a check that counts how much the agent loads before every job. Type `/aios` and it'll point you straight at it.

— Daniel
