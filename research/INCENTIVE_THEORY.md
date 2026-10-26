# Prospective exact unilateral audit under a public reset script

This note defines the next proposed study. It authorizes no case execution.
The finite numerical games, saved binary64 profit weights, masks and physical
caps are inherited without modification. Exactness below means rational
arithmetic on those saved finite-game weights, not exact-real logit economics.
The prior continuous or misspecified-demand guarantees are not substituted.

## State, timing and the unilateral question

Fix a period K>=1 and a public clock. Phase 0 executes the competitive cap
instead of the guard; phases 1,...,K-1 execute the saved guard. The opponent
always chooses the largest currently permitted quote: cap index A at phase 0,
or U(i) at a guard phase, where i is the focal firm's previous executed index.
The focal firm may choose any quote <=A at phase 0, or any a in S(j) at a
guard phase, where j is the opponent's previous executed index. The next state
in focal coordinates is (a,b), with b the opponent's current executed quote.
Only the prior public state and public deterministic opponent script are used.
Predicting this known simultaneous quote is not reading a hidden proposal.

The baseline focal firm also chooses the largest permitted quote: A or U(j).
Both individual profit tables must be respected. In focal coordinates the
seller-B reward R_B(a,b) is the saved original-coordinate profitB(b,a), not
profitA(a,b) merely because a symmetric result is expected.

This fixes the opponent's policy after deviations. It does not introduce a
punishment response, strategic adaptation, private signals or learning.

## Finite blocks solve the infinite discounted response

Let 0<=gamma<1. Exclude the reward of the previously saved state. Set V_K=0.
For guard phases l=K-1,...,1, define

    V_l(i,j) = max[a in S(j)] { R(a,U(i)) + gamma V_(l+1)(a,U(i)) }.

At cap activation the value of the following block is state-independent:

    V_0 = max[a<=A] { R(a,A) + gamma V_1(a,A) },

where the continuation is zero when K=1. Future cap executions discard all
previous price history under this opponent script. Every future block has the
same conditional optimum V_0. A maximizing action at each phase is feasible,
and repeating that block attains the infinite value

    J_0 = V_0 / (1-gamma^K).

This also upper-bounds every history-dependent or randomized focal policy:
conditional on any history at a cap, its next block cannot exceed V_0; summing
these bounded blocks gives J_0. Deterministic maximizing actions attain the
bound, so randomization cannot improve it.

For a guard-phase initial state, the infinite optimal value is

    J_l(i,j) = V_l(i,j) + gamma^(K-l) J_0.

Compute the baseline block values B_l using the baseline action in the same
recursions, and B_0 from its cap action A. Its infinite value is

    H_l(i,j) = B_l(i,j) + gamma^(K-l) B_0/(1-gamma^K).

Its cap value is B_0/(1-gamma^K). The two next-block constants generally differ;
they must not cancel when reporting the optimal gain J_l-H_l. Every gain is
nonnegative because the baseline is an admissible focal policy. A negative
exact gain falsifies the implementation, rather than indicating stability.

When gamma=0 each value is simply its current phase's best immediate reward.
The activation value alone then reveals nothing about later guard incentives.
Reporting the complete baseline-path phase diagnostic is essential. The K=1
case is a repeated capped stage game and has no guard phase.

## Exact integer implementation

Choose D to be the smallest common power-of-two denominator of every saved
binary64 profit weight used by that focal game. Write r=R*D as an integer.
For gamma=p/q in lowest terms, define the integer finite-block layer by its
phase index: W_l = D*q^(K-l-1)*V_l for 0<=l<K, and W_K=0. Its recurrence is

    W_l = max[a] { r(a,b)*q^(K-l-1) + p*W_(l+1)(next) }.

At phase 0 the opponent quote is A and the next state is (a,A); this makes
W_0 a state-independent scalar. The next value is zero at l=K-1. This formula
includes gamma=0 using p=0,q=1;
there is no floating discount or numerical Bellman stopping rule. The baseline
uses the same scaling and its prescribed action. The cap infinite value is

    J_0 = q*W_0 / [ D*(q^K-p^K) ].

For primary gamma=19/20 this is 20*W_0/[D*(20^K-19^K)]. Rational output is
reduced before storage; display approximations do not decide signs or ties.
Choose the smallest original quote index among exactly tied maximizers.

## A deliberately elementary falsification screen

On the baseline path, consider its last guard phase K-1, for K>1. Its current
opponent quote is fixed by the previous public state. The maximum permitted
immediate profit minus the baseline immediate profit is an exact one-shot
gain. After any such deviation, the next execution is the history-independent
cap; returning to the baseline then gives precisely the original continuation.
Therefore a positive last-guard gain rejects this script's best-response
stability from that phase for every 0<=gamma<1. From cap activation the same
deviation yields a strictly positive gain for every gamma>0, multiplied by
gamma^(K-1); gamma=0 at activation ignores it. For K=1, the corresponding cap
one-shot deviation leaves every future cap unchanged and supplies the analogous
test. This screen is reported even if it makes full-DP qualitative findings
unsurprising. Full DP quantifies the optimal gain and policy, rather than
creating novelty by hiding this simpler explanation.

## Customer benefit remains a separate certificate

The inherited finite games have nondecreasing U and coordinate-decreasing
saved customer-benefit weights, both independently audited. Any feasible focal
deviation is still dominated coordinatewise by the both-firms upper path from
the same cap activation, since cap and guard retain their old masks. Thus an
individual incentive finding cannot invalidate the earlier all-policy floor.
For each new K reconstruct the upper path independently and store its exact
cycle mean and minimum nonempty prefix mean. Periodic renewal then makes that
minimum prefix mean the exact all-horizon cap-first floor for saved weights.
Even when K was inherited from a continuous 95% label, no finite-game 95%
protection follows without comparison to its fixed inherited threshold.

Positive unilateral gain rejects only the specified public script against its
fixed scripted opponent, at the stated phase and discount. Zero gain at the
examined path does not establish subgame perfection, multi-agent learning
convergence, private-information equilibrium or observed collusion. All-state
phase DP values permit further checks but do not change this reporting scope.
Exact finite unilateral dynamic-programming audits are established prior work;
the contribution is a controlled incentive audit of this particular enforced
handover/reset mechanism.
