# Continuous and mesh refinement results

Both independent audits passed and link to the exact frozen manifests and current result/index hashes. This export also verifies every source/input hash, every mesh case hash and every continuous journal record. The full enclosures and all target labels remain in `mesh-results/summary.json`; no new scenarios or optimization are introduced here.

The finite initializer guarantees remain valid on their original grids. In the declared continuous comparison, the validated upper-choice map has one attracting fixed point and the same worst long-run surplus from every initial price pair. A finite initializer cannot remove a below-target continuation once that unchanged continuous guard resumes. This is a conditional mathematical capacity result; it does not say sellers learn or prefer this policy.

## Complete continuous table

The primary effective tolerance is the exact real sum of imported binary64 epsilon and the imported binary64 `1e-12` allowance. Nominal epsilon is separately retained. The displayed numbers below are approximations; actual interval endpoints and signed root evidence are saved as decimal strings.

| Retained scenario | Continuous Nash CS | Continuous worst CS | Nash minus worst CS | Stationary profit per seller | 95% old cap | Near-Nash anchor |
|---|---:|---:|---:|---:|---|---|
| base-g15-t1 | 71.509771 | 66.272044 | 5.237727 | 24.576760 | all-start failing continuation | all-start failing continuation |
| scale0.5-g15-t1 | 69.149548 | 63.501600 | 5.647947 | 31.513677 | all-start failing continuation | all-start failing continuation |
| lower-quality-g15-t1 | 34.574774 | 31.750800 | 2.823974 | 15.756838 | all-start failing continuation | all-start failing continuation |
| lowcost-g15-t1 | 108.307631 | 101.960114 | 6.347516 | 27.425342 | all-start failing continuation | all-start failing continuation |
| base-g11-t1 | 71.509771 | 66.272044 | 5.237727 | 24.576760 | all-start failing continuation | all-start failing continuation |
| base-g31-t1 | 71.509771 | 66.272044 | 5.237727 | 24.576760 | all-start failing continuation | all-start failing continuation |
| base-g15-t0.5 | 71.509771 | 67.793159 | 3.716612 | 23.924705 | all-start failing continuation | all-start failing continuation |
| base-g15-t2 | 71.509771 | 64.141347 | 7.368424 | 25.472387 | all-start failing continuation | all-start failing continuation |

For effective tolerance: cap-90pct: 7/8 already guaranteed, 1/8 all-start failing continuation, 0/8 unresolved; cap-95pct: 0/8 already guaranteed, 8/8 all-start failing continuation, 0/8 unresolved; cap-99pct: 0/8 already guaranteed, 8/8 all-start failing continuation, 0/8 unresolved; cap-100pct: 0/8 already guaranteed, 8/8 all-start failing continuation, 0/8 unresolved; near-Nash-anchor-floor: 0/8 already guaranteed, 8/8 all-start failing continuation, 0/8 unresolved.

For nominal tolerance: cap-90pct: 7/8 already guaranteed, 1/8 all-start failing continuation, 0/8 unresolved; cap-95pct: 0/8 already guaranteed, 8/8 all-start failing continuation, 0/8 unresolved; cap-99pct: 0/8 already guaranteed, 8/8 all-start failing continuation, 0/8 unresolved; cap-100pct: 0/8 already guaranteed, 8/8 all-start failing continuation, 0/8 unresolved; near-Nash-anchor-floor: 0/8 already guaranteed, 8/8 all-start failing continuation, 0/8 unresolved.

Nominal/effective classifications agree in 8/8 retained labels. Requested targets and actual relaxed thresholds remain separate. Failure means a permitted continuation below the threshold is available from every initial state; it is not a prediction that all seller behavior fails. “Already guaranteed” means no initializer is needed for that threshold in this comparison model.

## All predeclared mesh diagnostics

