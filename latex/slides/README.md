# Editable LaTeX slide deck

`main.tex` is the seven-slide 16:9 Beamer presentation. All prose, the Q-learning equation, the methods table, and the three scientific charts are editable LaTeX. The two game screenshots are the original accepted illustrations, copied without alteration.

Build from this directory using a TeX distribution with Beamer and PGFPlots:

```
pdflatex -interaction=nonstopmode -halt-on-error main.tex
pdflatex -interaction=nonstopmode -halt-on-error main.tex
```

The default output has exactly seven slides. Speaker notes and source citations are in `\note{...}` after each slide. To produce a separate speaker copy, replace `\setbeameroption{hide notes}` with `\setbeameroption{show notes on second screen=right}` and rebuild. Keep the default seven-slide PDF for sharing.

Data:

- `data/reference.dat`: all 12 full-grid-after-cap minus retained-guard differences, rounded to six decimal places for plotting.
- `data/matched.dat`: all 12 recurring-cap minus startup-guard differences, rounded to six decimals.
- `data/*-exact.csv`: exact rational differences from the accepted analyses, in seed order 907001–907012.
- `data/source-manifest.json`: source hashes and exact mean fractions.
- Slide 3 preserves the report's rounded structural bounds 72.119 and 66.272, against target 68.513. Finite and continuous calculations have different scopes.

The deck preserves the narrative and evidence of `output/presentation/price-guard-research-cuhk.pptx`, with readable Beamer typography. This is an authoring-format conversion; no new market experiments, model players or paid tools were used. See `SOURCES.md` for provenance and scientific limits.
