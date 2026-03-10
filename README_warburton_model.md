Warburton Urgent Care Financial Model

Files:
- `warburton_model_inputs.csv` - editable input parameters. Edit values to model scenarios.
- `compute_warburton_model.py` - Python script that reads inputs, computes monthly P&L and break-even, and writes `warburton_model_outputs.csv`.
- `warburton_model_outputs.csv` - generated output (after running script).

How to run (macOS zsh)

1. Ensure Python 3 is available. This workspace was configured with `/usr/local/bin/python3`.
2. Install dependencies (if not installed):

```bash
/usr/local/bin/python3 -m pip install pandas
```

3. Run the model:

```bash
/usr/local/bin/python3 compute_warburton_model.py
```

4. Open `warburton_model_outputs.csv` to view detailed metrics.

Notes:
- The input CSV includes default assumptions for Warburton (outer Melbourne). Adjust `visits_per_day`, `pct_medicare`, `avg_private_fee`, `rent`, and `np_salary` to reflect local circumstances.
- The model is intentionally simple and designed for quick sensitivity analysis. For greater fidelity, we can add scenario tabs, seasonality, multi-provider scaling, and cashflow projections.
