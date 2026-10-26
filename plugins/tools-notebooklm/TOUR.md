# Tour: module 12, tools: NotebookLM

`/aios learn 12 tools-notebooklm` follows these steps, one at a time. Show the real output, then check it.
Never sign in for the member.

## Step 1: Find the command
- **Command:** `tools-notebooklm --version`, then `tools-notebooklm doctor`

## Step 2: Install the public CLI
- **Command:** `pipx install notebooklm-py`, then the member runs `notebooklm login` in their own terminal.
- **Check:** `tools-notebooklm doctor` says signed in.

## Step 3: Plan the sources
- **Command:** `tools-notebooklm sample ~/NotebookLM-practice`, then `tools-notebooklm plan ~/NotebookLM-practice`
- **They should see:** three ok, one SKIP with the reason.

## Step 4: A practice notebook
- **Command:** `notebooklm create "Practice: Northwind"`, `notebooklm source add` for each ok file, then `notebooklm ask "What is this about?"`
- **Check:** the answer mentions the bakery and the booking page.

## Step 5: Their first audio overview
- **Do:** prompt 2 from prompts.md with their own files.
- **Check:** the MP3 plays, and the notebook shows their sources.

## Recap
Plan, notebook, sources, ask, generate, download.
