# 10 · Models, effort and cost
pack: aios-models
cmd: models-check

## 10.1 · Pick the right model and effort, and set medium as my default
what: Shows which model, effort and login each harness uses and where each setting comes from, then sets medium effort as your default.
check: `models-check` shows `effort medium` for Claude Code, and the report lists the three commands you type yourself.
~~~
For each kind of job, tell me the cheapest model and effort that will do it well, and why. Then show me which model I am on now and set medium effort as my default.

<<INSTALL>>

1. Run `models-check`. For each harness, show me the login, model and effort lines, and where each was set. If it warns that `ANTHROPIC_API_KEY` is set, tell me plainly that this terminal bills the paid API, and ask whether I meant that.
2. Set my Claude Code effort to medium the way the pack's `models` skill says. Change only that one setting, and back up the settings file first.
3. Run `models-check` again and show the effort line for Claude Code. It should say medium.
4. Explain the split in four short lines: Sonnet for daily building, Opus for planning, hard bugs and reviews, Haiku for summaries and volume work, and Codex for GPT models.
5. List the commands I type myself in Claude Code, because an agent cannot run them for me: `/model sonnet`, `/effort medium`, `/advisor opus` and `/usage`. Say in one line what each does.

<<RULES>>

<<FINISH m10-models>>
~~~

## 10.2 · How much of my Claude week have I used?
what: Reads your plan's usage windows (the five-hour session and the week) and says in one line whether your week will last until the reset.
check: The report shows each window's percentage and reset time, and one plain-English answer.
~~~
How much of my Claude week have I used, and will it last until the reset?

Here is how:
1. Run `bb settings usage` and show me each usage window for Claude: how much is used and when it resets. If it shows no usage for Claude (for example, when Claude signs in through a proxy), say so plainly, tell me to type `/usage` in Claude Code instead, and stop: never guess a number.
2. Work out a simple forecast: the share used so far against the share of the week gone. Say in one line whether it will last.
3. If it will not last, give me two plain options: lower effort for routine jobs, or a second login in the account pool (prompt 10.3).
4. Tell me that with BB Overlay I can hover the usage line under the chat box to see the same windows as charts.

<<RULES>>

<<FINISH m10-usage>>
~~~

## 10.3 · Add my second Claude login to the account pool
what: Switches on bb's account pool and starts adding a second Claude login, so bb moves new chats to it when the first plan runs out. You finish the sign-in in your browser.
check: `bb pool account list` shows both accounts enabled after you sign in.
~~~
Add my second Claude login to the account pool and show me both accounts and how much each has left. If I do not have a second Claude subscription, say so and stop.

Here is how:
1. Read `bb pool --help` and `bb pool account add --help`.
2. Switch the pool on: `bb plugin enable account-pool`. It changes bb's settings: I allow that for this command, so if the sandbox blocks it, run it outside the sandbox.
3. Run `bb pool status` and `bb pool account list` and show me what is there now.
4. Keep routing off until an account is signed in, so new chats are never sent to an empty pool: `bb pool routing claude --off`.
5. Start adding the second login: `bb pool account add --provider claude --login`. It prints a sign-in link and a session id. Do not try to sign in for me. Give me the link and the exact next command, `bb pool account login-complete --session <id> --code-stdin`, to run with the code from my browser.
6. Tell me how to finish afterwards: when `bb pool account list` shows both accounts enabled, switch routing on with `bb pool routing claude`. Lower priority numbers run first: `bb pool account priority <id> 10`.

<<RULES>>

<<FINISH m10-account-pool>>
~~~
