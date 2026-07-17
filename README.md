# mcp-injector

AI coding assistants often fail because they retrieve the wrong context. On a large codebase, blindly dumping raw files into the prompt leads to hallucinations, slow responses, and high API costs.

Foldwork fixes this. It is a deterministic repository understanding engine that pre-indexes your entire codebase into a local SQLite catalog. It acts as the Context Layer for your IDE, serving exactly the functions the AI needs—no more, no less—maximizing the first-try success rate and reducing token usage by 41-89%.

By combining AST body folding (which strips out function bodies while preserving signatures) with canonical determinism (which guarantees byte-identical outputs to maximize Anthropic's KV cache hits), Foldwork transforms massive enterprise monorepos into lightweight, cache-friendly payloads. This drastically reduces token consumption, cuts API costs by up to 90%, and eliminates context window overflow.

No cloud. No telemetry. Runs entirely on your machine.--

##  Real-World Codebase Context Benchmarks

Estimate the impact of AST code compression on large open-source repositories (calculated at $2.00 / million input tokens for Claude Sonnet 5):

|  Repository |  Total Files |  Raw Context Tokens |  Compressed Context Tokens |  Token Reduction |  Cost Saved / Run |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Django** | 2,359 | 5,554,607 | 596,752 | **89.3%** | **$10.99** |
| **Tokio** | 789 | 1,597,813 | 444,164 | **72.2%** | **$3.11** |
| **Gin** | 99 | 197,300 | 47,718 | **75.8%** | **$0.39** |

*Numbers are reproducible. Run the open-source benchmark tool on any public repository:*  
 **[mcp-benchmark repository](https://github.com/foldwork-dev/mcp-benchmark)**

---

## What It Looks Like

Run `mcp-benchmark` on your own project to see your exact savings before installing anything:

```text
mcp-benchmark ./your-project

════════════════════════════════════════════════════════════════════════════════
  mcp-injector Benchmark — context
  Tier 3 compression  |  $2.00/1M tokens  |  2026-07-15T12:00:00Z
════════════════════════════════════════════════════════════════════════════════

FILE                                          RAW TOKENS    COMPRESSED     SAVED   COST SAVED*
──────────────────────────────────────────────────────────────────────────────────────────
cmd/license-gen/main.go                            3,633           214       94%       $0.0072
main.go                                           17,555         1,917       89%       $0.0347
website/api/webhook.go                             2,682           295       89%       $0.0053
main_test.go                                       1,576           353       78%       $0.0031
──────────────────────────────────────────────────────────────────────────────────────────
TOTAL (4 files)                                   25,446         2,779     89.1%       $0.0503

  * Based on $2.00 / 1M input tokens

  💡 Running this codebase through Claude 10×/day costs $0.51/day raw.
     With mcp-injector:  $0.01/day.  You save $0.50/day ($15/month).
```

---

## Tools

### `get_project_map`
Returns a compressed structural overview of the workspace. Function bodies are folded and replaced with placeholders to reduce token usage.
- `tier` (integer, optional): Compression tier to apply (default: 2).
- `unfolded_files` (array of strings, optional): Workspace-relative paths or glob patterns for files to serve at full resolution (uncompressed).
- `path_prefixes` (array of strings, optional): Scope the project map to specific microservices or packages, drastically reducing payload bloat.
- `git_context`: always includes current branch, changed files, and recent commits in the response.
- `secrets_redacted`: count of credentials automatically redacted before sending to Claude.

Example call:
```json
{
  "tool": "get_project_map",
  "arguments": {
    "tier": 3,
    "unfolded_files": ["src/auth/handler.go", "**/*_test.go"],
    "path_prefixes": ["src/auth/"]
  }
}
```

### `injector_retrieve`
Retrieves the full uncompressed source of a file from the local cache.
- `path` (string, required): The workspace-relative path of the file to retrieve.
- `retrievalKey` (string, optional): The SHA-256 retrieval key returned in a prior compressed payload.
- `start_line` (integer, optional): 1-indexed start line for range retrieval.
- `end_line` (integer, optional): 1-indexed end line for range retrieval.
- `expand_graph` (boolean, optional): Resolves and appends cross-file dependencies (limited to 50 1st-degree dependencies).

### `injector_search`
BM25-ranked full-text symbol search over the local SQLite catalog. Supports FTS5 boolean logic (e.g., `user AND (auth OR login)`).
- `query` (string, required): FTS5 query string (bare terms, "phrase", prefix*).
- `limit` (integer, optional): Maximum results (default: 20).
- `search_paths` (array of strings, optional): Scope search to specific isolated directories.

### `injector_diagram`
Generates a Mermaid sequence diagram for a given symbol by traversing its outbound dependencies (halts after 500 nodes).
- `symbol` (string, required): The exact symbol name.
- `max_depth` (integer, optional): Maximum traversal depth (default: 3).
- `include_primitives` (boolean, optional): Include basic types (String, boolean) and framework boundaries.

### `injector_regex_search`
Fallback for exact literal or regex searches against file contents. Bypasses FTS5 tokenization.
- `query` (string, required): The string or regex pattern to search for.
- `is_regex` (boolean, optional): Treats query as extended regex (-E).

### `injector_write_file`
Write a full file to disk. CRITICAL: Prevents data loss by intercepting and rejecting payloads containing compressed fold markers.

### `injector_blast_radius`
Analyzes the architectural impact of changing a symbol by traversing the dependency graph. Supports inbound and outbound directional traversal.

### `injector_git_context`
Integrates with local Git history to surface commit context, authorship, and code evolution directly into the LLM context.

### `injector_inspect_table`
Enables direct database introspection capabilities. Currently supports PostgreSQL and MySQL.
*CRITICAL:* You must start the daemon with the `FOLDWORK_DB_DSN` environment variable set to your database connection string (e.g. `postgres://user:pass@localhost:5432/dbname`) to activate this tool.

### `injector_clear_cache`
Wipes the SQLite index cache and triggers a clean cold-start full re-index.

### `injector_stats`
Returns index status, current compression ratio, total files indexed, and cache hit rate.

### `injector_sync` (Deprecated)
Read tools automatically wait for pending indexing implicitly. You never need to manually call this tool.

---

##  Quick Install

Install the daemon locally and configure your IDEs:

```bash
curl -fsSL https://foldwork.dev/install | sh
```

*Automatically configures **Claude Desktop**, **Cursor IDE**, **VS Code**, **Devin Desktop**, and **Antigravity**.*

---

## Getting Started

### Step 1: Check if your project qualifies for the free tier

Run the benchmark CLI on your project to see your token savings and line count:

```bash
mcp-benchmark ./your-project
```

If your project is under 50,000 lines, mcp-injector is completely free. The benchmark output shows your exact line count.

### Step 2: Install the daemon

```bash
curl -fsSL https://foldwork.dev/install | sh
```

The installer auto-detects Claude Desktop, Cursor, VS Code, Devin Desktop, and Antigravity and writes the MCP config automatically. You should see output like:

```text
* mcp-injector v0.2.0 installed to /usr/local/bin/mcp-injector
* Claude Desktop configured
* Cursor configured
Restart your IDE and mcp-injector will be active.
```

### Step 3: Restart your IDE

The MCP server starts automatically when your IDE launches. No separate daemon process to manage.

### Step 4: Verify it is working

In Claude Code or Cursor, ask Claude:

> "Use get_project_map to show me the structure of this project"

Claude will call the mcp-injector tool and return a compressed map of your entire codebase. If you see module names, entry points, and dependency information - it is working.

### Step 5: Get the full source when needed

When Claude needs to see the complete implementation of a compressed function, it automatically calls `injector_retrieve`. You can also trigger this explicitly:

> "Show me the full implementation of UserService.java"

Claude will fetch the uncompressed source from the local cache. 

**Editing Code:** You MUST use the `injector_write_file` tool to edit code. If Claude tries to write back folded placeholders into your source code, the daemon will hard-reject the payload to protect you from data loss.

### Step 6: Check your savings

```bash
injector_stats
```

Or ask Claude directly: "Call injector_stats and tell me my current token savings."

---

## Agent Use Cases & Advanced Usage

Now that your AI has deterministic tools to search, traverse, and retrieve code, you can ask it high-level architectural questions that usually fail on raw codebases:

- **Trace authentication flow** — Ask the agent to map out your login sequence; it will use `injector_retrieve` with `expand_graph=true` to traverse through middleware, validation, and database layers.
- **Find dead code** — The agent can leverage `injector_blast_radius` (inbound traversal) to identify unused functions and isolated structs.
- **Generate architecture diagrams** — Tell your AI to "Generate a Mermaid diagram for this workflow"; it uses `injector_diagram` to instantly draw the entire outbound execution sequence.
- **Understand dependency graphs** — Use `injector_blast_radius` to see exactly what services or packages rely on a specific core module.
- **Locate implementations** — The agent uses `injector_search` (BM25 full-text indexing) to find exact function definitions across millions of lines of code.
- **Refactor safely** — Before making a breaking change, the agent checks `injector_blast_radius` to see every caller that will be impacted.
- **Review pull requests** — Instruct the agent to analyze your uncommitted changes or branch diff. It uses `injector_git_context` to understand recent commits and author intent alongside the code.
- **Navigate large monorepos** — `get_project_map` gives the AI a compressed, birds-eye view of your entire architecture, allowing it to drill down into specific microservices using `path_prefixes`.

### Inspecting specific files uncompressed

Sometimes you need Claude to see the exact implementation of a file while keeping the rest compressed. Use the `unfolded_files` parameter:

In your MCP call or by asking Claude:
> "Get the project map but show me src/auth/handler.go at full resolution"

This passes `"unfolded_files": ["src/auth/handler.go"]` to get_project_map. That file is served raw; everything else stays compressed.

Glob patterns work too:
- `"**/*_test.go"` - all test files uncompressed
- `"src/auth/*.go"` - all files in a directory uncompressed

### Switching branches

mcp-injector installs a `post-checkout` git hook when it first runs. Branch switching automatically triggers a full re-index. You will see this in the daemon logs:

```text
[mcp-injector] Branch switched to feature/auth-refactor, re-indexing...
[mcp-injector] Re-index complete in 4.2s (47,293 lines indexed)
```

### Security First: Zero-Leak Guarantee

Enterprise security teams often block AI coding tools because developers accidentally leak sensitive credentials in their context window. 

mcp-injector solves this locally. The daemon includes a built-in Shannon entropy filter that analyzes all AST strings and comments in real-time. If it detects high-entropy strings (like AWS Access Keys, SSH private keys, or database passwords), it dynamically redacts them as `[REDACTED: high entropy]` *before* they ever leave your machine. Your API credentials are never sent to Anthropic.

If your codebase has a hardcoded API key or AWS credential, the `get_project_map` response will include:

```json
"secrets_redacted": 2,
"files_with_redactions": ["config/db.go", "scripts/deploy.sh"]
```

The actual values are replaced with `[REDACTED: high entropy]`. Variable names are preserved so Claude still understands the code structure.

### Manual MCP configuration

If the auto-installer does not detect your IDE, add this to your MCP config manually:

```json
{
  "mcpServers": {
    "mcp-injector": {
      "command": "/usr/local/bin/mcp-injector",
      "env": {
        "MCP_WORKSPACE": "/absolute/path/to/your/project",
        "FOLDWORK_DB_DSN": "postgres://user:pass@localhost:5432/dbname"
      }
    }
  }
}
```

> **Note:** VS Code supports `"${workspaceFolder}"`, but Claude Desktop, Cursor, and Devin Desktop require a hardcoded absolute path to your project.

Config file locations:
- Claude Desktop (Mac): `~/Library/Application Support/Claude/claude_desktop_config.json`
- Claude Desktop (Windows): `%APPDATA%\Claude\claude_desktop_config.json`
- Claude Desktop (Linux): `~/.config/Claude/claude_desktop_config.json`
- Cursor: `~/.cursor/mcp.json`
- VS Code: `.vscode/mcp.json`
- Devin Desktop: `~/.codeium/windsurf/mcp_config.json`
- Antigravity: `~/.gemini/antigravity/mcp_config.json`

---

##  How It Works

* **Incremental Parsing:** Foldwork scans your repository instantly using a single-pass AST parser, identifying all interfaces, classes, and function signatures without blocking.
* **Graph Generation:** It deterministically builds two structures: a Symbol Graph for precise definitions, and a Dependency Graph tracking outbound caller/callee relationships.
* **Local Catalog:** The graphs are durably stored in a local SQLite FTS5 catalog. Indexing happens exactly once per file change, meaning zero overhead during AI prompts.
* **MCP Serving:** Your AI agent securely communicates with Foldwork via the Model Context Protocol, fetching sub-graphs in milliseconds without the code ever leaving your machine.
* **Branch-Aware & Deterministic:** Switching branches triggers automatic incremental re-indexing via git hooks. By guaranteeing byte-identical outputs across runs, Foldwork maximizes Claude's **KV prompt caching** hits.

**Supports:** Go, Python, TypeScript, JavaScript, Java, C++, C, C#, Rust.

---

##  Pricing Tiers

* **Free Tier:** Workspaces under 50,000 total source lines (all tools and features fully active).
* **Pro Tier ($12/month or $99/year):** Unlocks unlimited workspace sizes and high-speed incremental diff indexing.  
 **[Activate Pro at foldwork.dev](https://foldwork.dev/#pricing)**

---

## Check your ROI (Savings Dashboard)

You can run `mcp-injector status` in your terminal at any time. This CLI dashboard visually proves your exact token savings and estimated dollars saved by comparing your raw codebase tokens against the AST-compressed tokens in real-time.

---

##  Security

mcp-injector automatically redacts secrets and credentials before they reach Claude's context window:

- AWS access keys, GitHub PATs, Stripe secret keys
- JWT tokens and bearer tokens
- High-entropy strings detected via Shannon entropy analysis
- Private key headers (`-----BEGIN RSA PRIVATE KEY-----`)
- **Air-Gapped Ready:** Pro license validation uses strictly offline Ed25519 cryptography. The daemon never makes an outbound network request, even to verify your subscription.

Redacted content is replaced with `[REDACTED BY MCP-INJECTOR]`. A count of redactions is included in the `get_project_map` response so you always know what was protected.

Your code never leaves your machine. Redaction happens locally before compression, and is always-on - it cannot be disabled.

---

##  Uninstall

To remove mcp-injector completely:

```bash
# Remove binary
sudo rm /usr/local/bin/mcp-injector

# Remove index cache and logs
rm -rf ~/.mcp-injector/

# Remove from IDE MCP config (edit manually):
# Claude Desktop (Linux): ~/.config/Claude/claude_desktop_config.json
# Claude Desktop (macOS): ~/Library/Application Support/Claude/claude_desktop_config.json
# Cursor: ~/.cursor/mcp.json
# VS Code: .vscode/mcp.json
# Devin Desktop: ~/.codeium/windsurf/mcp_config.json
# Antigravity: ~/.gemini/antigravity/mcp_config.json
# (Remove the "mcp-injector" entry from mcpServers)
```

---

##  What Gets Redacted

mcp-injector automatically redacts the following before your code reaches Claude:

| Pattern | Example Match |
| :--- | :--- |
| AWS access key IDs | `AKIAIOSFODNN7EXAMPLE` |
| GitHub PATs (ghp_, ghs_) | `ghp_aBcDeFg...` |
| Stripe secret keys | `sk_live_abc...` / `sk_test_abc...` |
| JWT tokens | `eyJ...` |
| PEM private key headers | `-----BEGIN RSA PRIVATE KEY-----` |
| Generic high-entropy strings >20 chars | Detected via Shannon entropy |
| Password / secret / token assignments | `password = "abc123"` |

Redacted values are replaced with `[REDACTED BY MCP-INJECTOR]`. File paths and variable **names** are never redacted - only the values.

---

##  License

Commercial. Free tier available. Source code not public.  
Support Contact: [foldwork@proton.me](mailto:foldwork@proton.me)
