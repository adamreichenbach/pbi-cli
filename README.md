<p align="center">
  <img src="assets/header.svg" alt="pbi-cli" width="800"/>
</p>

<p align="center">
  <strong>Manage Power BI semantic models from your terminal.</strong><br/>
  One command instead of 4,000 tokens of MCP schema.
</p>

<p align="center">
  <a href="https://pypi.org/project/pbi-cli-tool/"><img src="https://img.shields.io/pypi/v/pbi-cli-tool?style=flat-square&color=f2c811&label=PyPI" alt="PyPI"></a>
  <a href="https://pypi.org/project/pbi-cli-tool/"><img src="https://img.shields.io/pypi/pyversions/pbi-cli-tool?style=flat-square&color=3776ab&label=Python" alt="Python"></a>
  <a href="https://github.com/MinaSaad1/pbi-cli/actions"><img src="https://img.shields.io/github/actions/workflow/status/MinaSaad1/pbi-cli/ci.yml?style=flat-square&label=CI" alt="CI"></a>
  <a href="https://github.com/MinaSaad1/pbi-cli/blob/master/LICENSE"><img src="https://img.shields.io/github/license/MinaSaad1/pbi-cli?style=flat-square&color=06d6a0" alt="License"></a>
</p>

<p align="center">
  <a href="#-quick-start">Quick Start</a> &bull;
  <a href="#-commands">Commands</a> &bull;
  <a href="#-repl-mode">REPL Mode</a> &bull;
  <a href="#-ai-agent-skills">AI Skills</a> &bull;
  <a href="#-for-ai-agents">For AI Agents</a> &bull;
  <a href="#-contributing">Contributing</a>
</p>

---

## The Problem

When an AI agent connects to a Power BI MCP server directly, **each tool schema costs ~4,000+ tokens** in the context window. With 20+ tools, that's most of the context gone before any work begins.

pbi-cli wraps the same MCP server behind a CLI. A single command uses **~30 tokens**. Same capabilities, 100x more efficient.

```
                          Context Window Cost
  ┌─────────────────────────────────────────────────────┐
  │ Raw MCP schemas   ████████████████████████  ~4,000  │
  │ pbi-cli command   █                           ~30   │
  └────────────────────────────────���────────────────────┘
```

---

## How It Works

```mermaid
graph LR
    A["<b>You / AI Agent</b><br/>pbi measure list"] -->|"~30 tokens"| B["<b>pbi-cli</b><br/>Click CLI"]
    B -->|"stdio"| C["<b>MCP Server</b><br/>.NET binary"]
    C -->|"XMLA"| D["<b>Power BI</b><br/>Desktop / Fabric"]

    style A fill:#1a1a2e,stroke:#f2c811,color:#fff
    style B fill:#16213e,stroke:#4cc9f0,color:#fff
    style C fill:#0f3460,stroke:#7b61ff,color:#fff
    style D fill:#1a1a2e,stroke:#f2c811,color:#fff
```

**No separate MCP server configuration needed.** pbi-cli downloads and manages the official Microsoft binary for you.

---

## Quick Start

### 1. Install

```bash
pip install pbi-cli-tool
```

### 2. Download the MCP binary

```bash
pbi setup
```

### 3. Connect and go

```bash
# Local Power BI Desktop
pbi connect --data-source localhost:54321

# Or a Fabric workspace
pbi connect-fabric --workspace "My Workspace" --model "Sales Model"
```

### 4. Start working

```bash
pbi measure list                    # See all measures
pbi dax execute "EVALUATE Sales"    # Run a DAX query
pbi database export-tmdl ./model/   # Export model to files
```

> **Requires:** Python 3.10+ and Power BI Desktop (local) or a Fabric workspace (cloud).

---

## Commands

pbi-cli covers every Power BI MCP server operation across **22 command groups**.

### Data & Queries

