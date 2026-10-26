# Integration notes for aios-harnesses (and aios-bb)

These are changes to shared files that stream B does not own. The chief of staff applies them when merging.

## 1. `.claude-plugin/marketplace.json`
Add the two entries from `plugins/aios-harnesses/MARKETPLACE_ENTRY.json` and `plugins/aios-bb/MARKETPLACE_ENTRY.json`
to the `plugins` array, after `aios-brain`.

## 2. `scripts/install_pack.py` (so `./install.sh aios-harnesses` and `./install.sh aios-bb` work in Codex and Cursor)
Apply this patch from the repository root with `git apply plugins/aios-harnesses/install_pack.patch`.
It generalises the pack list, makes every pack except `aios` depend on `aios`, and links each pack's one command
(`harness`, `aios-bb`) into `~/.local/bin`, with the same refuse-to-overwrite rule the brain uses.
The sandbox proof ran against a copy of the repository with this patch applied (`tests/aios-harnesses/sandbox_proof.py`).

```diff
--- a/scripts/install_pack.py	2026-10-26 10:25:21
+++ b/scripts/install_pack.py	2026-10-26 10:25:21
@@ -11,6 +11,9 @@
 from pathlib import Path
 
 ROOT = Path(__file__).resolve().parents[1]
+# Packs that put one command on PATH for Codex, Cursor and the terminal.
+PACK_BINS = {'aios-harnesses': 'harness', 'aios-bb': 'aios-bb'}
+PACKS = ['aios', 'aios-brain'] + sorted(PACK_BINS)
 
 
 def atomic_write(path,text):
@@ -68,9 +71,9 @@
     home = Path.home()
     plugin = ROOT/'plugins'/pack
     if not plugin.is_dir():
-        raise ValueError('Unknown pack. Available: aios, aios-brain')
-    if pack=='aios-brain' and not all((home/d/'aios').is_symlink() and (home/d/'aios').resolve()==(ROOT/'plugins/aios/skills/aios').resolve() for d in ('.codex/skills','.cursor/skills','.agents/skills')):
-        raise ValueError('aios-brain depends on aios. First run: ./install.sh aios')
+        raise ValueError('Unknown pack. Available: '+', '.join(PACKS))
+    if pack!='aios' and not all((home/d/'aios').is_symlink() and (home/d/'aios').resolve()==(ROOT/'plugins/aios/skills/aios').resolve() for d in ('.codex/skills','.cursor/skills','.agents/skills')):
+        raise ValueError(pack+' depends on aios. First run: ./install.sh aios')
     manifest = json.loads((plugin/'.claude-plugin/plugin.json').read_text())
     links = []
     for parent in ('.codex/skills','.cursor/skills','.agents/skills'):
@@ -81,6 +84,11 @@
                     raise ValueError('Existing skill preserved: '+str(dest)+'. Move it aside yourself before opting into 2.0.')
             links.append((source,dest))
     configs = []
+    if pack in PACK_BINS:
+        command = home/'.local/bin'/PACK_BINS[pack]
+        if (command.exists() or command.is_symlink()) and (not command.is_symlink() or ROOT not in command.resolve().parents):
+            raise ValueError('Existing '+PACK_BINS[pack]+' executable preserved; move it aside before opting into this pack')
+        links.append((plugin/'bin'/PACK_BINS[pack],command))
     if pack=='aios-brain':
         command = home/'.local/bin/brain'
         if (command.exists() or command.is_symlink()) and (not command.is_symlink() or ROOT not in command.resolve().parents):
@@ -121,12 +129,13 @@
         print('Linked '+str(dest.relative_to(home)))
     receipt = home/'.local/share/aios/packs'/f'{pack}.json'
     atomic_write(receipt,json.dumps({'name':pack,'version':manifest['version'],'root':str(plugin),'harnesses':['codex','cursor','agents']},indent=2)+'\n')
-    print('Installed '+pack+' '+manifest['version']+'. Restart Codex and Cursor. Add ~/.local/bin to PATH for brain.')
+    print('Installed '+pack+' '+manifest['version']+'. Restart Codex and Cursor. Add ~/.local/bin to PATH for brain.' if pack=='aios-brain' else
+          'Installed '+pack+' '+manifest['version']+'. Restart Codex and Cursor.'+(' Add ~/.local/bin to PATH for '+PACK_BINS[pack]+'.' if pack in PACK_BINS else ''))
 
 
 def main():
     parser = argparse.ArgumentParser(description='Install one AIOS 2.0 pack for Codex and Cursor. No Claude config is changed.')
-    parser.add_argument('pack',choices=['aios','aios-brain'])
+    parser.add_argument('pack',choices=PACKS)
     args = parser.parse_args()
     try:
         install(args.pack)
```

## 3. `plugins/aios/skills/aios/SKILL.md`
Change the line "Only `aios` and `aios-brain` ship in phase 1." to
"`aios`, `aios-harnesses`, `aios-bb` and `aios-brain` ship now." so `/aios` offers modules 3 and 4.

## 4. `README.md` and `ROADMAP.md`
List module 3 (`aios-harnesses`) and module 4 (`aios-bb`) as available.

## 5. Privacy grep hits in shared files (inherited from `aios-v2`, not from this stream)
The house privacy grep finds machine paths in files this stream must not edit: `README.md`, `proof/*.md`,
`proof/*.json` and `plugins/aios-brain/aios_brain/sync.py`. Stream B's own paths are clean. Clean those before
the repository goes public.

## 6. Plugin evals skip packs that declare `dependencies`
`claude plugin eval plugins/<pack>` loads no plugin when `plugin.json` lists `"dependencies": ["aios"]`, and scores
the run as if the pack were absent (no error is shown). The eval notes are in the build-proof folder (see section 7). Until this changes, run evals on a
copy with the `dependencies` line removed, and re-check `aios-brain`'s eval the same way.

## 7. Kept out of the repo (Daniel, 26 October 2026)
The repo holds only packs, their README and install steps, tests and evals. These stay out of it:
- `lessons/` (lesson sources and Skool HTML): `NAS_Local/150_Navbot_Classroom/aios-2/lessons_v2/<NN>-<slug>/`
- `video/` (tutorial scripts, shot lists, SRTs, clips): `NAS_Local/150_Navbot_Classroom/aios-2/tutorials_v2/<NN>-<slug>/`
- `plugins/*/proof/` (sandbox and eval proof notes): `NAS_Local/150_Navbot_Classroom/aios-2/build-proof/<pack>/`
