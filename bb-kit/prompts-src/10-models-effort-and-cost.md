# 10 · Models, effort and cost
pack: aios-models
cmd: models-check

## 10.1 · See which model you are on and set medium effort
what: Shows which model, effort and login each harness uses and where each setting comes from, then sets medium effort as your default.
check: `models-check` shows `effort medium` for Claude Code, and the report lists the three commands you type yourself.
~~~
Set up module 10 on this computer: see my models, then set a sensible default.

<<INSTALL>>

1. Run `models-check`. For each harness, show me the login, model and effort lines, and where each was set. If it warns that `ANTHROPIC_API_KEY` is set, tell me plainly that this terminal bills the paid API, and ask whether I meant that.
2. Set my Claude Code effort to medium the way the pack's `models` skill says. Change only that one setting, and back up the settings file first.
3. Run `models-check` again and show the effort line for Claude Code. It should say medium.
4. Explain the split in four short lines: Sonnet for daily building, Opus for planning, hard bugs and reviews, Haiku for summaries and volume work, and Codex for GPT models.
5. List the commands I type myself in Claude Code, because an agent cannot run them for me: `/model sonnet`, `/effort medium`, `/advisor opus` and `/usage`. Say in one line what each does.

<<RULES>>

<<FINISH m10-models>>
~~~

## 10.2 · Prepare a second login (only if you have a second plan)
what: Prepares a second Claude login in its own folder, with a short command to start it, so you can switch when one plan runs out. You do the sign-in yourself.
check: The report shows the sign-in command and the alias line to add. After you sign in, `models-check` counts two logins.
~~~
I have a second Claude subscription. Prepare a second login called "work" so I can switch to it when my main plan runs out.

<<INSTALL>>

1. Run `models-check login add work`. Show me the sign-in command and the alias line it prints.
2. Do not run the sign-in yourself: it opens a browser and needs me. Tell me to run it in a terminal.
3. Tell me where to add the alias line (`~/.zshrc` on a Mac) and to open a new terminal after.
4. Tell me how to check it: run the alias, then `/status`, and run `models-check`, which should end with `Claude logins ready for failover: 2`.
5. Remind me that plugins are per login, so I install my AIOS packs inside the second login too.

If I do not have a second subscription, this prompt is not for me: say so and stop.

<<RULES>>

<<FINISH m10-second-login>>
~~~
