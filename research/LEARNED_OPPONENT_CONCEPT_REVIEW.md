# Independent conceptual review: response to a frozen learned opponent

Status: prospective conceptual review only, outside the frozen V9 payload.
The candidate was read as source text. No inherited market, Q checkpoint,
controller case or learned outcome was opened or calculated for this review.
This is not a new goal, experimental protocol, source freeze or numerical GO.
The pending mixed-timing source review remains the current priority.

## Verdict

The candidate is mathematically sound and scientifically consequential. The
earlier fixed-script audit does not establish incentives against a learned
opponent that remembers both completed prices at cap rounds. A complete-state
discounted MDP directly addresses that gap. A certified achieved improvement
would refute unilateral optimality against that particular frozen opponent,
without assuming the numerical optimizer is exact. A sufficiently small
certified optimality gap could also make a near-zero result informative.

This is a known-model policy audit, not a new learning algorithm or an adaptive
equilibrium test. Related frozen-policy response work must remain credited;
the candidate's prior-work warning is appropriate. No methodological priority
claim is established by this conceptual review.

## Required state and information convention

Let s=(phase, previousA, previousB) denote the completed public state immediately
before the next execution. Reconstruct the saved opponent's deterministic
masked-greedy action at that state, including its original tie rule. A focal
action a must satisfy its CURRENT cap or guard support. The opponent action
must not depend on the focal seller's simultaneous a. Only the next completed
state contains both newly executed prices. For focal B, own/rival observations
and the profit-table orientation both transpose relative to the joint state.

The clock is the original controller clock. Startup-only stays in absorbing
guard after its already executed startup cap. Periodic cap rounds retain full
price history. Evaluation starts from the exact saved terminal state and NEXT
execution phase; there is no fresh cap, new startup reward or fictitious reset.
The baseline is the original saved focal greedy policy against the same frozen
opponent, in precisely this MDP. Its actions must be legal everywhere checked.

These conditions invalidate the old independent cap-block continuation value.
A cap resets current price constraints, not the learned opponent's state or
its choice among allowed cap quotes. The candidate correctly avoids that
shortcut. Markov stationary responses suffice for a finite discounted MDP;
the numerical certificate must still check every legal state-action edge.

## Achieved value certificate

For any proposed legal stationary response, the joint response/opponent
transition is deterministic. From the actual terminal state it has a finite
transient of length h followed by a nonempty cycle of length c. With exact
saved-weight rewards r_t and mathematical gamma=19/20, its achieved value is

    sum_(t=0)^(h-1) gamma^t*r_t
      + gamma^h * sum_(j=0)^(c-1) gamma^j*r_(h+j)/(1-gamma^c).

The first reward is the next executed pair's private profit. Repeat the same
calculation for the original joint greedy baseline. Their exact difference is
an attained gain certificate; no claim of response optimality is needed to
establish a strictly positive sign. Save both legal trajectories and ensure a
cycle closes in the FULL state, including phase and both completed prices.

A short-horizon or cycle-mean comparison cannot replace this expression.
Transient losses, the saved phase and discounted repetition can change the
gain's sign. Training used binary64 gamma, while this audit uses the explicitly
chosen rational19/20 discount. That small modeling difference must be stated,
not silently equated with bitwise replay of the training objective.

## Bellman upper certificate

For any exact finite vector v, define T using all legal focal actions against
the reconstructed opponent. Let delta be any rigorously certified scalar with

    r(s,a)+gamma*v(next(s,a))-v(s) <= delta

for every state and action. Since T(v+c)=Tv+gamma*c, the vector

    u = v + delta/(1-gamma)

is a Bellman supersolution. Monotonicity and contraction imply V_star<=u.
Consequently u(s_terminal)-V_response(s_terminal) is a certified upper bound
on the response's optimality gap. The exact achieved response is a lower bound
on V_star. The computed upper gap must be nonnegative; a negative exact gap
signals an invalid certificate or mismatched MDP. A lower-rounding display is
not allowed to disguise that inconsistency.

Delta need not be an absolute residual and may mathematically be negative.
Using max(0,delta) is a valid, weaker upper certificate if explicitly chosen.
An absolute-residual stopping criterion is useful for optimization but cannot
replace the actual independent one-sided all-edge comparison.

Exact dyadic v permits a particularly simple independent residual check. Take
a common power-of-two denominator L for all saved rewards and candidate values,
write r=R/L, v=Z/L and gamma=p/q. Then compute the maximum exact integer

    M = max_(s,a) [q*R(s,a)+p*Z(next(s,a))-q*Z(s)].

The certified upper value at s is exactly

    [(q-p)*Z(s)+M]/[(q-p)*L].

No floating residual or per-edge interval division is necessary. BigInt or
Python integers avoid fixed-width overflow assumptions. This is an efficient
certificate format, not a new Bellman theorem. Candidate values must remain
finite and their scale/quantization/hash must be bound to the receipt.

## Failure modes and negative controls

1. Reconstruct all opponent masked argmax actions from Q rather than trusting
   exported policy bytes; test ties, seller B transposition and full cap-state
   dependence. Opponent Q and counts remain frozen after the audit starts.
2. Check every legal focal action and transition in the all-state residual.
   Omitting an unvisited or cap state invalidates the global upper bound.
3. Preserve the actual terminal clock/history. A fresh-cap response is a
   separately labeled basin counterfactual and cannot replace the primary gain.
4. Verify the proposed response's full trajectory and baseline before using
   their exact values. Corrupting a transient reward or closing a cycle one
   phase early must fail independently of hashes.
5. Mutate a non-argmax counterfactual action to have a larger Bellman residual;
   a checker that verifies only the proposed policy's edges must reject this
   negative control. Also test wrong residual sign and gamma/(1-gamma) factors.
6. The optimizer may propose a response worse than the baseline or fail its
   residual target within budget. Retain that failed candidate and status;
   using the baseline as a separately certified legal fallback is allowed only
   with explicit provenance, never relabeling the failed solve as optimal.
7. Exact rationals can become large on long transients/cycles. Bound runtime,
   integer and output sizes prospectively. A compressed exact representation
   may be preferable to enormous decimal strings; hashes alone are not a
   scientific value certificate. Retain budget failures rather than shortening
   paths or replacing exact signs by tolerance-selected signs.
8. A residual interval straddling the required gap tolerance is unresolved.
   A tiny positive achieved gain is still positive; relative gain is undefined
   or misleading when the exact baseline is zero/nonpositive. Preserve exact
   signs and explicit null reasons before choosing display precision.

## What would make the next study useful

Freeze a modest complete paired matrix, one primary checkpoint and a single
mathematical discount before observing responses. Keep both sellers and all
seeds as paired counterfactuals, with unavailable records retained. Do not select
only visually interesting learned cycles or pool checkpoints as new samples.
The main comparison should keep achieved gains separate from upper bounds on
possible missed gain. A positive attained gain refutes exact unilateral
optimality; a nonpositive proposed gain without a tight upper bound says little.

Report which newly visited opponent states or chosen opponent actions were
unvisited/untried in original training. A response can exploit deterministic
ties in poorly trained off-path Q rows. That is a property of this frozen
policy, not evidence that the opponent would continue responding that way
after retraining. The all-state upper bound necessarily includes such states;
the actual response path's dependence on them is an important separate metric.

This direction is more consequential than another favorable calibration sweep
if the goal is to test strategic stability of the already learned behavior.
It requires a distinct protocol/source-freeze/audit gate after mixed timing.
No inference about collusive intent, robustness to misspecified economics,
subgame perfection or mutual adaptation follows from this fixed-opponent audit.
