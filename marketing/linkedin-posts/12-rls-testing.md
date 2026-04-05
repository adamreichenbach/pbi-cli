<!-- Post 12 | Phase 3: Skill Deep Dives | Day 12 -->
<!-- Image: rls-testing.png (Test Row-Level Security in Seconds) -->

Setting up Row-Level Security in Power BI Desktop means clicking through multiple dialogs, switching tabs, testing manually.

Create a role. Switch to the DAX editor. Write the filter. Go to "View as Roles." Pick the role. Check the visuals. Repeat for every role.

With 𝗽𝗯𝗶-𝗰𝗹𝗶, I did this in one conversation:

1. "Create an RLS role called Europe Sales" ✅
2. "Filter the Region table where Continent = Europe" ✅
3. "Run a query as that role to verify" ✅

Claude created the role, added the filter expression, then executed a DAX query 𝗮𝘀 𝘁𝗵𝗮𝘁 𝗿𝗼𝗹𝗲 to validate it. Result: 12 of 48 regions visible. Exactly right. 🔒

Build, test, and validate. All from one place. No tab switching, no dialog hunting, no manual verification. Add more roles the same way. Scale security without scaling complexity.

Build and validate security from conversation.

GitHub: https://github.com/MinaSaad1/pbi-cli
Learn more: mina-saad.com/pbi-cli

#PowerBI #RowLevelSecurity #RLS #ClaudeCode #VIbeModeling #OpenSource #DataSecurity #AI
