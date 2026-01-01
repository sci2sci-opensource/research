import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm
from scipy.special import log_ndtr

# =============================================================================
# FIGURE 1: Main Phase Transition Diagram with Power-law  Thresholds
# =============================================================================

fig, ax = plt.subplots(figsize=(14, 10))

# Define the grid
sigma_log = np.logspace(-2, np.log10(4), 500)
sigma = sigma_log
k_th = np.linspace(-3.0, 5.0, 500)
SIGMA, K_TH = np.meshgrid(sigma, k_th)

Z = K_TH / SIGMA

# Numerically stable computation
log_p = log_ndtr(-Z)
p = np.exp(log_p)
log_phi = -0.5 * Z**2 - 0.5 * np.log(2 * np.pi)
beta_eff = np.exp(np.log(SIGMA) + log_phi - log_p)

# Calculate power-law exponent α
with np.errstate(divide='ignore', invalid='ignore'):
    alpha = -log_p / np.log(beta_eff)
    alpha = np.where(beta_eff > 1, alpha, np.nan)

# Create filled contour for β_eff regions
levels_beta = np.linspace(0, 5.0, 50)
contourf = ax.contourf(SIGMA, K_TH, beta_eff, levels=levels_beta, cmap='RdYlBu_r', extend='both', alpha=0.85)
cbar = plt.colorbar(contourf, ax=ax, label=r'$\beta_{eff}$ (conditional growth factor)', pad=0.02)

# Plot the critical boundary β_eff = 1
critical_contour = ax.contour(SIGMA, K_TH, beta_eff, levels=[1.0], colors=['black'], linewidths=[3])
ax.clabel(critical_contour, fmt=r'$\beta_{eff}=1$', fontsize=11, inline=True)

# Analytical critical curve (extended range)
z_range = np.linspace(-1, 1000, 10000)
log_p_crit = log_ndtr(-z_range)
log_phi_crit = -0.5 * z_range**2 - 0.5 * np.log(2 * np.pi)
sigma_critical = np.exp(log_p_crit - log_phi_crit)
k_th_critical = z_range * sigma_critical
mask = (sigma_critical <= 4.0) & (sigma_critical > 0) & (k_th_critical <= 5.0) & (k_th_critical >= -3.0)
ax.plot(sigma_critical[mask], k_th_critical[mask], 'k--', linewidth=2, alpha=0.5)

# Key constants
sigma_th = np.sqrt(np.pi/2)
sigma_star = np.sqrt(2*np.pi)

ax.axvline(x=sigma_th, color='green', linestyle=':', linewidth=2, alpha=0.8)
ax.annotate(r'$\sigma^*_{th} = \sqrt{\pi/2}$' + f'\n≈ 1.25 (125.3%)',
            xy=(sigma_th, 4.5), fontsize=10, ha='center', color='darkgreen',
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.9, edgecolor='darkgreen'))

ax.axvline(x=sigma_star, color='red', linestyle=':', linewidth=2, alpha=0.8)
ax.annotate(r'$\sigma^* = \sqrt{2\pi}$' + f'\n≈ 2.51 (250.7%)',
            xy=(sigma_star, 4.5), fontsize=10, ha='center', color='darkred',
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.9, edgecolor='darkred'))

# k*_max = 1 asymptote
ax.axhline(y=1.0, color='orange', linestyle=':', linewidth=2, alpha=0.8)
ax.annotate(r'$k^*_{max} = 1$',
            xy=(0.08, 1.0), xytext=(0.12, 1.5), fontsize=10, ha='left', color='darkorange',
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.9, edgecolor='darkorange'),
            arrowprops=dict(arrowstyle='->', color='darkorange', lw=1.5))

# Intersection point z* ≈ 0.7286
z_intersection = 0.7286
k_th_intersection = -z_intersection * sigma_star
ax.plot(sigma_star, k_th_intersection, 'o', markersize=14, markerfacecolor='yellow',
        markeredgecolor='black', markeredgewidth=2, zorder=10)
ax.annotate(r'$z^* \approx 0.7286$' + '\n' + r'$k^*_{th} = -z^* \sqrt{2\pi} \approx -1.83$',
            xy=(sigma_star, k_th_intersection), xytext=(3.2, -2.3),
            fontsize=10, ha='left', color='black',
            bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.95, edgecolor='black', linewidth=1.5),
            arrowprops=dict(arrowstyle='->', color='black', lw=1.5))

