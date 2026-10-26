# Prompts: shelf-web-scrape

Paste one of these into Claude. Claude picks the right tool: Exa to find pages, Firecrawl to read one, and the keyless sources for papers.

Every prompt below was run headless in a clean sandbox with this pack installed, on the fictional data shown.
Replace the sample names and figures with your own.

## Prompt 1: Find three good sources and give me the point of each

**You need:** Exa key (EXA_API_KEY) in ~/.claude/.env.

```text
Use the web-scrape skill. I run Northwind Bakery and I am thinking about a loyalty scheme. Find three good sources on how independent bakeries run them. For each source give me the key point in one sentence and its link. Keep the text you pull short: use highlights, not full pages.
```

## Prompt 2: Read a page that only fills in with JavaScript

**You need:** Firecrawl key (FIRECRAWL_API_KEY) in ~/.claude/.env.

```text
Use the web-scrape skill to read https://quotes.toscrape.com/js/ . It only fills in with JavaScript, so a plain fetch comes back empty. Give me the first three quotes with their authors, and tell me which command you used to get them.
```

## Prompt 3: Find recent papers with free PDFs

**You need:** Nothing. Papers come from OpenAlex and Unpaywall, which need no key.

```text
Use the web-scrape skill's academic source to find three recent papers (2022 or later) on customer loyalty programmes in small retail. Give me title, year, citation count and a free PDF link where one exists. Sort by citations.
```
