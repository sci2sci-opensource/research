#!/usr/bin/env python3
"""
Unified paper compiler: markdown -> PDF / HTML / arXiv source bundle.

One copy for every paper in this repository. All per-paper information comes from the
paper's own YAML front matter; nothing is baked into this script.

    python paper-tools/compile_paper.py path/to/paper.md            # html (+ pdf if LaTeX present)
    python paper-tools/compile_paper.py paper.md --pdf --twocol
    python paper-tools/compile_paper.py paper.md --html
    python paper-tools/compile_paper.py paper.md --arxiv            # source bundle for arXiv
    python paper-tools/build_all.py                                 # every registered paper

Front-matter keys used: title (required), subtitle, date, author, institute, lang.
Defaults: author "Valerii Kremnev", institute "Independent Researcher, sci2sci llc".
Per-paper LaTeX additions: place `header-extra.tex` next to the paper; it is appended
after the canonical paper-tools/latex-header.tex. Do not fork the shared files.

Requires: pandoc; pdflatex for PDF output (PDF steps are skipped with a notice otherwise).
"""

import argparse
import datetime
import re
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
HEADER = TOOLS / "latex-header.tex"
CSS = TOOLS / "paper-style.css"
FILTERS = [TOOLS / "filters" / "pagebreak-filter.lua",
           TOOLS / "filters" / "bold-headers-filter.lua"]

# The single markdown dialect for all papers in this repo: pandoc markdown with
# \( \) inline and \[ \] / $$ display math, no forced line wrapping surprises.
FROM_FORMAT = "markdown+tex_math_single_backslash+tex_math_dollars"

DEFAULTS = {
    "author": "Valerii Kremnev",
    "institute": "Independent Researcher, sci2sci llc",
}


def read_front_matter(path: Path) -> dict:
    """Minimal YAML front-matter reader: `key: value` lines between --- fences."""
    meta = {}
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0].strip() != "---":
        return meta
    for line in lines[1:]:
        if line.strip() == "---":
            break
        m = re.match(r'^(\w[\w-]*):\s*(.*)$', line)
        if m:
            meta[m.group(1).lower()] = m.group(2).strip().strip('"')
    return meta


def out_stem(paper: Path) -> str:
    """Output basename: strips a legacy `.latex` inner extension (foo.latex.md -> foo.*)."""
    s = paper.stem
    return s[:-6] if s.endswith(".latex") else s


def discover_figures(path: Path) -> list:
    """Image references in the markdown, resolved relative to the paper."""
    text = path.read_text(encoding="utf-8")
    refs = re.findall(r'!\[[^\]]*\]\(([^)\s]+)', text)
    figures, missing = [], []
    for ref in refs:
        p = (path.parent / ref)
        (figures if p.exists() else missing).append(ref)
    for ref in missing:
        print(f"  ! figure referenced but not found: {ref}")
    return figures


def have(tool: str) -> bool:
    return shutil.which(tool) is not None


def pandoc_version() -> tuple:
    out = subprocess.run(["pandoc", "--version"], capture_output=True, text=True).stdout
    m = re.match(r"pandoc(?:\.exe)?\s+(\d+)\.(\d+)", out)
    return (int(m.group(1)), int(m.group(2))) if m else (0, 0)


def metadata_args(meta: dict) -> list:
    date = meta.get("date") or datetime.date.today().strftime("%B %Y")
    args = ["--metadata", f"title={meta.get('title', 'Untitled')}",
            "--metadata", f"author={meta.get('author', DEFAULTS['author'])}",
            "--metadata", f"institute={meta.get('institute', DEFAULTS['institute'])}",
            "--metadata", f"date={date}"]
    if meta.get("subtitle"):
        args += ["--metadata", f"subtitle={meta['subtitle']}"]
    if meta.get("lang"):
        args += ["--metadata", f"lang={meta['lang']}"]
    return args


def header_args(paper: Path) -> list:
    args = ["-H", str(HEADER)]
    extra = paper.parent / "header-extra.tex"
    if extra.exists():
        args += ["-H", str(extra)]
    return args


def run(cmd: list, timeout: int = 180) -> bool:
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    if result.returncode != 0:
        tail = "\n".join(result.stderr.splitlines()[-15:])
        print(f"  x failed:\n{tail}")
        return False
    return True


