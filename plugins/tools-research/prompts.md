# Prompts: tools-research

Paste one into Claude Code, Codex or Cursor.

## 1. What do people who actually do it say?

```text
Use tools-research. Research what small business owners on Reddit and in Substack newsletters say about AI receptionists this year. Put every finding in a ledger with its link and an honest confidence label, run the check, then give me a one-page summary.
```

**What it does:** asks you three scope questions, searches Reddit (your app) and Substack, reads the best items and
writes a ledger.
**How you know it worked:** the check says `PASS`, every finding has a link you can open, and the summary keeps the
low-confidence points labelled as low.

## 2. Is there research on this?

```text
Use tools-research. Find research papers on online ordering for small food businesses, tell me which have a free PDF, and summarise the three most relevant in plain English with their links.
```

**What it does:** searches OpenAlex by relevance, reads the abstracts and free PDFs, and summarises.
**How you know it worked:** three papers with a DOI link each, and the free PDF link where one exists. No paper is
summarised from its title alone.

## 3. Read one newsletter properly

```text
Use tools-research. Read the last five posts from www.lennysnewsletter.com that are free, and list what each one argues, with the link.
```

**What it does:** lists the archive, skips paid posts, reads the free ones.
**How you know it worked:** five links, each with a one-line argument, and paid posts listed as skipped.
