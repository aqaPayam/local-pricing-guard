# Bounded numerical boundary extensions

Prospective protocol, 25 October 2026. These are deterministic numerical toy checks, not learned-agent effectiveness evidence. No APIs or model players. Freeze this document and runner source hashes before the first execution. Retain every evaluated case and every selected trajectory. Do not transfer the earlier simultaneous symmetric two-firm theorem.

1. Finite adversarial search: symmetric two-firm true/model cost1 quality2 mu.25, bounded prices[0,3], epsilon .1/1/8, horizon12, beam16. At each step enumerate both firms' lower/midpoint/upper feasible interval prices (nine pairs), retain the16 trajectories with smallest cumulative consumer surplus. Compare greedy upper endpoints at identical initial prices [1.47,1.47], [1.92,1.92], held-out [1.1,2.6], [2.4,1.3]. Report best found, never global optimum; beam pruning can remove future best paths.

2. Demand shock: symmetric two firms, quality2 cost1, true mu .25 initially, .35 from round21. Believed model updates after delay0/10/100 rounds. Both propose3 and execute upper feasible endpoint; eps .1/1/8,120rounds, initial[1.92,1.92]. Settlements use the current true demand. Delay100 remains stale through horizon. No estimated parameter learning is claimed.

3. Timing: symmetric true/model mu.25, two firms, eps0/.1/8,120rounds. Only A updates on odd rounds and B on even rounds; inactive firm retains its prior executed quote. Active guard observes rival quote from completed round max(0,t−lag), lag1/3/10, using archived prices (initial record round0). Proposal3. Report consumer surplus and realized instantaneous regret; no convergence theorem.

4. Structural extensions: three identical firms; two firms with qualities[2,2.2]; two firms with costs[1,1.2]. All other qualities2/costs1, mu.25. Derive each unilateral best response through one-dimensional bisection on own profit derivative, solve Nash by damped simultaneous responses until residual<1e−10 or10000iterations. Report residual and failure explicitly. For eps0/.1/8 run120 simultaneous rounds, all proposals3, initialall1.92, guards use previous complete rival vector and correct firm costs/qualities. Record discrete-time trajectories, not a new proof or general robustness claim.

All numeric runs use pure JavaScript CPU. The file manifest records exact case grids, protocol/source hashes and timestamp before running. No parameter changes after observing results; numerical failures are fatal and remain visible.
