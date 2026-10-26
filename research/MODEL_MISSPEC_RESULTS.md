# Fixed enforcement with lower actual demand quality

This export runs only after the independent audit passes and exactly binds the primary manifest/results, current auditor/backend sources, frozen dependencies and all per-record journals. It adds no sensitivity cases or controller optimization. The target remains the original absolute F-delta amount; enforcement and the physical cap are not refitted to demand.

## Three policy slots and their different questions

Guard-only, the CLOSED-study selected timing and permanent activation of the same physical cap are preserved for every old target. Repeated policies are explicitly marked duplicates. A policy already below target at d=0 has an empty safe nonnegative set; it is not called a safe zero-radius policy. Exact zero, unresolved overlaps and censored radii remain distinct. The compact summary retains complete radius sign records and the simple nominal-reserve/(B*mu) sufficient comparison.

Here d is a taste-scale displacement: actual inside quality falls by d*mu while outside quality remains fixed. It is not percentage error, a confidence level or an estimated real-market error rate. All four tested bounds are predeclared exact rationals.

## Effective-model 95% target radius comparison

Displayed positive endpoints are approximate; full directed decimal enclosures are retained in the summary and raw records. Empty or unresolved sets are never converted to ordinary positive/zero radii.

| Scenario | Guard-only radius | Inherited selected timing radius | Permanent same-cap radius |
|---|---|---|---|
| base-g15-t1 | empty (fails at zero) | ≈0.0069632…0.0069632 | ≈0.15346…0.15346 |
| scale0.5-g15-t1 | empty (fails at zero) | ≈0.028895…0.028895 | ≈0.093709…0.093709 |
| lower-quality-g15-t1 | empty (fails at zero) | ≈0.028895…0.028895 | ≈0.093709…0.093709 |
| lowcost-g15-t1 | empty (fails at zero) | ≈0.0038608…0.0038608 | ≈0.22182…0.22182 |
| base-g11-t1 | empty (fails at zero) | ≈0.0033182…0.0033182 | ≈0.15092…0.15092 |
| base-g31-t1 | empty (fails at zero) | ≈0.0012929…0.0012929 | ≈0.15389…0.15389 |
| base-g15-t0.5 | empty (fails at zero) | ≈0.00071615…0.00071615 | ≈0.15346…0.15346 |
| base-g15-t2 | empty (fails at zero) | ≈0.051977…0.051977 | ≈0.15346…0.15346 |

## All fixed-target robust timing comparisons, effective model

These periods are new design comparisons for a KNOWN bound [0,d_bar], within the same fixed-cap fixed-period family. They are not changes to the inherited fixed-policy slot or adaptation to observed demand. The d=0 comparison must reproduce the closed selection.

