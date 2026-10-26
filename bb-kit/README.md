# YOUR AIOS 2.0 starter kit for bb

Track A of YOUR AIOS 2.0: open bb, ask Claude, paste the prompt, and let Claude set it up and show you the result.
This kit gives you a NavAIgate bb in one step.

## Install (members)

You need a Mac (or Linux) with:

1. **bb**, from https://getbb.app. Open it once and finish its first screen.
2. **Claude Code**, from https://claude.com/claude-code. Sign in once with your Claude plan.
3. **The bb command in your terminal.** In bb, open Settings, General, bb CLI, and press Install.
   (The kit also finds bb inside the app if you skip this.)

Then open the Terminal app and paste this one line:

```sh
curl -fsSL https://raw.githubusercontent.com/skyremote/skool-navaigate-install/main/bb-kit/install.sh | bash
```

It takes about a minute. It ends with a list of `OK` lines and the next step.

Want a different folder or name? Add options after `bash -s --`:

```sh
curl -fsSL https://raw.githubusercontent.com/skyremote/skool-navaigate-install/main/bb-kit/install.sh | bash -s -- --folder ~/Documents/AIOS --name "Acme AIOS"
```

| Option | What it does |
|---|---|
| `--folder <path>` | Your AIOS folder. Default `~/AIOS`. Created if missing; existing files are never touched. |
| `--name <name>` | The bb project name. Default "My AIOS". |
| `--all` | Install every core pack now, instead of one pack per module. |
| `--no-skin` | Skip the NavAIgate skin and mods. |
| `--dry-run` | Show what would happen and change nothing. |

Running it again is safe: each step checks first and keeps what is there.

## What it does

1. **Installs the AIOS start pack for Claude Code**: adds the `navaigate-aios` marketplace and installs `aios`.
   With `--all` it installs `aios-complete` (modules 1 to 11). If Codex is installed, it also links `aios` for Codex.
2. **Creates a bb project** for your AIOS folder, or keeps the one you have.
3. **Adds the prompt library** where you can see it:
   - an **AIOS course** page in the bb sidebar, with every module's prompts and a **Start chat** button;
   - every prompt saved in bb's built-in **Prompt Library**: press `Ctrl+R` in any chat box and type "AIOS".
4. **Installs the NavAIgate skin and five mods** (helper desk, cache clock, reflect, screen share, Finder links),
   when this computer can reach those repositories. See "Private parts" below.

## Use it

1. Open bb. Click **AIOS course** in the sidebar.
2. Open module 1 and press **Start chat** on prompt 1.1. Claude installs the start pack and shows you where you stand.
3. When it finishes, the report shows inside the chat, the chat moves to the **Review** lane, and the last five lines
   tell you what worked and what to do next.
4. Go module by module. If a prompt has lines marked "edit", change them to your own details before you start it.

The same prompts are in `prompts/`, one file per module, and in each lesson as `prompts_v1.md`.
They also work in Claude Code in a terminal: open it in your AIOS folder and paste the prompt.

## When something goes wrong

| What you see | Do this |
|---|---|
| `bb is not installed` or `not running` | Install bb from getbb.app, open it, then run the line again. |
| `Claude Code is not installed` | Install it, run `claude` once to sign in, then run the line again. |
| Claude says the sandbox blocked an install | The prompt allows those commands; say "yes, run it outside the sandbox" in the chat. |
| No **AIOS course** in the sidebar | Run `bb plugin list`. If `aios-starter` is missing, run the install line again. |
| `Ctrl+R` does not find "AIOS" | Run `bb plugin enable bb--prompt-library`, then `bb aios-kit star`. |

## Private parts

The NavAIgate skin (`skyremote/bb-plugin-navaigate-skin`) and the mods (`skyremote/navaigate-bb-mods`) are private
repositories today. The kit checks whether this computer can reach them. If it cannot, it says SKIP for each one and
finishes everything else. The course works without them: the prompts, the AIOS course page and the Prompt Library
need only this public repository.

The `fleet` mod is never installed by the kit: it uses NavAIgate's own memory service.

## For maintainers

- `prompts-src/<NN-slug>.md`: the prompt sources, one module per file. Edit these.
- `scripts/build_prompts.py`: builds `prompts/`, `plugin/prompts.json` and `plugin/prompts.ts`, with the shared
  "get the pack", "ground rules" and "show me the result" blocks. `--check` fails if a built file is stale.
  `--lessons <dir>` also writes `<dir>/<NN-slug>/prompts_v1.md` for the classroom.
- `scripts/prove_prompt.py`: runs one prompt for real in a bb thread and saves the evidence.
- `plugin/`: the AIOS Starter bb plugin.
- `install.sh`: the one-line installer.
