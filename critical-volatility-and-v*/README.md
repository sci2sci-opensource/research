
# V* Distribution Paper & Simulations

This repository contains the paper "Critical Volatility Threshold for Log-Normal to Power-Law Transition: Iterated Options Model" and accompanying simulation code.

## Quick Start

### 1. Run Simulations

Generate figures and data:

```bash
python plots.py
```

This creates:
- `atm_transition.png` - Phase transition chart (9 volatility levels)
- `regime_comparison.png` - Subcritical vs supercritical comparison
- `simulation_results.csv` - Detailed statistics

### 2. Compile Paper to PDF

```bash
python compile_paper.py
```

Generates:
- `v*-paper-single.pdf` - Single-column version (easier reading)

## Requirements

### Python packages:
```bash
pip install numpy matplotlib scipy
```

### For PDF compilation:
- **pandoc**: `brew install pandoc` (macOS) or `sudo apt-get install pandoc` (Linux)
- **LaTeX distribution**: MacTeX (macOS) or TeX Live (Linux)

## Files

- `v*.latex.md` - Paper source (markdown with LaTeX math)
- `main.py` - Simulation code
- `compile_paper.py` - PDF compilation script
- `simulation_results.csv` - Output data
- `*.png` - Generated figures

## Key Findings

The paper demonstrates a critical volatility threshold at **σ* = √(2π) ≈ 2.507 (251%)**:

- **Below σ***: Log-normal outcomes, convergent behavior
- **At σ***: Self-similar, critical transition
- **Above σ***: Power-law outcomes, divergent behavior

## License

- Paper: CC-BY 4.0 (cite as: Kremnev, V. (2025). Critical Volatility Threshold for Log-Normal to Power-Law Transition)
- Code: Apache 2.0 as stated in LICENSE

## Citation

```
@article{vstar2026,
  title={Critical Volatility Threshold for Log-Normal to Power-Law Transition: Iterated Options Model},
  year={2026}
}
```
