# Changelog

All notable changes to mcp-injector are documented here.

## [0.3.1] - 2026-07-17

### Net-New Agent Intelligence Tools
- **`injector_blast_radius`**: Analyzes the architectural impact of changing a symbol by traversing the dependency graph (now with inbound/outbound directional traversal).
- **`injector_git_context`**: Integrates with local Git history to surface commit context and code evolution.
- **`injector_inspect_table`**: Enables direct database introspection capabilities. *Note: Requires `FOLDWORK_DB_DSN` environment variable (supports PostgreSQL & MySQL).*

### Enterprise Hardening
- **Instant Regex Visibility**: Bypassed OS fsnotify debouncers for zero-latency regex search availability on daemon-injected files.
- **Config-Driven Graph Filtering**: Replaced hardcoded language ignore strings with a robust `.mcp-ignore-symbols` engine, dynamically stripping noisy primitives and utility classes from architectural graph expansion.
- **Stability Fixes**: Fixed critical crash (`EOF`) when clearing the cache (`injector_clear_cache`) and ensured `injector_search` correctly returns standard empty JSON arrays `[]` instead of `null` on zero matches.

## [0.3.0] - 2026-07-15

### Zero-OOM Enterprise Engine (Net-New Core Architecture)
- **Asynchronous Background Indexer**: Completely eradicated legacy global in-memory maps and lock contention. Replaced with isolated local variables and sequential SQLite streaming (`InsertSymbolNodes`), preventing memory exhaustion on massive monorepos (50,000+ files).
- **Massive-Repo Graph Preservation**: Fixed the massive-repo fallback mode to explicitly persist and read import nodes, ensuring dependency graphs (especially for Java) are no longer lost at scale.
- **Schema Auto-Migration**: Implemented `_v2.db` workspace hashing to guarantee clean, native background re-indexing upon major schema upgrades.

### Data Loss Prevention & IDE Protection
- **API-Level Compression Guardrail (`injector_write_file`)**: Completely eliminated the "Compression Trap." The daemon now aggressively intercepts write operations via a dedicated tool and statically analyzes the payload. Attempts to write codebase files containing compressed `FOLDWORK: CODE COMPRESSED` markers are hard-rejected before touching the disk.
- **Anti-EOF Handshake State**: Removed hard `os.Exit(1)` background crashes. Free-tier limit violations now enter a degraded `fatalErr` state, keeping lightweight tools active and returning graceful JSON-RPC explanations to the agent instead of crashing the IDE pipe.

### Enterprise Resilience
- **OS File Watcher Auto-Remediation**: For massive 100k+ file monorepos, the daemon now intercepts Linux `inotify` queue limit crashes (ENOSPC / "too many open files"). It safely pauses indexing, opens a direct `/dev/tty` interactive bridge to prompt the user for an automatic `sudo sysctl fs.inotify.max_user_watches` increase, and dynamically resumes indexing without requiring a restart.

### Surgical Scope Filtering
- **`path_prefixes` for Project Maps**: Agents can now generate architectural maps strictly scoped to specific microservices or packages, drastically reducing payload bloat.
- **`search_paths` for Semantic Search**: The SQLite FTS5 engine dynamically injects strict file-path constraints, allowing agents to search for symbols within a specific isolated folder.

### Context Window Circuit Breakers
- **LIMIT 50 Graph Expander**: Added a hard ceiling to `injector_retrieve` (`expand_graph`) to prevent agents from accidentally inlining thousands of 1st-degree dependencies.
- **Standard-Library Pruning**: The dependency graph now explicitly ignores framework bloat (`java.lang.*`, `java.util.*`, `go/ast`) at the query level.
- **Diagram Node Breaker**: The new Mermaid generator will automatically halt after traversing 500 unique nodes to protect the LLM context window.

### Agent Feedback Loops
- **Raw FTS5 Boolean Logic**: Removed legacy hardcoded string escaping. Agents can now use advanced SQLite FTS5 syntax (e.g., `user AND (auth OR login)`).
- **Self-Correcting Syntax Errors**: If an agent provides malformed search syntax, the daemon now intercepts the SQLite error and explicitly returns an invalid search syntax payload so the agent can learn and rewrite its prompt.
- **Implicit State Synchronization**: Added a 3-second non-blocking sync hook (`PendingEvents.Wait()`) into read tools. Agents are now guaranteed real-time AST state without ever needing to manually call `injector_sync` (now deprecated).
- **Index Desync "Busy" Warnings**: Added real-time tracking of the fsnotify queue (`PendingCount`). If the indexer is lagging behind by >100 files (e.g., during massive git checkouts), read tools dynamically inject a clear "Results may be stale" warning directly into the JSON-RPC payload.
- **Diagram Noise Filtering**: Added an `include_primitives` parameter to `injector_diagram`. The layout engine now actively prunes noise like language primitives (`String`, `boolean`) and abstract boundaries (`<<Framework Core>>`) for crisp business-logic sequences.

### Net-New Tools
- **`injector_diagram`**: Architectural Mermaid sequence generator via BFS traversal.
- **`injector_regex_search`**: A new fallback tool that bypasses the SQLite FTS5 tokenizer entirely, providing a direct bridge to native `git grep -nE/-nF` for flawless punctuation matching and extended regex syntax.
- **`injector_write_file`**: The strict, FOLD-aware file-writing bridge mandated for all agent-driven codebase edits to prevent data loss.
- **`injector_clear_cache`**: A manual cache wiping tool bridging the gap for automated recovery from database corruption or massive bloat.
- **`injector_stats`**: Lightweight repository metrics, replacing the deprecated audit tool.

## [0.2.1] - 2026-07-07

### Agent UX (AX) Overhaul

This patch focuses entirely on feedback from AI Agents (Claude Sonnet 5 & GPT-4o) to drastically reduce their blind retrievals and hallucination loops.

**Zero-Friction Search:**
- `injector_search` now returns `line_start`, `line_end`, `symbol_type`, and a `context_snippet` so agents can instantly verify symbols without wasting tokens on full file retrievals.
- The BM25 search engine now explicitly ranks symbol definitions (classes, functions, methods) above references and comments to eliminate search noise.

**Sync Transparency:**
- `injector_sync` now returns an array of `files_reindexed` so agents receive immediate, concrete proof that their OS-level edits were picked up by the daemon.

**Agent Proactivity & Parsing:**
- We updated the MCP tool description for `get_project_map` to inject a system prompt override that commands conservative AI agents to proactively use the tool when exploring unfamiliar architectures.
- Replaced ambiguous `... (folded)` stubs with explicit `FOLDWORK: CODE COMPRESSED` markers to prevent LLM confusion when reading heavily compressed files.

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
- Workspaces under 50,000 lines: fully free, no license key
- Pro ($12/month): unlimited workspace size + advanced features

**Supported IDEs:**
- Claude Desktop, Cursor, VS Code, Devin Desktop
- Auto-detection and configuration on install

**Supported platforms:**
- Linux amd64/arm64
- macOS amd64/arm64  
- Windows amd64
