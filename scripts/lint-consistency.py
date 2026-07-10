import json
import sys
import os

def fail(msg):
    print(f"LINT ERROR: {msg}")
    sys.exit(1)

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

d_raw = benchmarks["repositories"]["django"]["raw_formatted"]
d_comp = benchmarks["repositories"]["django"]["comp_formatted"]
d_pct = benchmarks["repositories"]["django"]["reduction_pct"]
d_saved = benchmarks["repositories"]["django"]["cost_saved"]

s_raw = benchmarks["repositories"]["spring"]["raw_formatted"]
s_comp = benchmarks["repositories"]["spring"]["comp_formatted"]
s_pct = benchmarks["repositories"]["spring"]["reduction_pct"]
s_saved = benchmarks["repositories"]["spring"]["cost_saved"]

n_raw = benchmarks["repositories"]["nextjs"]["raw_formatted"]
n_comp = benchmarks["repositories"]["nextjs"]["comp_formatted"]
n_pct = benchmarks["repositories"]["nextjs"]["reduction_pct"]
n_saved = benchmarks["repositories"]["nextjs"]["cost_saved"]

# File checks: list of tuples (filename, list of expected strings)
# If a string isn't found, it fails.
checks = {
    "website/index.html": [
        f"Free for codebases under {free_limit} lines",
        monthly, yearly, savings_range,
        # Django
        d_raw, d_comp, d_pct, d_saved,
        # Spring
        s_raw, s_comp, s_pct, s_saved,
        # Nextjs
        n_raw, n_comp, n_pct, n_saved,
    ],
    "website/benchmarks.html": [
        # Django
        d_raw, d_comp, d_pct, d_saved,
        # Spring
        s_raw, s_comp, s_pct, s_saved,
        # Nextjs
        n_raw, n_comp, n_pct, n_saved,
    ],
    "README.md": [
        savings_range,
        d_pct, d_saved,
        s_pct, s_saved,
        n_pct, n_saved
    ],
    "../mcp-benchmark/README.md": [
        d_pct, d_saved,
        s_pct, s_saved,
        n_pct, n_saved
    ],
    "website/vs/repomix.html": [
        f"{lang_count} Languages"
    ]
}

failed = False
for path, expected_strings in checks.items():
    if not os.path.exists(path):
        continue
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    for s in expected_strings:
        if s not in content:
            print(f"LINT ERROR: {path} is missing expected value '{s}'")
            failed = True

if failed:
    sys.exit(1)
print("Lint passed.")
