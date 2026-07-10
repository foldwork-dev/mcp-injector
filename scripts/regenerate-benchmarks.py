import json
import sys
import os

PRODUCT_PATH = 'website/data/product.json'
BENCHMARKS_PATH = 'website/data/benchmarks.json'

def main():
    if not os.path.exists(PRODUCT_PATH) or not os.path.exists(BENCHMARKS_PATH):
        print("Error: Required JSON files not found.")
        sys.exit(1)

    with open(PRODUCT_PATH, 'r') as f:
        product = json.load(f)
    
    with open(BENCHMARKS_PATH, 'r') as f:
        benchmarks = json.load(f)

    base_price = product['pricing']['base_price_per_million']
    cache_mult = product['pricing']['cache_hit_multiplier']

    print(f"Regenerating benchmarks.json using Base Rate: ${base_price:.2f}/1M and Cache Multiplier: {cache_mult}x")
    
    updated = False
    for key, repo in benchmarks["repositories"].items():
        # Parse tokens
        raw_tokens = int(repo["raw_formatted"].replace(',', ''))
        comp_tokens = int(repo["comp_formatted"].replace(',', ''))
        
        # Calculate new costs
        raw_cost = (raw_tokens / 1_000_000) * base_price
        comp_cost = (comp_tokens / 1_000_000) * (base_price * cache_mult)
        savings = raw_cost - comp_cost
        
        # Format strings
        new_raw_cost_str = f"${raw_cost:.2f}"
        new_comp_cost_str = f"${comp_cost:.2f}"
        new_cost_saved_str = f"${savings:.2f}"
        
        # Update if changed
        if (repo.get("raw_cost") != new_raw_cost_str or 
            repo.get("comp_cost") != new_comp_cost_str or 
            repo.get("cost_saved") != new_cost_saved_str):
            
            repo["raw_cost"] = new_raw_cost_str
            repo["comp_cost"] = new_comp_cost_str
            repo["cost_saved"] = new_cost_saved_str
            updated = True
            print(f"Updated {repo['name']}: Savings is now {new_cost_saved_str}")
        else:
            print(f"Unchanged {repo['name']}: Savings remains {new_cost_saved_str}")

    if updated:
        with open(BENCHMARKS_PATH, 'w') as f:
            json.dump(benchmarks, f, indent=2)
            f.write('\n')
        print("\nSuccessfully regenerated benchmarks.json.")
    else:
        print("\nNo changes needed. benchmarks.json is already mathematically accurate.")

if __name__ == "__main__":
    main()
