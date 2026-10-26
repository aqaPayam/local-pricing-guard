# Independent conceptual review: mixed cap timing

Status: conditional theoretical acceptance for a future prospective protocol.
This is not a new experiment, source freeze, achieved market result or change
to the accepted Goal7/V9 evidence. I read the candidate de novo and used only
clearly artificial rational reward sequences for the calculations below. No
new inherited-market controller or parameter was evaluated.

Reviewed candidate SHA256:
`2649a26afbc15d67a774d48056267b231c73b65a2bd249101d5622164dbb183c`.

## Verdict and contribution

The candidate's core argument is sound under its stated strong assumptions.
Jensen's inequality supplies a lower bound against every causal two-mode
controller, including controllers depending on public history or randomization.
A deterministic funded calendar of adjacent gap lengths attains it while
protecting every prefix from the actual activation cap. This is stronger than
optimality over fixed integer periods. It does not require selfish sellers to
choose the adverse path, because the promise is explicitly for every permitted
policy.

The remaining work is precise boundary handling and a verified numerical
implementation, not discovery of a general scheduling algorithm. Concavity,
renewal reward and credit arguments are established. The meaningful incremental
question is whether the old integer-period restriction causes a measurable
enforcement-frequency penalty in this same known-model benchmark. A small or
zero saving is a legitimate outcome. Nothing here establishes a new collusion
mechanism, optimal regulation with arbitrary actuators, useful seller autonomy
or the behavior of the previously trained learners under a new clock.

## Required model and quantifier assumptions

1. Both firms face the same externally enforced mode: full cap or unchanged
   guard. The controller cannot introduce a third mode, alter cap strength,
   constrain just one firm, or inspect the hidden current choices before
   selecting the mode. Announce each mode before current prices are selected.
2. The physical cap A is itself an attainable legal quote, not only an upper
   bound above the available quote set. Each nonempty guard set attains its
   maximum U(q). The feasible policy choosing both current maxima is causal.
3. The upper map is nondecreasing, and a real cap yields both prices at most A.
   Its iterates from A give a nondecreasing upper-price orbit with a
   nonincreasing, bounded reward sequence r_j converging to C_star. The
   accepted continuous contraction or a verified finite monotone orbit can
   justify these premises; monotonicity alone should not be advertised as a
   general continuity or fixed-point theorem.
4. Customer benefit is coordinate-decreasing. Induction therefore bounds
   every allowed path's age-j reward below by r_j, while the maximum-price
   path attains exactly r_j. This requires an age-independent known model;
   changing economics or a changed guard requires new premise checks.
5. Start at execution 1 with an actual cap and zero virtual credit. Count its
   earned reward, never an old observed price pair. Require cumulative benefit
   at least F*T for every integer T>=1 and every permitted seller history and
   realized controller random path. The cost is the worst-path limsup of
   executed cap-rule applications divided by executions.

Expectation-only promises or expected intervention cost are different problems.
If randomization is admitted, say explicitly whether the promise is pathwise
or almost sure and whether cost uses a supremum or essential supremum. The
candidate's stronger pathwise/supremum convention is unambiguous and sufficient.
No independence assumption about the controller's random stream is needed for
the stated pathwise proof.

## Necessity: why adaptation and a partial final gap do not evade the bound

Fix any admissible controller and follow the feasible policy that takes both
maxima after each announced mode. At horizon T, let m>=1 be the number of caps
actually executed. Partition the executions into the completed cap-to-next-cap
gaps and the last, possibly incomplete, gap. Each of these m lengths is a
positive integer; each includes its own real cap reward r_0; their sum is T.
An announced but unexecuted next cap is not counted.

Writing S_l=sum_{j=0}^{l-1} r_j, the actual adverse-path reward is exactly
sum_i S_(l_i). This remains true when the controller chooses later modes from
the observed path. Protection and concavity of the linear interpolation give

    F*T <= sum_i S_(l_i) <= m*S_interp(T/m).

For C_star<F<r_0, D(L)=S_interp(L)-F*L starts positive at L=1 and eventually
becomes negative because S_l/l tends to C_star. Its slopes r_j-F are
nonincreasing. The positive crossing is consequently unique. If K is the
largest safe integer and a=D(K)>=0, b=D(K+1)<0, then

    H=a-b>0,  p=a/H in [0,1),  L_star=K+p.

