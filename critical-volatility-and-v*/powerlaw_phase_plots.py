import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm

# Set up the figure
fig, ax = plt.subplots(figsize=(12, 9))

# Define the grid - extended to include negative k_th (risk tolerance)
sigma = np.linspace(0.01, 4.0, 500)
k_th = np.linspace(-3.0, 5.0, 500)
SIGMA, K_TH = np.meshgrid(sigma, k_th)

# Calculate z = k_th / sigma
Z = K_TH / SIGMA

# Calculate survival probability p = 1 - Φ(z)
p = 1 - norm.cdf(Z)

# Calculate β_eff = σ · φ(z) / p
# Avoid division by zero
p_safe = np.where(p > 1e-10, p, 1e-10)
beta_eff = SIGMA * norm.pdf(Z) / p_safe

# Calculate power-law exponent α = -log(p) / log(β_eff)
# Only valid where β_eff > 1 and p > 0
with np.errstate(divide='ignore', invalid='ignore'):
    log_p = np.log(p_safe)
    log_beta = np.log(np.where(beta_eff > 1e-10, beta_eff, 1e-10))
    alpha = -log_p / log_beta
    alpha = np.where((beta_eff > 1) & (p > 1e-10), alpha, np.nan)

# Create filled contour for β_eff regions - more granular steps for smooth transitions
levels_beta = np.linspace(0, 5.0, 50)
cmap = plt.cm.RdYlBu_r

# Plot β_eff as filled contours
contourf = ax.contourf(SIGMA, K_TH, beta_eff, levels=levels_beta, cmap=cmap, extend='both', alpha=0.85)

# Add colorbar
cbar = plt.colorbar(contourf, ax=ax, label=r'$\beta_{eff}$ (conditional growth factor)', pad=0.02)

# Plot the critical boundary β_eff = 1
critical_contour = ax.contour(SIGMA, K_TH, beta_eff, levels=[1.0], colors=['black'], linewidths=[3])
ax.clabel(critical_contour, fmt=r'$\beta_{eff}=1$', fontsize=12, inline=True)

# Calculate and plot the analytical critical curve (extended for negative k_th)
z_range = np.linspace(-3.0, 3.0, 400)
sigma_critical = (1 - norm.cdf(z_range)) / norm.pdf(z_range)
k_th_critical = z_range * sigma_critical

# Filter to plot range
mask = (sigma_critical <= 4.0) & (sigma_critical > 0) & (k_th_critical <= 5.0) & (k_th_critical >= -3.0)
ax.plot(sigma_critical[mask], k_th_critical[mask], 'k--', linewidth=2, alpha=0.5, label='Analytical critical curve')

# Mark key points
# σ*_th = sqrt(π/2) ≈ 1.253 (critical with any threshold, k_th → 0+)
sigma_th = np.sqrt(np.pi/2)
ax.axvline(x=sigma_th, color='green', linestyle=':', linewidth=2, alpha=0.8)
ax.annotate(r'$\sigma^*_{th} = \sqrt{\pi/2}$' + f'\n≈ {sigma_th:.2f} (125.3%)',
            xy=(sigma_th, 4.7), fontsize=10, ha='center', color='darkgreen',
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.9))

# σ* = sqrt(2π) ≈ 2.507 (unconditional critical, k_th = 0)
sigma_star = np.sqrt(2*np.pi)
ax.axvline(x=sigma_star, color='red', linestyle=':', linewidth=2, alpha=0.8)
ax.annotate(r'$\sigma^* = \sqrt{2\pi}$' + f'\n≈ {sigma_star:.2f} (250.7%)',
            xy=(sigma_star, 4.7), fontsize=10, ha='center', color='darkred',
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.9))

# THE INTERSECTION POINT: where σ* = √(2π) meets the critical boundary
# z* ≈ 0.7286 is the unique positive root of Φ(z) = exp(-z²/2)
# k_th* = -z* × √(2π) ≈ -1.826
z_intersection = 0.7286  # The V* constant
k_th_intersection = -z_intersection * sigma_star
ax.plot(sigma_star, k_th_intersection, 'ko', markersize=12, markerfacecolor='yellow',
        markeredgewidth=2, zorder=10)
