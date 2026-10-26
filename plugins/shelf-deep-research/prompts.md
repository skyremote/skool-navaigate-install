# Prompts: shelf-deep-research

Paste one of these into Claude. It scopes, recons, reads the sources, runs a critic pass and writes up with confidence labels. Research takes a few minutes, so let it run.

Every prompt below was run headless in a clean sandbox with this pack installed, on the fictional data shown.
Replace the sample names and figures with your own.

## Prompt 1: A full research pass with a labelled write-up

**You need:** Exa and Firecrawl keys in ~/.claude/.env. Papers need no key.

```text
Use the deep-research skill. Question: do loyalty apps bring independent bakeries more repeat visits than paper punch cards? I run Northwind Bakery, so I care about what is true for a small shop. I agree the scope: small independent food shops, evidence from the last five years. Keep it small: at most 4 web sources, 3 papers and 3 Reddit threads, and no video. Do the critic pass, then write the answer to research/bakery-loyalty_v1.md with a confidence label on every claim and a link for every source. Put anything you could not confirm in its own section.
```

## Prompt 2: What practitioners say, from Reddit and newsletters only

**You need:** No paid key. Reddit and Substack are read without one (Exa or Firecrawl help find newsletter posts).

```text
Use the deep-research skill, practitioner voices only: Reddit and Substack, no video and nothing paid. Question for Acme Studio: do small design studios do better with fixed-price projects or hourly billing? Read at most 3 threads and 3 newsletter posts. Quote people word for word, name where each quote came from, and label how sure we can be. Save it as research/billing_v1.md.
```

## Prompt 3: Run only the critic pass on notes you already have

**You need:** A file called claims.md in the folder. No key.

```text
Use the deep-research skill, but only the critic pass. The file claims.md in this folder holds claims and sources I gathered for Northwind Bakery. Score each source on recency, source type, specificity and independence, say which claims to drop, which to keep and which need a second source, and write that to research/critic_v1.md. Do not search for anything new.
```
