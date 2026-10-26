# Independent review: proposal compliance versus economic choice

25 October 2026. This review supersedes the initial grading memo only where
the new credit/interface experiments provide new evidence. It is independent
of the experiment runner and analysis implementation. It accepts a scoped
claim, not a competition rank or a claim of deployment safety.

## Decision

**Accept the new extension as a valid bounded experiment and accept its main
measurement caution.** Actual feasible-action choice and proposal retention
must be reported separately. A feasible-aware chooser can achieve 100%
retention without widening the price set or changing the observed protected
economic outcome. The guard's one-price limiting behavior in these runs is
not a general impossibility result about action shielding or useful autonomy.

The original low-retention result remains true for its proposal interface.
The stronger interpretation that low retention itself measures low autonomy
must be corrected in the report, abstract, results page and game. A successful
20% retention gate under a changed interface would likewise not establish
meaningful discretion.

## Implementation and protocol review

- Read CREDIT_PROTOCOL.md and CREDIT_LONG_AMENDMENT.md, credit-learning.js,
  credit-study.js, credit-long-study.js and credit-analysis.js.
- The feasible-aware rule uses the image of the controller for the **previous
  completed rival quote** when selecting/exploring. Its Bellman next maximum
  uses the feasible set for the **newly executed rival action**. Both choices
  respect the simultaneous commitment boundary.
- The executed-index diagnostic still selects over all proposals and
  bootstraps over all Q entries. The protocol correctly calls it potentially
  misspecified; it is not standard constrained-MDP learning. Unexecuted
  optimistic Q cells can remain selectable/bootstrap targets. No sole-cause
  claim about aliasing follows from this diagnostic.
- In the released branch the projector and feasible mask are both removed;
  proposal and execution then coincide. This is a declared regime change,
  not a continuation with the constraint secretly retained.
- Five equal-budget training variants use twelve new paired seeds. The old
  deployment branches reuse existing checkpoints and are not twelve additional
  replications of training. The 100k amendment uses the same old checkpoints,
  separately frozen sources and a declared final-20k reporting window.
- Projection idempotence makes trace reexpression mathematically valid:
  M_j(M_j(a)) = M_j(a). Reexpressing a saved proposal as its execution preserves
  the executed path and rewards while making retention 100%. This is an
  ex-post representation, not a learned policy or extra independent experiment.
- Frozen files and their snapshot hashes agree. I found no source-change or
  refreezing discrepancy in this extension. Local timestamps establish ordering
  in the artifact; they are not an external preregistration service.

## Independent numerical verification

The auditor is **research/audit-credit-study.js**. It imports only platform
filesystem, path, hashing and URL utilities; it does not import an economic,
controller, learner or analysis module from the experiment. It reconstructs
logit demand, profit and consumer surplus, controller maps, feasible masks,
random draws, greedy decisions, temporal-difference updates and aggregates.

Final machine-readable record: **credit-results/independent-audit.json**.

| Verification scope | Result |
|---|---:|
| Main extension branches | 384 |
| Main evaluated settlements | 4,224,000 |
| Longer-continuation branches | 60 |
| Longer evaluated settlements | 6,000,000 |
| Actual branches in total | 444 |
| Evaluated settlements in total | 10,224,000 |
| Independent assertions | 69,184,729 |
| Maximum numerical discrepancy | 0 |
| Greedy near-tie exceptions used | 0 |
| Summary cells independently reconstructed | 42 |
| Paired contrast cells independently reconstructed | 32 |

Every available four-byte transition was replayed. Checks include proposal and
execution ranges, controller projection, aware feasibility, PRNG and choice,
every evaluation Q update, initial matched checkpoint identity, final Q arrays,
final PRNG/state/clock, update samples, bins, action counts, marginal entropies,
all mean outcomes, and the separately reported final-20k window. Every summary
mean/range and every 10,000-resample bootstrap interval was reproduced exactly.
Intervals resample whole seeds, pair alternatives within seed, and keep
training/deployment cohorts and reporting windows separate.

The 60 terminal-window rows reused by analysis do not create 60 new branches:
the 504 analysis rows comprise 444 branches plus 60 dependent terminal windows.
The bootstrap remains a small-n seeded-protocol summary, not a confidence claim
over market populations. The published fixed-index percentile calculation is
reproduced as implemented; resampling cannot repair limited external validity.

The independent auditor was also checked against intentional corruption in
memory: it accepted the original branch, rejected an altered executed-action
byte, and rejected an altered terminal Q entry. Frozen experiment files were
not modified for these checks.

**Scope limit:** the 180 million training transitions were not independently
replayed by this auditor. Their fast/general parity tests and frozen sources
provide implementation evidence, while the full replay above starts from saved
evaluation checkpoints. Do not describe 69 million assertions as independent
economic replications or claim all training transitions were independently
verified.

## Scientific interpretation and remaining limitations

The matched extension is a substantive improvement over the earlier submission
idea. It changes a vague concern about low retention into a directly tested
measurement distinction. Protected new-trained guard learners and the terminal
long-run deployment windows share the same reported customer welfare while
aware retention becomes 100%; feasible action fraction is 1/15, price span is
zero and marginal execution entropy is zero in those stated cells. Those last
three measurements explain why the retention improvement alone is insufficient.

Do not use zero marginal entropy by itself to prove zero strategic freedom:
even an unconstrained agent can choose a constant action. Here the directly
enumerated one-action feasible set supplies the separate choice restriction.
The short frozen deployment transients and all-100k means should not be
replaced with terminal-window values without labeling the window.

Released aware versus proposal-trained policies differ little on the reported
paired customer-welfare comparison, and its interval crosses zero. This is
consistent with no detected advantage at the available budget; it does not
prove equivalence, universally absent learning, or that aliasing is the sole
mechanism. The existing profit/cap comparisons remain multi-objective.

The cap's large early customer-surplus advantage is not enduring in this
bounded continuation: its terminal-window advantage over the aware guard is
only about .00261 per round, with paired interval [.002301, .002936]. Statistical
sign consistency in twelve seeds should not be confused with economic size.
Any summary that says the cap has a large lasting welfare advantage must be
revised to identify the early 20k window explicitly.

The small positive-tolerance grid often allows only one action. This is a
property of the chosen grid, tolerance and trajectories; a denser grid,
different tolerance, demand parameters or economic information may permit
different choice. Hundred-thousand-round evaluation is a bounded robustness
check, not proof of convergence. High prices alone remain a harmful-pricing
outcome, not established legal or strategic collusion. No semantic LLM claim is
tested by these tabular agents, and no API or account-backed game player is
needed for this result.

## Revised provisional grading

| Dimension | Current defensible assessment |
|---|---|
| Impact and innovation | **About 3/5**, subject to the closest-work check. The interface-invariant evidence is more focused than the original guard story, but projection idempotence, action shielding and aliasing are established. A case-study application does not itself establish new-to-field novelty. |
| Execution quality | **About 4/5 for this bounded question.** Matched variants, release, simple controls, fixed horizons, honest negative findings and full evaluation replay now support the claim. Not 5 solely because the numeric audit is large. |
| Presentation and clarity | **Final PDF pending.** A clear short report can plausibly reach 4; 5 requires unusually accessible and precise communication, not merely more pages or graphics. |

A first-place prediction remains unjustified. The best score improvement now
comes from a precise closest-work comparison, a concise submission report and
figures that show retention, feasible choice and economic outcomes together.
No additional engine change is needed to support the carefully limited result
accepted here. If report claims broaden, the evidence requirements broaden too.
