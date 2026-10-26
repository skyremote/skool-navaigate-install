# Native whiteboard design language

## The target

A strong board is a spatial explanation, not a document arranged on a canvas.
The viewer should understand where to start, what can move, where it should land,
and what outcome the movement creates.

## Reliable presentation composition

Use this left-to-right pattern when the material describes transformation:

1. **Instruction band** — one title and one short subtitle.
2. **Movable tray** — independent actor, task, or evidence cards.
3. **Source zone** — the current system, private repository, or starting state.
4. **Transition** — one strong arrow or gate explaining the change.
5. **Destination zone** — a larger coloured boundary containing the target
   worktree, workflow, or future state.
6. **Proof/outcome** — a live destination, review state, decision, or artefact.
7. **Takeaway band** — the invariant or safety rule the presenter should repeat.

Other useful patterns:

- **Workshop runway:** question → evidence → synthesis → decision → owner.
- **Architecture map:** users → channels → services → data → controls.
- **Journey map:** stage columns with actors, actions, friction, evidence, and
  opportunities.
- **Decision board:** options → criteria → trade-offs → recommendation → next
  action.

## Layout rules

- Work on an 80 px rhythm. Align related cards to shared x or y positions.
- Leave at least 24 px between ordinary cards and 48–80 px between clusters.
- Keep the full scene roughly within a 16:9 or 3:2 footprint when it will be
  presented on screen.
- Use background containers sparingly. Their centred labels can clash with
  children, so give the label a deliberate empty region or keep it very short.
- Put large containers first in the node array so child shapes render above.
- Keep important labels under roughly 32 visible characters per line.
- Use line breaks intentionally; do not rely on accidental wrapping.

## Connector rules

- A board with 20 nodes rarely needs 20 arrows. Use three to eight story arrows.
- Connect major states, not every card to its nearest neighbour.
- Route across whitespace. When an arrow crosses a node or label, change its
  bend or remove the less important connector.
- Edge labels should be verbs: `CHOOSE`, `PACKAGE`, `PUBLISH`, `REVIEW`.
- Curved arrows feel hand-drawn and preserve the teaching-board character.

## Colour semantics

Use a small repeatable vocabulary:

| Meaning | Suggested colour/fill |
|---|---|
| Primary actor or current action | blue + semi |
| Public/target zone | violet + none |
| Approved/safe/ready | green + none or semi |
| Warning/private/excluded | orange or red + pattern |
| Neutral file or evidence | grey + none |
| Main structure | black + none |

## What to avoid

- One large generated image pretending to be a whiteboard.
- A sparse grid of generic post-its.
- More edge labels than node labels.
- Huge text boxes centred behind other content.
- Decorative icons that do not teach anything.
- Adding a second canvas technology when Bluplai owns the tldraw surface.
- Declaring success without a live visual inspection at zoom-to-fit.
