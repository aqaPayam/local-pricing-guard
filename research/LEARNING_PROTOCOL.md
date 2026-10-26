# Local learned-pricing protocol

Version local-learning-1, prepared 25 October 2026 **before learner implementation or substantive training**. The user authorizes local CPU research and coding agents, not Codex/ChatGPT game players, paid APIs, purchases, or cloud compute. Prior scripted results and historical LLM pilots are separate evidence.

## Primary question and predictions

Does a positive-tolerance persistent price constraint improve customer welfare against **independently learned adaptive proposals**, while retaining useful discretion beyond ordinary direct best response? Replacement is a secondary mechanism question: does an inherited Q table carry behavior that survives resetting the last-price observation, and does a separately trained competent successor behave differently from a cold start?

Primary contrast: bilateral discrete epsilon=.1 versus matched unguarded continuation, across all 12 held-out independently trained markets. Report frozen and adaptive outcomes separately; the primary adaptive outcome is mean consumer surplus over 100,000 continuation steps. A useful positive result must improve mean customer benefit by at least 5% of the continuous Nash–joint-monopoly reference gap **and** retain at least 20% of proposed actions, with complete per-market distributions. These are provisional research criteria, not universal safety standards. Compare business profit and simple controllers before claiming meaningful value. A small or reversed welfare difference, near-zero retained discretion, or equivalent/better simple-controller performance rejects the proposed practical advantage.

Handover prediction: resetting only the compressed last-price observation while retaining Q may preserve more high-price behavior than a cold Q reset. Treat a null or reversed effect as a valid result. Text-note deletion is meaningless for this tabular learner and is not a treatment.

## Primary literature check and reproduction boundary

