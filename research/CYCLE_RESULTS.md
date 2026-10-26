# Coordinated finite-game audit: results and interpretation

This derived analysis was written after the frozen 24-case search and independent audit. It adds no optimized scenarios and does not retroactively preregister the initialization interpretation. Four economic calibrations cover three dimensionless demand shapes. All outcomes use the same finite grids, tolerance normalization and controller maps as the earlier learner study.

## What was calculated

For each of eight fixed scenarios, compute the minimum feasible infinite-average customer surplus and maximum feasible infinite-average joint profit under guard, cap and no control. A deliberately coordinated public-state controller replaces the learners. Its optimal outcome is a feasible policy envelope; it is not evidence of spontaneous collusion or an equilibrium. Results include all initial states, explicit prefixes and cycles, both seller profits, every finite-grid Nash pair and numerical potential certificates.

All 24 graphs and 48 objectives passed independent audit, including all 1,275,565 implicit edges, 7,296 initial-state instances, structural finite-horizon certificates and five actual-evidence corruption controls. Maximum cycle primal-dual gap is 2.186965275541297e-8. Every primary witness is stationary; no result requires a nontrivial repeating price cycle. The predeclared interval/monotone-upper-set argument exactly predicts all 24 minimum-CS solutions.

## Guard comparison across every scenario

The learned column is the mean of eight guard-aware seeds, protected, updates enabled, exploration .01, full 20,000 evaluation rounds. It is a finite observed average, while graph columns are infinite-average attainable values. No cross-economy customer-surplus means are pooled.

|Scenario|Guard global worst CS|From near-Nash anchor|Learned guard-aware CS|From none-trained starts|Cap global floor|No-control global floor|
|---|---:|---:|---:|---:|---:|---:|
|base-g15-t1|68.477|72.119|72.119|68.477–68.477|72.119|29.492|
|scale0.5-g15-t1|64.654|64.654|64.748|64.654–64.654|69.565|41.037|
|lower-quality-g15-t1|32.327|32.327|32.374|32.327–32.327|34.783|20.519|
|lowcost-g15-t1|103.114|109.348|109.348|103.114–103.114|109.348|34.167|
|base-g11-t1|65.590|70.658|70.658|65.590–65.590|70.658|29.492|
|base-g31-t1|67.271|68.961|69.004|67.271–67.271|72.363|29.492|
|base-g15-t0.5|68.477|72.119|72.119|68.477–68.477|72.119|29.492|
|base-g15-t2|64.872|68.477|68.527|64.872–64.872|72.119|29.492|

## Initialization is a real distinction

All 64 saved unprotected-training endpoints can reach their scenario’s global guard worst-CS solution. Saved protected-training endpoints lie in safer reachable basins in six scenarios; the two affine-equivalent altered-demand calibrations share a common reachable floor. These are diagnostic starts from the earlier study, not additional independent seeds. The summary retains all 256 terminal starts with checkpoint provenance and counterfactual guard/cap/no-control bounds.

For base15/tolerance .1, the near-Nash anchor and every protected-trained terminal start cannot reach the global worse basin: their reachable floor is 72.119040. Starting from every saved unprotected-trained endpoint, a feasible coordinated prefix can reach 68.477352. Both stationary pairs are exact finite-grid Nash equilibria. This is equilibrium selection within a coarse grid, so labeling this particular gap a newly discovered collusive outcome would be wrong. No forged history or unseen current proposal is required by the saved witnesses.

The global guard witness lies above every exact finite-Nash price pair in five scenarios: scale0.5-g15-t1, lower-quality-g15-t1, base-g11-t1, base-g31-t1, base-g15-t2. This establishes only finite-model feasibility under the declared tolerance. Seller incentives, discoverability and mutual stability remain separate questions.

## Individual profits and all finite Nash references

