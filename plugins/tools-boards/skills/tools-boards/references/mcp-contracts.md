# Bluplai whiteboard MCP contracts

Use the connected `bluplai` MCP schemas as the final authority. This reference
captures the stable map surface used by the skill.

## Discovery and reads

- `list_whiteboards(limit?, include_shared?, project_id?)`
- `read_whiteboard(whiteboard_id, color?)`
- `read_whiteboard_selection(selection_id)`
- `analyze_whiteboard_selection(selection_id, question)`

Use `list_whiteboards` before selecting a target and `read_whiteboard` before
and after a mutation.

## Create and replace

`create_whiteboard_map(name, nodes, edges, account_id?, project_id?)` creates a
new populated native tldraw board.

`replace_whiteboard_map(whiteboard_id, nodes, edges, name?)` replaces the full
scene. It resets the collaboration generation and requires explicit user intent.

### Node shape

```json
{
  "id": "short-stable-id",
  "label": "Visible label",
  "x": 120,
  "y": 200,
  "width": 280,
  "height": 80,
  "size": "m",
  "color": "blue",
  "fill": "semi"
}
```

Limits:

- 1–50 nodes.
- Unique non-empty ids.
- Label length 1–300.
- Width 120–2000; height 60–2000.
- Coordinates -20000 to 20000.
- Size: `s`, `m`, `l`, `xl`.
- Colour: `black`, `grey`, `light-violet`, `violet`, `blue`, `light-blue`,
  `yellow`, `orange`, `green`, `light-green`, `light-red`, `red`, `white`.
- Fill: `none`, `semi`, `solid`, `pattern`.

All generated geometry uses tldraw's native draw dash and draw font.

### Edge shape

```json
{
  "from_id": "source",
  "to_id": "target",
  "label": "PUBLISH",
  "bend": 80
}
```

Limits:

- 0–100 edges.
- Both ids must reference nodes in the same payload.
- Label length up to 160.
- Bend -1000 to 1000.

Edges become native bound arc arrows.

## Images

Use images only when the user wants a reference, photograph, or external visual
to remain on the board. An image should not replace native structure.

- `request_whiteboard_image_upload` → upload bytes to the returned URL →
  `attach_whiteboard_image`.
- `attach_whiteboard_image_url` places a stable public HTTPS image.

## Verification signals

After a successful write, `read_whiteboard` should return:

- The new `scene_revision`.
- Every expected node label.
- Labelled edges with readable from/to names.
- Styled native geometry in `visual_elements`.

If a supposed native rebuild returns one image and no labelled nodes/edges, it
did not satisfy the request.
