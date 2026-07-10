# mcp-injector

Claude Code reads raw files on demand, quickly exhausting your context window and budget. On a large codebase, this leads to slow responses and high API costs.

mcp-injector fixes this. It runs as a background daemon, pre-indexes your entire repository into a local SQLite catalog, and serves a compressed snapshot of your whole codebase to Claude on every query at roughly 30-89% the normal token cost.

I built this after my team's Claude API bill hit $400/month on a 500K line Spring Boot monorepo. After installing mcp-injector the same workflow costs ~$80/month. The difference is AST body folding (strips function bodies, keeps signatures) plus canonical determinism (byte-identical output every run so Anthropic's KV cache fires instead of miss).

No cloud. No telemetry. Runs entirely on your machine.--

##  Real-World Codebase Context Benchmarks

Estimate the impact of AST code compression on large open-source repositories (calculated at $3.00 / million input tokens for Claude 3.5 Sonnet):

|  Repository |  Total Files |  Raw Context Tokens |  Compressed Context Tokens |  Token Reduction |  Cost Saved / Run |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Django** | 2,359 | 5,554,607 | 596,752 | **89.3%** | **$10.99** |
| **Spring Framework** | 9,193 | 15,032,871 | 5,185,299 | **65.5%** | **$29.03** |
| **Next.js** | 21,985 | 23,963,330 | 10,212,684 | **57.4%** | **$45.88** |

*Numbers are reproducible. Run the open-source benchmark tool on any public repository:*  
 **[mcp-benchmark repository](https://github.com/foldwork-dev/mcp-benchmark)**

---

## What It Looks Like

Run `mcp-benchmark` on your own project to see your exact savings before installing anything:

```text
mcp-benchmark ./your-project

════════════════════════════════════════════════════════════════════════════════
  mcp-benchmark - context
  Tier 3 compression  |  $3.00/1M tokens  |  2026-07-06T12:00:00Z
════════════════════════════════════════════════════════════════════════════════

FILE                                          RAW TOKENS    COMPRESSED     SAVED   COST SAVED*
──────────────────────────────────────────────────────────────────────────────────────────
cmd/license-gen/main.go                            3,633           214     94.1%       $0.0103
main.go                                           17,555         1,917     89.1%       $0.0469
website/api/webhook.go                             2,682           295     89.0%       $0.0072
main_test.go                                       1,576           353     77.6%       $0.0037
──────────────────────────────────────────────────────────────────────────────────────────
TOTAL (4 files)                                   25,446         2,779     89.1%       $0.0680

  * Based on $3.00 / 1M input tokens

  Running this codebase through Claude 10x/day costs $0.76/day raw.
  With mcp-injector:  $0.08/day.  You save $0.68/day ($20/month).
```

---

##  Quick Install

Install the daemon locally and configure your IDEs:

```bash
curl -fsSL https://foldwork.dev/install | sh
```

*Automatically configures **Claude Desktop**, **Cursor IDE**, and **VS Code**.*

---

## Getting Started

### Step 1: Check if your project qualifies for the free tier

Run the benchmark CLI on your project to see your token savings and line count:

```bash
mcp-benchmark ./your-project
```

If your project is under 100,000 lines, mcp-injector is completely free. The benchmark output shows your exact line count.

### Step 2: Install the daemon

```bash
curl -fsSL https://foldwork.dev/install | sh
```

The installer auto-detects Claude Desktop, Cursor, VS Code, and Devin Desktop and writes the MCP config automatically. You should see output like:

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

### Step 6: Check your savings

```bash
injector_stats
```

Or ask Claude directly: "Call injector_stats and tell me my current token savings."

---

## Advanced Usage

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
        "MCP_WORKSPACE": "${workspaceFolder}"
      }
    }
  }
}
```

Config file locations:
- Claude Desktop (Mac): `~/Library/Application Support/Claude/claude_desktop_config.json`
- Claude Desktop (Windows): `%APPDATA%\Claude\claude_desktop_config.json`
- Claude Desktop (Linux): `~/.config/Claude/claude_desktop_config.json`
- Cursor: `~/.cursor/mcp.json`
- VS Code: `.vscode/mcp.json`
- Devin Desktop: `~/.devin/mcp.json`

---

##  How It Works

* **Persistent Local Daemon:** Indexes your repository structure into a high-performance WAL-mode SQLite database catalog.
* **Smart File Watchers:** Monitors files incrementally via OS notification hooks (`inotify`/`FSEvents`) and local `git post-checkout` / `post-merge` triggers.
* **Branch-Aware Re-indexing:** Installs a `post-checkout` git hook on startup. Switching branches triggers automatic workspace re-indexing. `get_project_map` always reflects your current branch including uncommitted changes.
* **Canonical Output Determinism:** Guarantees byte-identical outputs across runs, maximizing Claude's **KV prompt caching** hits.
* **Compress-Cache-Retrieve (CCR):** Employs lossless AST compression. The LLM gets the high-level outline and calls `injector_retrieve` to fetch raw file bodies on-demand.
* **100% Local & Offline:** Running entirely on your local machine, keeping your intellectual property private and secure.

**Supports:** Go, Python, TypeScript, JavaScript, Java, C++, Rust.

---

##  Pricing Tiers

* **Free Tier:** Workspaces under 100,000 total source lines (all tools and features fully active).
* **Pro Tier ($12/month or $99/year):** Unlocks unlimited workspace sizes and high-speed incremental diff indexing.  
 **[Activate Pro at foldwork.dev](https://foldwork.dev/#pricing)**

---

##  Exposed MCP Tools

* **`get_project_map`** - Generates a hierarchical outline of module exports, structures, and internal dependencies.
  * `unfolded_files` parameter: pass specific file paths or glob patterns to receive those files uncompressed while everything else stays folded.
  * `git_context`: always includes current branch, changed files, and recent commits in the response.
  * `secrets_redacted`: count of credentials automatically redacted before sending to Claude.

  Example call:
  ```json
  {
    "tool": "get_project_map",
    "arguments": {
      "tier": 3,
      "unfolded_files": ["src/auth/handler.go", "**/*_test.go"]
    }
  }
  ```

* **`injector_retrieve`** - Retrieves the raw source code of any compressed symbol from the local cache. Supports `start_line` and `end_line` parameters for surgical snippet extraction.
* **`injector_search`** - BM25 full-text search over indexed symbols. Returns line ranges, symbol types, and context snippets so you can skip redundant file retrievals.
* **`injector_stats`** - Visualizes index status, current token savings, and CCR cache hit rates.
* **`injector_sync`** - Synchronously waits for the daemon to finish indexing pending filesystem edits. Returns a list of exactly which files were reindexed to confirm changes.

### Check your ROI (Savings Dashboard)

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
# Devin Desktop: ~/.devin/mcp.json
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
