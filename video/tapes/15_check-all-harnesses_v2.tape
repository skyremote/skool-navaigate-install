Output video/clips/15_check-all-harnesses_v2.mp4
Require python3
Set Shell "bash"
Set Width 1920
Set Height 1080
Set FontFamily "Menlo"
Set FontSize 28
Set LineHeight 1.2
Set Padding 40
Set Theme "Catppuccin Mocha"
Set TypingSpeed 85ms
Set Framerate 30
Hide
Type@0ms `export HOME=/tmp/aios-member-sandbox CLAUDE_CONFIG_DIR=/tmp/aios-member-sandbox/.claude CODEX_HOME=/tmp/aios-member-sandbox/.codex; export PATH="$HOME/.local/bin:$PATH"; export PS1='$ '; unset PROMPT_COMMAND; set +m; cd /tmp/aios-video-checkout-v2; clear`
Enter
Sleep 500ms
Show
Type `python3 plugins/aios/scripts/status.py | more`
Sleep 3s
Enter
Sleep 18s
Space
Sleep 18s
Space
Sleep 18s
Space
Sleep 18s
Space
Sleep 4s
