"""
V* Distribution - Simple ATM Model Simulation
Demonstrates the phase transition at σ* = √(2π) ≈ 2.507
"""

import numpy as np
import matplotlib.pyplot as plt
import csv


def simulate_atm_model(n=10_000_000, t=15, w0=20_000, sigma=2.5, threshold_k=2.5):
    """
    Paper's ATM model: payoff = max(X, 0) where X ~ N(0, σw)

    Args:
        n: Number of participants
        t: Number of time periods (years)
        w0: Initial wealth
        sigma: Volatility parameter
        threshold_k: Dropout threshold - stay in game only if payoff >= threshold_k * w
                     (e.g., 1.5 means you need 1.5x returns to justify staying)

    Returns:
        Array of final wealth values
    """
    w = np.full(n, w0, dtype=float)
    in_high_risk = np.ones(n, dtype=bool)
    sigma_low = 0.1  # Low-risk option for dropouts

    for year in range(t):
        # High-risk ATM option: max(X, 0) where X ~ N(0, σw)
        x_high = np.random.randn(n) * sigma * w
        payoff_high = np.maximum(x_high, 0)

        # Low-risk alternative for dropouts
        payoff_low = w * (1 + np.random.randn(n) * sigma_low)
        payoff_low = np.maximum(payoff_low, 0)

        # Dropout condition: payoff not good enough (need at least threshold_k * w to stay)
        threshold = threshold_k * w
        dropout = in_high_risk & (payoff_high < threshold)

        # Update wealth
        w = np.where(in_high_risk, payoff_high, payoff_low)
        in_high_risk = in_high_risk & ~dropout

    return w


def plot_transition():
    """Plot the phase transition around σ* = √(2π)"""

    # Volatilities to test - wide range including low volatilities
    sigmas = [0.1, 0.5, 1.0, 1.5, 2.0, 2.507, 3.0, 3.5, 4.0]
    critical = np.sqrt(2 * np.pi)

    # Colors for different regimes
    colors = plt.cm.RdYlBu_r(np.linspace(0.1, 0.9, len(sigmas)))

    fig, ax = plt.subplots(figsize=(14, 10))

    print("\n" + "="*140)
    print("PHASE TRANSITION AT σ* = √(2π) ≈ 2.507")
    print("="*140 + "\n")
    print(f"{'σ':>6} {'β':>6} {'Bankrupt':>10} {'Heavy Loss':>10} {'$2k-20k':>10} {'>$20k':>10} {'>$50k':>10} {'>$100k':>10} {'>$1M':>10} {'>$10M':>10} {'>$100M':>10} {'>$1B':>8} {'Ratio':>8}")
    print("-" * 140)

    # Collect statistics for CSV export
    stats_data = []

    for i, sigma in enumerate(sigmas):
        np.random.seed(42)
        wealth = simulate_atm_model(sigma=sigma)
        living = wealth[wealth > 0]

        # Plot rank-wealth distribution
        sorted_w = np.sort(living)[::-1]
        ranks = np.arange(1, len(sorted_w) + 1)
        idx = np.unique(np.logspace(0, np.log10(len(ranks)-1), 1000).astype(int))

        beta = sigma / critical
        regime_label = "Sub" if beta < 0.95 else "Super" if beta > 1.05 else "CRITICAL"

        # Line style: solid for key values, dashed otherwise
        linestyle = '-' if sigma in [0.1, 1.0, 2.0, 2.507, 3.0, 4.0] else '-'
        linewidth = 3 if abs(sigma - critical) < 0.01 else 2

        ax.loglog(ranks[idx], sorted_w[idx],
                 linestyle=linestyle, linewidth=linewidth, alpha=1, color=colors[i],
                 label=f'σ={sigma:.1f} (β={beta:.2f}) {regime_label}')

        # Calculate statistics at various wealth thresholds
        full_bankruptcies = np.sum(wealth < 100)  # Essentially $0 (allowing for floating point)
        heavy_loss = np.sum((wealth >= 100) & (wealth < 2000))  # Lost 90%+ but not fully bankrupt
        middle_bucket = np.sum((wealth >= 2000) & (wealth <= 20000))
        c20k = np.sum(living > 20000)
        c50k = np.sum(living > 50000)
        c100k = np.sum(living > 100000)
        m1 = np.sum(living > 1e6)
        m10 = np.sum(living > 1e7)
        m100 = np.sum(living > 1e8)
        b1 = np.sum(living > 1e9)
        ratio = m1/m10 if m10 > 0 else float('inf')

        print(f"{sigma:>6.2f} {beta:>6.2f} {full_bankruptcies:>10,} {heavy_loss:>10,} {middle_bucket:>10,} {c20k:>10,} {c50k:>10,} {c100k:>10,} {m1:>10,} {m10:>10,} {m100:>10,} {b1:>8,} {ratio:>8.1f}")

        # Collect for CSV
        stats_data.append({
            'sigma': sigma,
            'beta': beta,
            'count_full_bankruptcies': full_bankruptcies,
            'count_heavy_loss': heavy_loss,
            'count_2k_to_20k': middle_bucket,
            'count_20k': c20k,
            'count_50k': c50k,
            'count_100k': c100k,
            'count_1M': m1,
            'count_10M': m10,
            'count_100M': m100,
            'count_1B': b1,
            'ratio_1M_to_10M': ratio,
            'total_survivors': len(living),
            'mean_wealth': np.mean(living),
            'median_wealth': np.median(living),
            'max_wealth': np.max(living) if len(living) > 0 else 0
        })

    # Add reference lines
    ax.axhline(1e6, color='gray', linestyle=':', alpha=1, linewidth=1, label='$1M')
    ax.axhline(1e9, color='green', linestyle=':', alpha=1, linewidth=2, label='$1B')

    # Add Pareto reference
    ranks_ref = np.logspace(0, 7, 100)
    alpha_p = 1.5
    x_min = 20000
    pareto = x_min * (1e7 / ranks_ref) ** (1/alpha_p)
    ax.loglog(ranks_ref, pareto, 'k--', linewidth=2, alpha=0.5, label='Pareto α=1.5 (reference)')

    ax.set_xlabel('Rank', fontsize=14)
    ax.set_ylabel('Wealth ($)', fontsize=14)
    ax.set_title(f'V* Distribution: Phase Transition at σ* = √(2π) ≈ {critical:.3f}',
                 fontsize=16, fontweight='bold', pad=20)
    ax.set_ylim(1e2, 1e12)
    ax.grid(True, alpha=0.3, which='both')
    ax.legend(loc='upper right', fontsize=10, framealpha=0.9)

    plt.tight_layout()
    plt.savefig('atm_transition.png', dpi=150, bbox_inches='tight')
    print("\n✓ Saved: atm_transition.png")

    # Export statistics to CSV
    csv_filename = 'simulation_results.csv'
    with open(csv_filename, 'w', newline='') as csvfile:
        fieldnames = ['sigma', 'beta', 'count_full_bankruptcies', 'count_heavy_loss', 'count_2k_to_20k', 'count_20k', 'count_50k', 'count_100k',
                     'count_1M', 'count_10M', 'count_100M', 'count_1B',
                     'ratio_1M_to_10M', 'total_survivors', 'mean_wealth', 'median_wealth', 'max_wealth']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(stats_data)

    print(f"✓ Saved: {csv_filename}")
    print("="*140 + "\n")
    plt.show()


