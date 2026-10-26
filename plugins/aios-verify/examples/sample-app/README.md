# Sample app for module 8

A tiny fictional price list for Acme Studio: `prices.py`, its tests and a build that writes
`dist/index.html`. Copy it somewhere, make it a git repository, and follow the lesson:

```
cp -R plugins/aios-verify/examples/sample-app ~/acme-prices && cd ~/acme-prices
git init -q && git add -A && git commit -qm "Start"
aios-verify init
aios-verify run
```

Then break a test (for example change `'£12.34'` to `'£12.35'`), ask Claude Code to make any
small change and finish, and watch the Stop gate send it back.
