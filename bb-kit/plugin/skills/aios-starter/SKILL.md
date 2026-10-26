---
name: aios-starter
description: The YOUR AIOS 2.0 prompt library in bb. Use when the member asks for the next AIOS prompt, a module's prompts, or to start an AIOS module from bb.
---

# AIOS Starter

The member's course prompts live in this plugin, one to three per module, fourteen modules.

- `bb aios-kit list` lists every module and prompt id (1.1, 2.1 ... 12v.2).
- `bb aios-kit show <id>` prints one prompt exactly as the member would paste it.
- `bb aios-kit start <id> [--project <id>]` starts a new Claude chat with that prompt in the member's AIOS project.
- `bb aios-kit star` saves every prompt in bb's Prompt Library, so Ctrl+R in any chat box finds them by typing "AIOS".

The same prompts show on the "AIOS course" page in the bb sidebar, with Start chat and Copy buttons.

Rules:
- Run prompts in order inside a module. A later prompt says so when it needs an earlier one.
- Never edit a prompt's "edit" lines for the member without asking: they hold the member's own details.
- A prompt installs its own pack. In bb's Auto mode, the prompt itself allows the install commands to run outside the sandbox.
