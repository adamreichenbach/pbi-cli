# Security Policy

## Supported Versions

| Version | Supported |
|---------|-----------|
| 0.2.x   | Yes       |
| < 0.2   | No        |

## Reporting a Vulnerability

If you discover a security vulnerability in pbi-cli, please report it responsibly.

**Do not open a public issue.**

Instead, email **security@pbi-cli.dev** or use [GitHub private vulnerability reporting](https://github.com/MinaSaad1/pbi-cli/security/advisories/new).

Please include:

- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

## Response Timeline

- **Acknowledgment**: Within 48 hours
- **Initial assessment**: Within 1 week
- **Fix release**: As soon as possible, depending on severity

## Security Considerations

pbi-cli connects to local Power BI instances via MCP (Model Context Protocol) over stdio. Key security notes:

- **No network exposure**: The MCP server binary communicates over local stdio pipes, not network sockets
- **No credentials stored**: Connection details are saved locally but passwords and tokens are never persisted
- **Local binary execution**: pbi-cli launches `PBIDesktopMCPServer.exe` as a subprocess; ensure the binary is from a trusted source
- **Config file permissions**: Connection store at `~/.pbi-cli/connections.json` should have user-only read/write permissions
