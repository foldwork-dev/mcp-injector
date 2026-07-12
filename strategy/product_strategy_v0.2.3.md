# Foldwork Company Strategy (v0.2.3 & Beyond)

## Our Mission Statement
*Foldwork exists to maximize the probability that an AI coding assistant can solve a repository-specific task correctly on the first attempt by providing the smallest correct context and making that context fully explainable.*

### What Foldwork Is
Foldwork is a deterministic repository understanding layer that gives AI coding assistants exactly the context they need—no more, no less—and can explain why that context was chosen. Compression is a feature; understanding is our platform.

### What Foldwork Is NOT
Clarity comes from boundaries. Foldwork is **not**:
- an IDE or a code editor
- an AI model or AI coding assistant
- a Vector Database
- a documentation platform
- "just another MCP server" (MCP is merely one integration protocol; our architecture is designed to support MCP, A2A, OpenAI APIs, and whatever comes next).

---

## The Core Differentiators

### The Moat: Repository Understanding
Determinism is our engineering principle, but **Repository Understanding** is our moat. Lots of tools parse ASTs. Our true differentiator is consistently solving the hard problem: *What does the AI actually need to understand this specific repository right now?*

### The North Star Metrics
* **External (User-Facing):** **First-Try Success Rate.** (e.g., "Foldwork enables the AI to complete tasks correctly on the first attempt 82% of the time.")
* **Internal (Engineering):** **Context Precision.** (Maximizing useful symbols while minimizing unused/missing symbols).

### The Product Flywheel
`Repository → Graph improves → Context improves → AI answers improve → Developers trust Foldwork → Developers use Foldwork more → More benchmark data → Retrieval improves → Repeat.`

---

## The Product vs. Capability Matrix
*Features are capabilities. We sell Products.*

### Product A: Intelligent Context Retrieval
*The flagship engine that consistently gives the AI exactly the right context.*
**Powered by:** Symbol Graph, Dependency Navigation, Precise Chunk Selection, AST Compression.

### Product B: Repository Understanding
*High "wow-factor" workflows that help both the AI and the human understand how the system works.*
**Powered by:** Signature `/explain` Workflow, Sequence Diagram Generation.

### Product C: Repository Knowledge
*Persistent memory for team conventions and architectural decisions.*
**Powered by:** Markdown-backed Memory (`.foldwork/decisions.md`), Automated Convention Injection.

### Product D: Repository Intelligence
*Information humans want, not just LLMs. Expanding our audience to tech leads.*
**Powered by:** Exposing architectural hotspots, high-coupling alerts, God object detection, and circular dependency maps.

---

## Explainability & Infrastructure

### `foldwork inspect` (Explainable Context)
Developers don't trust black boxes. `foldwork inspect` outputs exactly why context was retrieved:
```text
Context Query: "Explain authentication"
Confidence: 98%
Missing Context: None
Retrieved: 9 symbols
Ignored: 284 files
Reason: Traversed entry point -> middleware -> JWT handler -> UserService.
```

### `foldwork graph export`
We already have the most valuable asset: deterministic graph construction. By exposing it, we allow the community to build tooling on top of Foldwork, transforming it into true infrastructure.

### The Foldwork Benchmark Suite
A public regression suite of **100 Real-World Tasks** comparing Claude alone vs. Claude + Foldwork (measuring tokens, latency, accuracy, and manual edits required). This suite becomes our marketing, our internal engineering roadmap, and our definitive proof of ROI.
