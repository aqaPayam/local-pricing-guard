# Mathematical scope of the strategic audit

This note supplies derivations for review, not unreviewed claims of novelty.
Standard minimum-mean-cycle and potential arguments are established tools.
The economic application and numerical assumptions must be checked separately.

## Finite paths, cycles and long-run objectives

Let G=(V,E) be the finite public-state graph. Edge(u,v) receives reward w(u,v)
from the newly executed pair v. Every feasible infinite path eventually stays
in one strongly connected component: the condensation graph is finite and has
no directed cycle. In that component, finite walks can be decomposed into
cycles and a remainder of at most |V|-1 edges. Since rewards are bounded, the
remainder's contribution to average reward vanishes as horizon tends to infinity.
Consequently the liminf average is at least the smallest reachable cycle mean.
A finite prefix to a minimizing cycle followed by endless repetition attains
that mean. Maxima follow by negating reward. Randomization or extra finite
policy memory cannot improve an unconstrained extremal time-average objective.
For multiple simultaneous reward constraints, however, mixtures of cycles may
matter; optimizing each objective separately does not solve that problem.

## Potential certificate and finite-horizon correction

Suppose a finite potential h and bound L satisfy, for every relevant edge,

    w(u,v) + h(u) - h(v) >= L.

Summing a T-step path from v0 to vT telescopes, giving

    average(w) >= L + (h(vT)-h(v0))/T
               >= L + (min(h)-h(v0))/T.

The cycle mean is at least L because potentials cancel around a cycle. A
feasible witnessed cycle of mean U therefore sandwiches the optimum in [L,U].
The maximum-reward version applies to -w. With residual numerical tolerance r,
replace L by L-r before making an inequality claim. An audit certificate over
only internal SCC edges bounds recurrent averages there; it is not by itself
a finite-horizon certificate covering cross-component prefixes. A worst
long-run mean is not a per-round safety guarantee. Floating-point calculations
with explicit residuals are numerical evidence, not exact real-arithmetic proof.

## Candidate structural result: when cycles cannot worsen the stationary ceiling

Assume a symmetric two-seller finite price grid p0<...<p(n-1). When the previous
rival index is j, the allowed own indices are a nonempty integer interval
S(j)=[L(j),U(j)]. Assume U(j) is nondecreasing. A graph edge from(i,j) to(a,b)
exists exactly when a belongs to S(j) and b belongs to S(i).

Take any recurrent cycle and let M be the largest price index used by either
seller anywhere on it. Some edge produces M against a previous rival index
j<=M. Thus M<=U(j)<=U(M). A cycle state containing M also has a successor;
the other seller's next index k belongs to S(M) and k<=M by definition. Thus
L(M)<=k<=M. Combining inequalities gives L(M)<=M<=U(M), so M belongs to S(M).

There is at least one cycle in a finite graph with nonempty outgoing support,
so the set D={j: j belongs to S(j)} is nonempty under these assumptions. Let
m*=max D. The preceding argument gives M<=m*: every price on every recurrent
cycle is no larger than p(m*). If customer surplus C(p,q) decreases in each
coordinate, each recurrent cycle has average surplus at least C(p(m*),p(m*)).
The self-loop at(m*,m*) is feasible and attains that bound. Therefore the
global, all-initial-state minimum cycle mean equals this stationary value.

For the specified logit demand,

    C(p,q)=B*mu*log(1+exp((v-p-v0)/mu)+exp((v-q-v0)/mu)),
    partial C / partial p = -B*sA < 0,

and analogously for q. The monotonicity requirement is therefore satisfied.
The interval and nondecreasing-U assumptions must still be verified on every
declared finite guard map. This is not yet a theorem that every continuous
logit guard, tolerance, asymmetric economy or arbitrary grid has these properties.

For no control and the existing cap, S(j) is an identical complete rectangle
support independent of j. The same result reduces to the constant largest
allowed pair. For maximum joint profit, monotonicity of customer surplus is
irrelevant: maximize the joint-profit reward over the allowed support for
rectangle controls, and use the graph objective for the lagged guard.

## Interpretation and reachability

The stationary ceiling result concerns the all-state envelope. A minimizing
self-loop may be unreachable from a particular public initial state, so the
reachable graph computation and explicit prefix remain necessary. Allowed
prices may fluctuate transiently above a recurrent ceiling, and finite-horizon
harm can differ from its asymptotic value. A deliberately coordinated feasible
policy is neither evidence of emergence nor a strategic equilibrium. Benefits
to each seller and unilateral incentives require their own analysis.

## Candidate finite-horizon corollary for the stationary-ceiling case

Assume the interval/monotone-upper-map lemma above applies, and set
C*=C(p(m*),p(m*)). Every state on any cycle then has reward at least C*.
Consequently a state v with C(v)<C* lies in an acyclic singleton SCC: any
nontrivial strongly connected component or singleton with a self-loop would
put v on a cycle. Such a below-ceiling-reward state can be visited at most once.

Collapse the graph to its condensation DAG. Give component c the nonnegative
weight d(c)=max(0,C*-C(v)) if it is an acyclic singleton {v}, and zero otherwise.
For each starting component c define the reverse-topological recurrence

    D(c) = max({0} union {d(k)+D(k): edge c->k in the DAG}).

Every possible future path's total positive deficit below C* is bounded by
D(c). The starting state's reward is not counted: state means the previous
executed pair, and payoffs begin at the next destination. Moving within a
cyclic component incurs no positive deficit, and leaving it follows the DAG;
an acyclic starting component can never be revisited. Hence for every horizon
T>=1 and every feasible, potentially coordinated/adaptive path from state s,

    average_T(C) >= C* - D(component(s))/T.

This bound can be combined with the smallest one-period reward reachable from
s. It needs finite-map assumptions and correctly computed SCC/DAG weights;
it is not inferred from an internal-SCC potential alone. D may be conservative
because it ignores above-C* rewards during paths connecting harmful transient
states. The inequality is pathwise in the specified deterministic finite game,
and does not require the sellers to follow any learning rule. Numerical
implementation must report reward/residual tolerances; a floating calculated
number is not an exact symbolic certificate. This corollary is a candidate
supplement, independently review before any implementation or report claim.

Equivalently, h(s)=D(component(s)) is a nonnegative potential over every edge
of the full graph, including transitions between components. On a cross-edge
u->v the recurrence gives h(u)>=max(0,C*-C(v))+h(v), so
C(v)-C*+h(u)-h(v)>=0. On an internal cyclic edge, h is constant and C(v)>=C*.
Directly checking this full-edge inequality independently verifies the finite
horizon correction and distinguishes it from internal-SCC-only certificates.
