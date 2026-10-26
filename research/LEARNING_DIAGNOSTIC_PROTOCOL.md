# Separate post-training diagnostics

Prospective,25October2026. Run only after main completion.json exists. Before first numerical evaluation save protocol/script SHA256 and main manifest SHA256 in a separate output manifest. These diagnostics cannot retroactively alter main design or claims. No inference/network/model calls.

Warm competence: all12 primary competitive-pretrained final checkpoints; frozen greedy A against fixed rival continuous Nash (executed grid index nearest Nash),2000rounds. Also test every possible prior state. There are225 completed-price states plus sentinel. For all226 states set A state appropriately, choose its greedy action without learning, and compute one-round profit against fixed nearest-grid Nash. Report action histogram, mean and worst one-step gap versus grid best reply; those unvisited states need not be competent. Set sentinel through reset flag. Main horizon2000checks visited competence separately.

Policy stability: all12 base checkpoints at1M/2M/3M, frozen simultaneous greedy unguarded2000rounds. Detect first repeated joint executed grid index; because policy is deterministic and stationary with no exploration, repeated state implies subsequent periodicity. Report transient/cycle length, mean customer benefit over full evaluation and final200rounds. High prices alone are not labelled collusion. These tests share training seeds and cannot enlarge independent n.

Continuous handling: seeds1001/1002 final base checkpoints, frozen greedy1000rounds, calibrated simultaneous continuous projection tolerance0/.005/.1. Exact last continuous rival quote goes to guard; learner observations use nearest executed grid indices. Save full traces including quantities/prices/profits/customer benefit, original proposals, corrections and Q-update diagnostics. This separates continuous enforcement from discrete training and does not establish generalization for protected adaptive learning.

No zero-initialization or executed-index-credit retraining is performed in this diagnostic. Those remain uncompleted algorithm sensitivities; runtime convenience must not be represented as evidence of equivalence.
