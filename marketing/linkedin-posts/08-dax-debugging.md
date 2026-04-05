<!-- Post 08 | Phase 3: Skill Deep Dives | Day 8 -->
<!-- Image: dax-debugging.png (Debug DAX Like Never Before) -->

Your YTD Revenue measure is returning blank. What do you do?

Most people start guessing. Comment out lines. Add variables. Stare at CALCULATE filters. Waste 45 minutes before finding it was a date table issue the whole time.

With 𝗽𝗯𝗶-𝗰𝗹𝗶, I told Claude: "My YTD Revenue measure returns blank. Can you investigate?"

Claude traced the problem like a senior developer would 🔍

- Checked the measure definition. Syntax was fine.
- Checked the DAX logic. TOTALYTD looked correct.
- Checked the Calendar table. Found it. The table wasn't 𝗺𝗮𝗿𝗸𝗲𝗱 𝗮𝘀 𝗮 𝗱𝗮𝘁𝗲 𝘁𝗮𝗯𝗹𝗲.
- Fixed it with one command. Measure started working immediately.

Systematic. Methodical. No guessing.

That's the difference. Claude doesn't just write DAX. It 𝗱𝗲𝗯𝘂𝗴𝘀 it. It reads your model structure, understands context, and traces root causes.

Stop guessing. Let Claude trace it. 🛠️

GitHub: https://github.com/MinaSaad1/pbi-cli
Learn more: mina-saad.com/pbi-cli

#PowerBI #DAX #Debugging #ClaudeCode #VIbeModeling #OpenSource #DataModeling #AI
