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
* **Canonical Output Determinism:** Guarantees byte-identical outputs across runs, maximizing Claude's **KV prompt caching** hits.
* **Compress-Cache-Retrieve (CCR):** Employs lossless AST compression. The LLM gets the high-level outline and calls `injector_retrieve` to fetch raw file bodies on-demand.
* **100% Local & Offline:** Running entirely on your local machine, keeping your intellectual property private and secure.

**Supports:** Go, Python, TypeScript, JavaScript, Java, C++, Rust.

---

## 💎 Pricing Tiers

* **Free Tier:** Workspaces under 100,000 total source lines (all tools and features fully active).
* **Pro Tier ($12/month or $99/year):** Unlocks unlimited workspace sizes and high-speed incremental diff indexing.  
👉 **[Activate Pro at foldwork.dev](https://www.foldwork.dev/#pricing)**

---

## 🔌 Exposed MCP Tools

* `get_project_map` — Generates a hierarchical outline of module exports, structures, and internal dependencies.
* `injector_retrieve` — Resolves and retrieves the raw source code of any compressed symbol from the local cache.
* `injector_stats` — Visualizes index status, current token savings, and CCR cache hit rates.

---

## 🔑 SEO Keywords
`Model Context Protocol`, `MCP server`, `Claude Desktop MCP`, `Cursor context optimizer`, `LLM prompt token compression`, `AST code folding`, `codebase context injection`, `AI agent coding context`, `context window optimization`, `prompt token optimizer`, `VS Code Continue MCP`.

---

## 📄 License

Commercial. Free tier available. Source code not public.  
Support Contact: [contact@foldwork.dev](mailto:contact@foldwork.dev)
