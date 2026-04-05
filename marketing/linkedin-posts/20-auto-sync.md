<!-- Post 20 | Technical Showcase: Auto-Sync | Post after #19 -->
<!-- Image: auto-sync-ai.png -->

The biggest problem with editing Power BI reports from code: Desktop doesn't detect file changes on disk.

You edit the PBIR JSON, Desktop ignores it. You save in Desktop, it overwrites your changes. The workaround? Close Desktop, edit files, reopen manually. Every single time. About 45 seconds of friction per edit, plus the risk of losing unsaved work.

So I built 𝗗𝗲𝘀𝗸𝘁𝗼𝗽 𝗔𝘂𝘁𝗼-𝗦𝘆𝗻𝗰 Technique into 𝗽𝗯𝗶-𝗰𝗹𝗶 v3.10.1.

𝗛𝗼𝘄 𝗶𝘁 𝘄𝗼𝗿𝗸𝘀:

1️⃣ Claude executes the CLI to write your PBIR files (page.json, visual.json, filters.json)
2️⃣ Claude snapshots the changes from the last 5 seconds
3️⃣ Claude closes Desktop for you: sends a WM_CLOSE message via pywin32 and auto-accepts the save dialog so nothing is lost
4️⃣ Claude re-applies the snapshots and reopens your .pbip file automatically

~2-5 seconds. Fully automated. You never touch Desktop yourself.

Your unsaved modeling work (measures, relationships) stays safe because Desktop saves before closing. Your report-layer changes (visuals, filters, themes) survive because they're snapshotted and rewritten after Desktop's save. Then Desktop launches right back with everything in place.

This is what makes 𝗩𝗶𝗯𝗲 𝗕𝗜 actually usable. Without it, you'd close Desktop, edit files, reopen manually, every single time. With Auto-Sync, Claude handles the entire close-reopen cycle for you. You just ask for the change and keep working. ✨

GitHub: https://github.com/MinaSaad1/pbi-cli
Details: https://mina-saad.com/pbi-cli

#PowerBI #VibeBi #PBIR #ClaudeCode #OpenSource #PowerBIDeveloper #DataModeling #AI
