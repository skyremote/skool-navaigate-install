# The decision record: rules

A decision record is a working document, not a summary. Someone who missed the call reads it and knows what was
agreed, who does what next, and what is still open. Every line points back to the transcript.

## Shape

```markdown
# Decision record: <meeting title>

Meeting: <title>, <date>. Source: <transcript file>.

## Decisions
- <what was decided> (quote: "<the words that show it>")

## Actions
- <action> | Owner: <name said in the call, Me, or not stated> | Due: <date said in the call, or not stated> | Quote: "<the words>"

## Open questions
- <what is open> (who can answer it, or not stated)

## Source
<transcript file>
```

## How to read a transcript

1. Read the whole transcript before you write anything.
2. Mark each statement as one of four kinds:
   - **fact**: said plainly in the call ("we take about 40 cake orders a week");
   - **inference**: follows from what was said, but nobody said it outright;
   - **assumption**: something the plan relies on that nobody checked;
   - **unknown**: a gap the call left open.
3. Only facts become decisions. Inferences and assumptions go under open questions, labelled as such.
4. An action needs a verb and a person. If nobody took it on, the owner is `not stated`. Say so to the member
   and suggest who might own it, marked "proposed".

## Guardrails (the `check` command enforces the first three)

- An owner is a name that appears in the transcript, `Me`, or `not stated`.
- A number appears only if it was said in the call. No estimates, savings, headcounts or ROI.
- A quote is word for word from the transcript.
- Dates: write the date as it was said ("Friday 31 October"). If none was said, write `not stated`.
- Distil. Drop the filler, false starts and small talk. Never quote filler.
- If the transcript is cut off or unclear in places, say where in the Open questions section.

## Next steps the member may ask for

- **Follow-up email:** one paragraph on what was agreed, the actions with owners, and one question. Draft only.
- **Tasks:** one task per action, with the owner and due date as written in the record.
- **30/60/90 plan:** group the actions by when they are due. Where no date was said, put them under "not scheduled",
  never in a guessed slot.
