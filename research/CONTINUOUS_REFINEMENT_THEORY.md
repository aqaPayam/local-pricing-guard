# Conditional continuous contraction and finite-grid refinement

Status: independently derived and reviewed next-goal theory, 26 October 2026.
No new numerical scenarios, grids, root evaluations, API players or experiments
were run for this note. The earlier continuous and order-envelope candidate
documents are preserved. This note is outside the frozen Goal 1/2 certificates.
It establishes conditional mathematical statements, not a claim of originality.

## 1. Exact model, normalization and assumptions

Use two symmetric sellers with buyer mass B>0, demand scale mu>0, cost c, value v
and outside value v0. Normalize prices x=(p-c)/mu and previous rival prices y in
the same compact interval I=[ell,H], ell<H. Put

    k = exp((c-v+v0)/mu) > 0,
    lambda(y) = k + exp(-y),
    f(x,y) = x / [1 + lambda(y) exp(x)],
    C(x,y) = B mu log[1 + (exp(-x)+exp(-y))/k].

Profit is B mu f. Let t=epsilon/(B mu)>0 be the exact normalized tolerance. The
continuous guard allows x iff f(x,y)>=M(y)-t, where M(y)=max_{z in I} f(z,y).
Both allowed prices execute simultaneously against the *previous* public pair.

Assume throughout the continuous contraction theorem:

1. The unrestricted unique best response
   b(y)=1+w(y), w(y)=W_0(1/[e lambda(y)]), lies strictly inside I for every y in I.
   Thus M(y)=w(y); no constrained-boundary formula is silently substituted.
2. 0<t<m, where m=min_{y in I} w(y)>0.
3. The raw upper root u_t(y)>b(y) of f(u_t(y),y)=w(y)-t is nondecreasing in y.
   A sufficient explicit condition is

       0<t<min{m^2/[2(1+m)], m^3(1+m)/2}.

   The derivative proof below verifies this sufficient condition. It is not
   necessary, and upper-map monotonicity is false in general at larger tolerance.

Define the bounded upper allowed price U_t(y)=min{H,u_t(y)}. It belongs to the
continuous allowed set, and is greater than ell because b(y) is interior.
The exact guard sets are intervals by unimodality, but the order comparison
below itself only requires their nonempty maximum and its monotonicity.

All statements use exact model functions. Ordinary floating evaluations, a
sampled derivative check, or a finite collection of grid checks do not validate
these assumptions over an entire continuous interval.

## 2. Upper-root derivative and contraction

For a=w-t>0 and u=u_t(y), the upper-root profit derivative is

    f_x(u,y) = a(1+a-u)/u < 0.

View the upper root as u(w,t), using lambda=exp(-1-w)/w. At fixed t,

    u_w = [1-a(1-a/u)(1+1/w)] / f_x(u,y).

The numerator minus f_x is exactly

    (t/w)(1-a/u) > 0.

Because f_x<0, **u_w<1**. This does not by itself give a positive lower bound:
u_w can be negative, as the preserved counterexample demonstrates.

For completeness, positivity under assumption 3's sufficient condition follows
from the exact sign test. Set z=u-a-1>0 and d=w^2-t(1+w). Differentiation gives

    sign u_y = sign(d z-t).

The upper-root identity is

    z-log(1+z) = t-log(1-t/w) >= t(1+1/w).

Since z-log(1+z)<=z^2/2, z>=sqrt[2t(1+1/w)]. The first sufficient bound gives
d>w^2/2; the second gives sqrt[2t(1+1/w)]>2t/w^2. Therefore z>t/d and u_y>0.
The same conclusion holds if monotonicity is established by another rigorous
argument rather than this conservative bound.

Best-response sensitivity satisfies

    w_y = [w/(1+w)] exp(-y)/[k+exp(-y)] > 0.

Let w_bar=W_0(1/[e k]) and rho=w_bar/(1+w_bar)<1. Then w_y<=rho throughout I.
Combining 0<=u_w<1 with w_y<=rho gives 0<=u_y<=rho. Ceiling clipping preserves
nondecreasing rho-Lipschitz behavior. Thus U_t:I->I is a contraction.

The response b=1+w is also a contraction on I and has a unique fixed point N,
the interior normalized continuous symmetric Nash price. The upper allowance at
N is strictly above N because t>0 and H>N. Iterating U_t from N is increasing;
its unique fixed point q_star therefore satisfies q_star>N. No global
profit-maximality or repeated-game incentive compatibility follows.

## 3. Order envelope and the all-start continuous welfare floor

