# Integration: aios-skills (stream C)

The chief of staff applies these changes to shared files. This stream did not edit them.

## 1. `.claude-plugin/marketplace.json`
Append the object in `MARKETPLACE_ENTRY.json` to `plugins`, after `aios-brain`.

## 2. `scripts/install_pack.py` (one patch for all three stream C packs)
The installer accepts only `aios` and `aios-brain`. This patch:
- lists every folder in `plugins/` that has a manifest as a valid pack;
- makes every pack except `aios` depend on `aios` (same check `aios-brain` used);
- links each file in a pack's `bin/` into `~/.local/bin` (all packs except `aios` and `aios-brain`,
  which keep their current handling), refusing to replace a file it did not create.

The sandbox install proof ran with this patch applied to a temporary copy (record kept outside the repo, in the course build-proof folder).

```diff
--- a/scripts/install_pack.py
+++ b/scripts/install_pack.py
@@ -64,13 +64,17 @@
     return result
 
 
+def available_packs():
+    return sorted(p.name for p in (ROOT/'plugins').iterdir() if (p/'.claude-plugin/plugin.json').is_file())
+
+
 def install(pack):
     home = Path.home()
     plugin = ROOT/'plugins'/pack
     if not plugin.is_dir():
-        raise ValueError('Unknown pack. Available: aios, aios-brain')
-    if pack=='aios-brain' and not all((home/d/'aios').is_symlink() and (home/d/'aios').resolve()==(ROOT/'plugins/aios/skills/aios').resolve() for d in ('.codex/skills','.cursor/skills','.agents/skills')):
-        raise ValueError('aios-brain depends on aios. First run: ./install.sh aios')
+        raise ValueError('Unknown pack. Available: '+', '.join(available_packs()))
+    if pack!='aios' and not all((home/d/'aios').is_symlink() and (home/d/'aios').resolve()==(ROOT/'plugins/aios/skills/aios').resolve() for d in ('.codex/skills','.cursor/skills','.agents/skills')):
+        raise ValueError(pack+' depends on aios. First run: ./install.sh aios')
     manifest = json.loads((plugin/'.claude-plugin/plugin.json').read_text())
     links = []
     for parent in ('.codex/skills','.cursor/skills','.agents/skills'):
@@ -80,6 +84,13 @@
                 if not dest.is_symlink() or ROOT not in dest.resolve().parents:
                     raise ValueError('Existing skill preserved: '+str(dest)+'. Move it aside yourself before opting into 2.0.')
             links.append((source,dest))
+    if pack not in ('aios','aios-brain') and (plugin/'bin').is_dir():
+        # Packs ship small commands in bin/; link each one, never replacing a foreign file.
+        for source in sorted(p for p in (plugin/'bin').iterdir() if p.is_file()):
+            command = home/'.local/bin'/source.name
+            if (command.exists() or command.is_symlink()) and (not command.is_symlink() or ROOT not in command.resolve().parents):
+                raise ValueError('Existing '+source.name+' executable preserved; move it aside before opting into this pack')
+            links.append((source,command))
     configs = []
     if pack=='aios-brain':
         command = home/'.local/bin/brain'
@@ -121,12 +132,12 @@
         print('Linked '+str(dest.relative_to(home)))
     receipt = home/'.local/share/aios/packs'/f'{pack}.json'
     atomic_write(receipt,json.dumps({'name':pack,'version':manifest['version'],'root':str(plugin),'harnesses':['codex','cursor','agents']},indent=2)+'\n')
-    print('Installed '+pack+' '+manifest['version']+'. Restart Codex and Cursor. Add ~/.local/bin to PATH for brain.')
+    print('Installed '+pack+' '+manifest['version']+'. Restart Codex and Cursor. Add ~/.local/bin to PATH for pack commands.')
 
 
 def main():
     parser = argparse.ArgumentParser(description='Install one AIOS 2.0 pack for Codex and Cursor. No Claude config is changed.')
-    parser.add_argument('pack',choices=['aios','aios-brain'])
+    parser.add_argument('pack',choices=available_packs())
     args = parser.parse_args()
     try:
         install(args.pack)
```

## 3. `plugins/aios/scripts/status.py` and `plugins/aios/skills/aios/SKILL.md`
The start pack names module 6's pack `aios-skills-kit`. The pack is `aios-skills`.
- `status.py`, `PACKS`: replace `'aios-skills-kit'` with `'aios-skills'`.
- `status.py`, the `skill = ...` line: map packs to a skill they install so Codex/Cursor
  links are detected: `{'aios-skills':'skill-craft','aios-agents':'agent-or-not','aios-verify':'verify-setup'}`.
- `SKILL.md`, line 6 of the path: `aios-skills-kit` becomes `aios-skills`.
- `SKILL.md`: "Only `aios` and `aios-brain` ship in phase 1" becomes a list that includes
  `aios-skills`, `aios-agents` and `aios-verify` once they are merged.

## 4. Root `README.md`
Add one row per pack to the pack table (if there is one): `aios-skills`, module 6,
"Write, measure, hide and test skills".

## Kept out of the repo (Daniel, 26 October 2026)
The repository holds plugins, skills, tests, evals and install instructions only. These stay
outside it, in the course folders the chief of staff publishes from:
- `lessons/` (lesson Markdown and Skool HTML)
- `video/` (tutorial scripts, shot lists, SRTs, clips)
- `plugins/*/proof/` (eval results, sandbox install records, comparisons)