| Command | What it does |
|---------|-------------|
| [`pbi dax execute`](#) | Run DAX queries inline, from file, or piped from stdin |
| [`pbi dax validate`](#) | Check DAX syntax without executing |
| [`pbi dax clear-cache`](#) | Clear the formula engine cache for benchmarking |

### Model Structure

| Command | What it does |
|---------|-------------|
| [`pbi table`](#) | Create, list, rename, delete, refresh tables |
| [`pbi column`](#) | Add data columns or calculated columns to tables |
| [`pbi measure`](#) | Full CRUD for measures with DAX expressions and formatting |
| [`pbi relationship`](#) | Create star-schema relationships between tables |
| [`pbi hierarchy`](#) | Build drill-down hierarchies (Year > Quarter > Month) |
| [`pbi calc-group`](#) | Calculation groups for reusable time intelligence |

### Deployment & Lifecycle

| Command | What it does |
|---------|-------------|
| [`pbi database export-tmdl`](#) | Export entire model as human-readable TMDL files |
| [`pbi database import-tmdl`](#) | Deploy TMDL files into a connected model |
| [`pbi database export-tmsl`](#) | Export as TMSL JSON (SSAS/AAS compatible) |
| [`pbi model refresh`](#) | Refresh model data (Full, DataOnly, Calculate, Defragment) |
| [`pbi transaction`](#) | Wrap multiple changes in atomic begin/commit/rollback |

### Security & Governance

| Command | What it does |
|---------|-------------|
| [`pbi security-role`](#) | Create and manage row-level security (RLS) roles |
| [`pbi perspective`](#) | Control which tables/columns different users see |
| [`pbi advanced culture`](#) | Multi-language support with cultures and translations |

### Connections & Config

| Command | What it does |
|---------|-------------|
| [`pbi connect`](#) | Connect to Power BI Desktop via localhost |
| [`pbi connect-fabric`](#) | Connect to Fabric workspace models |
| [`pbi connections list`](#) | View and manage saved named connections |
| [`pbi setup`](#) | Download/update the MCP binary, check status |

<details>
<summary><b>See all remaining commands</b></summary>

| Command | What it does |
|---------|-------------|
| `pbi model get` | View model metadata (name, compatibility level, culture) |
| `pbi model stats` | Table count, measure count, column count at a glance |
| `pbi partition` | Manage table partitions and partition-level refresh |
| `pbi expression` | Named expressions and model parameters |
| `pbi calendar` | Calendar/date table management |
| `pbi trace` | Diagnostic tracing (start, stop, fetch, export) |
| `pbi advanced function` | Model functions |
| `pbi advanced query-group` | Query groups |
| `pbi repl` | Interactive REPL session |
| `pbi skills` | Install AI agent skills for Claude Code |

</details>

Run `pbi <command> --help` for full options on any command.

---

## REPL Mode

Each `pbi` command starts and stops the MCP server process (~2-3 seconds). The **REPL** keeps it running:

```
$ pbi repl
pbi-cli interactive mode. Type 'exit' or Ctrl+D to quit.

pbi> connect --data-source localhost:54321
Connected: localhost-54321

pbi(localhost-54321)> measure list
┌──────────────┬────────────────────────┬────────┐
│ Name         │ Expression             │ Table  │
├──────────────┼────────────────────────┼────────┤
│ Total Sales  │ SUM(Sales[Amount])     │ Sales  │
│ Order Count  │ COUNTROWS(Sales)       │ Sales  │
└──────────────┴────────────────────────┴────────┘

pbi(localhost-54321)> dax execute "EVALUATE TOPN(5, Sales)"
...

pbi(localhost-54321)> exit
Goodbye.
```

```mermaid
graph TD
    A["pbi repl"] -->|"Start once"| B["MCP Server Process"]
    B --> C["command 1"]
    B --> D["command 2"]
    B --> E["command N"]
    B -->|"Stop on exit"| F["Cleanup"]

    style A fill:#16213e,stroke:#4cc9f0,color:#fff
    style B fill:#0f3460,stroke:#f2c811,color:#fff
    style C fill:#1a1a2e,stroke:#06d6a0,color:#fff
    style D fill:#1a1a2e,stroke:#06d6a0,color:#fff
    style E fill:#1a1a2e,stroke:#06d6a0,color:#fff
    style F fill:#1a1a2e,stroke:#7b61ff,color:#fff
```

**REPL features:**
- Persistent MCP connection (no restart between commands)
- Tab completion for all commands and subcommands
- Command history across sessions (`~/.pbi-cli/repl_history`)
- Dynamic prompt showing your active connection

---

## AI Agent Skills

pbi-cli ships with **5 Claude Code skills** that teach AI agents how to work with Power BI models. Install them once and Claude Code automatically discovers them.

```bash
pbi skills install     # Install all 5 skills
pbi skills list        # Check what's installed
```

```mermaid
graph TD
    subgraph Skills["Bundled Skills"]
        S1["<b>Modeling</b><br/>Tables, columns, measures<br/>relationships, hierarchies"]
        S2["<b>DAX</b><br/>Queries, aggregations<br/>time intelligence, ranking"]
        S3["<b>Deployment</b><br/>TMDL export/import<br/>Git workflows, Fabric"]
        S4["<b>Security</b><br/>RLS roles, perspectives<br/>access patterns"]
        S5["<b>Documentation</b><br/>Auto-document models<br/>data dictionaries"]
    end

    Skills -->|"pbi skills install"| CC["~/.claude/skills/"]
    CC --> AI["Claude Code auto-discovers them"]

    style S1 fill:#16213e,stroke:#f2c811,color:#fff
    style S2 fill:#16213e,stroke:#4cc9f0,color:#fff
    style S3 fill:#16213e,stroke:#7b61ff,color:#fff
    style S4 fill:#16213e,stroke:#06d6a0,color:#fff
    style S5 fill:#16213e,stroke:#ff6b6b,color:#fff
    style CC fill:#0f3460,stroke:#f2c811,color:#fff
    style AI fill:#1a1a2e,stroke:#f2c811,color:#fff
```

| Skill | What the AI agent learns |
|-------|------------------------|
| **Modeling** | Create star schemas, add measures with format strings, build hierarchies and calculation groups |
| **DAX** | Execute queries, write CALCULATE/SUMMARIZECOLUMNS patterns, time intelligence, performance tips |
| **Deployment** | Export/import TMDL for version control, promote dev to production, atomic transactions |
| **Security** | Set up row-level security roles, create perspectives, region/department/manager access patterns |
| **Documentation** | Auto-catalog all model objects, generate data dictionaries, measure inventories, manage translations |

---

## For AI Agents

Add `--json` before any subcommand for machine-readable output:

```bash
pbi --json measure list              # JSON array of all measures
pbi --json dax execute "EVALUATE X"  # Query results as JSON
pbi --json model stats               # Model statistics as JSON
```

**JSON goes to stdout. Status messages go to stderr.** This makes piping and parsing clean:

```bash
pbi --json measure list | jq '.[].name'
```

Use `-c` to target a specific named connection:

```bash
pbi -c dev measure list
pbi -c prod dax execute "EVALUATE Sales"
```

---

## Architecture

```mermaid
graph TB
    subgraph CLI["pbi-cli (Python)"]
        direction TB
        MAIN["main.py<br/>Click CLI + routing"]
        CMDS["22 command modules"]
        MCP["mcp_client.py<br/>Sync wrapper over async MCP SDK"]
        BIN["binary_manager.py<br/>Download + resolve binary"]
        CFG["config.py + connection_store.py<br/>~/.pbi-cli/ persistence"]
        REPL["repl.py<br/>prompt-toolkit REPL"]
    end

    subgraph Server["MCP Server (.NET)"]
        MCPS["powerbi-modeling-mcp"]
    end

    subgraph Target["Power BI"]
        PBI["Desktop / Fabric Workspace"]
    end

    MAIN --> CMDS
    CMDS --> MCP
    MCP -->|"stdio JSON-RPC"| MCPS
    MCPS -->|"XMLA"| PBI
    MAIN --> REPL
    REPL --> MCP
    BIN -->|"Downloads from<br/>VS Marketplace"| MCPS
    MAIN --> CFG

    style CLI fill:#16213e,stroke:#4cc9f0,color:#fff
    style Server fill:#0f3460,stroke:#7b61ff,color:#fff
    style Target fill:#1a1a2e,stroke:#f2c811,color:#fff
```

### Binary Resolution

pbi-cli finds the MCP server binary in this order:

```
1. $PBI_MCP_BINARY           Environment variable (explicit override)
          |
          v
2. ~/.pbi-cli/bin/{version}/  Managed by `pbi setup`
          |
          v
3. ~/.vscode/extensions/      VS Code extension fallback
```

### Configuration

All config lives in `~/.pbi-cli/`:

```
~/.pbi-cli/
  config.json          # Binary version, path, args
  connections.json     # Named connections
  repl_history         # REPL command history
  bin/
    {version}/
      powerbi-modeling-mcp[.exe]
```

---

## Development

```bash
git clone https://github.com/MinaSaad1/pbi-cli.git
cd pbi-cli
pip install -e ".[dev]"
```

```bash
ruff check src/ tests/         # Lint
mypy src/                      # Type check
pytest -m "not e2e"            # Run 120 tests
pytest -m "not e2e" --cov      # With coverage
```

### Project Structure

```
src/pbi_cli/
  main.py                 # CLI entry point, context, command registration
  commands/               # 22 command modules (one per group)
    _helpers.py           # Shared run_tool() and build_definition()
  core/
    mcp_client.py         # Sync MCP client wrapper
    binary_manager.py     # Binary download and resolution
    config.py             # Configuration persistence
    connection_store.py   # Named connection management
    errors.py             # User-facing error hierarchy
    output.py             # Dual output (JSON + Rich)
  utils/
    repl.py               # Interactive REPL
    platform.py           # OS/arch detection
  skills/                 # 5 bundled Claude Code skills
```

---

## Contributing

Contributions are welcome! Please open an issue first to discuss what you'd like to change.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/my-change`)
3. Make your changes with tests
4. Run `ruff check` and `mypy` before submitting
5. Open a pull request

---

<p align="center">
  <a href="https://github.com/MinaSaad1/pbi-cli"><img src="https://img.shields.io/badge/GitHub-pbi--cli-1a1a2e?style=flat-square&logo=github" alt="GitHub"></a>
  <a href="https://pypi.org/project/pbi-cli-tool/"><img src="https://img.shields.io/badge/PyPI-pbi--cli--tool-f2c811?style=flat-square&logo=pypi&logoColor=white" alt="PyPI"></a>
</p>

<p align="center">
  <sub>MIT License &bull; Built for Power BI developers and AI agents</sub>
</p>