Here H also equals F-r_K. The proportion p refers to blocks of length K+1,
not their share of execution time; the latter is p*(K+1)/(K+p).

Hence T/m<=L_star at every horizon on this one feasible adverse history, so
liminf m/T>=1/L_star there. Its limsup is also at least that value; therefore
the supremum of limsups over histories is at least that value. This establishes
the minimax lower bound. It does not impose that density on a cooperative path
that earns more benefit, or claim the adverse policy is profit-optimal.

This step is valid as written in the candidate. Treating only completed gaps
and dropping the current partial gap would be an invalid shortcut.

## Sufficiency: exact credit, prefixes and limiting frequency

At each block boundary use virtual credit B with B_0=0. Choose K+1 if B>=-b;
otherwise choose K. Add b or a after executing that full block. Inductively,
0<=B<H: a short block ends below -b+a=H, and a long block ends at or above
zero and below H+b=a. When a=0, always use K.

For a chosen block length l, the prefix excess

    D_u=S_u-F*u,  0<=u<=l

is concave in integer u. Thus D_u>=min(0,D_l). A short block has D_l=a>=0.
A long block is started only after funding its entire debt -b. The prior
worst-path accumulated excess is at least B; therefore even a prefix ending
inside a long gap remains nonnegative. Every other permitted price path earns
at least these age-dependent rewards under the same calendar. This proves all
activation-prefix averages, not merely block-end or asymptotic averages.

After N completed blocks,

    B_N=N*a-N_long*(a-b).

Bounded B_N gives N_long/N -> p. Average block length tends to K+p and cap
frequency tends to 1/(K+p). Since every block has length at most K+1, the
unfinished last block changes only a bounded remainder; the same frequency
limit holds at arbitrary execution horizons. The deterministic calendar has
this limit on every seller history. It matches the minimax lower bound.
This is asymptotic rate optimality under finite-prefix protection, not a claim
of the smallest possible cap count at every individual finite horizon.

For rational a,b, use exact integers after multiplying by a common denominator.
The credit map is a rotation B <- (B+a) mod H, with repeat period
H/gcd(a,H) in those integer units when a>0. Its period may be enormous even
though the stored credit is bounded. Do not enumerate the full calendar cycle
to prove frequency or safety. Exact BigInt/Fraction comparisons are essential;
rounding a near-threshold credit upward can incorrectly authorize debt.

## What protection does not transfer

Every prefix measured from activation is different from every sliding window.
For a purely artificial reward list r=(3,1,0,0,...) and F=3/2, K=2, a=1,
b=-1/2. The funded calendar repeats gap lengths 2,3,3, with boundary credits
1,1/2,0. It earns 12 over 8 executions, has exact cap frequency 3/8 and protects
every activation prefix. Some individual guard executions earn zero, so their
one-execution sliding windows fail F. Requiring all sliding windows, including
length 1, is a much stronger problem. Likewise no phase-shifted initial state
inherits an activation-prefix certificate without accounting for its true
initial credit and reward history.

Independently drawing a long gap with probability p is also insufficient for
the prefix claim: its first long block has excess b<0 if no credit was earned.
Expected block excess can be zero while a realized activation prefix fails.
The funded order, not just the eventual mixture proportions, is essential.

Do not average per-gap means without time weights. For the same artificial
list, alternating length 1 and length 3 gives an unweighted average of gap
means 13/6, but an actual execution-time mean only 7/4. At target F=2 the
unweighted calculation falsely appears safe. The correct control cost is
1/mean(gap length), not mean(1/gap length).

I checked the first artificial funded calendar for 300 blocks with exact
Fractions: every activation prefix was safe, all credits remained in [0,H),
and its exact rate was 3/8. This is a synthetic falsification check, not proof
by simulation or a result for an inherited economic calibration.

## Equality and exceptional targets

| Target case | Correct conclusion, assuming the premises are certified |
| --- | --- |
| F<=C_star | One actual startup cap then guard forever has zero asymptotic cap frequency; r_j>=C_star also protects each activation prefix. |
| C_star<F<r_0 | Finite K and the adjacent-gap optimum above. Equality a=0 gives p=0 and fixed K, with no mixed saving. |
| F>r_0 | Infeasible for this cap-first two-mode family: the adverse first cap already fails the T=1 promise. |
| F=r_0>C_star | Let h be the finite initial plateau length r_0=...=r_(h-1)=F, followed by r_h<F. The adverse path has no positive credit to fund a later loss, so gaps cannot exceed h. Optimum rate is 1/h. |
| F=r_0=C_star | The whole nonincreasing reward list is constant; startup-only again has rate zero. |