[Calvano et al., AER 2020](https://www.aeaweb.org/articles?id=10.1257/aer.20190623) studies Q-learning price competition; its official page links replication materials. A [primary research preprint](https://thema.u-cergy.fr/IMG/pdf/emilio_calvano.pdf) describes initialization from discounted profit against uniformly random rivals and a long unchanged-policy convergence criterion. The official full-text/replication link could not be downloaded in this check; do not claim the replication package was executed or all published settings independently reproduced. We adopt the familiar 15-price, one-period-memory Q-learning design; our exact choices below are an adaptation, not a faithful reproduction.

[Eschenbaum, Mellgren, Zahn, Robust Algorithmic Collusion](https://arxiv.org/html/2201.00345), sections 3.4 and 3.6, uses alpha .15, exploration exp(−4e−6 t), uniform-rival initialization, and separate frozen/adaptive deployment contexts. It evaluates previously unseen counterparts and warns that training behavior can fail to transfer. Its convergence stopping rule and simulation scale are substantially larger than our bounded run. We adopt the listed learning settings and deployment distinction; we do not reproduce its complete context design or claim replacement novelty.

Departures include fixed training length, only 12 held-out markets, compressed executed-grid state with a sentinel, proposal-index credit under a guard, discrete action acceptance, independently stated success gates, and bounded controls/sensitivities. No cited protocol guarantees formation or convergence. Primary-source search/check completed before implementation; source-access limitations are disclosed rather than filled from memory.

## Economy, grid, and benchmarks

Use the existing true logit economy (quality2, cost1, outside quality0, mu.25, buyers100). Let PN and PM be its computed continuous symmetric Nash and joint-profit prices and D=PM−PN. Main actions are 15 equally spaced prices from `PN−.1D` to `PM+.1D`, inclusive. This is a narrow economic grid, not the earlier [0,3] action space. Store exact grid values in the manifest.

Compute the full 15×15 payoff table, own best-response sets, **all pure grid Nash pairs**, and grid joint-profit-maximizing pairs before training. Report continuous benchmark error. If multiple grid equilibria exist, show all and use a declared symmetric grid reference if available; otherwise use the mean outcomes over all pure grid pairs as a descriptive normalization and report its limitations. Do not silently treat a continuous Nash price as an available grid action.

## Learner definition and information boundary

Each firm has its own private Q table, independent PRNG stream, and own-profit reward. State is the last joint **executed** grid-price pair (225 possible states), plus a dedicated no-history sentinel, for 226 states and 15 actions. Firm-relative state order must be documented and identical between training/evaluation. Main training begins at a uniformly sampled completed grid pair, not a seeded monopoly convention. No current rival price, rival Q table, rival reward, or future random draw is observable before choice.

At each step: construct both observations from the same previous completed state; choose both proposal indices; independently constrain each protected action using the completed rival quote; settle both executed prices; compute each reward; then update both Q tables. No seller observes the other's newly updated Q or current action before committing. Logs must make this timing auditable.

For proposal index a, update only its own cell:

`Q(s,a) ← Q(s,a) + alpha * [own realized profit + gamma * max_a' Q(s_next,a') − Q(s,a)]`.

Main alpha=.15, gamma=.95. Exploration probability is exp(−beta*t), beta=4e−6, with t starting at zero; explore by uniform proposal index. Greedy ties select the lowest index, fixed in advance. Initial Q(s,a) is mean own grid profit against a uniformly random rival divided by (1−gamma), identical across states. The policy maximizes its own reward only; no cooperative reward, joint-profit objective, scripted retaliation, or monopoly instruction is supplied.

### Proposal versus execution credit

The main algorithm updates the **proposed index**, using reward from its actual executed action and the next executed-price state. If multiple proposals map to one executed price, only the chosen proposal cell is updated; do not secretly update all aliases. This is learning over proposals through a constrained actuator, not unconstrained executed-action Q-learning. Save proposal, execution, correction flag, reward, next state, and sample Q updates. Whether a guard intervened is logged for analysis, but not added to the learner state; neither guard interval nor opponent identity is an extra policy input. An executed-index-credit algorithm, if added, is a separately labeled sensitivity.

Public cost/demand can inform trusted preprocessing and benchmarks. The Q learner's decision input is only its state and Q table; it does not read notes, semantic market history, privileged payoffs of unchosen actions, or a rival's learning parameters. Precomputing rewards for speed is environment implementation, not giving the actor counterfactual reward feedback.

## Guard and simple baselines

The primary learned study uses a **discrete guard**. For last rival grid quote j, permit indices k whose own payoff is within epsilon of the **grid** best-response payoff. Execute the nearest permitted grid price to the proposal; ties choose the lower index. Nonempty acceptance is guaranteed by including grid maximizers. Epsilons are 0, .005, .1, and 8 profit units. Compare none, A-only, B-only, and both coverage in declared core/targeted branches. The continuous contraction theorem does **not** automatically apply to this finite action system: grid dynamics may cycle or have multiple equilibria.

Simple controls, fixed before test results: direct grid best response to the last rival quote; fixed price nearest the continuous PN (ties lower); and a cap at that same grid price, executing min(proposal,cap). Compare under the same bilateral deployment, checkpoints, rewards, windows, and correction metrics. Exact grid guard and direct grid BR can differ only in tied-maximizer choices; declare matching ties for the equivalence check.

Limited **continuous** evaluation uses the existing exact `projectQuote` with the **actual** last executed continuous rival price, not a quantized substitute. Only the learner state is discretized to nearest grid indices. Reward uses continuous execution. Keep these diagnostics separate from the discrete main experiment and save actual reference quotes. Restrict this slower branch to epsilon0/.005/.1, bilateral coverage, frozen policies, 1,000 steps per held-out checkpoint. It validates the continuous interface and highlights quantization, not a separate general learning study.

## Training, held-out units, and CPU budget

Development seeds are 11 and 22. First run an engineering timing benchmark of at most 200,000 steps per seed, then diagnostics/fixed-opponent competence checks and development training. Development outcomes may identify implementation bugs, not justify tuning until formation appears. Main seed IDs are **1001–1012**, independent market pairs. They may not be replaced because outcomes are unattractive.

Default main unguarded training is **3,000,000 steps per market**, 36 million total. Save rolling 10,000-step summaries and checkpoint Q tables at 1m, 2m, and 3m. Stop at the fixed horizon, not at a favorable formation frame. Also record policy-change diagnostics if cheap; no general convergence assertion from the horizon alone.

Use a local hard budget of **15 CPU wall minutes for the core main runs**, with a separate manifest-declared bounded extension budget for sensitivities. Measure throughput and estimated full cost first. If 3m is infeasible, reduce all main runs uniformly to 1m **before inspecting main outcomes**, record the budget-triggered departure, and freeze that horizon before training. Never give failed formation seeds more training than successful seeds selectively. No parallel process should exhaust the user's machine; document workers and memory. Preserve errors/censored runs.

Main-run manifest precedes its first training step and freezes protocol/source hashes, actual horizon, all seed mappings, observation/action/update definitions, primary branches, evaluation randomness, benchmark table, budget, and output paths. Two development pilots are not part of the main estimate.

## Formation screen and pivot

After all main runs, assess each **unselected final checkpoint**, alongside the 1m/2m checkpoints. Define candidate harmful profitable pricing when both sellers' window-mean profits exceed the declared grid Nash reference, both mean prices exceed their grid reference, and mean consumer surplus is below that reference. Require persistence in each of five consecutive 10,000-step terminal training windows, plus a separate 10,000-step no-exploration/no-update frozen evaluation. Also report magnitude and a stronger normalized-profit-gain >.5 screen, without using that screen to exclude markets from the primary welfare comparison.

These screens identify pricing outcomes, not intent or sustained strategic collusion. Paired one-step undercut probes and no-cut continuations test responses and deviation profitability. If fewer than half the 12 held-out markets pass the basic stable screen, reject a **reliable formation** premise for this budget and make the control/learning-null result primary. Still report every declared branch for all markets; do not reseed high prices and call it emergence. Passing does not establish a general population formation rate.

## Replacement and matched checkpoint arms

Fork the terminal environment, both Q tables, last executed state, learner clocks, and PRNG streams. Retain the incumbent in every branch. Swap protected/replaced identities in a targeted role-symmetry check. Main replacement arms for A:

| Arm | Q policy | Observation | Competence interpretation |
|---|---|---|---|
| Continue | Both unchanged | Retained last pair | Counterfactual reference |
| Inherited restart | Exact cloned A Q | Retained | Must match continue; process restart alone is a null |
| Information-only reset | Same A Q | A receives sentinel once | Changes its initial observation, not learned weights or B's history |
| Fresh policy | Reset A Q to declared initialization | Retained | Cold-start/inexperience, not a fair competence-matched defense |
| Fresh + reset | Fresh Q | A sentinel once | Combined intervention, labeled separately |
| Warm competent | Separately trained A against fixed competitive grid rival | Retained | Comparable training length, different training context disclosed |
| Cross-play | A Q from the next independent market in a fixed cyclic seed mapping | Retained | Tests unseen counterpart/overfitting; comparisons have cross-market dependence |

The warm controller receives the same number of own update opportunities and same hyperparameters as a main seller; it is not guaranteed equally skilled against an adaptive rival. Report fixed-rival competence and the remaining context mismatch. Cross-play is close to established deployment tests; do not claim new replacement novelty.

At an information reset only A sees the sentinel for the first successor choice; B sees its true last pair. After execution both receive the new executed pair. A sentinel row that was rarely visited may introduce an out-of-distribution initialization effect. Report it explicitly; add a one-period known-Nash-state reset sensitivity to separate missing-state artifacts from genuine forgetting. Do not call this deleting a whole learned history: the original state was already a one-round compression.

## Frozen and adaptive evaluations

For all 12 terminal checkpoints run the main replacement arms, unguarded continuation, guard epsilon0/.005/.1/8 bilateral, direct BR, fixed competitive, and price cap. First evaluate each for **10,000 steps frozen**, exploration off and Q unchanged. Separately run **100,000 adaptive steps**, alpha unchanged and a fixed evaluation exploration rate .01, with own clocks reset to a declared common continuation clock. This deliberate exploration restart differs from late-training exp(−12); keep it explicit and add a no-exploration-updating control. Branches share random streams for paired comparisons where meaningful, not forced identical actions.

Train a second matched set under bilateral epsilon=.1 from the start, same main seeds and training horizon, to distinguish guarded training from deploying a guard after unguarded learning. Include no-guard training as the equal-budget reference. Warm training and guarded training costs are separate disclosed compute, not extra evidence from the same market counted as independent seeds.

Deviation probes: force A's first executed successor action to grid best response against the last rival quote once, update through the declared proposal-credit semantics, then resume its branch rule. Compare with no-cut over 1,000 frozen steps and 10,000 adaptive steps; discount cumulative gains at .90/.95/.99. Log zero-size or price-increase probes instead of calling all interventions undercuts. If a guard would prohibit the chosen action, record whether the probe deliberately bypasses it; main diagnostic uses a **declared one-round exogenous override** and retains the originally intended proposal index for the update. No claim of equilibrium from one profitable/unprofitable deviation.

## Outcomes and uncertainty

Primary: paired market-level customer-benefit difference epsilon=.1 bilateral minus unchanged adaptive continuation, all markets. Report each market, mean difference, median, range, and a paired bootstrap interval with 10,000 resamples of whole training markets (fixed analysis seed20261025). Rounds/checkpoints/branches are dependent and cannot enlarge n. With only 12 markets, uncertainty is imprecise. Cross-play shares donor markets; report it descriptively or bootstrap complete seed networks, never independently resample those branches.

Secondary: both profits separately, prices/sales, normalized gain relative to grid and continuous references, cumulative customer benefit, fraction of proposals unchanged, correction distance, accepted interval width, and recovery time. Recovery means five consecutive 200-step windows with customer benefit at least grid Nash benefit minus 5% of the continuous Nash–monopoly gap; nonrecoveries are right-censored at the evaluation horizon. Report cold-start profit costs, no-formation seeds, errors, and unfavorable interventions.

Keep believed-model opportunity loss against the prior quote, true-model loss there, and true loss against the simultaneous current rival quote distinct. Calibrated main branches share believed/true parameters, but stale/current quantities can still differ. “Accepted interval width” alone is not business utility. Report whether discretion produces outcomes a simple price cap or BR achieves equally well.

## Bounded sensitivities and scope gates

Before sensitivity execution save a separate fixed manifest using nonmain seeds 2001–2004; no sensitivity result changes the main study retroactively. Targeted one-factor comparisons: gamma0; alpha.05/.30; beta2e−6/8e−6; initializationzero; training1m versus3m; memoryzero versus last joint state; grids11/21; and executed-index-credit versus proposal-credit. Keep the equal-budget baseline in every comparison. Run only the subsets supportable within the separately declared CPU cap; record omissions as uncompleted rather than marking all 52 tasks done from a small surrogate.

Targeted deployment checks include A-only/B-only, release after 1,000/10,000 adaptive steps, believed cost .95/1.05, believed mu .225/.275, and one declared mu shift .25→.30 at continuation step50,001 while the guard retains its old estimate for 1,000 steps. Exact subsets and a computationally bounded accepted-harm search must be frozen before their first results; no global optimality claim from a local search. Asynchronous and extra-firm checks need a separate benchmark derivation and cannot inherit the two-firm theorem. Human comprehension must remain unverified unless independent humans actually participate.

Completion requires independent learner/guard timing checks, deterministic replay, payoff/grid benchmark verification, fixed-rival competence, proposal-credit traces, unchanged/inherited equivalence, complete frozen/adaptive outputs, full seed accounting, paired analysis, simple-baseline comparisons, reproducible extraction, and adversarial interpretation review. A negative formation or zero-discretion result is a legitimate endpoint. If replacement proves incidental or ordinary BR/capping matches the benefit, narrow the story accordingly rather than preserve an unsupported handover or novelty claim.
