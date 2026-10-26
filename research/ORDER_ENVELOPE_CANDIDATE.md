# Candidate next result: an order envelope for every finite horizon

Provisional mathematical derivation, to receive independent review before any
new numerical study or report claim. It does not modify the frozen cycle study.

## Statement

Consider the same symmetric lagged public-state game on an ordered finite price
grid. Every allowed set S(j) is nonempty. Let U(j)=max S(j), and suppose U is
nondecreasing. Unlike the earlier stationary-ceiling lemma, the sets need not
be intervals. Suppose customer surplus C decreases in each executed price.

From any fixed public starting state z0=(i,j), define the top-choice path

    z[t+1] = (U(z[t].B), U(z[t].A)).

This path is feasible because each maximum belongs to its allowed set. For
every other feasible path x starting at the same public pair, including paths
selected with randomization, complete coordination or arbitrarily long memory,

    x[t].A <= z[t].A and x[t].B <= z[t].B for every t>=0.

Proof is by induction. Equality holds at t=0. If x[t]<=z[t] coordinatewise,
then x[t+1].A<=U(x[t].B)<=U(z[t].B)=z[t+1].A, and symmetrically for B.
Hence C(x[t])>=C(z[t]) at every execution. The top-choice path simultaneously
attains the minimum customer surplus at every individual future time and the
minimum cumulative or average surplus for every finite horizon. The comparison
uses a fixed starting pair and excludes its previous-state reward.

## Long-run behavior on a finite grid

Iteration of a nondecreasing self-map on a finite totally ordered set becomes
stationary: after its first step the sequence is either nondecreasing or
nonincreasing, and it must stop. Let F(j) be the eventual fixed point reached
by iterating U from j. Applying the two-shop recursion twice acts separately
as U composed with U on each coordinate. It eventually alternates between
(F(i),F(j)) and (F(j),F(i)). When the two fixed points coincide it is constant.
For symmetric C the two alternating rewards agree. Therefore a start-specific
infinite-average minimum can also be read from this top-choice path, with no
claim that every start shares the global worst stationary pair.

This explains the possible mixed intermediate welfare region in the earlier
state heatmaps. It is more precise than saying every start-specific optimizer
must be constant: only the 48 global primary witnesses were all stationary.

## Numerical study that could test this consequence

Do not run yet. A separate prospective protocol can reuse all24 audited games,
verify nonempty support/U-monotonicity/surplus monotonicity, and compute every
start's top-choice path and finite-horizon sums at fixed horizons. Crosscheck
long-run means against the existing graph certificates. Compare short-horizon
values to independent full dynamic programming and compare longer-horizon sums
to independent functional-graph prefix/cycle arithmetic. Never call a floating
sum an exact real-arithmetic enclosure without numerical error accounting.

The result is conditional order comparison, not a new graph optimization
algorithm or an incentive-compatible collusion mechanism. The continuous-guard
candidate separately supplies a counterexample to unconditional monotonicity:
the assumption cannot be silently imported to every tolerance or economy.

## Potential implication for grid refinement

For a symmetric starting pair, the top envelope stays on the diagonal. A
refinement study can therefore investigate reachable worst prices using a
one-dimensional U-map rather than enumerating an n-squared-state graph. That
reduction needs the stated monotonicity and a separate reviewed protocol.
Finer-grid or continuous behavior must not be inferred merely from the three
grids in the completed study. The strongest continuous statement currently
being reviewed concerns reachability of a small above-Nash stationary tail,
which is different from reaching an exact global upper-boundary optimum.
