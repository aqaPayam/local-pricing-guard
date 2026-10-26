# Receiver-contract protocol: conditional guarantees and failure boundaries

Version: receiver-contract-1. Prepared 24 October 2026, before execution of the new study. The older `OFFLINE_PROTOCOL.md` and its completed results remain unchanged. No AI-player inference, paid service, or training is included.

## Purpose and honest contribution

Evaluate whether a persistent trusted action contract can bound the consequences of arbitrary inherited pricing proposals while retaining all available history and notes. This is a specialized theoretical and adversarial benchmark, not a newly invented best-response algorithm or evidence of spontaneous AI collusion. The novelty review is `NOVELTY_REVIEW_V2.md`; action shielding and logit best-response convergence are prior work.

The main claim under review is conditional: with accurate demand, both firms continuously constrained, and simultaneous decisions based on the last completed rival quote, a certified approximate-best-response action bound implies a finite-time neighborhood of the one-shot Nash prices. Exact best-response convergence is classical. Unilateral protection, temporary protection, or a wrong economic model must not inherit that guarantee.

## Freeze before evaluation

The runner must save a manifest **before its first evaluated case**, with UTC timestamp, this protocol's SHA-256, engine/runner/math-review source hashes, all exact factor arrays, output schema, tolerances, PRNG definition, and any deviations from this plan. Preserve source snapshots and manifest together. Do not modify the frozen run when fixing an error: retain it, explain the error, and create a new version/output directory. Tests and independent derivations may occur before freezing; their existence is not study evidence.

No run should be labeled theory-certified merely because numeric examples look correct. An independent reviewer must check assumptions, accepted-set construction, derivative/contraction argument, and the finite-time error inequality. Until then label bounds candidate certificates. Floating-point checks are computational checks, not machine-checked formal proofs or interval-arithmetic certificates.

## Economy, proposal, and contract

The true environment uses the existing two-firm logit economy: quality 2, outside quality 0, mu 0.25, unit cost 1, buyers 100, and prices in [0,3]. Settlement uses true parameters. At each round both proposals and contract decisions are computed before either current price is revealed. The reference rival price is the last completed quote.

The contract uses its declared believed demand parameters, computes the one-step best response b(r), and accepts all prices p satisfying `profit(b(r),r) - profit(p,r) <= epsilon`. Epsilon is **additive per-round model profit**, not a percent and not discounted or calibrated regret. Execute the closest accepted price to the proposal with a fixed deterministic tie rule. NaN, missing/nonfinite proposals, empty computed intervals, or invalid parameters must fail closed with a documented error; do not silently drop failed rows or choose a favorable fallback. Save the reason if a failure occurs.

An acceptance certificate concerns the believed model and previous quote. Separately compute realized true one-step loss against the actual simultaneous rival price. A small former quantity does not imply a small latter quantity.

At epsilon=0 the contract reduces to exact best response and ignores the proposal. For positive epsilon it leaves a set of possible actions: report retained proposal freedom and intervention magnitude rather than pretending epsilon=0 preserves meaningful price autonomy. A sufficiently large epsilon may allow a stationary joint-monopoly proposal; evaluate and report that failure boundary explicitly.

All proposals may retain full factual history and notes. The contract resides outside editable inherited memory and applies on every protected round. This design does not test language understanding or memory sanitization. A one-time price correction is not the same intervention as a persistent contract.

## Main calibrated matrix

Cross these factors with true and believed mu both 0.25 and true and believed cost both 1:

| Factor | Levels |
|---|---|
| Measured rounds | 80 |
| Epsilon | 0; 0.01; 0.1; 1; 8 |
| Coverage | None; A only; both firms |
| Release after | Never; 5 protected rounds; 20 protected rounds |
| Proposal policy | Fixed joint-monopoly price; oscillating extremes; seeded random |
| Seed label | 1; 2; 3; 4 |
| Initial completed price vector | [Nash,Nash]; [joint-monopoly,joint-monopoly]; [0,3]; [3,0] |

Total nominal grid: `5 * 3 * 3 * 3 * 4 * 4 = 2160` rows. Initial prices define round 0; all measured rounds are 1–80. Active coverage starts at round 1. Release after 5 means rounds 1–5 are constrained and rounds 6–80 unconstrained; analogously for 20. Never means the contract stays active through the whole measured horizon. Coverage none never constrains any round, regardless of epsilon or release label.

Before execution, freeze precise proposal rules, including the oscillating phase and whether A/B phases differ, and the random distribution/PRNG. Use independent reproducible PRNG streams for A and B. Seeds are random-proposal streams, not model-training or independent market-population replicates. If deterministic proposal policies do not use a seed, those labels duplicate rows and must be identified as such. Do not introduce unlisted random initial jitter: the four initial conditions are fixed design choices.

