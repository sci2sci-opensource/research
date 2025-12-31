#!/usr/bin/env python3
"""
Compile the V* paper from markdown to PDF with embedded figures.
Requires: pandoc and a LaTeX distribution (e.g., MacTeX, TeX Live)
"""

import subprocess
import sys
import os
from pathlib import Path


def check_pandoc():
    """Check if pandoc is installed."""
    try:
        result = subprocess.run(['pandoc', '--version'],
                              capture_output=True, text=True)
        print(f"✓ Found pandoc: {result.stdout.split()[1]}")
        return True
    except FileNotFoundError:
        print("✗ Pandoc not found!")
        print("\nTo install pandoc:")
        print("  macOS:   brew install pandoc")
        print("  Ubuntu:  sudo apt-get install pandoc")
        print("  Windows: choco install pandoc")
        return False


def check_latex():
    """Check if pdflatex is installed."""
    try:
        result = subprocess.run(['pdflatex', '--version'],
                              capture_output=True, text=True)
        print(f"✓ Found pdflatex (LaTeX installed)")
        return True
    except FileNotFoundError:
        print("✗ pdflatex not found!")
        print("\nTo install LaTeX:")
        print("  macOS:   brew install --cask basictex")
        print("           # Or download MacTeX from http://www.tug.org/mactex/")
        print("  Ubuntu:  sudo apt-get install texlive-latex-base texlive-latex-extra")
        print("  Windows: Install MiKTeX from https://miktex.org/")
        return False


def compile_to_pdf(input_file='v*.latex.md', output_file='v*-paper.pdf'):
    """Compile markdown to PDF using pandoc."""

    print(f"\nCompiling {input_file} -> {output_file}...")

    # Pandoc command with LaTeX options
    cmd = [
        'pandoc',
        input_file,
        '-o', output_file,
        '--pdf-engine=pdflatex',
        '--lua-filter=pagebreak-filter.lua',
        '--toc',
        '--toc-depth=2',
        '-V', 'geometry:margin=1in',
        '-V', 'fontsize=11pt',
        '-V', 'documentclass=article',
        '-V', 'classoption=twocolumn',  # Two-column academic style
        '--metadata', 'title=Critical Volatility Threshold for Log-Normal to Power-Law Transition',
        '--metadata', 'subtitle=Iterated Options Model',
        '--metadata', 'author=Valerii Kremnev',
        '--metadata', 'institute=Independent Researcher, sci2sci llc',
        '--metadata', 'date=' + subprocess.run(['date', '+%B %Y'],
                                               capture_output=True, text=True).stdout.strip()
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)

        if result.returncode == 0:
            print(f"\n✓ Successfully compiled to {output_file}")

            # Check file size
            size_mb = Path(output_file).stat().st_size / (1024 * 1024)
            print(f"  File size: {size_mb:.2f} MB")

            return True
        else:
            print(f"\n✗ Compilation failed!")
            print(f"\nError output:\n{result.stderr}")
            return False


    except subprocess.TimeoutExpired:
        print("\n✗ Compilation timed out (>60s)")
        return False
    except Exception as e:
        print(f"\n✗ Error: {e}")
        return False


