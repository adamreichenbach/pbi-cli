<!-- Post 09 | Phase 3: Skill Deep Dives | Day 9 -->
<!-- Image: model-health-check.png (Model Health Check audit) -->

When was the last time you audited your semantic model?

Be honest. Most teams ship models to production and never look back. Until something breaks.

I asked Claude to run a 𝗳𝘂𝗹𝗹 𝗵𝗲𝗮𝗹𝘁𝗵 𝗰𝗵𝗲𝗰𝗸 on a production model. One prompt. Here's what came back:

❌ 𝗘𝗿𝗿𝗼𝗿𝘀: Circular dependency between two calculated tables. Missing relationship between Sales and Store.

⚠️ 𝗪𝗮𝗿𝗻𝗶𝗻𝗴𝘀: 12 unused measures. Bidirectional filter on a fact table. Calendar table missing continuous date coverage.

✅ 𝗣𝗮𝘀𝘀𝗲𝘀: Star schema structure. Single-direction relationships on dimensions. Date table properly marked.

Then Claude offered to fix each issue, one by one. "Want me to remove the unused measures?" Yes. "Set the bidirectional filter to single direction?" Yes. Done.

Manual review? 30+ minutes if you know what to look for. With 𝗽𝗯𝗶-𝗰𝗹𝗶? Instant. And it catches things you'd miss.

Catch issues before production. Not after.

GitHub: https://github.com/MinaSaad1/pbi-cli
Learn more: mina-saad.com/pbi-cli

#PowerBI #DataModeling #DataQuality #ClaudeCode #VIbeModeling #OpenSource #SemanticModel #AI
