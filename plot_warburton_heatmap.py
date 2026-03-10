import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
import argparse

SCRIPT_DIR = Path(__file__).resolve().parent

def parse_args():
    p = argparse.ArgumentParser(description='Plot heatmap of net operating result vs visits/day and avg fee')
    p.add_argument('--input', '-i', default=str(SCRIPT_DIR / 'warburton_sweep.csv'), help='Path to sweep CSV')
    p.add_argument('--output', '-o', default=str(SCRIPT_DIR / 'warburton_heatmap.png'), help='Output PNG path')
    return p.parse_args()


def main():
    args = parse_args()
    df = pd.read_csv(args.input)

    # Ensure numeric types
    df['visits_per_day'] = df['visits_per_day'].astype(float)
    df['avg_fee'] = df['avg_fee'].astype(float)
    df['net_operating'] = df['net_operating'].astype(float)

    # Pivot table: rows=visits/day, cols=avg_fee, values=net_operating
    pivot = df.pivot_table(index='visits_per_day', columns='avg_fee', values='net_operating', aggfunc='mean')

    # Sort rows/cols
    pivot = pivot.sort_index()
    pivot = pivot.reindex(sorted(pivot.columns), axis=1)

    visits = pivot.index.values
    fees = pivot.columns.values
    Z = pivot.values

    # Create heatmap
    fig, ax = plt.subplots(figsize=(10, 8))
    cmap = plt.get_cmap('RdYlGn')
    # Show centered colorbar at zero for clear profit/loss
    max_abs = np.nanmax(np.abs(Z))
    im = ax.imshow(Z, aspect='auto', origin='lower', cmap=cmap, vmin=-max_abs, vmax=max_abs)

    # Ticks
    ax.set_xticks(np.arange(len(fees)))
    ax.set_xticklabels([int(x) for x in fees], rotation=45)
    ax.set_yticks(np.arange(len(visits)))
    ax.set_yticklabels([int(x) for x in visits])

    ax.set_xlabel('Average fee per visit (AUD)')
    ax.set_ylabel('Visits per day')
    ax.set_title('Net operating result (monthly) — Warburton clinic')

    # Annotate some cells (only if grid is not too large)
    if Z.shape[0] <= 40 and Z.shape[1] <= 30:
        for i in range(Z.shape[0]):
            for j in range(Z.shape[1]):
                val = Z[i, j]
                if not np.isnan(val):
                    ax.text(j, i, f"${val:,.0f}", ha='center', va='center', fontsize=7, color='black')

    cbar = fig.colorbar(im, ax=ax)
    cbar.set_label('Net operating ($/month)')

    plt.tight_layout()
    plt.savefig(args.output, dpi=150, bbox_inches='tight')
    print(f"Saved heatmap to {args.output}")

if __name__ == '__main__':
    main()
