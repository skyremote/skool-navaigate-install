# Prompts: shelf-diagrams

Paste one of these into Claude. It writes the D2 source, renders a PNG, looks at the picture, and fixes what is ugly before it hands the diagram over. You need D2 installed (see the README).

Every prompt below was run headless in a clean sandbox with this pack installed, on the fictional data shown.
Replace the sample names and figures with your own.

## Prompt 1: A client version and an expanded version of one flow

**You need:** D2 installed (`d2 --version` works).

```text
Use the diagrams skill. Draw how an online order moves through Northwind Bakery: customer places an order on the website, payment is taken, the order lands on the kitchen screen, the baker bakes it, the order is packed, and the customer collects it or a courier delivers it. Make two versions: a one-glance version for a client, and an expanded version for me with the systems and the hand-offs. Save the D2 source in diagrams/ and render both to PNG. Look at each picture and fix anything ugly before you tell me you are done.
```

## Prompt 2: A data pipeline for your own head

**You need:** D2 installed.

```text
Use the diagrams skill. This diagram is for my own head, so keep the detail. Acme Studio pipeline: supplier invoices arrive by email, a parser pulls the totals, the totals go into a spreadsheet, a monthly report is built from the spreadsheet, and I get a person check before the report goes to the accountant. Draw it as a source, store, ask pipeline with the human checkpoint clearly marked. Render a PNG, look at it, and fix overlaps.
```

## Prompt 3: A funnel for a team document

**You need:** D2 installed.

```text
Use the diagrams skill. I need a funnel diagram for a team document about the Acme Studio course: attention, lesson, install, result. Under each stage put one line saying what the learner does and one line saying what we measure. Render a PNG that fits on one slide, look at it, and fix anything crammed or overlapping.
```
