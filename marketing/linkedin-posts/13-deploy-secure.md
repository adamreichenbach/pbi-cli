<!-- Post 13 | Phase 4: Enterprise & Architecture | Day 13 -->
<!-- Image: deploy-secure.png (Deploy + Secure: TMDL versioning + RLS) -->

Two things every Power BI model needs: version control and access control.

Most teams have neither. Models get overwritten with no rollback. Security rules get configured by clicking through menus and hoping nothing breaks.

pbi-cli handles both from a single conversation.

On the 𝗱𝗲𝗽𝗹𝗼𝘆𝗺𝗲𝗻𝘁 side, you get full TMDL export and import. Every change becomes a version snapshot you can track in git:

- v1: Baseline schema
- v2: +Revenue measures
- v3: +RLS roles applied

Need to roll back? One command. No guesswork.

On the 𝘀𝗲𝗰𝘂𝗿𝗶𝘁𝘆 side, Claude configures role-based filters directly on your model. Per-user data visibility, row-level security rules, all defined in plain English and applied through the TOM API.

Both skills work from conversation. Describe what you need, Claude builds it. 🔐

Version control your models. Secure them with one prompt.

GitHub: https://github.com/MinaSaad1/pbi-cli
Learn more: mina-saad.com/pbi-cli

#PowerBI #DataSecurity #RLS #VersionControl #TMDL #OpenSource #ClaudeCode #VIbeModeling
