# Your AIOS coach

A tab that already knows the Your AIOS course. You host it. Your
`OPENAI_API_KEY`. It is not GPLS and it is not on navaigate.dev.

## Put it online

```bash
npx vercel --yes
```

In the Vercel project:

- `OPENAI_API_KEY` — yours
- `OPENAI_MODEL` — optional. Tries `gpt-5.6-luna`, then `gpt-4o-mini`

Local:

```bash
npx vercel dev
```

## Knowledge

`knowledge/your-aios.json` holds the titles and Skool links of the twenty-six
lessons, plus the community skill fronts. The lesson text lives on Skool only, so
add your own notes in `extra/` if you want the coach to answer from more.

Do not scrape live Skool pages. If you want more, drop markdown in
`knowledge/extra/` or list URLs in `knowledge/extra-urls.txt`, pull them
with `/web-scrape`, then:

```bash
python3 scripts/build-knowledge.py
```
