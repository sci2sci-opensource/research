"""
V* Distribution - Interactive Dashboard with Dash
"""

import numpy as np
import plotly.graph_objects as go
from dash import Dash, dcc, html, callback, Output, Input
from scipy.stats import norm
from scipy.optimize import brentq
from scipy.special import log_ndtr

def expected_wealth(sigma, k_th, n, N=1000, w0=1.0):
    """Calculate expected total wealth at step n."""
    sigma = np.maximum(sigma, 1e-6)
    term1 = (sigma / np.sqrt(2 * np.pi)) ** n
    term2 = np.exp(-n * k_th**2 / (2 * sigma**2))
    return N * w0 * term1 * term2


def asymmetric_log_scale(W, compress_negative=0.3):
    """
    Asymmetric log scale: compress negative log values, expand positive.

    For W >= 1: log10(W) as normal
    For W < 1: compress by factor (so negative log takes less space)
    """
    W_log = np.log10(np.maximum(W, 1e-10))
    # Compress negative values (log < 0)
    W_scaled = np.where(W_log >= 0, W_log, W_log * compress_negative)
    return W_scaled

def calc_p(sigma, k_th):
    """Survival probability."""
    z = k_th / np.maximum(sigma, 1e-10)
    return 1 - norm.cdf(z)

def calc_beta_eff(sigma, k_th):
    """Conditional growth factor - numerically stable."""
    sigma = np.maximum(sigma, 1e-10)
    z = k_th / sigma
    log_p = log_ndtr(-z)
    log_phi = -0.5 * z**2 - 0.5 * np.log(2 * np.pi)
    return np.exp(np.log(sigma) + log_phi - log_p)

def calc_alpha(sigma, k_th):
    """Power-law exponent α = -log(p) / log(β_eff) - numerically stable."""
    sigma = np.maximum(sigma, 1e-10)
    z = k_th / sigma
    log_p = log_ndtr(-z)
    log_phi = -0.5 * z**2 - 0.5 * np.log(2 * np.pi)
    beta = np.exp(np.log(sigma) + log_phi - log_p)

    with np.errstate(divide='ignore', invalid='ignore'):
        alpha = -log_p / np.log(beta)

    # Only valid when β_eff > 1
    alpha = np.where(beta > 1, alpha, np.nan)
    return alpha

def find_alpha_contour(sigma_range, target_alpha):
    """Find k_th where α = target_alpha for each σ, only in supercritical region."""
    k_th_vals = []
    sigma_vals = []

    for sig in sigma_range:
        def f_alpha(k):
            z = k / sig
            log_p = log_ndtr(-z)
            log_phi = -0.5 * z**2 - 0.5 * np.log(2 * np.pi)
            beta = np.exp(np.log(sig) + log_phi - log_p)

            if beta <= 1.0:
                return 1000 * (1 - beta)

            alpha = -log_p / np.log(beta)
            return alpha - target_alpha

        k_range = np.linspace(-3.0, 5.0, 100)
        f_vals = [f_alpha(k) for k in k_range]

        for i in range(len(k_range)-1):
            if f_vals[i] * f_vals[i+1] < 0:
                try:
                    k_sol = brentq(f_alpha, k_range[i], k_range[i+1])
                    z = k_sol / sig
                    log_p = log_ndtr(-z)
                    log_phi = -0.5 * z**2 - 0.5 * np.log(2 * np.pi)
                    beta = np.exp(np.log(sig) + log_phi - log_p)

                    if beta > 1.001:
                        k_th_vals.append(k_sol)
                        sigma_vals.append(sig)
                except:
                    pass

    if len(sigma_vals) == 0:
        return np.array([]), np.array([])

    sigma_vals = np.array(sigma_vals)
    k_th_vals = np.array(k_th_vals)
    sort_idx = np.argsort(k_th_vals)

    return sigma_vals[sort_idx], k_th_vals[sort_idx]

