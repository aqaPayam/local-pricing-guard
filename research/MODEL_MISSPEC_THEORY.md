# Fixed enforcement, uncertain actual demand: conditional robustness margins

Prospective theory only. No new alternative-demand case calculation is part of
this document. The previous recurring-cap evidence remains unchanged.

## What changes, and what does not

The deployed external guard evaluates the SAME nominal economic model and uses
the same frozen tolerance semantics, physical cap, public phase and permitted
sets. Its normalized upper allowance is U_hat, with the previously validated
nondecreasing contraction and fixed point q_star. It is an external restriction,
not a prediction that sellers voluntarily optimize that nominal profit model.

Let nominal quality minus outside-option quality be g_hat. Actual demand has
g_actual=g_hat-d*mu, by lowering inside product quality while holding outside
quality fixed, for a fixed but unknown d>=0. Here d is dimensionless, in
units of the inherited taste scale mu. Actual buyers B and mu, the price domain,
physical cap and all other parameters are held fixed. We do not refit the
enforcement guard when changing actual demand. Unknown enforcement parameters,
unknown mu, non-logit demand, estimated error distributions and time-varying
demand are different questions, not covered by this statement.

For normalized prices x=(p-c)/mu and nominal
k_hat=exp((c-g_hat)/mu), define

    S_hat(x,y)=(exp(-x)+exp(-y))/k_hat,
    C_d(x,y)=B*mu*log(1+exp(-d)*S_hat(x,y)).

Thus C_0 is the original continuous surplus. Actual demand shares and profits
may change, but every allowed seller policy remains bounded by the same
enforced price correspondence. Sellers may adapt arbitrarily within it.

## The nominal price envelope still gives the actual worst outcome

For every finite d>=0, C_d strictly decreases in either price and in d. Its
price derivatives have the same share form as ordinary logit surplus, so it is
B*mu-Lipschitz in the maximum norm of normalized prices. The sum of the absolute
two price derivatives is at most B*mu. Also

    -B*mu < partial C_d / partial d < 0.

The previously certified cap-first price envelope therefore applies without
change: A=(p_cap-c)/mu, a_0=A, a_(j+1)=U_hat(a_j). For phase j every allowed pair
is at most (a_j,a_j), and both shops selecting upper quotes attains equality.
Consequently r_j(d)=C_d(a_j,a_j) is the exact worst reward at that phase.
Its prices increase, so its rewards decrease toward C_star(d)=C_d(q_star,q_star).

For period K the exact worst long-run average is

    G_K(d)=(1/K)*sum_(j=0..K-1) r_j(d).

From an immediate real cap execution EVERY finite activation average is at
least G_K(d), with the same cumulative prefix formula as the closed recurring
study. Arbitrary initial phase has only the long-run conclusion unless an
initial partial cycle is separately controlled. The unchanged nominal guard
has worst all-start long-run floor C_star(d); an immediate startup cap followed
by that guard also bounds every finite activation average by C_star(d).

For an actual but unknown fixed d in [0,d_bar], the least surplus occurs at
d_bar. A certificate for G_K(d_bar)>=F is therefore uniform over that entire
declared uncertainty interval. It is not an average over an assumed error
distribution. The adversary that chooses both upper quotes is the same for
every d, so this is an attaining adverse policy, not incompatible separate
stage optimizations. No selfish equilibrium or autonomous emergence follows.

## Robustness radius at a fixed absolute target

Keep the original imported ACTUAL F-delta threshold F fixed in economic units;
do not renormalize it to the actual market's smaller benchmark. For a fixed
finite K, G_K(d) is continuous, strictly decreasing in d, and tends to zero.
For F>0 and G_K(0)>F there is a unique positive crossing d_crit satisfying
G_K(d_crit)=F. The target holds exactly for d in [0,d_crit].

If the target already fails at d=0, the safe nonnegative set is empty. Report
that status rather than an ordinary zero radius that could imply safety at
zero. Exact equality at zero gives zero robustness; numerical straddling at
zero is unresolved unless additional certified signs settle it. A finite
search ceiling only gives censoring, never a fabricated root.

The same crossing statement applies to the unchanged-guard floor C_star(d).
For a stationary equal-price pair z, its crossing has the explicit expression

    d_crit=log(S_hat(z,z))-log(exp(F/(B*mu))-1).

This gives an independent check for permanent-cap z=A and guard-floor
z=q_star policies. Classification at zero still precedes interpreting a
negative expression as a nonnegative safe radius. A fixed-point enclosure must
remain enclosed throughout the stationary calculation.

A simple conservative margin check is

    G_K(d) >= G_K(0)-B*mu*d.

Hence a positive nominal surplus reserve gives the sufficient radius
(G_K(0)-F)/(B*mu). This need not be the tight radius. Near-100% targets have a
mechanically small reserve by construction, so small radii there are expected
from a fixed absolute target and declining demand. They are not a new emergent
collusion mechanism.

## Reusing the certified finite orbit without inventing a tail

The nominal price orbit is unchanged. For J=64 and L=K-J>0, the uniform
price-Lipschitz bound gives, for every fixed d>=0,

    L*C_star(d) <= sum_(j=J..K-1) r_j(d)
    <= L*C_star(d)
       +B*mu*(q_star-a_J)*(1-rho^L)/(1-rho).

All quantities and positive-factor distances require directed enclosures. This
is deliberately conservative and its excess term does not claim to shrink
with weaker demand. The price and contraction uncertainty from the closed
study must be retained. Root or period boundaries that these enclosures cannot
separate remain unresolved/censored.

For each fixed d, G_K(d) strictly decreases in K toward C_star(d). The original
same-family largest-period certification and its 65536 ceiling therefore apply
at a predeclared d_bar. If C_star(d_bar)>=F, no recurring cap is needed for the
long-run target; keep zero versus one startup cap distinct. If G_1(d_bar)<F,
no member of this inherited fixed-cap family meets the target. This does not
rule out a stricter physical cap or another controller.

These are conditional known-structure robustness statements. They provide no
empirical calibration of d, no guarantee against inaccurate enforcement or
non-logit demand, and no evidence that the nominal guard is economically
appropriate in the actual market.
