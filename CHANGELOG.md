# Changelog

All notable changes to mcp-injector are documented here.

## [0.2.1] - 2026-07-07

### Agent UX (AX) Overhaul

This patch focuses entirely on feedback from AI Agents (Claude 3.5 Sonnet & GPT-4o) to drastically reduce their blind retrievals and hallucination loops.

**Zero-Friction Search:**
- `injector_search` now returns `line_start`, `line_end`, `symbol_type`, and a `context_snippet` so agents can instantly verify symbols without wasting tokens on full file retrievals.
- The BM25 search engine now explicitly ranks symbol definitions (classes, functions, methods) above references and comments to eliminate search noise.

**Sync Transparency:**
- `injector_sync` now returns an array of `files_reindexed` so agents receive immediate, concrete proof that their OS-level edits were picked up by the daemon.

**Agent Proactivity & Parsing:**
- We updated the MCP tool description for `get_project_map` to inject a system prompt override that commands conservative AI agents to proactively use the tool when exploring unfamiliar architectures.
- Replaced ambiguous `... (folded)` stubs with explicit `# FOLD START` and `# FOLD END` markers to prevent LLM confusion when reading heavily compressed files.

## [0.2.0] - 2026-07-07

### Agent UX & Stability Fixes

This update solidifies the daemon for AI coding agent workflows by eliminating race conditions and fixing concurrency crashes under heavy load.

**Architectural Stability:**
- Migrated from WASM to native `modernc.org/sqlite` to fix OOM panics and database locking issues.
- Fixed interleaved JSON-RPC payloads by introducing Mutex-locked atomic `stdout` writes.
- Built-in SQLite self-healing: automatically detects "database disk image is malformed" and rebuilds the cache natively.

**Agent UX Improvements:**
- `injector_sync` (NEW): Synchronously waits for pending filesystem edits to finish indexing, removing race conditions between writing files and querying the map.
- Surgical Context Extraction: `injector_retrieve` now accepts `start_line` and `end_line` arguments to retrieve exact snippets rather than massive file dumps.
- Actionable Search Results: `injector_search` now explicitly returns the relative `FilePath` for each matched symbol to allow immediate, zero-guesswork retrieval by AI agents.
- Java Module Intelligence: Implemented robust parsing for Java packages and Spring annotations (`@RestController`, `@Service`, etc.) to semantically group enterprise Spring Boot applications inside a new `layer_summary` output.
- Read-Only Warnings: The daemon now explicitly warns AI agents via the MCP handshake and JSON responses to prevent them from attempting to modify folded, read-only code.

**Developer Experience:**
- Added `mcp-injector status` CLI command to display a terminal dashboard of indexed lines, token compression, and estimated cost savings.

## [0.1.0] - 2026-07-04

### Initial Release

**Core features:**
- AST body folding for Go, Python, TypeScript, JavaScript, Java, and Rust - 41-89% token reduction on real codebases
- Persistent SQLite WAL-mode catalog with inotify/FSEvents file watchers
- Canonical determinism - byte-identical output on every run for Anthropic KV prompt cache hits
- Branch-aware re-indexing via post-checkout git hook
- Atomic catalog swap on branch switch (no empty-index window)

**MCP tools exposed:**
- `get_project_map` - compressed codebase structure with module graph, entry points, dependency map
- `unfolded_files` parameter in `get_project_map` - selective bypass of AST folding for specific files
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
- Claude Desktop, Cursor, VS Code, Devin Desktop
- Auto-detection and configuration on install

**Supported platforms:**
- Linux amd64/arm64
- macOS amd64/arm64  
- Windows amd64
