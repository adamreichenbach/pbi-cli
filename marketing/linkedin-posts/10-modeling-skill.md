<!-- Post 10 | Phase 3: Skill Deep Dives | Day 10 -->
<!-- Image: modeling-skill.png (Describe schema, Claude builds it) -->

Describe your schema in plain English. Claude builds it.

I told Claude: "Create a star schema with Sales as the fact table, and Products, Calendar, Customers, and Store as dimensions."

In seconds, Claude created:

- 📦 𝟱 𝘁𝗮𝗯𝗹𝗲𝘀 with appropriate columns and data types
- 🔗 𝟰 𝗿𝗲𝗹𝗮𝘁𝗶𝗼𝗻𝘀𝗵𝗶𝗽𝘀, all one-to-many, single direction
- 📅 Calendar 𝗱𝗮𝘁𝗲 𝘁𝗮𝗯𝗹𝗲 properly configured
- 📐 Properly structured for performance and usability

No drag-and-drop. No switching between diagram view and table properties. No manual relationship setup where you pick the wrong cardinality and spend 20 minutes figuring out why your numbers are doubled.

The modeling skill handles tables, relationships, measures, and date table configuration. All from conversation.

Need to iterate? "Add a Geography dimension" or "Create a Total Revenue measure on the Sales table." Claude keeps building on what's already there. 🔧

From description to working schema in one prompt.

GitHub: https://github.com/MinaSaad1/pbi-cli
Learn more: mina-saad.com/pbi-cli

#PowerBI #DataModeling #StarSchema #ClaudeCode #VIbeModeling #OpenSource #SemanticModel #AI
