# pbi-cli

**Token-efficient CLI for Power BI semantic models.**

pbi-cli wraps Microsoft's Power BI MCP server so you can manage semantic models from the terminal. MCP tool schemas consume ~4,000+ tokens in an AI agent's context window; a `pbi` command uses ~30. One install, no separate MCP server configuration required.

```
pip install pbi-cli-tool
pbi setup
pbi connect --data-source localhost:54321
pbi measure list
```

## Why pbi-cli?

| Approach | Context cost | Setup |
|----------|-------------|-------|
| Raw MCP server | ~4,000 tokens per tool schema | Manual config per project |
| **pbi-cli** | **~30 tokens per command** | **`pip install pbi-cli-tool`** |

Designed for Claude Code and other AI agents, but works great for humans too. Use `--json` for machine-readable output or enjoy Rich-formatted tables by default.

## Installation

```bash
pip install pbi-cli-tool
```

### Prerequisites

- Python 3.10+
- Power BI Desktop (for local development) or a Fabric workspace

### First-time setup

Download the Power BI MCP binary:

```bash
pbi setup
```

This downloads the official Microsoft binary from the VS Code Marketplace to `~/.pbi-cli/bin/`. You can also point to an existing binary:

```bash
export PBI_MCP_BINARY=/path/to/powerbi-modeling-mcp
```

## Quick Start

### Connect to Power BI Desktop

```bash
# Connect to a local Power BI Desktop instance
pbi connect --data-source localhost:54321

# Connect to a Fabric workspace model
pbi connect-fabric --workspace "My Workspace" --model "Sales Model"
```

### Run DAX queries

```bash
pbi dax execute "EVALUATE TOPN(10, Sales)"
pbi dax execute --file query.dax
cat query.dax | pbi dax execute -
```

### Manage measures

```bash
pbi measure list
pbi measure create "Total Revenue" --expression "SUM(Sales[Revenue])" --table Sales
pbi measure get "Total Revenue" --table Sales
```

### Export and import models

```bash
pbi database export-tmdl ./my-model/
pbi database import-tmdl ./my-model/
```

## Command Reference

| Group | Description | Examples |
|-------|-------------|---------|
| `setup` | Download and manage the MCP binary | `pbi setup`, `pbi setup --check` |
| `connect` | Connect to Power BI via data source | `pbi connect -d localhost:54321` |
| `connect-fabric` | Connect to Fabric workspace | `pbi connect-fabric -w "WS" -m "Model"` |
| `disconnect` | Disconnect from active connection | `pbi disconnect` |
| `connections` | Manage saved connections | `pbi connections list` |
| `dax` | Execute and validate DAX queries | `pbi dax execute "EVALUATE Sales"` |
| `measure` | CRUD for measures | `pbi measure list`, `pbi measure create` |
| `table` | CRUD for tables | `pbi table list`, `pbi table get Sales` |
| `column` | CRUD for columns | `pbi column list --table Sales` |
| `relationship` | Manage relationships | `pbi relationship list` |
| `model` | Model metadata and refresh | `pbi model get`, `pbi model refresh` |
| `database` | Import/export TMDL and TMSL | `pbi database export-tmdl ./out/` |
| `security-role` | Row-level security roles | `pbi security-role list` |
| `calc-group` | Calculation groups and items | `pbi calc-group list` |
| `partition` | Table partitions | `pbi partition list --table Sales` |
| `perspective` | Model perspectives | `pbi perspective list` |
| `hierarchy` | User hierarchies | `pbi hierarchy list --table Date` |
| `expression` | Named expressions | `pbi expression list` |
| `calendar` | Calendar table management | `pbi calendar list` |
| `trace` | Diagnostic traces | `pbi trace start` |
| `transaction` | Explicit transactions | `pbi transaction begin` |
| `advanced` | Cultures, translations, functions | `pbi advanced culture list` |
| `repl` | Interactive REPL session | `pbi repl` |

Run `pbi <command> --help` for full option details.

## REPL Mode

The interactive REPL keeps the MCP server process alive across commands, avoiding the 2-3 second startup cost on each invocation:

```
$ pbi repl
pbi-cli interactive mode. Type 'exit' or Ctrl+D to quit.
pbi> connect --data-source localhost:54321
Connected: localhost-54321 (localhost:54321)
pbi(localhost-54321)> measure list
...
pbi(localhost-54321)> dax execute "EVALUATE Sales"
...
pbi(localhost-54321)> exit
Goodbye.
```

Features:
- Persistent MCP server connection (no restart between commands)
- Command history (stored at `~/.pbi-cli/repl_history`)
- Tab completion for commands and subcommands
- Dynamic prompt showing active connection name

## For AI Agents

Use `--json` before the subcommand for machine-readable JSON output:

```bash
pbi --json measure list
pbi --json dax execute "EVALUATE Sales"
pbi --json model get
```

JSON output goes to stdout. Status messages go to stderr. This makes piping and parsing straightforward.

### Named connections

Use `-c` to target a specific named connection:

```bash
pbi -c my-conn measure list
pbi -c prod-model dax execute "EVALUATE Sales"
```

## Configuration

pbi-cli stores its configuration in `~/.pbi-cli/`:

```
~/.pbi-cli/
  config.json          # Binary version, path, args
  connections.json     # Named connections
  repl_history         # REPL command history
  bin/
    {version}/
      powerbi-modeling-mcp[.exe]
```

### Binary resolution order

1. `PBI_MCP_BINARY` environment variable (explicit override)
2. `~/.pbi-cli/bin/{version}/` (managed by `pbi setup`)
3. VS Code extension fallback (`~/.vscode/extensions/analysis-services.powerbi-modeling-mcp-*/server/`)

## Development

```bash
git clone https://github.com/pbi-cli/pbi-cli.git
cd pbi-cli
pip install -e ".[dev]"

# Lint
ruff check src/ tests/

# Type check
mypy src/

# Test
pytest -m "not e2e"
```

## Contributing

Contributions are welcome! Please open an issue first to discuss what you would like to change.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/my-change`)
3. Make your changes with tests
4. Run `ruff check` and `mypy` before submitting
5. Open a pull request

## License

[MIT](LICENSE)