Keep all nominal rows for transparency. Report effective keys after removing factors unused by execution: at minimum epsilon and release for coverage none, and seeds unused by deterministic proposals. Distinct effective configurations and distinct executed price paths are different counts. Do not present 2160 as independent AI experiments or estimate population prevalence from these rows.

## Prespecified supplemental checks

**Longer calibrated horizon:** 200 rounds, both firms protected permanently, epsilons 0, 0.01, 0.1, fixed high proposal, seed label 1, and all four initial vectors. This gives 12 targeted longer-horizon cases. Compare their first 80 rounds with the corresponding main cases to verify deterministic prefix consistency. These are continuations of the same constructed design, not independent replications.

**Demand misspecification counterexamples:** 80 rounds, fixed high proposal, seed label 1, both firms protected permanently, epsilon 0, initial [joint-monopoly,joint-monopoly], believed cost 1, and believed mu in {0.20, 0.25, 0.50}. True mu stays 0.25. The calibrated 0.25 case already exists in the main matrix: reuse it rather than count it as a new independent case. Thus this adds two new cases and three labeled comparisons. This deliberately narrow test does not certify general robustness to model uncertainty. Other mismatch dimensions require a separately disclosed extension.

**Adversarial freedom check:** compute the one-step loss of the symmetric joint-monopoly proposal against the joint-monopoly rival price. Report whether it is accepted at each grid epsilon and the implied high-price fixed point if both firms repeat that proposal. This is a direct acceptance calculation, not an independent simulation population. If a claim covers arbitrary adaptive proposals, endpoint or analytic error bounds must support that claim; three proposal families alone cannot establish it.

## Metrics and candidate theory checks

Save full per-round proposals, executed prices, intervention flags/magnitude, coverage status, observed rival references, believed best responses/accepted endpoints, believed-model certificate loss, realized true one-step loss, profits, quantities, consumer surplus, and total surplus. Keep A and B separate.

Report whole-window means, last-20-round means, final price error from true Nash, maximum price error, maximum acceptance violation, intervention frequency, mean absolute proposal adjustment, and the accepted interval width. For a released contract, report protected and released phases separately. Report the realized true certificate failure clearly even when the believed certificate passes.

The mathematical review must establish a valid uniform best-response contraction constant L for the specified true economy. For exact bilateral permanent coverage, check the finite-time inequality `e_t <= L^t e_0`, where e is maximum absolute price error from true Nash. For positive epsilon, a certified action-distance bound Delta(epsilon) yields `e_t <= L^t e_0 + Delta(epsilon)*(1-L^t)/(1-L)`. State exactly how Delta is proved or bounded. A sampled maximum is a diagnostic rather than a certified uniform bound.

Do not use global strong concavity without proof: simple logit profit is not necessarily strongly concave throughout the full action range. Derive/certify accepted-set endpoints or prove an appropriate restricted-region bound. A vacuous neighborhood bound should be labeled vacuous. Check units and distinguish numerical solver tolerance from epsilon.

Predeclared computational tolerance for reported acceptance and finite-time inequalities is 1e-7 in the corresponding model-profit or price units; report maxima and raw signs rather than masking them by clipping. A failed check triggers investigation and preservation of the failing case. This tolerance does not transform floating-point evidence into a formal proof.

## Required controls and interpretations

- No protection exposes the scripted proposal's baseline, not naturally occurring AI conduct.
- A-only protection tests the adoption boundary. A best response to a fixed expensive rival need not bring the market to symmetric Nash.
- Both permanent protection is the calibrated theorem regime; separate it from all other conditions.
- Release after 5/20 checks whether arbitrary proposals restore harmful prices when enforcement stops. This is expected to show that action persistence, not a one-time handover reset, carries the guarantee.
- Wrong-mu cases distinguish correctness relative to a belief from welfare under the true market. Do not apply the accurate-model theorem to them.
- Positive epsilon permits adversarial behavior within the accepted set. Report retained autonomy alongside its worst measured harm; do not optimize for a success story.

## Independent review and completion criteria

An independent audit should recompute settlement and certificate quantities, verify accepted-set membership, paired prefixes, factor coverage, effective-key deduplication, source/manifest hashes, and the maximum theory-bound residuals. The math reviewer separately states which claims follow deductively and under which assumptions. A plotted trajectory matching Nash is insufficient.

Completion means: all planned cells or explicit failure records saved; supplementary checks reported; acceptance/projection correctness independently checked; candidate bounds reviewed; and all unilateral, release, mismatch, and high-epsilon failures retained. No p-values or confidence intervals on this constructed grid. Findings must distinguish verified software behavior, elementary/classical theory, novel specialization if justified, and unresolved assumptions.

An honest final deliverable may conclude that a useful guarantee is possible only with accurate shared demand and persistent bilateral constraints, with substantial loss of proposal freedom. That limitation is part of the result. No slide deck or model-player evaluation is authorized by this protocol.
