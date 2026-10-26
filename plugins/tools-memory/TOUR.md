# Tour: module 12, tools: memory

`/aios learn 12 tools-memory` follows these steps, one at a time. Show the real output, then check it.
Never change a member's database during the tour. Never paste credentials into the chat.

## Step 1: Find the command
- **Command:** `tools-memory --version`, then `tools-memory doctor`
- **They should see:** what is ready and the install line for the rest.

## Step 2: The check on practice databases
- **Command:** `tools-memory sample ~/Memory-practice`, then `tools-memory check ~/Memory-practice/acme-orders_v1.db`
- **They should see:** `NOT READY` and the row-number reason. Then `acme-orders_v2.db` says `READY`.

## Step 3: Their own database
- **Command:** `tools-memory check <their app's database>`
- **Check:** they understand each line before deciding anything.

## Step 4: Turso and db-sync
- **Do:** `turso auth signup`, clone db-sync, back up the database, run db-sync setup on the main machine.
- **Check:** `db-sync status` shows the cloud address set and the copy outside file-sync folders.

## Step 5: Prove it on two machines
- **Do:** one test row on machine A, `db-sync now`, read it on machine B.

## Step 6: The clipboard
- **Do:** turn on Paste's MCP server and add it. Ask the agent for something they copied today.
- **Check:** it finds it, and only that.

## Recap
Check, back up, sync, prove on two machines. Clipboard recall stays on the Mac.
