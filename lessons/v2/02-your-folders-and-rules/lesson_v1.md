---
title: "Your folders and your rules"
module: 2
pack: aios-rules
video: aios2-m02-folders-and-rules_v1.mp4
narration: aios2-m02_v1.mp3
---

# Your folders and your rules

[VIDEO: aios2-m02-folders-and-rules_v1.mp4]

**By the end of this lesson you'll have a folder map for your business, one short AGENTS.md that Claude Code, Codex and Cursor all read, a few rules that only load when the agent works in that folder, and a check that tells you when the always-on part has got too big.**

## What you get

So this is the module where we sort out what the agent reads before it does anything, and the whole idea is that we keep that part small, because everything in it gets loaded into every single session, and the more you put in there, the less of it the agent actually follows. Anthropic's own advice is under 200 lines per file, and we're going to aim for under 150, and we've got a checker in the pack that counts it for you, so you never have to guess.

You get four things from the `aios-rules` pack:

- **A folder map.** Eight numbered folders, from `00_inbox` to `90_archive`, and you rename them to fit your business.
- **A starter AGENTS.md.** About 50 lines, with gaps for you to fill in, and a CLAUDE.md that holds one line, `@AGENTS.md`, so Claude Code reads the same file as Codex and Cursor.
- **Path-scoped rules.** Small files in `.claude/rules/` that load only when the agent opens a file in that folder, for example your finance rules only load when it's working on an invoice.
- **A checker and a monthly audit.** `aios-rules check` counts the lines and tokens of everything that's always loaded, and `/rules-audit` runs Claude Code's own audits once a month and saves what they find in a dated file.

## What you need

- Module 1 done, so the `aios` start plugin is installed.
- Claude Code, Codex or Cursor, or all three. You don't need all three, and the pack works with whichever you've got.
- Python 3.9 or newer. Type `python3 --version` to see yours. A Mac has it already.
- A folder for your business. If you haven't got one, we'll make it in step 1.

There's no account to make, no API key, and nothing goes over the network, apart from the monthly audit, which runs on your own Claude Code sign-in.

## Install

### Claude Code

If you did module 1, the marketplace is already added, so it's one line. Type this inside Claude Code:

```text
/plugin install aios-rules@navaigate-aios
```

If you skipped module 1, add the marketplace and the start plugin first:

```text
/plugin marketplace add skyremote/skool-navaigate-install
/plugin install aios@navaigate-aios
/plugin install aios-rules@navaigate-aios
```

Then restart Claude Code. You'll see two new skills, `/rules` and `/rules-audit` (they can show as `/aios-rules:rules` and `/aios-rules:rules-audit`).

[SCREENSHOT: m02_01_install-claude-code.png]

### Codex and Cursor

These two install from a copy of the repository on your Mac, and the installer links the pack in, so keep the folder where it is afterwards. In your terminal:

```sh
git clone https://github.com/skyremote/skool-navaigate-install.git ~/aios-install
cd ~/aios-install
./install.sh aios
./install.sh aios-rules
export PATH="$HOME/.local/bin:$PATH"
```

If you already cloned it in module 1, just `cd ~/aios-install`, run `git pull`, and then `./install.sh aios-rules`. You should see six `Linked` lines for the skills and one for `.local/bin/aios-rules`. Add the `export PATH` line to your `~/.zshrc` so it's there every time, and then restart Codex and Cursor.

[SCREENSHOT: m02_02_install-codex-cursor.png]

## First use

### 1. Make the folder and look before you write

Open a terminal in your business folder, or make a new one:

```sh
mkdir -p ~/my-aios
cd ~/my-aios
aios-rules init --business "Your Business" --owner "Your Name" --dry-run
```

The dry run shows you every folder and file it would make, and it writes nothing, so you can see it first. Every line says `CREATED`. If a file is already there, it says `KEPT`, and it never overwrites anything you've got.

### 2. Set it up

```sh
aios-rules init --business "Your Business" --owner "Your Name"
```

You now have the eight folders, `AGENTS.md`, `CLAUDE.md` and three rules in `.claude/rules/`. If you've already got your own folders, add `--no-folders`, and we'll put your folder names into the AGENTS.md table instead of making new ones.

[SCREENSHOT: m02_03_init.png]

### 3. Fill in the gaps with the agent

Open Claude Code in the folder, type `/rules`, and tell it whether you're empty, halfway or already running. It asks you one question at a time: what the business does, who buys, one line per folder, the rules that must never break, and one check the folder can run. It fills in every `{{...}}` line as you answer.

The rule for what stays in AGENTS.md is pretty simple. If it matters in every session, it stays. If it's a step-by-step process, it goes into a skill, and if it only matters in one folder, it goes into a rule for that folder.

### 4. Look at a path-scoped rule

Open `.claude/rules/finance.md`. The top three lines are what make it path-scoped:

