# Prompts: tools-reverse

Paste one into Claude Code, Codex or Cursor.

## 1. See what a good investigation looks like

```text
Use tools-reverse. Make the practice investigation in ~/Reverse-practice, check it, and explain the difference between an observed and an inferred finding.
```

**What it does:** writes a fictional investigation of a price calculator and checks it.
**How you know it worked:** the check says `PASS`, and you can say why "discount codes are checked on the server" is
inferred, not observed.

## 2. How does this website feature work?

```text
Use tools-reverse and REA. Explain how the pricing calculator on my own website works, with the evidence for each step. Start with the scope file.
```

**What it does:** writes the scope (your site, your basis), analyses the shipped JavaScript with REA, and fills in
the findings.
**How you know it worked:** every finding cites an REA evidence id, the check says `PASS`, and anything the page cannot
show is listed under Unknowns.

## 3. What changed between two versions?

```text
Use tools-reverse and REA. Compare version 1.2 and 1.3 of my desktop app in ~/Builds and tell me what behaviour changed, with evidence, and what is only a guess.
```

**What it does:** compares the two builds with REA and separates proven changes from candidates.
**How you know it worked:** each change has evidence from both versions, and possible changes are marked inferred.