| Scenario | Original target | d=0 | d=0.001 | d=0.01 | d=0.05 |
|---|---|---|---|---|---|
| base-g15-t1 | cap-90pct | none needed | none needed | none needed | none needed |
| base-g15-t1 | cap-95pct | 4 | 4 | 3 | 2 |
| base-g15-t1 | cap-99pct | 1 | 1 | 1 | fixed cap insufficient |
| base-g15-t1 | cap-100pct | 1 | fixed cap insufficient | fixed cap insufficient | fixed cap insufficient |
| base-g15-t1 | near-Nash-anchor-floor | 1 | fixed cap insufficient | fixed cap insufficient | fixed cap insufficient |
| scale0.5-g15-t1 | cap-90pct | none needed | none needed | none needed | 8 |
| scale0.5-g15-t1 | cap-95pct | 2 | 2 | 2 | 1 |
| scale0.5-g15-t1 | cap-99pct | 1 | 1 | 1 | fixed cap insufficient |
| scale0.5-g15-t1 | cap-100pct | 1 | fixed cap insufficient | fixed cap insufficient | fixed cap insufficient |
| scale0.5-g15-t1 | near-Nash-anchor-floor | 6 | 6 | 5 | 2 |
| lower-quality-g15-t1 | cap-90pct | none needed | none needed | none needed | 8 |
| lower-quality-g15-t1 | cap-95pct | 2 | 2 | 2 | 1 |
| lower-quality-g15-t1 | cap-99pct | 1 | 1 | 1 | fixed cap insufficient |
| lower-quality-g15-t1 | cap-100pct | 1 | fixed cap insufficient | fixed cap insufficient | fixed cap insufficient |
| lower-quality-g15-t1 | near-Nash-anchor-floor | 6 | 6 | 5 | 2 |
| lowcost-g15-t1 | cap-90pct | none needed | none needed | none needed | none needed |
| lowcost-g15-t1 | cap-95pct | 7 | 7 | 6 | 4 |
| lowcost-g15-t1 | cap-99pct | 1 | 1 | 1 | fixed cap insufficient |
| lowcost-g15-t1 | cap-100pct | 1 | fixed cap insufficient | fixed cap insufficient | fixed cap insufficient |
| lowcost-g15-t1 | near-Nash-anchor-floor | 1 | fixed cap insufficient | fixed cap insufficient | fixed cap insufficient |
| base-g11-t1 | cap-90pct | none needed | none needed | none needed | none needed |
| base-g11-t1 | cap-95pct | 8 | 8 | 6 | 3 |
| base-g11-t1 | cap-99pct | 1 | 1 | 1 | fixed cap insufficient |
| base-g11-t1 | cap-100pct | 1 | fixed cap insufficient | fixed cap insufficient | fixed cap insufficient |
| base-g11-t1 | near-Nash-anchor-floor | 1 | fixed cap insufficient | fixed cap insufficient | fixed cap insufficient |
| base-g31-t1 | cap-90pct | none needed | none needed | none needed | 717 |
| base-g31-t1 | cap-95pct | 4 | 4 | 3 | 2 |
| base-g31-t1 | cap-99pct | 1 | 1 | 1 | fixed cap insufficient |
| base-g31-t1 | cap-100pct | 1 | fixed cap insufficient | fixed cap insufficient | fixed cap insufficient |
| base-g31-t1 | near-Nash-anchor-floor | 3 | 3 | 3 | 2 |
| base-g15-t0.5 | cap-90pct | none needed | none needed | none needed | none needed |
| base-g15-t0.5 | cap-95pct | 10 | 9 | 7 | 3 |
| base-g15-t0.5 | cap-99pct | 1 | 1 | 1 | fixed cap insufficient |
| base-g15-t0.5 | cap-100pct | 1 | fixed cap insufficient | fixed cap insufficient | fixed cap insufficient |
| base-g15-t0.5 | near-Nash-anchor-floor | 1 | fixed cap insufficient | fixed cap insufficient | fixed cap insufficient |
| base-g15-t2 | cap-90pct | 17 | 16 | 13 | 6 |
| base-g15-t2 | cap-95pct | 2 | 2 | 2 | 2 |
| base-g15-t2 | cap-99pct | 1 | 1 | 1 | fixed cap insufficient |
| base-g15-t2 | cap-100pct | 1 | fixed cap insufficient | fixed cap insufficient | fixed cap insufficient |
| base-g15-t2 | near-Nash-anchor-floor | 2 | 2 | 2 | 2 |

## Reserve, startup and scope

Every fixed policy retains its surplus, reserve and certification at all four bounds. Welfare decreases with d, so checking the endpoint certifies a uniform bound over fixed unknown d in [0,d_bar]; no distribution or failure probability is assumed. Near-100% fragility may simply reflect a target that already consumes nearly all modeled cap welfare. It is not evidence of a new emergent mechanism. Timing alone can fail when even permanent activation of the inherited cap misses the fixed target; stronger caps or other controllers are outside this family.

Guard-only has zero startup caps and a long-run floor from arbitrary old history. Its separate single-immediate-cap variant additionally protects the activation average under the inherited condition. Cap frequency is not quote-change frequency or economic cost. Continuous calculations do not alter or recertify the earlier finite playable game.

Retained inventory: 80 model/target groups, 240 policy slots (54 duplicates), 960 fixed-level reserve rows, 320 robust-period comparisons. d=0 reproduces 80/80 closed selections; nominal/effective classification agreement holds in 8/8 retained labels. All unresolved/censored statuses are saved rather than filtered.

Primary runtime 94.376 seconds; largest after-model RSS sample 58863616 bytes, not a continuously measured peak. No new learner training, experimental seller/model API calls or paid inference services were used; Codex development assistance is separately disclosed.

The independent audit uses separate alternative-demand, radius and selection logic with its frozen 130-digit backend. Both interval stacks share standard Decimal arithmetic; this is not formal verification or arithmetic-library independence. Only this bounded quality-shift family is studied: inaccurate enforcement, uncertain taste scale, other demand shapes, time-varying errors, empirical calibration and individually optimizing seller behavior remain unaddressed. Earlier archives and numerical evidence are preserved.
