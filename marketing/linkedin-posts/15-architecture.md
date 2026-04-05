<!-- Post 15 | Phase 4: Enterprise & Architecture | Day 15 -->
<!-- Image: architecture-flow.png (Architecture: Claude Code -> pbi-cli -> pythonnet -> .NET TOM -> Power BI) -->

No MCP server. No REST API. No external binaries.

Here's how pbi-cli actually works, end to end. ⚙️

Claude Code calls 𝗽𝗯𝗶-𝗰𝗹𝗶, a Python CLI installed via pipx. pbi-cli uses 𝗽𝘆𝘁𝗵𝗼𝗻𝗻𝗲𝘁 to bridge into .NET. From there, the .NET 𝗧𝗮𝗯𝘂𝗹𝗮𝗿 𝗢𝗯𝗷𝗲𝗰𝘁 𝗠𝗼𝗱𝗲𝗹 (TOM) and ADOMD.NET talk directly to Power BI Desktop over the local XMLA endpoint.

The full chain:

```
Claude Code -> pbi-cli -> pythonnet -> .NET TOM/ADOMD -> XMLA -> Power BI
```

Everything runs in-process on your machine. No network hops. No middleware. Sub-second execution for most operations.

Why does the architecture matter? Because direct access means 𝗳𝗮𝘀𝘁𝗲𝗿 execution, 𝗺𝗼𝗿𝗲 𝗿𝗲𝗹𝗶𝗮𝗯𝗹𝗲 results, and 𝟭𝟯𝟬𝘅 𝗰𝗵𝗲𝗮𝗽𝗲𝗿 than MCP tool calls. No JSON-RPC schema bloat. No server process to manage. Just a CLI that does exactly what you ask. 🏗️

Open source. MIT License.

GitHub: https://github.com/MinaSaad1/pbi-cli
Learn more: mina-saad.com/pbi-cli

#PowerBI #SoftwareArchitecture #Python #DotNET #OpenSource #ClaudeCode #VIbeModeling #DataEngineering