ax.annotate(r'$z^* \approx 0.7286$' + '\n' + r'$\Phi(z^*)=e^{-z^{*2}/2}$' + '\n' + r'$k^*_{th}=-z^*\sqrt{2\pi}$',
            xy=(sigma_star, k_th_intersection), xytext=(3.3, -2.5),
            fontsize=9, ha='left', color='black',
            bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.95, edgecolor='black'),
            arrowprops=dict(arrowstyle='->', color='black', lw=1.5))

# Add region labels - positioned for clarity
ax.text(0.3, 3.2, 'SUBCRITICAL\n' + r'$\beta_{eff} < 1$' + '\nLog-normal\n(convergent)',
        fontsize=12, ha='center', va='center', fontweight='bold',
        bbox=dict(boxstyle='round', facecolor='white', alpha=0.9, edgecolor='blue', linewidth=2))

ax.text(3.0, 2.5, 'SUPERCRITICAL\n' + r'$\beta_{eff} > 1$' + '\nPower-law (V*)\n(divergent)',
        fontsize=12, ha='center', va='center', fontweight='bold',
        bbox=dict(boxstyle='round', facecolor='white', alpha=0.9, edgecolor='red', linewidth=2))

# Add label for risk tolerance region
ax.text(0.8, -2.5, 'Risk Tolerant\n' + r'($k_{th} < 0$)',
        fontsize=10, ha='center', va='center', style='italic',
        bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

# Add label for risk averse region
ax.text(0.55, 1.5, 'Risk Averse\n' + r'($k_{th} > 0$)',
        fontsize=10, ha='center', va='center', style='italic',
        bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

# Add contours for power-law exponent α in supercritical region
alpha_levels = [0.5, 1.0, 1.5, 2.0, 3.0]
alpha_contour = ax.contour(SIGMA, K_TH, alpha, levels=alpha_levels, colors='purple',
                           linewidths=1.5, linestyles='--', alpha=0.7)
ax.clabel(alpha_contour, fmt=r'$\alpha$=%.1f', fontsize=9, inline=True)

# Labels and title
ax.set_xlabel(r'Volatility $\sigma$', fontsize=14)
ax.set_ylabel(r'Survival Threshold $k_{th}$', fontsize=14)
ax.set_title(r'V* Phase Transition: Log-Normal → Power-Law', fontsize=16, fontweight='bold')

# Add subtitle with the key equation
ax.text(0.5, -0.12,
        r'Critical boundary: $\beta_{eff} = \frac{\sigma \cdot \phi(k_{th}/\sigma)}{1 - \Phi(k_{th}/\sigma)} = 1$'
        r'    |    Power-law exponent: $\alpha = -\frac{\log(p)}{\log(\beta_{eff})}$',
        transform=ax.transAxes, fontsize=11, ha='center', style='italic')

# Set axis limits - extended for negative k_th
ax.set_xlim(0, 4.0)
ax.set_ylim(-3.0, 5.0)

# Add horizontal line at k_th = 0 for reference
ax.axhline(y=0, color='gray', linestyle='-', linewidth=1, alpha=0.5)

# Add grid
ax.grid(True, alpha=0.3, linestyle='-', linewidth=0.5)

# Add secondary x-axis for percentage volatility
ax2 = ax.twiny()
ax2.set_xlim(0, 400)
ax2.set_xlabel('Volatility (%)', fontsize=12)

plt.tight_layout()
plt.savefig('phase_transition.png', dpi=150, bbox_inches='tight',
            facecolor='white', edgecolor='none')
print("Phase transition diagram saved!")

# Also create a second plot showing the survival probability and growth rate separately
fig2, axes = plt.subplots(1, 2, figsize=(14, 6))

# Critical sigma values
sigma_th = np.sqrt(np.pi/2)
sigma_star = np.sqrt(2*np.pi)

# Left plot: Survival probability p - more granular
ax1 = axes[0]
p_levels = np.linspace(0.01, 0.99, 50)
contourf1 = ax1.contourf(SIGMA, K_TH, p, levels=p_levels, cmap='viridis', extend='both')
plt.colorbar(contourf1, ax=ax1, label=r'Survival probability $p = 1 - \Phi(k_{th}/\sigma)$')
ax1.contour(SIGMA, K_TH, beta_eff, levels=[1.0], colors=['red'], linewidths=[2.5])
# Add critical sigma lines
ax1.axvline(x=sigma_th, color='darkgreen', linestyle='--', linewidth=2.5, alpha=0.9)
ax1.axvline(x=sigma_star, color='darkred', linestyle='--', linewidth=2.5, alpha=0.9)
ax1.text(sigma_th + 0.1, 4.3, r'$\sigma^*_{th}=\sqrt{\pi/2}$', fontsize=10, color='darkgreen', fontweight='bold',
         bbox=dict(facecolor='white', alpha=0.9, edgecolor='darkgreen', pad=2))
ax1.text(sigma_star + 0.1, 4.3, r'$\sigma^*=\sqrt{2\pi}$', fontsize=10, color='darkred', fontweight='bold',
         bbox=dict(facecolor='white', alpha=0.9, edgecolor='darkred', pad=2))
ax1.set_xlabel(r'Volatility $\sigma$', fontsize=12)
ax1.set_ylabel(r'Survival Threshold $k_{th}$', fontsize=12)
ax1.set_title(r'Survival Probability per Iteration', fontsize=14)
ax1.set_xlim(0, 4.0)
ax1.set_ylim(-3.0, 5.0)
ax1.axhline(y=0, color='white', linestyle='-', linewidth=1, alpha=0.5)

# Right plot: Power-law exponent α (only in supercritical region) - more granular
ax2 = axes[1]
alpha_plot = np.where(beta_eff > 1, alpha, np.nan)
alpha_levels_full = np.linspace(0.5, 5.0, 50)
contourf2 = ax2.contourf(SIGMA, K_TH, alpha_plot, levels=alpha_levels_full, cmap='plasma', extend='both')
plt.colorbar(contourf2, ax=ax2, label=r'Power-law exponent $\alpha = -\log(p)/\log(\beta_{eff})$')
ax2.contour(SIGMA, K_TH, beta_eff, levels=[1.0], colors=['white'], linewidths=[2.5])
# Add critical sigma lines
ax2.axvline(x=sigma_th, color='darkgreen', linestyle='--', linewidth=2.5, alpha=0.9)
ax2.axvline(x=sigma_star, color='darkred', linestyle='--', linewidth=2.5, alpha=0.9)
ax2.text(sigma_th + 0.1, 4.3, r'$\sigma^*_{th}=\sqrt{\pi/2}$', fontsize=10, color='darkgreen', fontweight='bold',
         bbox=dict(facecolor='white', alpha=0.9, edgecolor='darkgreen', pad=2))
ax2.text(sigma_star + 0.1, 4.3, r'$\sigma^*=\sqrt{2\pi}$', fontsize=10, color='darkred', fontweight='bold',
         bbox=dict(facecolor='white', alpha=0.9, edgecolor='darkred', pad=2))
ax2.set_xlabel(r'Volatility $\sigma$', fontsize=12)
ax2.set_ylabel(r'Survival Threshold $k_{th}$', fontsize=12)
ax2.set_title(r'V* Distribution Exponent (Supercritical Region)', fontsize=14)
ax2.set_xlim(0, 4.0)
ax2.set_ylim(-3.0, 5.0)
ax2.axhline(y=0, color='white', linestyle='-', linewidth=1, alpha=0.5)

# Add annotation
ax2.text(0.5, 3.5, 'Subcritical\n(log-normal)', fontsize=10, ha='center', color='white',
         bbox=dict(boxstyle='round', facecolor='gray', alpha=0.8))

plt.tight_layout()
plt.savefig('phase_components.png', dpi=150, bbox_inches='tight',
            facecolor='white', edgecolor='none')
print("Component plots saved!")