# α contours - Power-law  thresholds
alpha_data = [
    (1, 'darkblue'),
    (1.5, 'blue'),
    (2, 'royalblue'),
    (3, 'green'),
    (5, 'yellowgreen'),
    (7, 'gold'),
    (10, 'orange'),
    (15, 'orangered'),
    (20, 'red'),
    (30, 'darkred'),
    (50, 'maroon'),
]

for level, color in alpha_data:
    cs = ax.contour(SIGMA, K_TH, alpha, levels=[level], colors=[color], linewidths=[1.8], linestyles=['--'])

# Region labels
ax.text(1, -2, 'SUBCRITICAL\n' + r'$\beta_{eff} < 1$' + '\nThin-tailed\n(convergent)',
        fontsize=11, ha='center', va='center', fontweight='bold',
        bbox=dict(boxstyle='round', facecolor='white', alpha=0.9, edgecolor='blue', linewidth=2))

ax.text(3.0, 2.5, 'SUPERCRITICAL\n' + r'$\beta_{eff} > 1$' + '\nPower-law (V*)\n(divergent)',
        fontsize=11, ha='center', va='center', fontweight='bold',
        bbox=dict(boxstyle='round', facecolor='white', alpha=0.9, edgecolor='red', linewidth=2))

ax.text(0.8, -2.5, 'Risk Tolerant\n' + r'($k_{th} < 0$)',
        fontsize=10, ha='center', va='center', style='italic',
        bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

ax.text(0.6, 3.8, 'Risk Averse\n' + r'($k_{th} > 0$)',
        fontsize=10, ha='center', va='center', style='italic',
        bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

# Labels and title
ax.set_xlabel(r'Volatility $\sigma$', fontsize=14)
ax.set_ylabel(r'Survival Threshold $k_{th}$', fontsize=14)
ax.set_title(r'V* Phase Transition with Power-law  Thresholds', fontsize=16, fontweight='bold')

ax.set_xlim(0, 4.0)
ax.set_ylim(-3.0, 5.0)
ax.axhline(y=0, color='gray', linestyle='-', linewidth=1, alpha=0.5)
ax.grid(True, alpha=0.3, linestyle='-', linewidth=0.5)

ax2 = ax.twiny()
ax2.set_xlim(0, 400)
ax2.set_xlabel('Volatility (%)', fontsize=12)

# Legend below the graph
from matplotlib.lines import Line2D
legend_labels = [
    ('darkblue', r'$\alpha=1$: Zipf law'),
    ('royalblue', r'$\alpha=2$: Pareto 80/20'),
    ('green', r'$\alpha=3$: Typical markets'),
    ('yellowgreen', r'$\alpha=5$: N > 150'),
    ('orange', r'$\alpha=10$: N > 22K'),
    ('red', r'$\alpha=20$: N > 485M'),
    ('maroon', r'$\alpha=50$: N > $10^{17}$'),
]

handles = [Line2D([0], [0], color=c, linestyle='--', linewidth=2) for c, _ in legend_labels]
labels = [l for _, l in legend_labels]

ax.legend(handles, labels, loc='upper center', bbox_to_anchor=(0.5, -0.08),
          ncol=4, fontsize=10, title=r'$\alpha$ contours: Power-law  when $N^{1/\alpha} < 1$ (N = population size)',
          title_fontsize=11)

plt.tight_layout()
plt.savefig('phase_transition.png', dpi=150, bbox_inches='tight',
            facecolor='white', edgecolor='none')
print("Phase transition diagram saved!")


# =============================================================================
# FIGURE 2: Component Plots (Survival Probability and α)
# =============================================================================

fig2, axes = plt.subplots(1, 2, figsize=(14, 6))

# Left plot: Survival probability p
ax1 = axes[0]
p_levels = np.linspace(0.01, 0.99, 50)
contourf1 = ax1.contourf(SIGMA, K_TH, p, levels=p_levels, cmap='viridis', extend='both')
plt.colorbar(contourf1, ax=ax1, label=r'Survival probability $p = 1 - \Phi(k_{th}/\sigma)$')
ax1.contour(SIGMA, K_TH, beta_eff, levels=[1.0], colors=['red'], linewidths=[2.5])
ax1.axvline(x=sigma_th, color='white', linestyle='--', linewidth=2.5, alpha=0.9)
ax1.axvline(x=sigma_star, color='white', linestyle='--', linewidth=2.5, alpha=0.9)
ax1.text(sigma_th + 0.1, 4.3, r'$\sigma^*_{th}$', fontsize=10, color='white', fontweight='bold',
         bbox=dict(facecolor='darkgreen', alpha=0.9, pad=2))
ax1.text(sigma_star + 0.1, 4.3, r'$\sigma^*$', fontsize=10, color='white', fontweight='bold',
         bbox=dict(facecolor='darkred', alpha=0.9, pad=2))
ax1.axhline(y=1.0, color='orange', linestyle='--', linewidth=2, alpha=0.8)
ax1.set_xlabel(r'Volatility $\sigma$', fontsize=12)
ax1.set_ylabel(r'Survival Threshold $k_{th}$', fontsize=12)
ax1.set_title(r'Survival Probability per Iteration', fontsize=14)
ax1.set_xlim(0, 4.0)
ax1.set_ylim(-3.0, 5.0)
ax1.axhline(y=0, color='white', linestyle='-', linewidth=1, alpha=0.5)

# Right plot: Power-law exponent α with Power-law  threshold interpretation
ax2p = axes[1]
alpha_levels_full = np.linspace(0.5, 20, 50)
contourf2 = ax2p.contourf(SIGMA, K_TH, alpha, levels=alpha_levels_full, cmap='plasma', extend='both')
cbar2 = plt.colorbar(contourf2, ax=ax2p, label=r'$\alpha = -\log(p)/\log(\beta_{eff})$')
ax2p.contour(SIGMA, K_TH, beta_eff, levels=[1.0], colors=['white'], linewidths=[2.5])

# Add specific α contours with labels
for level in [1, 2, 3, 5, 10]:
    cs = ax2p.contour(SIGMA, K_TH, alpha, levels=[level], colors=['white'], linewidths=[1.5], linestyles=['--'])
    ax2p.clabel(cs, fmt=r'$\alpha$=%d', fontsize=9, inline=True)

ax2p.axvline(x=sigma_th, color='white', linestyle='--', linewidth=2.5, alpha=0.9)
ax2p.axvline(x=sigma_star, color='white', linestyle='--', linewidth=2.5, alpha=0.9)
ax2p.text(sigma_th + 0.1, 4.3, r'$\sigma^*_{th}$', fontsize=10, color='white', fontweight='bold',
         bbox=dict(facecolor='darkgreen', alpha=0.9, pad=2))
ax2p.text(sigma_star + 0.1, 4.3, r'$\sigma^*$', fontsize=10, color='white', fontweight='bold',
         bbox=dict(facecolor='darkred', alpha=0.9, pad=2))
ax2p.axhline(y=1.0, color='orange', linestyle='--', linewidth=2, alpha=0.8)
ax2p.set_xlabel(r'Volatility $\sigma$', fontsize=12)
ax2p.set_ylabel(r'Survival Threshold $k_{th}$', fontsize=12)
ax2p.set_title(r'Power-law Exponent $\alpha$ (Power-law : $\alpha > \log N$)', fontsize=14)
ax2p.set_xlim(0, 4.0)
ax2p.set_ylim(-3.0, 5.0)
ax2p.axhline(y=0, color='white', linestyle='-', linewidth=1, alpha=0.5)

ax2p.text(1, -2.0, 'Subcritical\n(thin-tailed)', fontsize=10, ha='center', color='white',
         bbox=dict(boxstyle='round', facecolor='gray', alpha=0.8))

ax2p.text(3.0, 1, 'Fat tails\n' + r'$\alpha \approx 1-3$', fontsize=10, ha='center', color='white',
         bbox=dict(boxstyle='round', facecolor='purple', alpha=0.8))

plt.tight_layout()
plt.savefig('phase_components.png', dpi=150, bbox_inches='tight',
            facecolor='white', edgecolor='none')
print("Component plots saved!")