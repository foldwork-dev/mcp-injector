# Foldwork Execution Plan: Strategy to Reality

With the company strategy solidified, it is time to shift from ideation to execution. Based on the strategic imperative that our messaging must reflect our new identity ("The Context Layer for Software Engineering") and that the Benchmark Suite is our most critical engineering/marketing asset, I propose a two-phase implementation plan.

## Open Questions

> [!IMPORTANT]
> **Priority Decision Needed:** Would you like to execute Phase 1 (Marketing & Messaging Update) first to immediately reposition the product, or dive straight into Phase 2 (The Benchmark Suite) to establish the engineering ground truth?

## Phase 1: The Messaging & Identity Overhaul

We need to update the website, documentation, and product configuration to reflect the shift from "Token Compressor" to "The Context Layer for Software Engineering."

### Website Data & Content (`website/data/`)
* **[MODIFY]** `website/data/product.json`: Add new strategic fields (e.g., `mission_statement`, `core_principles`, `negative_goals`) so they can be injected into the HTML templates.
* **[MODIFY]** `website/data/seo_config.json`: Update primary keywords away from "MCP server" and "Token compression" toward "AI Context Engine," "Repository Understanding," and "Deterministic Context."

### Core Documentation (`README.md` & `website/`)
* **[MODIFY]** `README.md`: Rewrite the hero section and Introduction. Explicitly state the "What Foldwork is NOT" guardrails.
* **[MODIFY]** `website/index.html`: Update the primary H1 and hero subtext. Introduce the "Information Minimalism" philosophy and highlight the North Star Metric (First-Try Success Rate).
* **[MODIFY]** `website/partials/nav.html` & `footer.html`: Adjust navigation to reflect the new "Products" (Intelligent Context Retrieval, Repository Understanding, Repository Knowledge).

*Verification:* Run `scripts/lint-consistency.py` and `scripts/lint-seo.py` to ensure all claims match across the site, followed by `assemble-partials.py`.

---

## Phase 2: The Benchmark Suite (SWE-bench equivalent)

The strategy dictates that "The benchmark suite could become your biggest marketing asset." We need to build the scaffolding for a reproducible, 100-Task evaluation framework.

### Architecture
We will expand the existing `mcp-benchmark` tool (or create a new `benchmark-runner` module) to evaluate tasks against open-source repositories.

### Technical Implementation

* **[NEW]** `test/benchmark/tasks.json`: A schema defining the 100 evaluation tasks. Each task will contain:
  * `repo_url` / `commit_hash`
  * `prompt` (e.g., "Add a retry mechanism to the Stripe payment handler")
  * `ground_truth_symbols` (The exact files/functions required to solve it)
* **[NEW]** `cmd/foldwork-eval/main.go`: The execution harness. It will:
  1. Spin up the `mcp-injector` daemon on the target repo.
  2. Simulate the AI agent's tool calls (e.g., `get_project_map`, `injector_search`).
  3. Calculate **Context Precision** (Useful Symbols vs. Unused Symbols).
  4. Output a Markdown/JSON report of the results.

## Verification Plan

### Manual Verification
* Review the compiled HTML files locally to ensure the new messaging is sharp and aligns with the strategic document.
* Manually inspect the output of the first `foldwork-eval` run against a sample task to confirm the precision math is correct.

### Automated Verification
* Execute the SEO and Consistency Python linters on the website directory.
* Run the Go unit tests for the new benchmark runner to verify deterministic scoring logic.
