import pandas as pd
import math
import argparse
from pathlib import Path

# Locate files relative to this script so the script can be run from any CWD
SCRIPT_DIR = Path(__file__).resolve().parent

def parse_args():
    p = argparse.ArgumentParser(description='Compute Warburton urgent care monthly P&L from inputs CSV')
    p.add_argument('--input', '-i', default=str(SCRIPT_DIR / 'warburton_model_inputs.csv'), help='Path to inputs CSV')
    p.add_argument('--output', '-o', default=str(SCRIPT_DIR / 'warburton_model_outputs.csv'), help='Path to outputs CSV')
    return p.parse_args()

args = parse_args()
INPUT_CSV = args.input
OUTPUT_CSV = args.output

# Read inputs
df = pd.read_csv(INPUT_CSV, comment='#')
inputs = {row['parameter']: row['value'] for _, row in df.iterrows()}

# Helper to parse numeric values (they may be strings)
def num(x, default=0.0):
    try:
        return float(x)
    except Exception:
        return default

rent = num(inputs.get('rent', 0))
np_salary = num(inputs.get('np_salary', 0))
visits_per_day = num(inputs.get('visits_per_day', 0))
operating_days = num(inputs.get('operating_days_per_month', 22))
pct_medicare = num(inputs.get('pct_medicare', 50)) / 100.0
medicare_rebate = num(inputs.get('medicare_rebate', 40))
avg_private_fee = num(inputs.get('avg_private_fee', 90))
pathology_cost_per_test = num(inputs.get('pathology_cost_per_test', 25))
pct_path_tests = num(inputs.get('pct_pathology_tests_per_visit', 0.10))
consumables_per_visit = num(inputs.get('consumables_per_visit', 10))
admin_cost = num(inputs.get('admin_cost', 5000))
rn_support_cost = num(inputs.get('rn_support_cost', 3000))
insurance = num(inputs.get('insurance', 700))
it_costs = num(inputs.get('it_costs', 500))
marketing = num(inputs.get('marketing', 1000))
cleaning = num(inputs.get('cleaning', 600))
other_fixed = num(inputs.get('other_fixed', 500))

# Derived values
monthly_visits = visits_per_day * operating_days
medicare_visits = monthly_visits * pct_medicare
private_visits = monthly_visits * (1 - pct_medicare)

revenue_medicare = medicare_visits * medicare_rebate
revenue_private = private_visits * avg_private_fee
revenue_total = revenue_medicare + revenue_private

# Variable costs
pathology_costs = monthly_visits * pct_path_tests * pathology_cost_per_test
consumables_costs = monthly_visits * consumables_per_visit
variable_costs = pathology_costs + consumables_costs

# Fixed costs
fixed_costs = (
    rent + np_salary + admin_cost + rn_support_cost + insurance + it_costs + marketing + cleaning + other_fixed
)

gross_margin = revenue_total - variable_costs
net_operating = gross_margin - fixed_costs

# Break-even visits (monthly): fixed / (avg_rev_per_visit - var_cost_per_visit)
avg_rev_per_visit = revenue_total / monthly_visits if monthly_visits>0 else 0
var_cost_per_visit = variable_costs / monthly_visits if monthly_visits>0 else 0

if avg_rev_per_visit - var_cost_per_visit > 0:
    break_even_visits_month = fixed_costs / (avg_rev_per_visit - var_cost_per_visit)
else:
    break_even_visits_month = float('inf')

break_even_visits_day = break_even_visits_month / operating_days if operating_days>0 else float('inf')

# Output summary
summary = {
    'monthly_visits': monthly_visits,
    'medicare_visits': medicare_visits,
    'private_visits': private_visits,
    'revenue_medicare': revenue_medicare,
    'revenue_private': revenue_private,
    'revenue_total': revenue_total,
    'pathology_costs': pathology_costs,
    'consumables_costs': consumables_costs,
    'variable_costs': variable_costs,
    'fixed_costs': fixed_costs,
    'gross_margin': gross_margin,
    'net_operating': net_operating,
    'avg_rev_per_visit': avg_rev_per_visit,
    'var_cost_per_visit': var_cost_per_visit,
    'break_even_visits_month': break_even_visits_month,
    'break_even_visits_day': break_even_visits_day,
}

# Save outputs to CSV
out_df = pd.DataFrame(list(summary.items()), columns=['metric', 'value'])
out_df.to_csv(OUTPUT_CSV, index=False)

# Print readable summary
print('\nWarburton urgent care model results:\n')
print(f"Monthly visits (assumed): {monthly_visits:.0f}")
print(f"Revenue (total/month): ${revenue_total:,.2f}")
print(f"Variable costs (month): ${variable_costs:,.2f}")
print(f"Fixed costs (month): ${fixed_costs:,.2f}")
print(f"Gross margin: ${gross_margin:,.2f}")
print(f"Net operating result: ${net_operating:,.2f} per month")
print(f"Average revenue per visit: ${avg_rev_per_visit:.2f}")
print(f"Variable cost per visit: ${var_cost_per_visit:.2f}")
if math.isfinite(break_even_visits_month):
    print(f"Break-even visits/month: {break_even_visits_month:.0f} (~{break_even_visits_day:.1f} visits/day)")
else:
    print('Break-even visits: not reachable with current avg revenue <= variable cost per visit')

print(f"\nOutputs saved to {OUTPUT_CSV}")