def compile_single_column(input_file='v*.latex.md', output_file='v*-paper-single.pdf'):
    """Compile to single-column PDF for easier reading."""

    print(f"\nCompiling single-column version: {input_file} -> {output_file}...")

    # Create LaTeX header for better table and list handling
    latex_header = r"""
\usepackage{longtable}
\usepackage{graphicx}
\usepackage{lscape}
\usepackage{etoolbox}
\usepackage{float}
\usepackage{array}
\usepackage{booktabs}
\AtBeginEnvironment{longtable}{\tiny\setlength{\tabcolsep}{2pt}\renewcommand{\arraystretch}{2.5}}
\setlength{\LTpre}{1em}
\setlength{\LTpost}{1em}
\providecommand{\tightlist}{%
  \setlength{\itemsep}{0pt}\setlength{\parskip}{0pt}}
\renewcommand{\labelitemi}{$\bullet$}
\renewcommand{\labelitemii}{$\circ$}
\renewcommand{\labelitemiii}{$\ast$}
\renewcommand{\labelenumi}{\arabic{enumi}.}
\renewcommand{\labelenumii}{\alph{enumii}.}
\makeatletter
\def\fps@figure{H}
\makeatother
"""

    # Write header to file
    with open('latex-header.tex', 'w') as f:
        f.write(latex_header)

    cmd = [
        'pandoc',
        '-f', 'markdown',
        input_file,
        '-o', output_file,
        '--pdf-engine=pdflatex',
        '--lua-filter=pagebreak-filter.lua',
        '--lua-filter=bold-headers-filter.lua',
        '--toc',
        '--toc-depth=2',
        '-V', 'geometry:margin=1in',
        '-V', 'fontsize=11pt',
        '-V', 'documentclass=article',
        '-V', 'pagestyle=plain',
        '-V', 'tables=yes',
        '-H', 'latex-header.tex',
        '--variable', 'classoption=openany',
        '--metadata', 'title=Critical Volatility Threshold for Log-Normal to Power-Law Transition',
        '--metadata', 'subtitle=Iterated Options Model',
        '--metadata', 'author=Valerii Kremnev',
        '--metadata', 'institute=Independent Researcher, sci2sci llc',
        '--metadata', 'date=' + subprocess.run(['date', '+%B %Y'],
                                               capture_output=True, text=True).stdout.strip()
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)

        if result.returncode == 0:
            print(f"✓ Successfully compiled to {output_file}")
            size_mb = Path(output_file).stat().st_size / (1024 * 1024)
            print(f"  File size: {size_mb:.2f} MB")
            return True
        else:
            print(f"✗ Single-column compilation failed!")
            print(f"Error: {result.stderr}")
            return False

    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def compile_to_html(input_file='v*.latex.md', output_file='v*-paper.html'):
    """Compile to HTML as fallback when LaTeX is not available."""

    print(f"\nCompiling HTML version: {input_file} -> {output_file}...")

    # Create custom CSS file for styling
    custom_css = """body {
    max-width: 900px;
    margin: 0 auto;
    padding: 2em;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif;
    line-height: 1.6;
}
img {
    max-width: 100%;
    height: auto;
    display: block;
    margin: 2em auto;
    border: 1px solid #ddd;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}
table {
    border-collapse: collapse;
    width: 100%;
    margin: 2em 0;
    font-size: 0.85em;
}
th, td {
    border: 1px solid #ddd;
    padding: 8px;
    text-align: right;
}
th {
    background-color: #f2f2f2;
    font-weight: bold;
}
h1, h2, h3 {
    color: #333;
    margin-top: 1.5em;
}
code {
    background-color: #f5f5f5;
    padding: 2px 4px;
    border-radius: 3px;
    font-size: 0.9em;
}
"""

    # Write CSS to file
    with open('paper-style.css', 'w') as f:
        f.write(custom_css)

    cmd = [
        'pandoc',
        input_file,
        '-o', output_file,
        '--standalone',
        '--mathjax',
        '--number-sections',
        '--toc',
        '--toc-depth=2',
        '--metadata', 'title=Critical Volatility Threshold for Log-Normal to Power-Law Transition',
        '--metadata', 'subtitle=Iterated Options Model',
        '--css=paper-style.css'
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

        if result.returncode == 0:
            print(f"✓ Successfully compiled to {output_file}")
            size_kb = Path(output_file).stat().st_size / 1024
            print(f"  File size: {size_kb:.1f} KB")
            return True
        else:
            print(f"✗ HTML compilation failed!")
            print(f"Error: {result.stderr}")
            return False

    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def main():
    """Main compilation routine."""
    print("="*70)
    print("V* PAPER COMPILER")
    print("="*70)

    # Check dependencies
    if not check_pandoc():
        sys.exit(1)

    has_latex = check_latex()

    # Check input file exists
    if not Path('v*.latex.md').exists():
        print("\n✗ Input file 'v*.latex.md' not found!")
        sys.exit(1)

    # Check figures exist
    figures = ['atm_transition.png', 'regime_comparison.png']
    missing = [f for f in figures if not Path(f).exists()]
    if missing:
        print(f"\n⚠ Warning: Missing figures: {missing}")
        print("  Run main.py first to generate figures")
        response = input("\nContinue anyway? (y/n): ")
        if response.lower() != 'y':
            sys.exit(1)

    # Compile based on available tools
    success_single = False
    success_two_col = False
    success_html = False

    if has_latex:
        print("\n" + "-"*70)
        success_single = compile_single_column()

        print("\n" + "-"*70)
        success_two_col = compile_to_pdf()
    else:
        print("\n" + "="*70)
        print("LaTeX not available - compiling to HTML instead")
        print("="*70)
        print("\nHTML output includes all equations (rendered with MathJax)")
        print("and embedded figures. Open in a web browser to view.\n")

        print("-"*70)
        success_html = compile_to_html()

    # Summary
    print("\n" + "="*70)
    print("COMPILATION SUMMARY")
    print("="*70)
    if success_single:
        print("✓ Single-column PDF: v*-paper-single.pdf")
    if success_two_col:
        print("✓ Two-column PDF:    v*-paper.pdf")
    if success_html:
        print("✓ HTML version:      v*-paper.html")
        print("\n  Open in browser:  open v*-paper.html  (macOS)")
        print("                    xdg-open v*-paper.html  (Linux)")

    if success_single or success_two_col or success_html:
        print("\n✓ Compilation complete!")

        if success_html and not has_latex:
            print("\n" + "="*70)
            print("To generate PDF output, install LaTeX:")
            print("="*70)
            print("\nmacOS (lightweight):  brew install --cask basictex")
            print("macOS (full):         brew install --cask mactex")
            print("Ubuntu/Debian:        sudo apt-get install texlive-latex-base texlive-latex-extra")
            print("\nAfter installing, run: python compile_paper.py")
    else:
        print("\n✗ Compilation failed")
        sys.exit(1)


if __name__ == '__main__':
    main()
