# Prospective coordinated-policy finite-game audit

This extension follows known Q-learning/guard results. It asks a new question:
what repeating outcomes are feasible for jointly coordinated strategic sellers,
including policies not found by the saved learners? It is a local prospective
protocol, not an independent preregistration or a new learning algorithm.

## Frozen cases and economics

Use exactly the eight configurations in robust-results/manifest.json and each
of the existing guard, cap and unrestricted controllers:24 graphs. Preserve
the original prices, economic parameters, tolerance normalization, finite-grid
cap and guard tie rules. Four calibrations represent three dimensionless demand
shapes; retain the affine-equivalent pair as a normalization crosscheck. No new
markets may replace unsuccessful or uninteresting cases after observing results.

## Information and adversary

A state is the previous publicly executed price-index pair (i,j). Both sellers
see it. A transition to(a,b) exists precisely when a is allowed against j and b
is allowed against i under the existing controller. Choosing the allowed price
as one's proposal passes the guard unchanged. A pre-agreed joint policy or
finite public schedule can implement a path without seeing either current
sealed proposal. This grants fully coordinated choices and known economics.
It does not assume or demonstrate spontaneous coordination, private language,
an equilibrium, incentive compatibility or discoverability by a learner.

Rewards belong to the destination executed pair: modeled customer surplus,
shop A profit, shop B profit and their sum. No price-set projection reward or
proposal credit is substituted for the executed economic outcome.

## Two objectives, kept separate

1. Minimum attainable infinite-horizon time-average customer surplus.
2. Maximum attainable infinite-horizon time-average joint seller profit.

Both are extremal feasible-policy bounds. Always show both individual seller
profits alongside either witness and compare with finite-grid Nash and joint
benchmarks. A customer-harming witness may fail to benefit either seller; a
joint-profit maximum may distribute gains unequally. Neither objective alone
establishes mutually beneficial or self-enforcing collusion.

## Reachability and mathematics

Enumerate the finite directed graph, decompose strongly connected components
and solve the relevant cycle-mean objectives in cyclic components. Propagate
reachable optimum values through the condensation graph. Report the all-state
worst envelope and start-specific attainable values separately. Provide a
prefix and repeating cycle from the nearest continuous-Nash grid anchor,
high-high start and every initial grid state (compressed references may share
witnesses). Also map the32 saved training terminal states per scenario to the
same reachable values; these are dependent diagnostic starts, not new seeds.

Use Karp's minimum-mean-cycle dynamic program or a reviewed equivalent for
guard graphs. Complete support-rectangle graphs for no control and cap admit
closed-form state extrema with self-loop witnesses; validate that reduction.
Recover explicit cycles and shortest-path potential certificates at a declared
numerically relaxed bound. For each objective report attained cycle mean,
certified relaxed bound, primal/dual gap, edge-inequality residual and tolerance.
Enumerating all grid edges does not turn floating arithmetic into a formal
real-arithmetic proof. Finite prefixes affect transient outcomes but not the
infinite-horizon average. Do not equate average guarantees with per-round safety.

## Verification, freeze and output

Before substantive cases, review algorithms and test synthetic graphs with
negative weights, multiple components, unreachable superior cycles, periodic
components and ties. Compare small graphs against exhaustive simple cycles.
Freeze protocol, engine, runner and relevant tests with hashes/timestamp after
independent design review. Existing saved economics/results remain unchanged.
Record runtime, work counts, run failures and source hashes. Resource target:
under100MB working memory for core graphs and120 seconds of core computation;
record any overrun and retain evidence rather than silently reducing cases.

Independent audit reconstructs prices, edges, economic arithmetic, reachability,
cycle/prefix feasibility, stated means and every certificate inequality without
trusting the search routine. Corrupt a witness action, reward, bound and prefix
to demonstrate rejection. Report numerical tolerances and the exact scope.

Deliver all24 cases, machine-readable witnesses/certificates, benchmarks,
comparisons with existing learners, primary-source attribution and limitations.
Build a separate graphical replay labeled deliberately optimized worst-case
policy. Preserve the continuous human game and distinguish it from this finite
grid. Only conclude exploitation if verified evidence supports that wording;
a tight protective bound is a valid result. No API calls or new LLM players.

## Prospective structural diagnostic

Before substantive runs, a candidate lemma was identified: if allowed sets are
integer intervals and their upper endpoint is nondecreasing in the previous
rival price, the global minimum customer-surplus cycle mean is attained by the
largest symmetric self-feasible price pair. CYCLE_THEORY.md gives a proof for
independent review. Verify those finite-map assumptions and compare this
predicted stationary value to the graph result in every declared case. If an
assumption fails, retain the case and rely on the general graph audit. Do not
infer that all worst-case behavior requires a nontrivial cycle, or claim a new
graph algorithm when an existing optimization or this simpler argument suffices.

The independent referee also accepted a finite-horizon corollary before the
freeze: when the structural assumptions hold, every state below the stationary
customer-surplus floor is an acyclic singleton and can be visited only once.
A longest-deficit path on the condensation DAG bounds total positive future
deficit D(start), excluding the previous starting state's reward. Report
floor-D(start)/T at T=1,10,100,20000, using an explicit numerical slack. This is
a separate structural certificate, not an inference from internal-SCC potentials.
Store all starts, deficit weights, DAG edges and recurrence results for audit.
