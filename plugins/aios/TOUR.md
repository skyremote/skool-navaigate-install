# Tour: module 1, start here

Run this inside your own AIOS folder. Each step says what to do, the command, what you should see, and how to check it.
In Codex and Cursor the command is `aios-guide`. In Claude Code it is `"${CLAUDE_PLUGIN_ROOT}/bin/aios-guide"`, and `/aios` runs it for you.

## Step 1. See where you start
- Do: ask the start pack what this machine already has.
- Command: `aios-guide next`
- You should see: your harness, the packs installed so far, and "Next module: 1. Start here".
- Check: the output names `aios` as installed.

## Step 2. See the whole path
- Do: list every pack and its module.
- Command: `aios-guide list`
- You should see: one row per shipped pack with its module number, and a "Still being built" line for the rest.
- Check: the row for `aios` says installed.

## Step 3. Find a pack by what you want
- Do: ask for a capability in plain words.
- Command: `aios-guide find set up my brain`
- You should see: `aios-brain (module 5)` first.
- Check: the first line starts with `aios-brain`.

## Step 4. Install your first pack
- Do: install the brain. Its dependency, `aios`, is already there, so only the brain is added.
- Command: `aios-guide install aios-brain`
- You should see: the install lines, then a proof line that starts with `OK aios-brain`.
- Check: in Claude Code, type `/reload-plugins`, then `/brain` is offered. In Codex or Cursor, restart, then `brain status` runs.

## Step 5. Prove it again later
- Do: run the proof on its own. Use this whenever something feels off.
- Command: `aios-guide verify aios-brain`
- You should see: `OK aios-brain`.
- Check: `echo $?` prints 0.

## Step 6. Record the module
- Do: only if you are happy with module 1, record it.
- Command: `aios-guide progress --complete 1`
- You should see: `Confirmed modules: 1`.
- Check: `aios-guide next` now says "Next module: 2".

## Keep going
Type `/aios learn 2` (or `aios-guide learn 2`) to start module 2 in the same way.