def find_critical_boundary(z_range=None):
    """Find the critical boundary where β_eff = 1."""
    if z_range is None:
        z_range = np.linspace(-1, 100, 2000)

    log_p = log_ndtr(-z_range)
    log_phi = -0.5 * z_range**2 - 0.5 * np.log(2 * np.pi)

    sigma_critical = np.exp(log_p - log_phi)
    k_th_critical = z_range * sigma_critical

    mask = (sigma_critical > 0.3) & (sigma_critical < 4.0) & (k_th_critical > -3.0) & (k_th_critical < 5.0)

    return sigma_critical[mask], k_th_critical[mask]


# Pre-compute static data
SIGMA_CRIT = np.sqrt(2 * np.pi)
SIGMA_TH = np.sqrt(np.pi / 2)
SIGMA_RANGE = np.linspace(0.3, 4.0, 80)
K_TH_RANGE = np.linspace(-3.0, 5.0, 100)
SIGMA, K_TH = np.meshgrid(SIGMA_RANGE, K_TH_RANGE)
BETA_EFF = calc_beta_eff(SIGMA, K_TH)
SIG_CRIT_BOUNDARY, K_CRIT_BOUNDARY = find_critical_boundary()

# Pre-compute alpha contours (they don't depend on n, N, w0)
SIGMA_FINE = np.linspace(0.3, 4.0, 500)
ALPHA_VALUES = [1, 1.5, 2, 3, 5, 7, 10, 15, 20, 30, 50]
ALPHA_COLORS = ['#00008B', '#0000CD', '#4169E1', '#228B22', '#9ACD32', '#FFD700', '#FFA500', '#FF4500', '#FF0000', '#DC143C', '#800000']
ALPHA_CONTOURS = {}
for alpha_target in ALPHA_VALUES:
    sig_a, k_a = find_alpha_contour(SIGMA_FINE, alpha_target)
    if len(sig_a) > 2:
        ALPHA_CONTOURS[alpha_target] = (sig_a, k_a)


def create_figure(n, N, w0):
    """Create the 3D figure with current parameters."""

    # Calculate wealth surface with asymmetric log scale
    W = expected_wealth(SIGMA, K_TH, n, N, w0)
    W_scaled = asymmetric_log_scale(W)
    z_min, z_max = np.nanmin(W_scaled), np.nanmax(W_scaled)

    fig = go.Figure()

    # Main wealth surface - colored by β_eff
    fig.add_trace(go.Surface(
        x=SIGMA,
        y=K_TH,
        z=W_scaled,
        surfacecolor=BETA_EFF,
        colorscale='RdYlBu_r',
        cmin=0,
        cmax=5,
        colorbar=dict(title='β_eff', x=1.02, len=0.6, y=0.7),
        name='W surface',
        hoverinfo='x+y+z'
    ))

    # Critical boundary β_eff = 1
    if len(SIG_CRIT_BOUNDARY) > 0:
        z_crit = asymmetric_log_scale(
            expected_wealth(SIG_CRIT_BOUNDARY, K_CRIT_BOUNDARY, n, N, w0))

        fig.add_trace(go.Scatter3d(
            x=SIG_CRIT_BOUNDARY,
            y=K_CRIT_BOUNDARY,
            z=z_crit,
            mode='lines',
            line=dict(color='black', width=8),
            name='β_eff = 1',
            hoverinfo='skip'
        ))

    # α contour lines
    for alpha_target, color in zip(ALPHA_VALUES, ALPHA_COLORS):
        if alpha_target in ALPHA_CONTOURS:
            sig_a, k_a = ALPHA_CONTOURS[alpha_target]
            z_a = asymmetric_log_scale(
                expected_wealth(sig_a, k_a, n, N, w0))

            fig.add_trace(go.Scatter3d(
                x=sig_a,
                y=k_a,
                z=z_a,
                mode='lines',
                line=dict(color=color, width=5),
                name=f'α = {alpha_target}',
                hoverinfo='skip'
            ))

    # Vertical planes for σ* and σ*_th
    k_plane = np.linspace(-3.0, 5.0, 30)
    z_plane = np.linspace(z_min - 1, z_max + 1, 30)
    K_PLANE, Z_PLANE = np.meshgrid(k_plane, z_plane)

    fig.add_trace(go.Surface(
        x=np.full_like(K_PLANE, SIGMA_CRIT),
        y=K_PLANE,
        z=Z_PLANE,
        colorscale=[[0, 'rgba(255,0,0,0.15)'], [1, 'rgba(255,0,0,0.15)']],
        showscale=False,
        name=f'σ* ≈ {SIGMA_CRIT:.2f}',
        hoverinfo='skip'
    ))

    fig.add_trace(go.Surface(
        x=np.full_like(K_PLANE, SIGMA_TH),
        y=K_PLANE,
        z=Z_PLANE,
        colorscale=[[0, 'rgba(255,165,0,0.15)'], [1, 'rgba(255,165,0,0.15)']],
        showscale=False,
        name=f'σ*_th ≈ {SIGMA_TH:.2f}',
        hoverinfo='skip'
    ))

    fig.update_layout(
        title=dict(
            text=(
                f"<b>V* Distribution: Expected Wealth</b><br>"
                f"<sup>n={n}, N={N:,}, w₀=${w0:,.0f} | Surface colored by β_eff</sup>"
            ),
            x=0.5,
            font=dict(size=18)
        ),
        scene=dict(
            xaxis=dict(title=dict(text="σ (volatility)")),
            yaxis=dict(title=dict(text="k_th (threshold)")),
            zaxis=dict(title=dict(text="Wealth (asymmetric log)")),
            camera=dict(eye=dict(x=1.5, y=1.5, z=1.0)),
            aspectratio=dict(x=1, y=1, z=0.7)
        ),
        height=700,
        margin=dict(l=20, r=20, t=80, b=20),
        legend=dict(x=1.02, y=0.5, bgcolor='rgba(255,255,255,0.9)')
    )

    return fig


