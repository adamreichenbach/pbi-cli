# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2026-03-26

### Added
- Interactive REPL mode (`pbi repl`) with persistent MCP connection
- Tab completion and command history in REPL
- Dynamic prompt showing active connection name
- Error hierarchy (`PbiCliError`, `McpToolError`, `BinaryNotFoundError`, `ConnectionRequiredError`)

### Changed
- REPL mode reuses shared MCP client instead of spawning per command
- Connection commands (`connect`, `connect-fabric`, `disconnect`) are REPL-aware

## [0.1.0] - 2026-03-26

### Added
- Initial release with 22 command groups covering all Power BI MCP tool operations
- Binary manager: download Power BI MCP binary from VS Code Marketplace
- Connection management with named connections and persistence
- DAX query execution, validation, and cache clearing
- Full CRUD for measures, tables, columns, relationships
- Model metadata, statistics, and refresh operations
- Database import/export (TMDL and TMSL formats)
- Security role management (row-level security)
- Calculation groups, partitions, perspectives, hierarchies
- Named expressions, calendar tables, diagnostic traces
- Transaction management (begin/commit/rollback)
- Advanced operations: cultures, translations, functions, query groups
- Dual output mode: `--json` for agents, Rich tables for humans
- Named connection support with `--connection` / `-c` flag
- Binary resolution chain: env var, managed binary, VS Code extension fallback
- Cross-platform support: Windows, macOS, Linux (x64 and ARM64)
