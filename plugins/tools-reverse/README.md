# tools-reverse (AIOS 2.0, module 12: the shelf, tools)

How does that app or website actually work? You install **REA** (`rea-agents`, MIT), which connects to your agents
and brings its own skill. This pack gives your agent our way of running an investigation: a written scope you are
allowed to work in, REA evidence behind every claim, and the unknowns kept honest. `tools-reverse check` fails a
report with no basis, no evidence or a "probably" dressed up as observed.

## Install

1. Install the start plugin `aios` first (module 1).
2. Node.js LTS from nodejs.org.
3. `npx rea-agents setup`: choose your agents, review the plan, approve it, restart your agent. For native apps, an
   engine REA supports (Ghidra, IDA or Hopper).

**Claude Code:** `/aios install tools-reverse` (or `/plugin install tools-reverse@navaigate-aios`), then `/reload-plugins`.

**Codex and Cursor**, from your checkout of this repository:
```
./install.sh tools-reverse
./install.sh tools-reverse --check
```

## Use

```
tools-reverse doctor
tools-reverse sample ~/Reverse-practice
tools-reverse check ~/Reverse-practice/acme-calculator_investigation_v1.md
tools-reverse new ~/Investigations/pricing_v1.md --target "my site's price calculator" --question "How is the price worked out?"
```

Three starter prompts: [prompts.md](prompts.md). The method: [skills/tools-reverse/SKILL.md](skills/tools-reverse/SKILL.md).

## Licence

MIT. REA (`rea-agents`) is MIT and installed by you from npm. Reverse engineering is only for software you own or are
allowed to examine; this pack will not help break licence checks, DRM, logins or paywalls.