def plot_single_regime_comparison():
    """Compare subcritical vs supercritical in detail"""

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    critical = np.sqrt(2 * np.pi)

    # Subcritical: σ = 2.0
    print("Running subcritical simulation (σ = 1.0)...")
    np.random.seed(42)
    wealth_sub = simulate_atm_model(sigma=1.0, n=5_000_000)
    living_sub = wealth_sub[wealth_sub > 0]

    # Supercritical: σ = 3.0
    print("Running supercritical simulation (σ = 3.0)...")
    np.random.seed(42)
    wealth_super = simulate_atm_model(sigma=3.0, n=5_000_000)
    living_super = wealth_super[wealth_super > 0]

    # Plot 1: Histograms
    bins = np.logspace(2, 12, 100)
    ax1.hist(living_sub, bins=bins, alpha=0.6, label='Subcritical σ=1.0', color='blue', density=True)
    ax1.hist(living_super, bins=bins, alpha=0.6, label='Supercritical σ=3.0', color='red', density=True)
    ax1.set_xscale('log')
    ax1.set_yscale('log')
    ax1.set_xlabel('Wealth ($)')
    ax1.set_ylabel('Probability Density')
    ax1.set_title('Wealth Distribution: Log-Normal vs Power-Law', fontweight='bold')
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    # Plot 2: Rank-wealth (Zipf plot)
    sorted_sub = np.sort(living_sub)[::-1]
    ranks_sub = np.arange(1, len(sorted_sub) + 1)
    idx_sub = np.unique(np.logspace(0, np.log10(len(ranks_sub)-1), 1000).astype(int))

    sorted_super = np.sort(living_super)[::-1]
    ranks_super = np.arange(1, len(sorted_super) + 1)
    idx_super = np.unique(np.logspace(0, np.log10(len(ranks_super)-1), 1000).astype(int))

    ax2.loglog(ranks_sub[idx_sub], sorted_sub[idx_sub], 'b.', markersize=2, alpha=0.5, label='Subcritical σ=1.0')
    ax2.loglog(ranks_super[idx_super], sorted_super[idx_super], 'r.', markersize=2, alpha=0.5, label='Supercritical σ=3.0')

    # Add Pareto reference line
    ranks_ref = np.logspace(0, 7, 100)
    alpha_p = 1.5
    x_min = 20000
    pareto = x_min * (1e7 / ranks_ref) ** (1/alpha_p)
    ax2.loglog(ranks_ref, pareto, 'k--', linewidth=2, alpha=0.5, label='Pareto α=1.5 (reference)')

    ax2.set_xlabel('Rank')
    ax2.set_ylabel('Wealth ($)')
    ax2.set_title('Rank-Wealth Plot (Zipf)', fontweight='bold')
    ax2.legend()
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig('regime_comparison.png', dpi=150, bbox_inches='tight')
    print("✓ Saved: regime_comparison.png\n")
    plt.show()


def main():
    """Main execution"""
    print("\n" + "="*70)
    print("V* DISTRIBUTION - SIMPLE ATM MODEL")
    print("="*70)
    print("\nCritical threshold: σ* = √(2π) ≈ 2.507")
    print("Below σ*: Log-normal distribution (convergent)")
    print("Above σ*: Power-law distribution (divergent)")
    print("="*70)

    # Main transition plot
    plot_transition()

    # Detailed comparison
    plot_single_regime_comparison()

    print("✓ All simulations complete!\n")


if __name__ == '__main__':
    main()
