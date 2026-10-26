# What mathematics and algorithms are actually used?

This describes the historical continuous-contract stage. The subsequent local
Q-learning experiments and complete current algorithm explanation are in
[ALGORITHMS_AND_MATH.md](ALGORITHMS_AND_MATH.md) and
[LEARNING_RESULTS.md](LEARNING_RESULTS.md). The statements below about no
reinforcement learning refer only to that earlier stage.

The first version was a software demonstration of programmed behavior. The
second version asks a different, mathematical question: what can an external
price constraint guarantee even when the price proposer is arbitrary?

## The market

There are two differentiated products, 100 potential customers, and an option
to buy nothing. The multinomial-logit demand rule is

`quantity_i = 100 exp((2-price_i)/0.25) / (1 + exp((2-price_A)/0.25) + exp((2-price_B)/0.25))`.

Unit cost is 1. Profit is `(price_i-1) × quantity_i`. Customer benefit is the
logit consumer-surplus measure `25 log(1 + exp((2-price_A)/0.25) + exp((2-price_B)/0.25))`.
These are standard economic formulas, not a new economic model. Quantities are
expected demand, so fractional customers are intentional.

## Optimal prices and numerical algorithms

The one-round best response `b(q)` maximizes a seller's profit when the rival's
price is `q`. The code solves its first-order condition by bisection. It also
uses bisection for the competitive and symmetric joint-profit reference prices.
They are approximately 1.472927 and 1.924981 in this economy.

There is no neural network, reinforcement-learning algorithm or trained pricing
agent in these new studies. The random proposal stress tests use reproducible
PCG-style integer generators. They test inputs; they do not train anything.

## The receiver contract

For the **last completed** rival quote `q`, compute the interval of prices whose
one-round profit is within epsilon of the best available profit:

`allowed(q) = {p: profit(b(q),q) - profit(p,q) <= epsilon}`.

Clip the proposed price to that interval. If it is already inside, keep it.
The interval endpoints are found by bisection. Epsilon is a profit amount per
round, not a price difference, percentage, or calibrated-regret audit statistic.

The calculation cannot see the simultaneous current rival quote. We therefore
record loss against the last quote separately from loss against the actual
current quote after settlement. These are different quantities.

This changes the receiver's allowed actions. It is not merely cleaning a note,
and it may sacrifice the proposer's preferred repeated-game strategy.

## The mathematical guarantee and its price

For this calibrated market, the best-response function has derivative less than
one half in magnitude. If both sellers are permanently constrained with
epsilon zero, their maximum price distance from Nash shrinks by at least one
half per round in ideal real arithmetic. This follows from a contraction
argument. The notes and proposal generator can be arbitrary because the exact
contract replaces each proposal with the best response.

That is also the autonomy cost: epsilon zero leaves only one permitted price.
It is ordinary best-response dynamics, an established algorithm, not a newly
discovered AI behavior. Positive epsilon preserves an interval of choices; the
proof gives a conservative error neighborhood only under its stated conditions.

The [full derivation](RECEIVER_CONTRACT_MATH.md) uses implicit differentiation,
the Lambert W representation, contraction bounds, and strong concavity of
**log profit above cost**. It does not assume profit is globally strongly concave.
The implementations use floating-point arithmetic; numerical audits are not
machine-checked formal proofs.

## An exact failure boundary

For any constant common price `p`, let
`r(p) = profit(b(p),p) - profit(p,p)`.
If epsilon is at least `r(p)`, repeating price `p` is permitted by both contracts.
At the joint-profit price this threshold is approximately **7.420439** profit
units. A budget of 8 can therefore preserve that high-price path even with
permanent protection of both sellers and a correct model. This is a pointwise
admissibility statement, not a worst-case bound over all dynamic strategies.

Only one participating seller, temporary protection, or an inaccurate demand
model lies outside the bilateral calibrated convergence guarantee. Their
counterexamples are reported rather than discarded.

## What could be a contribution?

The proposed contribution is an explicit, reproducible boundary between
information cleanup and enforceable behavior: a conditional recovery argument,
an autonomy-versus-admissible-harm calculation, and counterexamples for missing
assumptions. Best responses, action shielding, logit demand and contraction
arguments are prior work. See [the novelty review](NOVELTY_REVIEW_V2.md).

The work does not establish spontaneous AI collusion or a validated language
filter. An evaluation of a language-aware handover would still need relevant
model evidence. No new account-backed model-player calls are authorized.
