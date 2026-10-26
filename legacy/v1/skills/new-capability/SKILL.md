---
name: new-capability
description: >
  Walk them through building a skill that talks to a tool we did not ship.
  Use when they type /new-capability or say they need HubSpot / an internal
  API / a feed we have no module for.
---

# /new-capability

Sooner or later they hit the edge of the shelf. This is the rod, not
another fish. They describe the connection. You turn it into an installed
skill on **their** machine.

Do not copy Daniel's house skills. Do not put his keys, his company, or
`user_id=daniel` in what you write.

## Do this

1. **Interrogate.** What data do they want out, where does it live, what
   authenticates them, how often does it run. Most failed integrations
   fail here, in the vagueness.
2. **Find the surface.** Official API, unofficial API, CLI, or scrape.
   Pick the one least likely to break in three weeks.
3. **Build the wiring.** Write a `SKILL.md` plus the smallest helper
   script that does the job. Keys go in `~/.claude/.env` under **their**
   names. Nothing runs they have not seen.
4. **Install it.** Drop it in their skills folder (or link it the same
   way `install.sh` does). Prove it with one command they can repeat.

## First build

Start with something they can verify in under a minute — list the last
ten items from a public feed, pull one HubSpot deal they already know.
Then the CRM link or the internal API.

Public pattern they can steal from: the `/web-scrape` helper in this
plugin (keys in `~/.claude/.env`, one CLI, `--json` when they need the
raw payload).

Then `/aios`.
