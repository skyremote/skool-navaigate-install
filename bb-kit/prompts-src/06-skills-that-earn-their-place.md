# 06 · Skills that earn their place
pack: aios-skills
cmd: aios-skill

## 6.1 · Turn a weekly job into a skill
what: Turns one job you explain to Claude every week into a skill (a saved set of steps), with three test cases, and checks it.
check: `aios-skill check` says PASS for the new skill and counts three cases.
~~~
About my weekly job (edit these lines before you send):
- The job: turn rough meeting notes into a list of actions.
- What I type to ask for it: "actions from these notes".
- The check that proves it is done: every action has an owner and a due date, and nothing in the notes is missing.

Set up module 6: turn this job into a skill with its own tests.

<<INSTALL>>

1. Pick a short name for the job, lower case with dashes (for example `meeting-actions`). If a skill with that name exists, pick another name.
2. Run `aios-skill new <name> --description "<what it does>. Use when <the words I type>."`. Show where it was created and the files it made.
3. Run `aios-skill check <the skill folder>`. It should fail with "still contains TODO" lines. That is expected.
4. Fill in SKILL.md: replace each `TODO:` line with the steps, the check above and the one mistake to avoid. The pack has a finished example at `examples/meeting-actions/SKILL.md` inside its plugin folder; read it for the style.
5. Fill in the three test cases under `evals/`: `should-fire` (a message I would type, without naming the skill), `should-not-fire` (a nearby job the skill must leave alone) and `edge-case`. Each `graders/result.md` gets one PASS line and one FAIL line.
6. Run `aios-skill check <the skill folder>` again. It must say PASS and count 3 cases.

<<RULES>>

<<FINISH m06-new-skill>>
~~~

## 6.2 · See what your skills cost and pick one to hide
what: Lists every skill you have with the tokens it costs on every turn, and previews hiding one you never use. Nothing is hidden yet.
check: The report lists your skills sorted by cost, and shows the dry run for one skill you could hide.
~~~
Show me what my skills cost me, and which one I could hide.

<<INSTALL>>

1. Run `aios-skill audit`. Show me the skills sorted by tokens per turn, and mark which ones come from plugins.
2. Pick the one skill that costs the most tokens per turn and is not from a plugin. If every skill comes from a plugin, say so, and tell me that plugin skills are switched off with `/plugin` instead.
3. Preview hiding it: `aios-skill hide <skill> off --dry-run`. Show me the result. Do not hide it for real.
4. Give me the exact command to hide it for real, and the one to undo it, so I can decide.
5. Tell me that `/skill-doctor` in Claude Code shows which skills were never used.

<<RULES>>

<<FINISH m06-skill-costs>>
~~~

## 6.3 · Test your skill against no skill
what: Runs your skill's three test cases with and without the skill, so you see whether it really helps. It uses your own Claude plan for six short runs.
check: The report shows WITH, WITHOUT and the difference for each case, and whether the skill fired.
~~~
Test the skill I made in prompt 6.1 against no skill. If there is no skill with three filled test cases, stop and tell me to run prompt 6.1 first.

<<INSTALL>>

1. Find the skill folder I made (run `aios-skill audit` if you need the path) and run `aios-skill check <folder>`. It must pass first.
2. Run `claude plugin eval <folder> --runs 1 --no-publish`. If it asks whether to trust the folder, answer yes. It makes six short runs on my plan.
3. Show me, for each case, the WITH score, the WITHOUT score, the difference, and whether the skill fired.
4. If the skill did not fire, rewrite the "Use when" words in its description and run the eval once more. If the difference is zero or below, tell me the model already does this job well without the skill.

<<RULES>>

<<FINISH m06-skill-eval>>
~~~
