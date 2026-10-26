# Independent research review — round 4

**Decision: accept the historical replay as a correctly labeled descriptive supplement, and accept the strengthened conditional mathematical corollary.** The resulting package supports a useful, bounded theory/application result. It still does not establish semantic handover safety, empirical efficacy on protected learning agents, general anti-collusion safety, or strong competition-ranking prospects.

No new model decisions, training, paid services, or protected counterfactual model trajectories were used in this review. The original 342 model requests consumed account allowance earlier; replaying their saved outputs does not reverse that usage.

## Independent historical audit

Reviewed `HISTORICAL_AUDIT_PROTOCOL.md`, `audit-historical-proposals.js`, and all generated outputs in `research/historical-audit`. A separate offline Node calculation independently verified the following rather than importing the contract's projection implementation:

- All 280 frozen input/source hashes and exact selected membership: six original manifests, 270 saved decisions, and four source/protocol files. No new or missing input silently entered the population.
- Every exported record's original model, formation origin, current receiver objective, known/unknown-demand condition, stage, branch, price, last visible rival quote, and synthetic-reference flag. Neutral replacement receivers retain the neutral label even at instructed origins.
- Exactly 270 decisions, 135 actual two-firm settlements, seven base formation episodes, and twelve dependent continuation branches. Each included settlement has one A and one B decision. Both fixed-checkpoint probe collections remain excluded.
- Exactly 267 auditable decisions and three excluded references. The missing references are the first minimal-history takeover observations in three branches; no hidden global price was substituted. Those records remain in the output with explicit missing status.
- All 1,350 decision/tolerance CSV rows and all 115 stratified summary groups. Using direct logit profit, an independent Lambert-W optimizer, and independently computed interval endpoints reproduced each proposed profit, best profit, lagged-reference regret, projected quote, distance, would-adjust flag, stratum count, fraction, and mean.
- Sanitized record/CSV schemas contain ordinal decision/episode labels and the declared economic/condition fields, without raw prompts, strategy notes, account data, or thread identifiers. The freeze inventory preserves relative source filenames and hashes; it is provenance, not publication of source decision content.

The reproduced would-adjust counts, each using the same 267-reference denominator, are:

| Profit tolerance | Would adjust |
|---|---:|
| 0 | 267 |
| 0.01 | 255 |
| 0.1 | 186 |
| 1 | 166 |
| 8 | 93 |

The criterion is absolute quote distance greater than `1e-9`. In general an exact-best-response test can count small rounding differences; a change flag is not a severity or intent label. In this particular convenience sample, the independently computed epsilon-zero distances range from approximately 0.000115 to 1.033651, with median 0.263298; 264 exceed 0.001. These are descriptive dependent-sample quantities, not independent-market statistics or proof of deliberate coordination.

## What historical replay does and does not add

It establishes that the receiver contract would alter many **actually generated historical proposals at their original observed states**, and quantifies the correction burden. That is a modest bridge from hand-written proposal families to saved language-model outputs. It does not show what either model would propose after a correction, how a rival would react, or whether protected model markets would recover. The historical prices were not generated under the new contract, and the study was post-hoc.

Keep instructed versus neutral origins, current receiver objectives, model competence/demand disclosure, and branch dependence visible. Do not present 270 quotes as independent trials, use all 270 as the comparison denominator despite missing references, call the replay a prospective defense evaluation, or claim a counterfactual customer-benefit effect. The present protocol correctly omits current-rival realized regret rather than silently reconstructing unavailable settlement alignment. It reports lagged-reference optimization only.

The freeze establishes a fixed post-hoc analysis plan and selected inputs before replay calculations. It does not make the original exploratory data confirmatory or make the later contract independent of insights learned during earlier work.

## Independently checked quantitative corollary

The reviewed calibrated model permits a stronger sufficient guarantee than merely saying prices approach a neighborhood. Set epsilon to `0.005`, which is among the previously listed analytical curve tolerances. For arbitrary initial prices in `[0,3]^2`, the maximum initial error is

`E0=max(pNash,3-pNash)=1.5270733399693772`.

Using the proved contraction constant 1/2 and the previously reviewed two-stage bounds gives

`E1 <= 0.5*E0 + delta(P0) = 1.256271737678215`,

`Et <= 0.5^(t-1)*E1 + 2*delta(P1)*(1-0.5^(t-1))`.

Since `E1 > 2*delta(P1)=0.15532138438504842`, this envelope decreases with t. At the sixth guarded update,

`E6 <= 0.1897260829254599`.

Consumer surplus decreases in each price. Therefore its worst value within this maximum-norm envelope is bounded below by surplus at the symmetric price `pNash+E6`, giving approximately **54.112193575543**. This exceeds the midpoint between competitive and joint-monopoly customer benefit:

`(71.509771124424 + 32.707804783713)/2 = 52.108787954068`.

Thus, under the stated accurate-model, authenticated-last-quote, simultaneous, bilateral, permanent, ideal-constraint assumptions, **from the sixth guarded round onward, customer harm relative to the Nash benchmark is at most half the Nash-to-monopoly benchmark gap**, for any allowed initial prices and arbitrary proposal policies. The fifth-round sufficient floor is approximately 51.091644, so this particular bound first establishes the target at round six. Later sufficient floors increase toward approximately 57.180891.

This is a benchmark-relative guarantee, not a promise to halve every initial market's actual harm; an initially competitive market may have zero harm already. It is a specialized corollary of the reviewed classical-dynamics/perturbed-contraction argument, with constants independently evaluated numerically. It is not a new general theorem or formally machine-checked floating-point certificate. The six-round interpretation is a derived analytical result, not a separately preregistered empirical six-round trial.

The cost of this useful sufficient bound must accompany it: epsilon 0.005 is only about **0.022429% of Nash per-seller profit** in this 100-buyer calibration. It allows very little departure from one-step forecast optimization. The guarantee concerns forecast loss against yesterday's rival quote; it does not promise that today's realized business profit is within 0.005 of its simultaneous best response, preserve optimal discounted repeated-game behavior, or retain meaningful language-agent discretion in every state.

## Final scope assessment

Version 1 was an honest but scientifically weak programmed-mechanism benchmark: the safe/facts null followed from controllers that did not interpret the factual note. Its correctness does not make that null a discovery about language models.

Version 2 adds a more substantive conditional result: an externally enforceable action contract, a transparent recovery argument, a quantified sufficient consumer-harm target, and independently verified unilateral, release, misspecification, and positive-epsilon failure cases. The stationary price-admissibility curve is still a symmetric slice of pure epsilon-Nash admissibility, and shielding/best-response convergence remain prior work. Historical replay adds descriptive correction-burden evidence rather than empirical defense efficacy.

I accept this package for a report that leads with these limits and attributes the known ingredients. No further model-player inference is needed to support the scoped theoretical/benchmark claim. A claim about semantic filtering, learned-agent adaptation, real-market robustness, or empirical prevention would need new relevant evidence and separately authorized resources. Reviewer acceptance means that the limited claim is supported, not that the novelty is strong enough to predict first place.
