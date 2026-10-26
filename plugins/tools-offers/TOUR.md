# Tour: module 12, tools: offers

`/aios learn 12 tools-offers` follows these steps, one at a time. Show the real output, then check it.
Never copy book content from anywhere. The member distils their own copies.

## Step 1: Find the command
- **Command:** `tools-offers --version`
- **They should see:** `tools-offers 2.0.0`.

## Step 2: Install the engine
- **Command:** `tools-offers doctor`, then the clone line it prints, then `tools-offers doctor` again.
- **They should see:** `Growth Engine skills: all five installed`.

## Step 3: The corpus folders
- **Command:** `tools-offers corpus init ~/Hormozi-corpus`
- **They should see:** `Corpus folders ready`.
- **Check:** `ls ~/Hormozi-corpus` shows offers, leads, money-models and EXTRACTION-SUMMARY.md.

## Step 4: One chapter, distilled
- **Do:** the member writes chapter 1 of a book they own in their own words, with `[p.NNN]` markers.
- **Command:** `tools-offers corpus check ~/Hormozi-corpus`
- **They should see:** 1 chapter with pages for that book.

## Step 5: Point the engine at it
- **Command:** `tools-offers corpus point ~/Hormozi-corpus`, read the list, then add `--yes`.
- **They should see:** `Pointed ...` lines. `doctor` then says the corpus is pointed.

## Step 6: First real question
- **Do:** prompt 2 from prompts.md with their own offer.
- **Check:** every claim has a citation, or says it cannot cite yet.

## Recap
Engine, corpus folders, distil your books, point, ask. Cite or say you cannot.