For example, the artificial list (5,5,2,2,...) at F=5 allows gap 2 and rate 1/2,
not automatically rate 1. The initial-plateau proof is necessary if strict
reward decrease was not separately established. Mere overlap of interval bounds
is not proof of either equality or a plateau.

## Continuous enclosures and an implementable calendar

For certified a in [aL,aU], b in [bL,bU] with aL>=0 and bU<0,

    dp/da = -b/(a-b)^2 > 0,
    dp/db = a/(a-b)^2 >= 0.

Thus the candidate's enclosure direction is correct:

    rateLower = 1/(K+p(aU,bU)),
    rateUpper = 1/(K+p(aL,bL)).

Use aL,bL as fixed exact rational conservative credits for the actual calendar.
The same prefix argument applies because each true block-end excess is at
least its stored lower bound. Its rate is exactly rateUpper, which is a
certified attainable upper bound on the optimum rate. rateLower is only a
lower bound; it must not be advertised as an achieved safe schedule. Report
the optimality gap rateUpper-rateLower, and keep it distinct from a genuine
exact optimum in a rational finite game.

As an artificial check, K=2, a in [1,2], b in [-3,-1] yields rate bounds
[3/8,4/9]. Taking a=3/2,b=-2 gives true rate 7/17, inside that interval.
The lower-bound-credit calendar has rate 4/9, not a claimed exact 7/17.

If the target straddles C_star or r_0, the K-safe sign is unresolved, or the
next-failure sign is not negative, retain an unresolved/censored label or use
only a predeclared precision-refinement rule. Never clamp a negative lower
credit to zero unless a separate certificate proves a>=0. Near-equality and
tiny positive savings must retain their status and precision.

The largest possible relative saving from mixing adjacent gaps is itself
bounded: compared with 1/K it is p/(K+p)<1/(K+1). Large K therefore admits only
a modest integer-period penalty. This is an analytic bound, not a calculation
on any inherited case.

## Minimal conditions for a new prospective protocol

1. Freeze the exact two-mode family, cap/guard timing, cap-first activation,
   pathwise all-prefix target and worst-path limsup objective. Keep old absolute
   targets and physical caps unchanged; do not add actuators post hoc.
2. Freeze a limited full matrix and inherited identities before calculation.
   Include guard-only zero-rate, infeasible, equality/plateau, straddling,
   censored and tiny-saving labels. Reuse old K/next-failure evidence only with
   exact target, economy, allowance and cap identity checks.
3. For finite games, verify the entire upper map and reward monotonicity and
   use exact saved-weight rational sums. Prove the tail/plateau classification,
   rather than testing finitely many late steps and assuming it continues.
4. For continuous cases, verify the original premises, certified crossing signs
   and directed rate bounds. Store an implementable exact lower-credit calendar
   and a numerical optimality-gap bound; do not silently equate this with the
   unknown exact-real optimum.
5. Predeclare precision limits, search/censor limits and output-size limits.
   Avoid a potentially huge rational calendar-period enumeration. Prefix proofs
   and bounded remainder algebra establish infinite-horizon properties.
6. Independently rederive rewards/rates, funding decisions, within-block prefix
   bounds and a genuine partial final gap. Negative controls should corrupt
   time weights, a credit threshold, a block debt, an exact equality and a
   claimed achieved lower rate. Include the artificial sliding-window and
   unweighted-mean failures above.
7. Report fixed-rate versus mixed-rate differences, conservative achieved rate,
   rate enclosure width and exact/interval statuses. Rule frequency is still
   not implementation cost, actual quote changes or strategic freedom.
8. Keep any graphical credit demonstration read-only or exact-rational; it is
   not behavioral evidence. Do not reuse Goal7's phase-dependent Q tables as
   though they were trained for this incompatible credit clock. Any new learner
   experiment requires a separate state/observation design and authorization.

Recommendation: worth a focused next goal after V9 verification, as a tightly
bounded refinement of the control result. It should not displace the current
clear narrative or be marketed as a general novelty breakthrough. This review
authorizes no numerical inherited-case run; a distinct goal, protocol and
source-freeze gate are still required.
