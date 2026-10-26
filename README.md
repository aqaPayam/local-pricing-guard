# When a Local Pricing Guard Is Not a Welfare Promise

**Mohammadpayam Taebi — The Chinese University of Hong Kong (CUHK)**  
AI Collusion Research Sprint, October 2026 · Team Local Pricing Guard (solo)

## For judges

- **[Play the game online](https://aqapayam.github.io/local-pricing-guard/)**
- **[Read the final report](report.pdf)** — eight main pages, references and appendices follow.
- **[Seven-slide presentation](slides.pdf)** and [four-minute recording script](VIDEO_SCRIPT.txt).
- [Editable report source](latex/report/main.tex) and [Beamer source](latex/slides/main.tex).
- [Evidence and downloadable release](https://github.com/aqaPayam/local-pricing-guard/releases/tag/submission-v1).

## What we found

In this bounded logit model, keeping a local profit-based pricing guard improves
frozen-cycle customer benefit in all twelve controlled pairs compared with
removing it after the same starting cap (mean difference for full-grid minus
guard: -12.733 model units). Repeating the cap gives a further +0.956 units in a
separate twelve-pair contrast. The guard still does not guarantee the stronger
all-policy welfare target. Continuous and saved finite-price results have
different scopes.

These are finite-budget tabular Q-learning studies, not experimental LLM
players. They do not establish convergence, real-market collusion, intent or a
universal defense. One full-grid shop earns below the static Nash benchmark.

## Play and watch

Open the online link above. **Play** lets a human choose both shops' allowed
prices. **Watch** replays saved learners and shows all twelve paired results.
The game needs no API key, payment or installed software. The human-controlled
game is an explanatory artifact, not human experimental data.

For local use, install Node.js 22 or later, then run `npm start` and open
http://127.0.0.1:3003/. This starts the read-only browser game; it does not train
models or make paid calls. The online `docs/` files adapt allowlisted routes to
GitHub Pages; the scientific kernels and original saved data remain separately
available under `research/` and the release archive.

## Reproduction and evidence

The release's full evidence archive contains the large checkpoints, frozen
sources, manifests and independent verification receipts required for full
reproduction. The repository includes browser data and scientific source code;
some audit commands require extracting that full archive into a separate folder.
Run the README commands from the full archive for that version. The old 192-run
study has narrower verification than the new 24-run and 12-run studies, which
have complete independent training replay. Repeated engineering checks do not
increase the scientific sample size.

The GitHub Pages build changes URL paths for hosting. `report.pdf` and
`slides.pdf` are the current LaTeX versions. Older versioned PDFs retain their
historical author spelling and metadata; use the current unversioned files for
submission. No experiment was rerun to make the static website.

## Prior work, contribution and assistance

The original browser game and market scaffold predate this sprint and are
preexisting work. The public Poseidon starter already supplies checkpoint
branching, replacement and history experiments. Q-learning, shielding, renewal
mixtures, cumulative safety budgets and frozen-partner dynamic programming are
established methods. This sprint's limited contribution is the linked pricing
guarantee audit and source-frozen controlled comparisons, not a new learning
algorithm. See the report for references, assumptions and ethical limitations.

Codex and collaborating AI agents substantially implemented, analyzed, checked
and drafted this work under the named author's direction. AI-agent checks are
not independent human peer review. The report states the scope of that
assistance and the earlier exploratory material excluded from its evidence.