Each row uses the same saved endpoints, with a new grid benchmark for best profit and binary64 interpolation. Its own permanent-cap floor is distinct from the fixed old targets. “Cap tail” is the worst top-choice continuation after one actual new-grid cap execution. All values here are numerical diagnostics, not validated real intervals or proof that the largest grid equals the limit.

| Scenario | Grid | Fixed points | Minimum across starts | Maximum across starts | Spread | One-round cap tail | Own cap floor |
|---|---:|---:|---:|---:|---:|---:|---:|
| base-g15-t1 | 11 | 2 | 65.589933 | 70.658311 | 5.068378 | 70.658311 | 70.658311 |
| base-g15-t1 | 15 | 2 | 68.477352 | 72.119040 | 3.641688 | 72.119040 | 72.119040 |
| base-g15-t1 | 31 | 2 | 67.271289 | 68.960917 | 1.689627 | 68.960917 | 72.362996 |
| base-g15-t1 | 61 | 2 | 66.429545 | 67.271289 | 0.841745 | 67.271289 | 71.509771 |
| base-g15-t1 | 121 | 2 | 66.429545 | 66.850155 | 0.420610 | 66.850155 | 71.509771 |
| base-g15-t1 | 241 | 1 | 66.429545 | 66.429545 | 0.000000 | 66.429545 | 71.509771 |
| base-g15-t1 | 481 | 2 | 66.324475 | 66.429545 | 0.105069 | 66.429545 | 71.509771 |
| base-g15-t1 | 961 | 1 | 66.324475 | 66.324475 | 0.000000 | 66.324475 | 71.509771 |
| base-g15-t1 | 1921 | 1 | 66.298213 | 66.298213 | 0.000000 | 66.298213 | 71.509771 |
| scale0.5-g15-t1 | 11 | 1 | 65.137089 | 65.137089 | 0.000000 | 65.137089 | 68.569413 |
| scale0.5-g15-t1 | 15 | 1 | 64.653674 | 64.653674 | 0.000000 | 64.653674 | 69.565316 |
| scale0.5-g15-t1 | 31 | 1 | 64.011862 | 64.011862 | 0.000000 | 64.011862 | 69.731945 |
| scale0.5-g15-t1 | 61 | 1 | 64.011862 | 64.011862 | 0.000000 | 64.011862 | 69.149548 |
| scale0.5-g15-t1 | 121 | 1 | 63.732061 | 63.732061 | 0.000000 | 63.732061 | 69.149548 |
| scale0.5-g15-t1 | 241 | 1 | 63.592387 | 63.592387 | 0.000000 | 63.592387 | 69.149548 |
| scale0.5-g15-t1 | 481 | 1 | 63.522607 | 63.522607 | 0.000000 | 63.522607 | 69.149548 |
| scale0.5-g15-t1 | 961 | 1 | 63.522607 | 63.522607 | 0.000000 | 63.522607 | 69.149548 |
| scale0.5-g15-t1 | 1921 | 2 | 63.505168 | 63.522607 | 0.017439 | 63.522607 | 69.149548 |
| lower-quality-g15-t1 | 11 | 1 | 32.568545 | 32.568545 | 0.000000 | 32.568545 | 34.284707 |
| lower-quality-g15-t1 | 15 | 1 | 32.326837 | 32.326837 | 0.000000 | 32.326837 | 34.782658 |
| lower-quality-g15-t1 | 31 | 1 | 32.005931 | 32.005931 | 0.000000 | 32.005931 | 34.865972 |
| lower-quality-g15-t1 | 61 | 1 | 32.005931 | 32.005931 | 0.000000 | 32.005931 | 34.574774 |
| lower-quality-g15-t1 | 121 | 1 | 31.866030 | 31.866030 | 0.000000 | 31.866030 | 34.574774 |
| lower-quality-g15-t1 | 241 | 1 | 31.796194 | 31.796194 | 0.000000 | 31.796194 | 34.574774 |
| lower-quality-g15-t1 | 481 | 1 | 31.761304 | 31.761304 | 0.000000 | 31.761304 | 34.574774 |
| lower-quality-g15-t1 | 961 | 1 | 31.761304 | 31.761304 | 0.000000 | 31.761304 | 34.574774 |
| lower-quality-g15-t1 | 1921 | 2 | 31.752584 | 31.761304 | 0.008720 | 31.761304 | 34.574774 |
| lowcost-g15-t1 | 11 | 1 | 106.851816 | 106.851816 | 0.000000 | 106.851816 | 106.851816 |
| lowcost-g15-t1 | 15 | 2 | 103.113958 | 109.348194 | 6.234236 | 109.348194 | 109.348194 |
| lowcost-g15-t1 | 31 | 2 | 103.943847 | 106.851816 | 2.907969 | 106.851816 | 109.764575 |
| lowcost-g15-t1 | 61 | 2 | 102.491837 | 103.943847 | 1.452009 | 103.943847 | 108.307631 |
| lowcost-g15-t1 | 121 | 2 | 102.491837 | 103.217670 | 0.725832 | 103.217670 | 108.307631 |
| lowcost-g15-t1 | 241 | 2 | 102.129054 | 102.491837 | 0.362784 | 102.491837 | 108.307631 |
| lowcost-g15-t1 | 481 | 2 | 102.129054 | 102.310434 | 0.181381 | 102.310434 | 108.307631 |
| lowcost-g15-t1 | 961 | 2 | 102.038372 | 102.129054 | 0.090682 | 102.129054 | 108.307631 |
| lowcost-g15-t1 | 1921 | 2 | 101.993033 | 102.038372 | 0.045339 | 102.038372 | 108.307631 |
| base-g11-t1 | 11 | 2 | 65.589933 | 70.658311 | 5.068378 | 70.658311 | 70.658311 |
| base-g11-t1 | 15 | 2 | 68.477352 | 72.119040 | 3.641688 | 72.119040 | 72.119040 |
| base-g11-t1 | 31 | 2 | 67.271289 | 68.960917 | 1.689627 | 68.960917 | 72.362996 |
| base-g11-t1 | 61 | 2 | 66.429545 | 67.271289 | 0.841745 | 67.271289 | 71.509771 |
| base-g11-t1 | 121 | 2 | 66.429545 | 66.850155 | 0.420610 | 66.850155 | 71.509771 |
| base-g11-t1 | 241 | 1 | 66.429545 | 66.429545 | 0.000000 | 66.429545 | 71.509771 |
| base-g11-t1 | 481 | 2 | 66.324475 | 66.429545 | 0.105069 | 66.429545 | 71.509771 |
| base-g11-t1 | 961 | 1 | 66.324475 | 66.324475 | 0.000000 | 66.324475 | 71.509771 |
| base-g11-t1 | 1921 | 1 | 66.298213 | 66.298213 | 0.000000 | 66.298213 | 71.509771 |
| base-g31-t1 | 11 | 2 | 65.589933 | 70.658311 | 5.068378 | 70.658311 | 70.658311 |
| base-g31-t1 | 15 | 2 | 68.477352 | 72.119040 | 3.641688 | 72.119040 | 72.119040 |
| base-g31-t1 | 31 | 2 | 67.271289 | 68.960917 | 1.689627 | 68.960917 | 72.362996 |
| base-g31-t1 | 61 | 2 | 66.429545 | 67.271289 | 0.841745 | 67.271289 | 71.509771 |
| base-g31-t1 | 121 | 2 | 66.429545 | 66.850155 | 0.420610 | 66.850155 | 71.509771 |
| base-g31-t1 | 241 | 1 | 66.429545 | 66.429545 | 0.000000 | 66.429545 | 71.509771 |
| base-g31-t1 | 481 | 2 | 66.324475 | 66.429545 | 0.105069 | 66.429545 | 71.509771 |
| base-g31-t1 | 961 | 1 | 66.324475 | 66.324475 | 0.000000 | 66.324475 | 71.509771 |
| base-g31-t1 | 1921 | 1 | 66.298213 | 66.298213 | 0.000000 | 66.298213 | 71.509771 |
| base-g15-t0.5 | 11 | 1 | 70.658311 | 70.658311 | 0.000000 | 70.658311 | 70.658311 |
| base-g15-t0.5 | 15 | 2 | 68.477352 | 72.119040 | 3.641688 | 72.119040 | 72.119040 |
| base-g15-t0.5 | 31 | 1 | 68.960917 | 68.960917 | 0.000000 | 68.960917 | 72.362996 |
| base-g15-t0.5 | 61 | 2 | 68.115101 | 68.960917 | 0.845815 | 68.960917 | 71.509771 |
| base-g15-t0.5 | 121 | 1 | 68.115101 | 68.115101 | 0.000000 | 68.115101 | 71.509771 |
| base-g15-t0.5 | 241 | 2 | 67.903958 | 68.115101 | 0.211143 | 68.115101 | 71.509771 |
| base-g15-t0.5 | 481 | 2 | 67.798434 | 67.903958 | 0.105524 | 67.903958 | 71.509771 |
| base-g15-t0.5 | 961 | 2 | 67.798434 | 67.851192 | 0.052758 | 67.851192 | 71.509771 |
| base-g15-t0.5 | 1921 | 2 | 67.798434 | 67.824812 | 0.026378 | 67.824812 | 71.509771 |
| base-g15-t2 | 11 | 2 | 65.589933 | 70.658311 | 5.068378 | 70.658311 | 70.658311 |
| base-g15-t2 | 15 | 2 | 64.872014 | 68.477352 | 3.605338 | 68.477352 | 72.119040 |
| base-g15-t2 | 31 | 1 | 65.589933 | 65.589933 | 0.000000 | 65.589933 | 72.362996 |
| base-g15-t2 | 61 | 1 | 64.752521 | 64.752521 | 0.000000 | 64.752521 | 71.509771 |
| base-g15-t2 | 121 | 2 | 64.334662 | 64.752521 | 0.417860 | 64.752521 | 71.509771 |
| base-g15-t2 | 241 | 1 | 64.334662 | 64.334662 | 0.000000 | 64.334662 | 71.509771 |
| base-g15-t2 | 481 | 1 | 64.230286 | 64.230286 | 0.000000 | 64.230286 | 71.509771 |
| base-g15-t2 | 961 | 1 | 64.178112 | 64.178112 | 0.000000 | 64.178112 | 71.509771 |
| base-g15-t2 | 1921 | 2 | 64.152029 | 64.178112 | 0.026084 | 64.178112 | 71.509771 |