```markdown
---
paths:
  - "30_finance/**"
---
```

That rule loads only when the agent reads or edits a file in `30_finance/`, so it costs nothing the rest of the time. A rule without `paths:` loads in every session, and the checker counts it. Copy this file to make your own, for example one for `10_clients/`.

### 5. Run the check

```sh
aios-rules check
```

You should see `CLAUDE CODE: OK`, the files that are always loaded with their lines and tokens, and your three rules listed under "On demand". The first time, you'll probably see a `WARN` line saying there are still `{{...}}` gaps in AGENTS.md, so fill those in and run it again.

[SCREENSHOT: m02_04_check-ok.png]

### 6. Give Cursor the same rules

Codex and Cursor don't read `.claude/rules/`. Cursor has its own rules folder, so we copy ours across:

```sh
aios-rules cursor-rules
aios-rules check --harness all
```

You'll see three `WRITTEN` lines for `.cursor/rules/*.mdc`, and the check now shows the same scoped rules under Cursor. Codex reads AGENTS.md from the top of the project down to the folder you're in, so anything Codex must always follow goes in the main AGENTS.md.

### 7. Run your first audit

```sh
aios-rules audit
```

This takes a few minutes. It runs the budget check, then Claude Code's `/doctor prompt-audit`, which looks for instructions written for older models, files that don't exist any more and rules that contradict each other, and then `/skill-doctor`, which shows what each skill costs and which ones you never use. It saves all of it in `80_aios/audits/` with today's date in the name, and it doesn't change a single rule. You read it, you tick what you want to change, and then you ask the agent to make only those changes.

[SCREENSHOT: m02_05_audit-file.png]

## Daily use

Day to day, you don't run anything. The agent reads AGENTS.md at the start of every session, and it loads a folder's rule when it works in that folder. What you do is notice when it gets something wrong twice, and then add one line, in the right place:

- It matters everywhere: one line in AGENTS.md, under "Gotchas".
- It matters in one folder: one line in that folder's rule in `.claude/rules/`, then `aios-rules cursor-rules`.
- It's a process with steps: that's a skill, and we cover skills in module 6.

Then run `aios-rules check` and make sure it still says OK. Once a month, on the first working day, and on the day a new Claude model comes out, type `/rules-audit` or run `aios-rules audit`.

## How to check it works

- `aios-rules check` ends with `OK` and exits 0. If you want the number, type `echo $?` straight after it.
- In Claude Code, type `/context`. Your `CLAUDE.md` and `AGENTS.md` show under **Memory files**.
- Ask the agent, without letting it open any files: "Quote the line in your instructions that says where invoices go." It should give you the `30_finance/` line back from AGENTS.md.
- Open an invoice in `30_finance/` and ask it for your invoice naming rule. That's the finance rule loading on demand.

> **Proof:** Anthropic cut over 80% of Claude Code's own system prompt with no measurable loss on its coding tests ("The new rules of context engineering", 24 July 2026), and the starter AGENTS.md in this pack is 47 lines, about 620 tokens.

## Common problems

| What you see | What it means | The fix |
|---|---|---|
| `aios-rules: command not found` | Codex or Cursor install, and `~/.local/bin` isn't on your PATH | Run `export PATH="$HOME/.local/bin:$PATH"` and add it to `~/.zshrc` |
| `Install stopped: aios-rules depends on aios` | The start plugin isn't installed for Codex and Cursor yet | Run `./install.sh aios`, then `./install.sh aios-rules` |
| `WARN ... CLAUDE.md does not import AGENTS.md` | You had a CLAUDE.md before, so Claude Code skips AGENTS.md | Put `@AGENTS.md` on the first line of CLAUDE.md |
| `OVER ./AGENTS.md: This file is 287 lines` | Too much is always loaded | Move steps into skills and folder rules into `.claude/rules/`, then check again |
| `WARN ... still has {{...}} placeholders` | Some starter lines aren't filled in | Fill them in, or delete the lines you don't need |
| A rule loads everywhere when it shouldn't | The `paths:` block has a typo, so Claude Code reads it as a normal rule | The checker warns about this one. Copy the three lines from `finance.md` exactly |
| The audit says `skill doctor unavailable` | That session can't run `/skill-doctor`, which happens over Remote Control or behind some proxies | Open Claude Code in your own terminal, type `/skill-doctor`, and paste the report under its heading in the audit file |
| The audit says `failed` | Claude Code isn't signed in, or `claude` isn't on your PATH | Run `claude` once and sign in, then run `aios-rules audit` again |

## Next module

Module 3 is the harnesses: what Claude Code, Codex and Cursor are each best at, and how we run them side by side on the same folder and the same rules you've just set up. Type `/aios` and it'll show you the next step.

Try this once before you move on: add one rule for your clients folder, run `aios-rules check`, and make sure it shows under "On demand" and not in the always-loaded list.

— Daniel
