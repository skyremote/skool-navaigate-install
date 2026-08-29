# skool-navaigate-install

The community plugin for [NavAIgate](https://www.skool.com/navaigate)
**ANNUAL ONLY — YOUR AIOS**.

This is the OS path. It is not Chief of Staff (that is the team —
[`skyremote/chief-of-staff-kit`](https://github.com/skyremote/chief-of-staff-kit)
0.4.2). It is not Daniel's private `navaigate-plugins` marketplace.

Fifteen classroom modules. After every one they type `/aios`. The plugin
asks where they are (empty / halfway / already running) and which lesson
they are in, then gives one next command. It will not wipe a messy folder
to make a clean demo.

## Install

### Claude Code

```text
/plugin marketplace add skyremote/skool-navaigate-install
/plugin install skool-navaigate-install@navaigate-aios
```

Restart, then type `/aios`.

### Cursor or Codex (or all three at once)

```bash
git clone https://github.com/skyremote/skool-navaigate-install.git
cd skool-navaigate-install
./install.sh
```

`install.sh` symlinks the skills into `~/.claude/skills`, `~/.cursor/skills`,
`~/.codex/skills` and `~/.agents/skills`. Restart the harness. Type `/aios`.

## Commands

| Command | Job |
|---|---|
| `/aios` | Status. Where are you. Which lesson. One next step. |
| `/install-crew` | Chief of Staff 0.4.2. Does not merge this course into the kit. |
| `/layer-1` | Context — their CLAUDE.md, not ContextOS. |
| `/layer-2` | Data — numbers they can ask. |
| `/layer-3` | Intelligence — meetings, brief, Grok Bot in the pocket. |
| `/layer-4` | Automate — task audit. No GTD zip. |
| `/layer-5` | Build — architect the residue. |
| `/design-brain` | The 1,119-entry corpus + the 19-chart gallery. Not `/design`. |
| `/your-voice` | Their voice. Never `daniel-voice`. |
| `/your-brain` | Their memory. Public kit: `skyremote/db-sync`. Never `brain-sync`. |
| `/your-ops` | Their invoice. Public kit: `skyremote/invoice-builder`. Never NavAIgate letterhead. |
| `/content-coach` | LinkedIn the way we actually run it. |
| `/hormozi` | Ask Hormozi + the four workbenches. Their books. |

## Lessons

Paste-ready bodies for the fifteen modules live in `lessons/`. Images and
voice are on Backblaze, already referenced from the HTML:

`https://f003.backblazeb2.com/file/NavAIgate-Website/navbot-community/lessons/your-aios/`

## What this will never ship

See `references/never-ship.md`. If a skill has Daniel's name, his register
number, his call recordings, or his old chats in it, it stays on his machines.

## License

MIT. Same as the chief-of-staff kit.