# Create Dash app
app = Dash(__name__)

W0_VALUES = [0.01, 0.1, 1, 10, 100, 1000, 10000, 100000, 1000000, 10000000]

app.layout = html.Div([
    html.H1("V* Distribution: Interactive Wealth Surface",
            style={'textAlign': 'center', 'marginBottom': '10px'}),

    html.Div([
        html.Div([
            html.Label("Steps (n):"),
            dcc.Slider(id='n-slider', min=1, max=50, step=1, value=5,
                      marks={i: str(i) for i in [1, 10, 20, 30, 40, 50]},
                      tooltip={"placement": "bottom", "always_visible": True})
        ], style={'flex': '1', 'padding': '0 20px'}),

        html.Div([
            html.Label("Participants (N):"),
            dcc.Slider(id='N-slider', min=1, max=8, step=1, value=3,
                      marks={i: f'10^{i}' for i in range(1, 9)},
                      tooltip={"placement": "bottom", "always_visible": True})
        ], style={'flex': '1', 'padding': '0 20px'}),

        html.Div([
            html.Label("Initial Wealth (w₀):"),
            dcc.Slider(id='w0-slider', min=0, max=9, step=1, value=2,
                      marks={0: '$0.01', 2: '$1', 4: '$100', 6: '$10K', 8: '$1M'},
                      tooltip={"placement": "bottom", "always_visible": True})
        ], style={'flex': '1', 'padding': '0 20px'}),
    ], style={'display': 'flex', 'marginBottom': '20px', 'padding': '20px',
              'backgroundColor': '#f5f5f5', 'borderRadius': '8px'}),

    dcc.Graph(id='wealth-plot', style={'height': '75vh'})
], style={'padding': '20px', 'fontFamily': 'Arial, sans-serif'})


@callback(
    Output('wealth-plot', 'figure'),
    Input('n-slider', 'value'),
    Input('N-slider', 'value'),
    Input('w0-slider', 'value')
)
def update_figure(n, N_exp, w0_idx):
    N = 10 ** N_exp
    w0 = W0_VALUES[w0_idx]
    return create_figure(n, N, w0)


if __name__ == "__main__":
    print("Starting V* Dashboard...")
    print(f"σ* = √(2π) ≈ {np.sqrt(2*np.pi):.4f}")
    print(f"σ*_th = √(π/2) ≈ {np.sqrt(np.pi/2):.4f}")
    print("\nOpen http://127.0.0.1:8050 in your browser")

    app.run(debug=True)
