# Finite coordinated-policy methods

This module adds a finite policy-envelope calculation to the unchanged logit economy and controller maps. It does not add learners or infer that a coordinated optimum would be discovered or sustained strategically. The primary matrix is fixed in CYCLE_PROTOCOL.md and the eight existing robustness scenarios.

## Public graph and rewards

Vertex i*n+j records the completed previous execution pair. Its outgoing destinations are a*n+b for every a in S(j), b in S(i), where S is the existing map image. Simultaneous current choices are not observed. A public pre-agreed schedule can choose the indicated allowed quotes; each projection is then a fixed point. Rewards on an edge are the destination outcome, not the source reward. The two objectives are separate: minimum customer-surplus mean and minimum negative joint-profit mean (reported as maximum joint profit).

All finite-grid states are possible initial conditions. Every result includes a feasible finite prefix followed by a repeatable cycle from each state. Near-continuous-Nash, high-high and all32 prior training endpoints per scenario are diagnostic references to this same graph, not additional independent experiments. Only saved executed indices/configuration supply those starts; the coordinated controller replaces the learned policy.

## Strong components and minimum means

Every directed cycle lies inside one strongly connected component. Tarjan decomposition identifies components; a singleton is cyclic only if it has a self-loop. On a cyclic component with m vertices, Karp's dynamic program computes D_k(v), the minimum weight of a length-k walk ending at v, with every vertex initialized D_0(v)=0. This is an implicit zero-cost super-source initialization. The minimum cycle mean is min_v max_(0<=k<m) [D_m(v)-D_k(v)]/(m-k). The code retains the full finite DP table, O(m²) memory and O(m*E_component) work. Reachable cyclic components are propagated through the acyclic condensation graph; an initial state's best reachable component is selected by attained witness mean. Its lower bound is the minimum certified component bound over every reachable cyclic component, including alternatives not selected for the witness.

No-control and cap have a state-independent target support rectangle. From every initial state the controller can reach any supported pair in one step and hold it with a self-loop. Consequently the optimum is the minimum destination weight over that rectangle. Constant zero potential certifies every graph edge, including transient edges from unsupported states. Small-graph tests compare this closed form with the generic SCC solver.

## Explicit witnesses and numerical bounds

Karp's value formula is not used as a substitute for a feasible witness. Chaturvedi and McConnell show a pitfall in Karp's original proposed extraction procedure: [A Note On Finding Minimum Mean Cycle](https://www.cs.colostate.edu/~rmm/minCycleMean.pdf), Information Processing Letters2017, DOI10.1016/j.ipl.2017.06.007. We instead shift every internal edge by KarpMean+delta and use Bellman–Ford predecessor updates to extract a negative cycle. The actual original-weight cycle mean is recomputed, and every cycle edge and prefix is saved for independent checking.

The preset delta is1e-10 times max(1, largest absolute internal edge weight). A second Bellman–Ford relaxation at KarpMean-delta supplies a potential h. The stored lower bound is min(KarpMean-delta, min_edges[w+h(u)-h(v)])-delta. Every internal edge then has checked nonnegative residual w-L+h(u)-h(v). Summing around any cycle cancels h and bounds its mean below by L. The witness gives the upper bound U. Each component must satisfy U-L between0 and1e-6 times the edge-weight scale; otherwise the case fails and is retained as a failure, rather than silently relaxing a tolerance. Report actual residuals, gaps and delta, not only acceptance flags. For maximum joint profit, negate the minimization interval.

These certificates cover internal edges of each cyclic SCC. Asymptotic reachability follows because an infinite walk eventually stays within a terminal visited component of the finite condensation DAG. They do not certify transient cross-component edges or a finite-horizon inequality for arbitrary initial states. A finite prefix has vanishing contribution only in the infinite-time average. Any later finite-horizon result requires its own correctly scoped certificate.

Arithmetic is IEEE754 floating point on already computed payoff weights; no interval enclosure of exponentials or exact real-number theorem is claimed. Both the cycle mean and potential are numeric evidence. Independent replay checks the economic arithmetic, complete feasible-edge coverage, component/reachability structure, cycle/prefix feasibility, individual seller profits, lower inequalities and primal-dual gaps. Neither an extremal customer-harm witness nor a joint-profit optimum establishes individual rationality, mutual gains, unilateral incentive stability, equilibrium or spontaneous collusion.

## Developer verification and limits

Tests cover negative edges, negative means, periodic components without self-loops, unreachable attractive cycles, transient prefixes, ties, fifty small deterministic graphs compared with exhaustive simple-cycle enumeration, complete-support reductions, and lagged-rival graph semantics. Primary cases are not run before independent review and source/input/checkpoint hash freezing. The core target is120seconds and100MB; overrun is recorded without selecting a subset of cases. All24 cases, including uninteresting protective bounds, are retained. No model account, API, external service, purchased compute or new training is used.
