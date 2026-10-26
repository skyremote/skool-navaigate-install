# 01 · Start here
pack: aios
cmd: aios-guide

## 1.1 · Install the AIOS and see where you start
what: Installs the start pack, reads what this computer already has, and shows the twelve modules with your next step.
check: The report lists the modules, says `aios` is installed, and names module 1 as your next module.
~~~
I am starting YOUR AIOS 2.0 in this folder. Set up the start pack and show me where I stand.

<<INSTALL>>

1. Run `aios-guide next`. Tell me which harness I am in, which packs are installed and my next module.
2. Run `aios-guide list`. Show the modules as a short table: module, pack, installed yes or no.
3. Run `aios-guide find set up my brain`. Check that the first line names `aios-brain`.
4. Run `ls -A` in this folder. Tell me whether it is empty, halfway (it already has an AGENTS.md, a CLAUDE.md or project files) or already running. Change nothing.
5. Run `aios-guide verify aios`. It must print a line that starts with `OK aios`.

Do not record module 1 as complete. I will do that myself once I am happy.

<<RULES>>

<<FINISH m01-start-here>>
~~~

## 1.2 · Install the whole AIOS in one go (optional)
what: Installs every core pack for modules 2 to 11 at once, then proves each one.
check: The report shows one `OK` line per core pack, and tells you to restart Claude so the new commands load.
~~~
I want the whole AIOS framework installed now, not one pack at a time.

<<INSTALL>>

1. Run `aios-guide install aios-complete`. It installs the start pack, the memory pack and every core pack for modules 2 to 11.
2. For each pack it installed, run `aios-guide verify <pack>` and keep the line it prints.
3. Run `aios-guide list` and show which packs are now installed.
4. Do not install the shelf packs (module 12). I will add those when I need them.

Tell me plainly that I must start a new chat (or type `/reload-plugins` in Claude Code) before the new commands load.

<<RULES>>

<<FINISH m01-install-everything>>
~~~