For initial public pair s_0 in I^2 define the feasible top-choice trajectory

    z_0=s_0,
    z_{j+1}=(U_t(z_j.B), U_t(z_j.A)).

For any other feasible trajectory x with x_0=s_0, induction gives x_j<=z_j
coordinatewise. Indeed x_{j+1}.A<=U_t(x_j.B)<=U_t(z_j.B), and likewise for B.
The result is pathwise, including coordinated, randomized and history-dependent
policies. Since C decreases in each coordinate, C(x_j)>=C(z_j) at every j.
Initial historical reward is excluded: future executions have indices j>=1.

The top-choice pair map is rho-contractive in the maximum norm, with fixed point
(q_star,q_star). Hence z_j converges there from every initial pair. Set

    C_star=C(q_star,q_star).

For every feasible path, liminf_{T->infinity} T^-1 sum_{j=1}^T C(x_j)>=C_star.
The top-choice path attains a convergent average equal to C_star. Therefore the
minimum long-run consumer surplus is C_star from **every** initial state. The
liminf formulation remains meaningful when a general policy's average fails to
converge. This is an all-policy capacity result, not independent learner behavior.

A convenient quantitative fact for refinement is that C is L_C-Lipschitz in the
maximum norm with L_C=B mu: the sum of absolute coordinate derivatives is
B mu (exp(-x)+exp(-y))/(k+exp(-x)+exp(-y))<B mu.

## 4. Exact grid-maximum error and a uniform upper-map sandwich

Take a uniform grid G_n={ell,ell+Delta,...,H}, including both endpoints, with
Delta=(H-ell)/(n-1). For rival grid price y let

    M_n(y)=max_{x in G_n} f(x,y),
    S_n(y)={x in G_n: f(x,y)>=M_n(y)-t},
    U_n(y)=max S_n(y).

This is the discretization in which the best-response benchmark is also computed
on the grid. Comparing it to a continuously benchmarked guard without accounting
for M-M_n would give a different game.

Write sigma=1/[1+lambda(y) exp(x)]. Then

    f_xx = sigma(1-sigma)[-2+x(1-2 sigma)],
    |f_xx|<=A:=1/2+max{|ell|,|H|}/4 on I^2.

The nearest grid point is within Delta/2 of the interior maximizer b(y).
Taylor's theorem, with f_x(b(y),y)=0, therefore gives

    0<=M(y)-M_n(y)<=d_n:=A Delta^2/8.

For the following sandwich assume additionally:

4. t+d_n<m, so raw upper roots exist throughout the expanded tolerance interval.
5. The clipped continuous allowed interval at tolerance t has width at least
   Delta for every y in I. This prevents rounding down from U_t past its lower
   allowed endpoint.
6. A uniform root-slope bound is available:

       -f_x(u_s(y),y)>=kappa>0
       for every y in I and s in [t,t+d_n].

   Here u_s is the *raw* upper root, even if above H. A proof or validated
   numerical bound for kappa is required before quoting a numerical error rate.
   Clipping does not invalidate a bound proved on the raw roots.

Since grid benchmarking lowers the best-profit target, a grid point allowed by
the continuous t-guard is also allowed by S_n. Rounding U_t downward to the grid
loses at most Delta and stays allowed by assumption 5. Conversely every S_n
point is allowed by the continuous guard at tolerance t+[M-M_n]<=t+d_n. Thus

    U_t(y)-Delta <= U_n(y) <= U_{t+d_n}(y), for every grid y.

Implicit differentiation in tolerance gives partial_s u_s=-1/f_x<=1/kappa=:K.
Therefore U_{t+d_n}-U_t<=K d_n. In particular

    |U_n(y)-U_t(y)|<=e_n:=Delta+K d_n.

The slightly tighter max{Delta,K d_n} is also valid; the displayed sum is a
convenient conservative bound. Monotonicity of expanded-tolerance U_s in *rival
price* is unnecessary for this sandwich: inclusion as tolerance increases is
enough. No assumption of monotonicity of the discrete U_n has been made.

For a refinement sequence, the extra conditions hold eventually if fixed t>0,
the original strict interior/positive-threshold assumptions hold, and one fixes
some d_0>0 with t+d_0<m. Compactness gives a positive minimum continuous allowed
width and a positive raw upper-root slope over I x [t,t+d_0]. Choose grids fine
enough that Delta is below that width and d_n<=d_0. This is an existence argument;
an explicit mesh threshold still requires quantitative width/slope bounds.

## 5. Grid trajectories: arbitrary policies require a one-sided argument

