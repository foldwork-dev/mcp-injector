# Changelog

All notable changes to mcp-injector are documented here.

## [0.1.0] - 2026-07-04

### Initial Release

**Core features:**
- AST body folding for Go, Python, TypeScript, JavaScript, Java, and Rust - 66-79% token reduction on real codebases
- Persistent SQLite WAL-mode catalog with inotify/FSEvents file watchers
- Canonical determinism - byte-identical output on every run for Anthropic KV prompt cache hits
- Branch-aware re-indexing via post-checkout git hook
- Atomic catalog swap on branch switch (no empty-index window)

**MCP tools exposed:**
- `get_project_map` - compressed codebase structure with module graph, entry points, dependency map
- `injector_retrieve` - fetch full uncompressed source for any file or symbol
- `injector_stats` - current compression ratio, cache hit rate, workspace line count

**Security:**
- Always-on secret/credential filtering (16 patterns + Shannon entropy detection)
- Variable names preserved, only values redacted
- Zero telemetry, zero outbound network calls
- Ed25519 offline license verification

**Free tier:**
- Workspaces under 100,000 lines: fully free, no license key
- Pro ($12/month): unlimited workspace size + advanced features

**Supported IDEs:**
- Claude Desktop, Cursor, VS Code (Continue extension)
- Auto-detection and configuration on install

**Supported platforms:**
- Linux amd64/arm64
- macOS amd64/arm64  
- Windows amd64
