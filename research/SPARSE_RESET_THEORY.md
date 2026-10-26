# Recurring inherited physical cap: conditional tight bounds

Reviewed mathematical statement for the new prospective study; no controller
case calculations are part of this file. Earlier studies remain closed.

Use the normalized exact continuous economy, compact interval I=[ell,H] and
validated nondecreasing rho-contractive upper allowance U:I->I, rho<1, from
CONTINUOUS_REFINEMENT_THEORY.md. Customer surplus C is coordinate-decreasing
and B*mu-Lipschitz in maximum norm. Let q_star be U's unique fixed point and
C_star=C(q_star,q_star). These statements concern all guard-permitted policies,
not an independently learned or incentive-compatible strategy.

Let p_cap be the exact imported ORIGINAL physical competitive-cap price, with
normalized A=(p_cap-c)/mu. Assume ell<=A<q_star, validated with enclosures. This
cap can lie above or below continuous Nash; it is not silently recalibrated.
Contraction implies

  U(A)-A >= (1-rho)*(q_star-A) > 0.

Define a_0=A and a_(j+1)=U(a_j). Monotonicity makes the sequence increasing and
bounded by q_star, hence it converges there. The rewards r_j=C(a_j,a_j) decrease
to C_star. Strict descent initially suffices for strict decrease of the finite
period means even if a later price ceiling is reached in finitely many steps.

## Exact worst policy under a public fixed-period controller

On phase0, REPLACE the profit guard by the full common cap interval[ell,A] for
both actual executed prices, independent of old public prices. On phases1..K-1,
use the unchanged lagged guard; repeat forever. The public phase clock is an
additional controller state. The first execution at activation is phase0 and
earns its actual reward. An old price pair is history, not an extra execution.

Each cap outcome is coordinatewise at most(A,A). Inductively, every later
permitted pair at phasej is at most(a_j,a_j): each quote is at most U(previous
rival), and U is nondecreasing. Since C decreases in either price, every reward
at phasej is at least r_j. Choosing the largest permitted quote in each shop
attains all of these bounds simultaneously, including every real cap round.

Thus the exact worst long-run consumer-surplus average is

  G_K=(1/K)*sum_{j=0}^{K-1} r_j,

from every initial public pair. It is an attained path value, not an assumption
about independent sellers' behavior. A round can have lower surplus than G_K:
the cycle's per-round floor is r_(K-1), a different quantity.

For T=mK+s future executions starting with the immediate cap,0<=s<K, the exact
worst cumulative reward is

  m*sum_{j=0}^{K-1}r_j + sum_{j=0}^{s-1}r_j.

Every initial-prefix mean of the descending reward list is at least G_K.
Consequently EVERY finite activation-average is at least G_K, as is the
long-run average. If observation instead starts at an arbitrary phase, retain
only the long-run claim unless that initial uncontrolled partial cycle and
public state are separately bounded.

## Largest safe period and numerical tail bounds

G_K strictly decreases to C_star. Its K=1 ceiling is C(A,A), not Nash surplus.
For C_star<F<C(A,A), the largest integer K meeting G_K>=F exists. Certifying
G_K.lower>=F and G_(K+1).upper<F establishes maximality only in this family.
Numerical overlap remains unresolved; a predeclared search cap is censoring.
If F>C(A,A), this cap family is insufficient; a stricter or different controller
is not ruled out. If F<=C_star, no recurring cap is required for the long-run
objective. An untouched guard can still have an unfavorable finite prefix.
A single immediate cap followed by no further caps yields r_j>=C_star forever,
so it additionally protects finite activation averages at such a target.

Let D=C(A,A)-C_star and S=B*mu*(q_star-A)/(1-rho). Contraction and Lipschitz
continuity give

  0<=r_j-C_star<=B*mu*rho^j*(q_star-A),
  D/K<=G_K-C_star<=S/K.

After computing the first J terms and a_J, a length L=K-J tail is enclosed by

  L*C_star <= sum_{j=J}^{K-1} r_j
  <= L*C_star+B*mu*(q_star-a_J)*(1-rho^L)/(1-rho).

All positive factors/distances use outward interval bounds. U applied to an
interval is bounded by separately signed scalar endpoint solves, using its
validated monotonicity; parameter uncertainty must not be guessed away.

The activation rate1/K counts applications of the cap RULE, not changed quotes.
Price-span measures and seller profits along the selected worst-CS path are
descriptive, not general autonomy, profit guarantees or economic intervention
cost. No optimum over adaptive/asymmetric/random controller families is shown.

## Separately saved finite numerical game

The same order proof applies to a finite action correspondence with nonempty
sets, a nondecreasing upper map, and a saved reward table coordinate-decreasing
in BOTH prices. The actual finite masks are those computed in declared binary64
arithmetic. Treat the saved binary64 reward values as exact rational weights;
this defines a numerical finite game, not a new certificate for exact logit
transcendentals or exact-rational profit eligibility.

Starting at the included cap quote, follow the scalar upper map to obtain the
K-phase reward list. Without presuming a descending list, the tight infimum of
all finite activation-average rewards is

  H_K=min_{1<=s<=K}(sum_{j=0}^{s-1}r_j)/s.

Every finite horizon is a weighted average of completed-cycle mean G_K and
one initial-prefix mean, so it is at least H_K. Conversely the minimizing
prefix is an actual horizon, and G_K is included at s=K. If U(cap)>=cap, the
scalar orbit is nondecreasing, rewards descend, and H_K=G_K. This condition and
the whole reward-table monotonicity must be independently verified before the
playable game uses the continuous-style prefix statement.
