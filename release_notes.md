### Agent UX (AX) Overhaul

This patch focuses entirely on feedback from AI Agents (Claude 5 Sonnet) to drastically reduce their blind retrievals and hallucination loops.

**Zero-Friction Search:**
- `injector_search` now returns `line_start`, `line_end`, `symbol_type`, and a `context_snippet` so agents can instantly verify symbols without wasting tokens on full file retrievals.
- The BM25 search engine now explicitly ranks symbol definitions (classes, functions, methods) above references and comments to eliminate search noise.

**Sync Transparency:**
- `injector_sync` now returns an array of `files_reindexed` so agents receive immediate, concrete proof that their OS-level edits were picked up by the daemon.

**Agent Proactivity & Parsing:**
- We updated the MCP tool description for `get_project_map` to inject a system prompt override that commands conservative AI agents to proactively use the tool when exploring unfamiliar architectures.
- Replaced ambiguous `... (folded)` stubs with explicit `# FOLD START` and `# FOLD END` markers to prevent LLM confusion when reading heavily compressed files.