def compile_pdf(paper: Path, meta: dict, twocol: bool = False) -> bool:
    suffix = "-twocol.pdf" if twocol else ".pdf"
    out = paper.with_name(out_stem(paper) + suffix)
    print(f"  pdf  -> {out.name}" + (" (two-column)" if twocol else ""))
    cmd = ["pandoc", "-f", FROM_FORMAT, str(paper), "-o", str(out),
           "--pdf-engine=pdflatex",
           "--resource-path", str(paper.parent),
           "-V", "geometry:margin=1in", "-V", "fontsize=11pt",
           "-V", "documentclass=article",
           "-V", "classoption=" + ("twocolumn" if twocol else "openany"),
           "-V", "pagestyle=plain",
           *[a for f in FILTERS for a in ("--lua-filter", str(f))],
           *header_args(paper), *metadata_args(meta)]
    return run(cmd)


def compile_html(paper: Path, meta: dict) -> bool:
    out = paper.with_name(out_stem(paper) + ".html")
    print(f"  html -> {out.name}")
    # asset embedding only on pandoc >= 2.19 (--embed-resources); older pandoc's
    # --self-contained tries to inline a system MathJax and fails on stock installs
    embed = ["--embed-resources"] if pandoc_version() >= (2, 19) else []
    cmd = ["pandoc", "-f", FROM_FORMAT, str(paper), "-o", str(out),
           "--standalone", "--mathjax", "--number-sections",
           "--resource-path", str(paper.parent),
           "--css", str(CSS), *embed,
           *metadata_args(meta)]
    if not run(cmd):
        # embedding needs every asset readable; fall back to a plain css link
        return run([c for c in cmd if c != "--embed-resources"]) if embed else False
    return True


def arxiv_bundle(paper: Path, meta: dict, figures: list) -> bool:
    """Source bundle: paper .tex + figures + header, zipped for arXiv upload."""
    outdir = paper.parent / "arxiv_submission" / "source"
    outdir.mkdir(parents=True, exist_ok=True)
    tex = outdir / (out_stem(paper) + ".tex")
    print(f"  arxiv -> {outdir.relative_to(paper.parent)}/")
    cmd = ["pandoc", "-f", FROM_FORMAT, str(paper), "-o", str(tex),
           "--standalone", "--resource-path", str(paper.parent),
           *[a for f in FILTERS for a in ("--lua-filter", str(f))],
           *header_args(paper), *metadata_args(meta)]
    if not run(cmd):
        return False
    for ref in figures:
        src = paper.parent / ref
        shutil.copy2(src, outdir / Path(ref).name)
    zpath = paper.parent / "arxiv_submission" / (out_stem(paper) + "-arxiv.zip")
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as zf:
        for f in outdir.iterdir():
            zf.write(f, f.name)
    print(f"  arxiv -> {zpath.name}")
    return True


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    ap.add_argument("paper", type=Path)
    ap.add_argument("--pdf", action="store_true", help="PDF (single-column)")
    ap.add_argument("--twocol", action="store_true", help="additionally build two-column PDF")
    ap.add_argument("--html", action="store_true")
    ap.add_argument("--arxiv", action="store_true")
    args = ap.parse_args()

    paper = args.paper.resolve()
    if not paper.exists():
        sys.exit(f"no such paper: {paper}")
    meta = read_front_matter(paper)
    if "title" not in meta:
        sys.exit(f"{paper.name}: no `title:` in front matter — not a registered paper")

    if not have("pandoc"):
        sys.exit("pandoc not found (apt/brew/choco/winget install pandoc)")
    latex_ok = have("pdflatex")

    everything = not (args.pdf or args.html or args.arxiv or args.twocol)
    print(f"{paper.name}: \"{meta['title']}\"")
    figures = discover_figures(paper)

    ok = True
    if args.html or everything:
        ok &= compile_html(paper, meta)
    if args.pdf or args.twocol or everything:
        if latex_ok:
            ok &= compile_pdf(paper, meta, twocol=False)
            if args.twocol:
                ok &= compile_pdf(paper, meta, twocol=True)
        else:
            print("  ~ pdflatex not found: skipping PDF (install texlive/MiKTeX)")
    if args.arxiv:
        ok &= arxiv_bundle(paper, meta, figures)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
