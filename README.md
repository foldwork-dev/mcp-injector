# mcp-injector 🚀

### Local Model Context Protocol (MCP) Server for Codebase Context Injection & Token Optimization

**mcp-injector** is a persistent local Model Context Protocol (MCP) daemon that compresses your entire codebase before sending it to LLMs like Anthropic Claude or OpenAI GPT-4o. It gives AI coding assistants a complete structural understanding of your repository—not just currently open files—at a fraction of the token cost.

---

## ⚡ Real-World Codebase Context Benchmarks

Estimate the impact of AST code compression on large open-source repositories (calculated at $3.00 / million input tokens for Claude 3.5 Sonnet):

| 📂 Repository | 🗂️ Total Files | 🚫 Raw Context Tokens | ⚡ Compressed Context Tokens | 📉 Token Reduction | 💰 Cost Saved / Run |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Django** | 2,359 | 5.5M | 1.5M | **72.6%** | **$12.09** |
| **Spring Framework** | 9,193 | 15.0M | 5.0M | **66.4%** | **$29.94** |
| **Next.js** | 21,848 | 23.8M | 4.9M | **79.2%** | **$56.65** |

*Numbers are reproducible. Run the open-source benchmark tool on any public repository:*  
👉 **[mcp-benchmark repository](https://github.com/foldwork-dev/mcp-benchmark)**

---

## 📦 Quick Install

Install the daemon locally and configure your IDEs:

```bash
curl -fsSL https://foldwork.dev/install | sh
```

*Automatically configures **Claude Desktop**, **Cursor IDE**, and **VS Code (Continue)**.*

---

## 🛠️ How It Works

* **Persistent Local Daemon:** Indexes your repository structure into a high-performance WAL-mode SQLite database catalog.
* **Smart File Watchers:** Monitors files incrementally via OS notification hooks (`inotify`/`FSEvents`) and local `git post-checkout` / `post-merge` triggers.
* **Branch-Aware Re-indexing:** Installs a `post-checkout` git hook on startup. Switching branches triggers automatic workspace re-indexing. `get_project_map` always reflects your current branch including uncommitted changes.
* **Canonical Output Determinism:** Guarantees byte-identical outputs across runs, maximizing Claude's **KV prompt caching** hits.
* **Compress-Cache-Retrieve (CCR):** Employs lossless AST compression. The LLM gets the high-level outline and calls `injector_retrieve` to fetch raw file bodies on-demand.
* **100% Local & Offline:** Running entirely on your local machine, keeping your intellectual property private and secure.

**Supports:** Go, Python, TypeScript, JavaScript, Java, C++, Rust.

---

## 💎 Pricing Tiers

* **Free Tier:** Workspaces under 100,000 total source lines (all tools and features fully active).
* **Pro Tier ($12/month or $99/year):** Unlocks unlimited workspace sizes and high-speed incremental diff indexing.  
👉 **[Activate Pro at foldwork.dev](https://foldwork.dev/#pricing)**

---

## 🔌 Exposed MCP Tools

* **`get_project_map`** — Generates a hierarchical outline of module exports, structures, and internal dependencies.
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

* `injector_retrieve` — Resolves and retrieves the raw source code of any compressed symbol from the local cache.
* `injector_stats` — Visualizes index status, current token savings, and CCR cache hit rates.

---

## 🔒 Security

mcp-injector automatically redacts secrets and credentials before they reach Claude's context window:

- AWS access keys, GitHub PATs, Stripe secret keys
- JWT tokens and bearer tokens
- High-entropy strings detected via Shannon entropy analysis
- Private key headers (`-----BEGIN RSA PRIVATE KEY-----`)

Redacted content is replaced with `[REDACTED BY MCP-INJECTOR]`. A count of redactions is included in the `get_project_map` response so you always know what was protected.

Your code never leaves your machine. Redaction happens locally before compression, and is always-on — it cannot be disabled.

---

## 🗑️ Uninstall

To remove mcp-injector completely:

```bash
# Remove binary
sudo rm /usr/local/bin/mcp-injector

# Remove index cache and logs
rm -rf ~/.mcp-injector/

# Remove from Claude Desktop config (edit manually):
# ~/.config/Claude/claude_desktop_config.json   (Linux)
# ~/Library/Application Support/Claude/claude_desktop_config.json  (macOS)
# Remove the "mcp-injector" entry from mcpServers
```

---

## 🔐 What Gets Redacted

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

Redacted values are replaced with `[REDACTED BY MCP-INJECTOR]`. File paths and variable **names** are never redacted — only the values.

---

## 📄 License

Commercial. Free tier available. Source code not public.  
Support Contact: [foldwork@proton.me](mailto:foldwork@proton.me)
