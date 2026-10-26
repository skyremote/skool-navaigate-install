# 15 · Work from anywhere, and share safely
pack: aios
cmd: aios-guide

## 15.1 · Check my agents from my phone
what: Checks whether this bb is signed in to a getbb.app account (needed for your phone), tells you the one step if it is not, and sends a test notification.
check: The report says whether remote access is on, gives your getbb.app link if it is, and shows the test notification result.
~~~
Set up bb so I can check my agents from my phone, and send me a test notification.

Here is how:
1. Run `bb account --help`, then check whether this bb is signed in to a getbb.app account. If it is not, tell me the one step: run `bb account login` in a terminal (or Settings, Account in bb) and approve the code in my browser. Do not sign in for me.
2. If it is signed in, run `bb connect --help` and give me my bb's https link on getbb.app, so I can open it on my phone and add it to my home screen.
3. Send a test notification: `bb push-notifications test`, and show `bb push-notifications status`. Tell me a phone needs the getbb.app page open once, with notifications allowed.
4. Tell me what I will see on my phone: the same sidebar and chats, and a notification when a chat finishes or needs me.

<<RULES>>

<<FINISH m15-phone>>
~~~

## 15.2 · Run a job on my other machine
what: Lists the machines this bb can use and starts a small job on the other one, so it keeps running with your laptop shut. If you have only one machine, it tells you how to add one.
check: The report lists your machines, and either a new chat running on the other machine or the steps to add one.
~~~
Start this job on my other machine, so it keeps going when I shut my laptop, and tell me when it is done.

The job (edit this line): write a one-page summary of this folder to `80_aios/reports/folder-summary_v1.md`.

Here is how:
1. Run `bb machine list` and show me the machines: name, status.
2. If there is only one machine, stop the job and tell me how to add one: Settings, Machines in bb, then follow the steps for a Mac at home, a mini PC or a small cloud server (VPS). Say that BB Overlay also adds "Send to my always-on machine" when I right-click a chat.
3. If there is a second machine that is connected, write the job to `80_aios/briefs/folder-summary_v1.md` and start it there: `bb thread spawn --project "$BB_PROJECT_ID" --machine "<its name>" --title "Folder summary (other machine)" --prompt-file 80_aios/briefs/folder-summary_v1.md --json`.
4. Wait for it with `bb thread wait <id> --timeout 20m` and show me its answer with `bb thread output <id>`.

<<RULES>>

<<FINISH m15-other-machine>>
~~~

## 15.3 · Hide names before I record or share my screen
what: Turns on BB Overlay's Screen Share mode, which greys out every name, email, phone number and amount on every bb screen, then checks it is on.
check: `bb screen-share status` says on, and names on your screen show as grey bars.
~~~
Turn on screen share mode before I record, and check it is on.

Here is how:
1. Run `bb screen-share on`, then `bb screen-share status`. If the command is not available, BB Overlay's Screen Share mod is not installed: say so.
2. Tell me what it does: names, emails, phone numbers and amounts turn into grey bars on every screen that shows this bb, my phone included. The agent still sees the real text.
3. Tell me the two things it does not do: it does not change what is copied or pasted, so I never paste a key on camera; and it does not hide what is in other apps.
4. Tell me how to switch it off after recording: `bb screen-share off`, or type `/screenshare` again.

<<RULES>>

<<FINISH m15-screen-share>>
~~~
