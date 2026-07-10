import json
import sys
import os
import re

failed = False

def fail(msg):
    global failed
    print(f"LINT ERROR: {msg}")
    failed = True

with open('website/data/product.json') as f:
    product = json.load(f)
with open('website/data/benchmarks.json') as f:
    benchmarks = json.load(f)

# The values we expect to find
monthly = f"${product['pricing']['monthly']}"
yearly = f"${product['pricing']['yearly']}"
free_limit = f"{product['pricing']['free_limit_loc']:,}"
lang_count = str(len(product['languages']))
savings_range = product['savings_range']
version = product['version']
model_name = product['pricing']['model_name']
base_price_string = f"${product['pricing']['base_price_per_million']:.2f}/1M"

base_price = product['pricing']['base_price_per_million']
cache_mult = product['pricing']['cache_hit_multiplier']

# Verify benchmarks.json mathematical consistency and build dynamic string checks
for repo_key, repo in benchmarks["repositories"].items():
    raw_tokens = int(repo["raw_formatted"].replace(',', ''))
    comp_tokens = int(repo["comp_formatted"].replace(',', ''))
    
    expected_raw_cost = (raw_tokens / 1_000_000) * base_price
    expected_comp_cost = (comp_tokens / 1_000_000) * (base_price * cache_mult)
    expected_savings = expected_raw_cost - expected_comp_cost
    
    current_savings = float(repo["cost_saved"].replace('$', ''))
    
    # 1 cent tolerance for float rounding
    if abs(expected_savings - current_savings) > 0.01:
        fail(f"benchmarks.json 'cost_saved' for {repo_key} is {repo['cost_saved']}, but math dictates it should be ${expected_savings:.2f}")

# File checks: list of tuples (filename, list of expected strings)
# If a string isn't found, it fails.
checks = {
    "website/index.html": [
        f"Free for codebases under {free_limit} lines",
        monthly, yearly, savings_range,
    ],
    "website/benchmarks.html": [
        model_name, base_price_string,
    ],
    "README.md": [
        savings_range,
    ],
    "../mcp-benchmark/README.md": [],
    "mcp-benchmark/README.md": [],
    "website/vs/repomix.html": [
        f"{lang_count} Languages"
    ]
}

# Dynamically populate checks from JSON
for repo_key, repo in benchmarks["repositories"].items():
    r_raw = repo["raw_formatted"]
    r_comp = repo["comp_formatted"]
    r_pct = repo["reduction_pct"]
    r_saved = repo["cost_saved"]
    
    # All repos must appear in benchmarks.html
    checks["website/benchmarks.html"].extend([r_raw, r_comp, r_pct, r_saved])
    
    # Only the top 3 highlight repos appear in the index and READMEs
    if repo_key in ["django", "tokio", "gin"]:
        checks["website/index.html"].extend([r_raw, r_comp, r_pct, r_saved])
        checks["README.md"].extend([r_pct, r_saved])
        checks["../mcp-benchmark/README.md"].extend([r_pct, r_saved])
        checks["mcp-benchmark/README.md"].extend([r_pct, r_saved])

regex_checks = {
    "website/index.html": [
        rf"baseRate\s*=\s*{base_price:.2f}",
        rf"cacheHitMultiplier\s*=\s*{cache_mult:.2f}"
    ]
}

for path, expected_strings in checks.items():
    if not os.path.exists(path):
        continue
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    for s in expected_strings:
        if s not in content:
            print(f"LINT ERROR: {path} is missing expected value '{s}'")
            failed = True
            
for path, expected_patterns in regex_checks.items():
    if not os.path.exists(path):
        continue
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    for pattern in expected_patterns:
        if not re.search(pattern, content):
            print(f"LINT ERROR: {path} failed regex match for '{pattern}'")
            failed = True

if failed:
    sys.exit(1)
print("Lint passed.")
