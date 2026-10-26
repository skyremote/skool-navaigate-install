---
name: tools-boards
description: Build, rebuild or polish presentation-ready BluPlai whiteboards as native, editable shapes through the member's own BluPlai account, from a brief, a screenshot, a deck or a call transcript. Use for "make a board", "workshop board", "feedback wall", "turn this transcript into a board", "architecture map", "make this whiteboard look like this screenshot".
---

# BluPlai boards, made of real shapes

The member signs in to their own BluPlai account (bluplai.com). The plugin connects BluPlai's MCP server
(`https://mcp.bluplai.com/mcp`), and the first tool call opens BluPlai's sign-in in the browser. Never ask for or paste
a token. This skill is how we build boards: native shapes a team can drag, zones that say where work lands, a few
story arrows, and a check before anything is written.

## The command

Claude Code: `"${CLAUDE_PLUGIN_ROOT}/bin/tools-boards"`. Codex and Cursor: `tools-boards` (in `~/.local/bin`).

| Command | What it does |
|---|---|
| `validate <scene.json> --payload <out.json> [--strict]` | Checks limits, overlaps, label fit and shape; writes the nodes and edges to send. |
| `sample <folder>` | Two practice scenes: a workshop runway (Northwind, fictional) and a teaching workflow with zones. |

Read `references/design-language.md` before laying out a scene, and `references/mcp-contracts.md` before a tool call.

## Preflight

1. Check the `bluplai` tools are there. If not, the member connects it (Codex and Cursor: add the URL above as an MCP
   server) and signs in when asked.
2. `list_whiteboards` to find the target. Never guess a board id from a title.
3. Existing board: `read_whiteboard` first. New board: `create_whiteboard_map`. Replace a whole board with
   `replace_whiteboard_map` only when the member asked to rebuild or overwrite it; it resets the live room.

## From a call transcript to a board people can talk on

When the source is a call or a workshop (for example from `tools-meetings`), the board drives the next conversation:

1. Read the whole transcript. Pull out the names, the questions, the promises and the decisions. Quote real lines,
   never invent them.
2. Pick the shape: a workshop runway (question, evidence, synthesis, decision, owner), a feedback wall (what we
   heard, then an empty marked area for answers), a journey map or a decision board.
3. Keep every label short (under about 32 characters per line, with deliberate line breaks).
4. Leave clearly marked space for people to write back. End on a decision or a vote.

## Compose in three passes

1. **Inventory.** 12 to 28 meaningful nodes and 3 to 8 story arrows. Short stable ids. Large background zones carry
   `"role": "container"` and come first in the list.
2. **Layout.** An 80 px rhythm, 24 px between cards, 48 to 80 px between clusters, roughly 16:9. Two or three meaning
   colours, not a rainbow: blue and semi for actors, violet for target zones, green for ready, orange or red with
   pattern for private or blocked, grey for evidence.
3. **Arrows last.** Only the ones that tell the story. Verbs as labels: CHOOSE, REVIEW, PUBLISH.

## Validate, write, verify

1. Save the scene, then `validate scene.json --payload scene.mcp.json`. Fix every error; review every warning.
2. Send the payload's nodes and edges with `create_whiteboard_map` (or an authorised replace).
3. `read_whiteboard` straight after: the node and edge counts, the key labels and a new scene revision. A board that
   comes back as one image did not work.
4. The member opens it and zooms to fit (Shift+1). If labels clash, move coordinates and send one clean replacement.
5. Public walkthrough: a view-only share link from BluPlai's Share dialog, with the expiry they asked for.

## Rules

- Native shapes, not one big generated picture. Images only when the member wants a reference image kept.
- Boards often hold client material: check before sharing a link or filming one.
- Report the board name and link, revision, node and arrow counts, and any share-link expiry.
