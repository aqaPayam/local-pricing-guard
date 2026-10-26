# Draft theory: mixed gaps between identical physical caps

Status: prospective, independently reviewable next-goal draft. Not an accepted
V9 result, numerical execution permission or source freeze. No inherited-market
case was evaluated to write this document. Earlier evidence remains immutable.
The matching protocol is `MIXED_TIMING_PROTOCOL.md`.

This is an application-level refinement, not a new adjacent-mixture algorithm.
[Sun and Cyr (2019), Theorem4](https://arxiv.org/html/1812.07241) already gives
two-threshold randomized discrete sampling policies for rate-constrained
monotone age costs. Renewal scheduling, sample-path constraints and funded
every-time cumulative budgets also have established literature, summarized in
`MIXED_TIMING_NOVELTY.md`, including conservative bandit work. Neither the
mixture nor generic pathwise-credit protection is claimed as an invention.
No general first-priority claim follows from this pricing application.

## Restricted model and quantifiers

The public controller chooses between exactly two existing modes before the
current prices are chosen: the same full physical cap for both shops, or the
same full lagged profit guard. A cap replaces the guard on that execution. It
does not intersect the rules, change the cap strength or inspect a hidden
current proposal before choosing a mode. Both shops may use any causal policy
allowed by the announced mode; cooperation or independent learning is not
assumed. Prices, eligibility and rewards retain their closed-model meanings.

Let A be the existing physical cap expressed in the model's price coordinate.
Prices lie in a bounded interval I (or its saved finite quote subset), and C
is finite on I squared. Upper-map iterates remain in that domain.
Assume every cap outcome is at most (A,A), and that this pair is feasible.
Let U(r) be the largest guard-permitted own price against previous rival price
r. Require nonempty supports, attainment of U, and a nondecreasing U over the
relevant invariant domain. Require customer benefit C(p,q) to be nonincreasing
in either price. For continuous cases these are the separately reviewed
known-model assumptions; they are not universal facts about arbitrary logit
guards. For finite cases they are checked on the saved numerical game.

Suppose U(A)>=A. Define a_0=A, a_(j+1)=U(a_j), r_j=C(a_j,a_j), and assume the
nondecreasing orbit is bounded. Write C_* for lim r_j. In a finite game this
is the cap-start upper orbit's eventual fixed-point reward, not a global floor
of arbitrary old guard histories or a minimum over all old guard cycles.
In continuous models its identification with C(q_star,q_star) also uses the
accepted contraction/continuity premises; monotonicity alone is not a general
continuous fixed-point theorem.

Time starts with one actual cap execution. Its reward is r_0 on the upper path;
the old memory pair earns nothing. A qualifying controller must guarantee

    sum_(t=1)^T C(p_t,q_t) >= F*T

for every integer T>=1, every allowed seller policy/history and every realized
controller-randomization path. This is a prefix guarantee from the first cap,
not a sliding-window guarantee and not an expectation-only or almost-sure
statement. In particular, a later individual block may have average below F.

Let m_pi(T) count applications of the CAP RULE through T, including the first
cap whether or not it changes a quote. The restricted objective is

    inf_(qualifying causal pi)
      sup_(allowed seller histories, controller realizations)
        limsup_(T->infinity) m_pi(T)/T.

It measures worst-path rule frequency. It does not measure realized price
changes, intervention cost, seller autonomy, equilibrium or learned behavior.

## Attained envelope after every cap

If j guard executions have followed the last cap, every permitted pair is at
most (a_j,a_j). Induction uses cap outcomes <=(A,A) and monotonicity of U.
Thus its reward is at least r_j. The causal policy that always takes the largest
currently permitted quote in each shop attains every bound simultaneously:
both quote A at a cap, then both follow the scalar U orbit. This response only
needs the announced current mode and prior prices; it is not clairvoyant.

Consequently r_j is nonincreasing. Set S_0=0 and
S_l=sum_(j=0)^(l-1) r_j for integer l>=1. Its linear interpolation S on real
nonnegative lengths is concave. Since S_l/l tends to C_*, if

    C_* < F <= r_0,

there is a finite largest integer K with S_K-KF>=0. Define

    a = S_K-KF >=0,
    b = S_(K+1)-(K+1)F <0,
    p = a/(a-b),              0<=p<1,
    L_* = K+p.

The set {L>=0 : S(L)-FL>=0} is [0,L_*]. When F<r_0 its positive terminal
crossing is unique. When F=r_0 an initial zero plateau is possible; use the
largest nonnegative crossing, not a false uniqueness claim.

## Necessary frequency against any qualifying causal controller

Fix the feasible upper-price response and any realized controller choices.
At horizon T, there are m>=1 executed caps. The m-1 completed inter-cap gaps
and the current last partial gap have positive integer lengths l_1,...,l_m
summing to T. The current cap belongs to the beginning of its gap. Adjacent
caps give a gap of length one. Its cumulative reward is exactly
sum_i S_(l_i); no reward is assigned to a future cap or the old memory pair.

Protection of this response, followed by Jensen's inequality, implies

    F*T <= sum_i S_(l_i) <= m*S(T/m).

Therefore T/m<=L_* and m/T>=1/L_* at every finite horizon on that response.
In particular its liminf frequency, hence its limsup frequency, is at least
1/L_*. Taking the supremum over allowed histories and realized randomizations
cannot decrease this lower bound. This does not require the same minimum
frequency on cooperative paths with larger actual rewards.

The argument covers history-dependent and randomized controllers under the
stated pathwise guarantee. It does not establish this bound for expectation-only
welfare promises, current-proposal-dependent retrospective caps, different cap
strengths or additional actuators.

## Sufficient calendar and exact all-prefix protection

Use a virtual worst-case credit B, initially zero, at each block boundary:

    if B >= -b: choose length K+1 and update B <- B+b at its end;
    otherwise:  choose length K   and update B <- B+a at its end.

Each block executes one actual cap, then its length minus one guard executions.
The decision is made before the block's first prices execute. The virtual
credit depends on the certified worst-case amounts, not on seller cooperation.
When a=0, choose K forever. For a>0, induction gives 0<=B<a-b: a long block
leaves 0<=B<a; a short block leaves 0<=B<a-b. Equality B=-b chooses the long
block and is safe, including its last prefix.

For a block of length l, let E_j=S_j-jF for j=0,...,l. Its successive increments
r_j-F are nonincreasing, so this discrete prefix sequence is concave. Hence
E_j>=min(0,E_l). A short block has E_l=a>=0. A long block has E_l=b<0 and is
chosen only with B>=-b. Thus B+E_j>=0 inside every block. Actual cumulative
excess since the first cap is at least the virtual worst-path excess. Every
activation prefix is therefore protected, even though a long block by itself
has negative excess. Do not reset its debt or erase previously earned credit.

After N completed blocks with N_L long blocks,

    B_N=(N-N_L)*a + N_L*b = N*a-N_L*(a-b).

Bounded B_N implies N_L/N -> p. Completed length is N*K+N_L, so frequency
tends to 1/(K+p). A partial final block has bounded length <=K+1 and cannot
alter that limit. No ergodic or irrational-rotation assumption is needed.
Here p is the fraction of BLOCKS that are long; their fraction of execution
time is p*(K+1)/(K+p). The cost is 1/(mean gap length), not mean(1/gap length),
and welfare is total reward divided by total executions, not an unweighted
average of per-gap means.
The calendar ignores actual seller rewards when choosing its gap lengths, so
its frequency is the same on every seller path. It attains the necessary bound
and hence is minimax optimal in exactly the restricted two-mode family.

The fixed-period comparator is 1/K. Its absolute reduction is
p/[K*(K+p)] and relative reduction is p/(K+p). These are activation-frequency
reductions, not monetary savings. If a=0, both reductions are exactly zero.
Because p<1, relative reduction is less than1/(K+1); large K cannot yield a
large relative benefit just from rounding to adjacent integers. This is
asymptotic rate optimality, not a smallest-cap-count claim at each finite T.

For rational credits multiplied by a common denominator, the boundary update
is the exact integer rotation B <- (B+a) mod H, H=a-b. When a>0 its repeat
period is H/gcd(a,H). This can be enormous, so an implementation must not
enumerate the repeat period to establish safety or limiting frequency.

## Validated continuous amounts and conservative implementation

Suppose directed enclosures certify a in [aL,aU], b in [bL,bU], with
aL>=0 and bU<0. The signs certify the same adjacent safe/next-failing frontier.
The mixing function has derivatives

    dp/da = -b/(a-b)^2 >0,
    dp/db =  a/(a-b)^2 >=0.

Thus the true optimum lies in

    [ 1/(K+p(aU,bU)), 1/(K+p(aL,bL)) ].

Interpret finite decimal interval endpoints as exact rationals and evaluate
both displayed formula endpoints by exact rational arithmetic. Outward decimal
renderings are a separate representation of those rational endpoints, not
equalities to the unknown exact-real optimum. Running the calendar with credits
aL and bL protects all actual prefixes: actual block
endpoints are no worse than these lower bounds, and the actual prefix sequence
is concave. Its limiting rate is exactly the rational 1/(K+p(aL,bL)) for these
chosen rational credits. This equals the EXACT rational upper-bound endpoint,
and is enclosed by its outward decimal rendering. It need not equal the
rounded upper decimal string. It is a
constructive guaranteed rate, not a proof of exact optimality for the underlying
continuous economy when the interval has nonzero width. A lower credit aL=0
can yield a fixed-K calendar even when the true a is positive.

Do not accumulate an indefinitely repeated calendar's credit using an
uncontrolled floating-point approximation. Exact rational credit avoids drift.
Independence of root/sign validation, interval-library assumptions and decimal
rounding must be disclosed separately from this symbolic theorem.

## Boundaries and limits of the result

If F<=C_*, one immediate cap followed by the original guard protects every
activation prefix and has zero asymptotic cap frequency. Its startup count is
one, not zero intervention. An untouched guard from arbitrary old prices does
not automatically inherit this finite-prefix statement.

If F>r_0, the required first cap on the feasible upper response already fails
at T=1. The defined cap-first two-mode family is infeasible, without ruling out
a stronger or different intervention.

If F=r_0>C_* and the initial reward plateau has finite length h, every upper
reward is <=F. Any gap longer than h contains an unfunded below-F reward;
there is no earlier positive surplus to fund it. The optimal rate is 1/h,
also obtained by K=h,a=0 above. A globally constant reward list has
F=r_0=C_* and falls in the zero-rate case. K=1 is valid; mixed gaps are then
one or two executions. A purported next-failure with b=0 is not a next failure.

If U(A)=A the upper reward list is constant. If U(A)<A, the descending-envelope
assumption used here is not established and this theorem is not applied.
Interval overlap is not equality. A search ceiling is censoring, not an exact
optimum or evidence that no recurring cap is needed. A finite preview cannot
establish the limiting rate or all-prefix theorem, and may show no long gap
despite a positive asymptotic mixing fraction.

These are conditional welfare/control statements, not incentive compatibility,
behavioral adaptation, collusion detection, a novel Jensen method or a claim
of first priority. They do not justify replaying frozen phase-Q learners under
an incompatible mixed-gap state representation.