All 72 labels, including every coarse-grid fluctuation, remain visible. A sampled downward trend does not establish monotonic mesh convergence. The conditional theorem gives the continuous conclusion; no explicit numerical width/slope constant or mesh error rate is claimed.

## Validation, resources and limits

Continuous records: 16 certified, 0 unresolved; runtime 274.966 seconds; largest after-record RSS sample 28409856 bytes. Mesh records: 72, 0 failures, 0 unresolved; runtime 2.018 seconds; largest observed RSS sample 106373120 bytes. Neither memory figure is a continuously measured peak. No training, model game players, APIs or paid services were used.

The continuous audit uses a separate calculation kernel and rechecks root signs, sufficient conditions, welfare/target enclosures and corruption controls. Both continuous implementations share the standard Decimal backend: independent calculation code does not provide independence from that arithmetic library or a formally verified proof. The mesh audit independently scans all predeclared price-profit pairs and tail data, including inherited graph matches and corruption controls. Exact audit counts, scope and source/result links are retained in the summary and original certificates.

The stationary unilateral deviation gain is a one-period payoff quantity. It does not establish repeated-game incentive compatibility or policy stability. These known symmetric deterministic logit calibrations provide sensitivity checks, with equivalent calibrations and repeated grid labels disclosed; they are not independent real-market replications. Earlier finite certificates and delivery archives are preserved.
