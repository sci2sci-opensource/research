from pylatexenc.latexencode import utf8tolatex

with open('oracle_axiom_equivalence.md', 'r', encoding='utf-8') as f:
    content = f.read()

latex_content = utf8tolatex(content)

with open('oracle_axiom_equivalence.latex.md', 'w', encoding='ascii') as f:
    f.write(latex_content)