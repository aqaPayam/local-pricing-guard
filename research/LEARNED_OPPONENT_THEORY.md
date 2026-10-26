# Conditional numerical certificates against a frozen learned shop

Prospective derivation for the separately frozen follow-up. These are standard
finite discounted-control arguments, not new algorithms or equilibrium claims.
The protocol, conceptual review and analysis contract define the population.

## State and objective

Let s=(phase, previousA, previousB). The opponent's reconstructed masked-greedy
choice b(s) is fixed before the focal current action a. Each legal a gives a
deterministic executed pair, private reward r(s,a) and next full state f(s,a).
For focalB, transpose its Q observation coordinates, not the original world's
profitB reward table. The original cap changes the legal set without deleting
history. Startup-only's post-cap guard phase is absorbing.

With gamma=p/q=19/20, maximize sum_(t>=0) gamma^t r(s_t,a_t), starting at the
actual saved final state/next clock. Finite states/actions and bounded rewards
give an optimal deterministic stationary response in this known MDP. The upper
certificate below also bounds arbitrary history-dependent/randomized legal
response paths against that same frozen opponent. It assumes no resumed
opponent learning, policy uncertainty or access to a simultaneous current move.

## A direct pathwise upper bound

Choose any finite dyadic candidate vector v. Lift saved reward rationals and v
to one common positive power-of-two denominator L, so r=R/L and v=Z/L. Compute
over EVERY legal state/action edge

    M = max [qR(s,a) + pZ(f(s,a)) - qZ(s)].

Set U(s)=[(q-p)Z(s)+M]/[(q-p)L]. Since q-p=1 here, U=(Z+M)/L.
For each edge, r(s,a)+gamma U(f(s,a)) <= U(s); substituting U leaves exactly
the checked inequality that its residual numerator is at most M.
Multiply by gamma^t and telescope along any legal path:

    sum_(t=0)^(T-1) gamma^t r_t + gamma^T U(s_T) <= U(s_0).

The finite vector U is bounded and gamma<1, so the final term vanishes as
T increases. Thus every admissible infinite response value is at most U(s_0).
The signed maximum M may be negative. No absolute residual, unchecked floating
comparison or inspection of only the proposed policy's edges supplies this
certificate.

The exact one-step argmax against v proposes a policy pi, with smallest
original-index ties. It is still merely a legal response unless its separately
computed exact value and upper gap show more. Approximate value-iteration
stopping is not part of the proof of this certificate.

## Exact achieved value

Under pi and the frozen opponent, full-state repetition gives a transient
h>=0 and a nonempty cycle c>=1, with h+c<=N. Discounted value is

    V_pi = sum_(t=0)^(h-1) gamma^t r_t
         + gamma^h * sum_(j=0)^(c-1) gamma^j r_(h+j)/(1-gamma^c).

All rewards are exact rationals of the saved binary64 table. Integer
polynomials and powers evaluate this expression without truncating the path
or approximating its sign. The baseline follows both original greedy policies
from the identical actual start, and receives its own independently replayed
transient/cycle value V_base. Mathematical19/20 is distinct from the old
binary64 training discount.

The raw attained gain is G=V_pi-V_base. Strict G>0 refutes baseline unilateral
optimality at that start. U-V_pi is a nonnegative upper bound on the remaining
response optimality gap. Because baseline is legal,

    max(0,G) <= V_star-V_base <= U-V_base.

Retain G even when negative; max(0,G) is a different bound justified by the
baseline option. A loose U-V_pi does not invalidate an attained profitable
deviation. Zero/negative G alone does not establish stability. Even a tiny
U-V_base supports only corresponding approximate optimality against this
particular fixed opponent, not subgame perfection or mutual adaptation.

## Discounted support exposure and separate welfare

For a deterministic indicator I_t of a previously unvisited source state or
never-tried chosen action, its full path shares the same h/cycle. Applying the
exact value formula to indicator rewards and multiplying by1-gamma gives
E=(1-gamma) sum gamma^t I_t in[0,1]. Save it separately from unweighted counts
over the transient and one cycle. This exposure is a descriptive diagnostic,
not a causal decomposition of profit improvement or a retraining prediction.

The optional customer-benefit diagnostic is instead the exact arithmetic mean
of original saved consumer-surplus weights on each eventual cycle. Its
response-minus-baseline difference is not discounted profit, a finite-prefix
promise or an outcome used to optimize the response.

## Conservative integer-size reasoning

The selected games have n=62 and at most4 phases, hence N<=15,376. Finite
binary64 reward denominators are at most2^1074 and lifted reward numerators
need at most about2,100 bits. Candidate integer parsing is limited to4,096 bits
per entry before lifting from denominator2^32. With p=19,q=20, each path power
needs fewer than5N+1 bits. Even a deliberately loose bound

    8*N*5 + 8*4096 + 16384 <= 664192 bits

covers intermediate path/rational products, differences, relative gains and
the declared residual/vector scales, below the1,000,000-bit scalar ceiling.
Implementations must validate N, dimensions, finite input exponents and
candidate sizes BEFORE large powers/products, then check actual output sizes
before serialization. This bound is not permission to accept malformed input
or allocate an unbounded integer first. Canonical hexadecimal rational strings
avoid decimal-digit serialization limits; they do not replace the arithmetic
checks or make a long path a short-horizon approximation.