Let R_n=e_n/(1-rho). The discrete top-choice pair map is feasible whether or not
U_n is monotone. If v_j is its trajectory, set
D_j=||v_j-(q_star,q_star)||_infinity. Uniform map approximation gives

    D_{j+1}<=rho D_j+e_n,
    D_j<=rho^j D_0+e_n(1-rho^j)/(1-rho),
    limsup D_j<=R_n.

This does **not** mean arbitrary permitted policies contract in absolute distance:
sellers can deliberately choose lower prices. For a general feasible path x_j
instead define the positive excess

    E_j=max{0,x_j.A-q_star,x_j.B-q_star}.

Monotonicity and contraction of the *continuous* U_t imply
U_t(r)-q_star<=rho max{0,r-q_star}. Since each permitted grid action is at most
U_n(r)<=U_t(r)+e_n, we have E_{j+1}<=rho E_j+e_n and limsup E_j<=R_n.
Consequently any policy's long-run consumer surplus is at least C_star-L_C R_n.
The feasible top-choice path has long-run surplus at most C_star+L_C R_n; it is
eventually periodic because its state space is finite. Thus for every grid start
s, defining W_n(s) as the infimum of liminf average surplus over feasible paths,

    C_star-L_C R_n <= W_n(s) <= C_star+L_C R_n.

The enclosure is uniform across starting states. In particular, differences
between start-specific worst welfare values are at most 2 L_C R_n and vanish as
Delta->0 under the uniform assumptions. Neither unique basins nor a unique
discrete fixed point is asserted for any finite n. Other permitted, lower-price
policies can still have substantially higher welfare. Only with separately
verified discrete U_n monotonicity is the discrete top-choice path guaranteed
to be *exactly* worst at every finite time by the order-envelope induction.

## 6. Consequences for a finite initializer and nearest-grid cap targets

A finite initializer eventually hands back to the original guard in some public
state. If a target threshold F_n-delta_n obeys

    C_star+L_C R_n < F_n-delta_n,

the top-choice continuation supplies a below-threshold tail from every state.
No such initializer can guarantee that threshold uniformly against permitted
continuations. This is an adversarial guarantee statement, not a prediction that
every actual seller chooses the tail. If C_star-L_C R_n>=F_n-delta_n, the unchanged
guard already guarantees the target from every state; no initialization repair
is needed. Intermediate cases remain unresolved by this enclosure.

For a permanent common-prefix cap whose ceiling is the grid point nearest N,
let F_n=C(N_n,N_n). Because C is decreasing and all prefix pairs are permitted,
this is its exact model floor, and |N_n-N|<=Delta/2 gives

    |F_n-C(N,N)|<=L_C Delta/2.

For the 100% cap-reference target a sufficient initializer-impossibility condition
is therefore

    C(N,N)-C_star > L_C R_n + L_C Delta/2 + delta_n.

The continuous gap is positive because q_star>N. It need not exceed a fixed
numerical relaxation merely by being positive. With delta_n=1e-8 max(1,F_n),
eventual failure of the relaxed 100% target follows only if the continuous gap
exceeds its limiting relaxation, or a direct validated inequality above is
proved. Percent-of-cap targets require their own scaled benchmark comparison.

The exact mathematical grid guard here has no floating comparison allowance.
If an implementation permits an extra payoff allowance (such as 1e-12 in the
existing finite engine), its normalized amount must be included as added
tolerance in the sandwich/error accounting. Floating root estimates likewise
need validated enclosures before being used as certificates. This note alone
does not numerically evaluate or invalidate any frozen finite-grid guarantee.

More explicitly, with an extra normalized allowance tau_n>=0, the upper sandwich
becomes U_{t+d_n+tau_n}; relative to the nominal t-map one may use
e_n=Delta+K(d_n+tau_n), provided all expanded-domain assumptions hold. A fixed
nonzero tau does not disappear merely by refining the grid. For exact convergence
to the nominal t-map require tau_n->0; alternatively define the comparison
continuous guard itself at tolerance t+tau and establish its contraction
assumptions. The same distinction applies to any other fixed numerical slack.

## 7. Scope and next evidence gate

The result is conditional on a known symmetric deterministic logit economy,
common compact price interval, positive tolerance, interior best responses and
rigorously established continuous upper-map monotonicity. It does not prove
incentive stability, spontaneous discovery, real-market harm or a new general
optimization method. The preserved counterexample shows why monotonicity cannot
be generalized to arbitrary tolerance/economies.

A separate prospective numerical protocol should freeze scenarios, mesh sizes,
validated width/slope/root methods, comparison targets and numerical error rules
before evaluation. It should retain failed assumptions and inconclusive target
comparisons. The earlier 24-case and 40-label evidence remains independently
valid in its stated finite model while the refinement question is investigated.