|Scenario|Guard worst-CS profit A|Profit B|Guard max joint profit|All finite Nash references: indices; CS; profit A,B|
|---|---:|---:|---:|---|
|base-g15-t1|23.628|23.628|47.256|(1,1); 72.119; 22.020,22.020<br>(2,2); 68.477; 23.628,23.628|
|scale0.5-g15-t1|31.215|31.215|62.431|(1,1); 69.565; 29.822,29.822|
|lower-quality-g15-t1|15.608|15.608|31.215|(1,1); 34.783; 14.911,14.911|
|lowcost-g15-t1|26.870|26.870|53.739|(1,1); 109.348; 23.844,23.844<br>(2,2); 103.114; 26.870,26.870|
|base-g11-t1|24.866|24.866|49.732|(0,0); 75.792; 20.355,20.355<br>(1,1); 70.658; 22.671,22.671|
|base-g31-t1|24.150|24.150|48.299|(2,2); 72.363; 21.911,21.911<br>(3,3); 70.658; 22.671,22.671|
|base-g15-t0.5|23.628|23.628|47.256|(1,1); 72.119; 22.020,22.020<br>(2,2); 68.477; 23.628,23.628|
|base-g15-t2|25.168|25.168|50.335|(1,1); 72.119; 22.020,22.020<br>(2,2); 68.477; 23.628,23.628|

Both seller profits are reported; positive joint profit alone does not demonstrate that either seller would resist deviating. The min-CS and max-joint-profit objectives remain distinct calculations even when their witnesses coincide in these guard cases. None/cap comparisons and continuous/grid joint benchmarks remain in each raw case and summary.json.

## Finite horizons and transient deficits

A separate structural certificate bounds every future T-step average by the stored certified stationary floor minus D(start)/T, excluding the previous starting-state reward. D is an all-edge checked condensation-DAG potential, not an inference from internal-SCC cycle potentials.

|Scenario|Largest future deficit D|Maximum D/20000 correction|Numerical allowance plus D/20000|
|---|---:|---:|---:|
|base-g15-t1|28.325172|0.001416259|0.001416334|
|scale0.5-g15-t1|4.735562|0.000236778|0.000236850|
|lower-quality-g15-t1|2.367781|0.000118389|0.000118425|
|lowcost-g15-t1|61.276046|0.003063802|0.003063918|
|base-g11-t1|19.652276|0.000982614|0.000982690|
|base-g31-t1|28.050256|0.001402513|0.001402589|
|base-g15-t0.5|28.325172|0.001416259|0.001416334|
|base-g15-t2|17.509159|0.000875458|0.000875534|

All 256 previously saved primary adaptive/protected learned evaluation averages also satisfy their matching controller’s newly certified 20,000-round lower bound. This is a consistency check against unchanged prior observations, not new training evidence. The bound does not imply every individual round exceeds the stationary floor.

## Resources and limits

Core run time was2.683 seconds. Largest observed whole-process RSS, sampled after completed cases rather than continuously, was238.5 MB, above the declared 100 MB target; heap used at that same RSS sample was80.5 MB. The overrun is retained and disclosed; no case was dropped. Zero failures and zero API calls were recorded.

Numerical certificates apply to floating computed weights, not exact real-valued exponentials. Symmetric deterministic two-firm logit pricing, known economics, finite price grids and pre-agreed joint coordination limit the scope. The algorithm is established graph optimization; the contribution here is the targeted controller/reachability audit and its explicit counterexamples, protective bounds and initialization distinction. The original learner evidence and frozen outputs remain unchanged.

## Proposed next reviewed goal — not run

Test a handover initializer that applies one competitive-cap round, then activates the unchanged guard. Predeclare the post-initializer target set and desired CS floor, verify that its forward reachability lies only in qualifying cyclic components, and certify every original start. A one-round initializer changes the public execution state; it must not rewrite authentic history silently. Report its one-round outcomes and its subsequent finite/infinite guarantees separately. Predeclare all eight scenarios and two desired floors: the existing near-Nash-anchor reachable floor, and the stronger competitive-cap floor. For each floor, derive the forward-invariant safe set before testing whether every cap-permitted first execution enters it. Retain scenarios where it offers no improvement or the desired safe set is empty.

Initialization alone cannot repair a requested floor above the best attainable start-specific worst-case floor: if no state belongs to a qualifying forward-invariant safe region, the tolerance/controller itself must change. Establish that feasibility before optimizing or choosing attractive starting quotes. Self-enforcement and unilateral incentive stability are a separate later MDP/game audit.
