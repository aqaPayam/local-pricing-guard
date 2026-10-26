# Independent review: recurring inherited-cap control

Status: theory, primary implementation, independent numerical audits, final PDF
and scoped developer browser evidence accepted.
Earlier frozen studies and packages remain unchanged.

## Question and contribution

The fixed inherited physical cap is applied repeatedly, starting with an actual
cap execution. The question is the largest fixed integer period that guarantees
each previously declared surplus threshold against every permitted seller
policy. This is a persistent controller, distinct from the already studied
finite initializer. Holding the physical cap fixed makes timing the intervention
that changes. The new public phase clock is part of the controller state.

This can establish a useful quantitative control frontier in a small known
model. It is not, by itself, a new general shielding algorithm, evidence of
emergent collusion, an incentive-compatible seller strategy, or a minimum-cost
controller across arbitrary policy families. Recurring interventions are a
standard idea; the contribution must be the tightly verified model-specific
comparison and its limits, rather than the existence of periodic resets.

## Prospective mathematical judgment

I read SPARSE_RESET_THEORY.md and SPARSE_RESET_PROTOCOL.md before any new case
execution. Their generalized inherited-cap argument is valid under the stated
previously certified monotonicity, contraction and welfare assumptions.

Writing A for the normalized inherited cap, A<q_star implies
U(A)-A >= (1-rho)(q_star-A)>0. The diagonal top-choice path therefore increases
toward q_star. Every allowed asymmetric path is coordinatewise below this
path after a cap, because U is nondecreasing. Coordinate-decreasing surplus
then makes the same attainable top-choice policy worst at every future stage.
This is stronger than separately minimizing incompatible stages.

The period mean G_K is an attained worst long-run average. From an immediate
cap execution its descending stage rewards also make every finite activation
average at least G_K. This does not make every individual round at least G_K,
and arbitrary observation phase does not inherit the activation-prefix claim.
The J=64 tail starts at a_J and uses K-J terms; the stated geometric tail has
the correct indices. Strict decrease of G_K survives a finite arrival at a
clipped ceiling because the initial reward is strictly above the limit.

For a saved finite numerical game, the exact min-prefix formula H_K is valid
even without descending rewards. Equality H_K=G_K additionally needs the
checked U(cap)>=cap condition and whole-table surplus monotonicity. Rational
arithmetic certifies the stored binary64 reward weights. It does not turn the
binary64 eligibility mask into an exact-real or exact-rational profit test.

## Required implementation gates

- Validate the inherited cap's price, index and economy against both old input
  sources. Retain an unmet A<q_star condition rather than changing the cap.
- Apply U to an input interval using separately signed scalar endpoint solves.
  Retain root and recurrence uncertainty, clipping and all failed calculations.
- Preserve all 80 model/target labels and their fixed imported actual F-delta
  thresholds. They are derived labels, not independent experimental samples.
- A largest-period claim needs a certified safe K and a certified failing K+1.
  Never evaluate 65537 under this protocol. A safe 65536 is censoring.
- Distinguish an untouched guard with zero startup caps from one immediate cap
  followed by guard forever. Their long-run rate can both be zero while their
  finite activation guarantees differ.
- Independently reproduce every finite payoff and mask in JavaScript arithmetic,
  then use separate Fraction arithmetic for cycle and prefix certificates.
- Reject deliberate corruptions of cap identity, phase/reward timing, orbit
  terms, period boundaries and finite prefix certificates.

## Actual implementation and independent evidence

Before either run I read the primary code/tests. Eleven continuous synthetic
tests and ten finite core/builder tests were independently rerun successfully.
The finite builder's initial provenance check omitted verification of the live
closed mesh-manifest dependencies. I required and verified that fix before
freeze; the corrected check binds the raw original thresholds to their earlier
audited inputs. The near-cap quote-priority rule was declared before any finite
case execution. No primary method was changed after the corresponding freeze.

The continuous manifest is
`47569ed71e5d7995328f5ffb9ee4bf9c948a0f741dd82ce634c70415bdd0d32f`.
The sixteen-record results hash is
`839364ea71fd892d10dec1550449001718b51a2d8d347b470b57bed63203541d`.
All sixteen models and eighty fixed model/target labels resolved; there were no
condition/calculation failures. Runtime was 307.300 seconds. The largest RSS
sample after a record was 41,242,624 bytes; it is not a continuous peak measure.

The independent controller audit imports no new primary controller functions.
It reuses the frozen independent 130-digit arithmetic/model backend, reruns
the earlier continuous audit read-only, verifies each saved Lambert bracket
using log-residual endpoint signs, and verifies each upper-branch root using
independently calculated profit residuals. It checks 2,048 scalar endpoint
certificates, all propagated price/reward intervals, the 64-term prefixes,
geometric tails, descriptive profits, period enclosures and every original
threshold comparison. Its receipt records 44,110 checks, plus 3,838 earlier
continuous-audit checks. Actual-result corruptions of cap identity, orbit
reward, reward timing, claimed maximal period and finite-prefix lower bound
were rejected. This is separate calculation logic with a shared standard
Decimal backend; it is not formal verification or independent arithmetic
library validation.

The finite manifest is
`bce40f35637ed8a0c28dee15357fea812307a53b55122be6878f99f0b386b367`;
the index is
`e5ab2fee741d4c711c7d9291e428e6e505a3f1b0d3806a574f133dcee6f36ecb`.
All eight games completed. Independently rebuilt numerical payoff tables cover
30,506 price pairs. Both shops' entire eligibility masks agree, all saved
surplus-coordinate inequalities and upper-map monotonicity checks hold, and no
near-mask-boundary flag occurred under the declared diagnostic. Every previous
public pair and every cap execution outcome was checked; 4,852 real core
executions exercised guard/cap phases, asymmetric lagged history, undo and
reset. This audit recorded 191,823 checks and rejected four economic/mask/cap/
orbit corruptions. Shared JavaScript Math arithmetic is explicitly disclosed.

A separate Python Fraction audit independently recomputed all 64 stored
cycle means and tight min-prefix floors from exact rational values of the
saved binary64 rewards, including their greatest outward lower binary64
displays. It recorded 810 checks and rejected three prefix/cycle corruptions.
Four independent Python synthetic tests and two Node synthetic audit tests
also passed. These checks certify the declared numerical finite game, not exact
transcendental logit payoffs or behavior in an actual market.

## What the actual result means

Effective and nominal continuum calculations agree on every integer-period
classification. The following are the largest periods for the inherited fixed
physical cap; target percentages still include their old declared relaxation.

| Inherited label | 90% target | 95% target | 99% target | 100% target | Old anchor target |
|---|---:|---:|---:|---:|---:|
| Base 15 | No recurring cap needed | 4 | 1 | 1 | 1 |
| Demand scale 0.5 | No recurring cap needed | 2 | 1 | 1 | 6 |
| Lower quality | No recurring cap needed | 2 | 1 | 1 | 6 |
| Lower cost | No recurring cap needed | 7 | 1 | 1 | 1 |
| Base 11 | No recurring cap needed | 8 | 1 | 1 | 1 |
| Base 31 | No recurring cap needed | 4 | 1 | 1 | 3 |
| Half tolerance | No recurring cap needed | 10 | 1 | 1 | 1 |
| Double tolerance | 17 | 2 | 1 | 1 | 2 |

The useful positive result is that recurring executions can meet the fixed 95%
target with periods 2–10 under this family. The equally consequential negative
result is that 99% and 100% require the cap every round in every label. Seven
90% targets already hold in the unchanged guard's long run, so recurring caps
cannot be credited for creating that protection. Zero asymptotic activation
frequency still distinguishes zero startup caps from one immediate startup cap
when finite activation averages matter. No censored/unresolved period or
infeasible fixed-family target occurred in these actual cases; synthetic tests
cover those branches without inventing favorable actual examples.

This is meaningful model-specific verification and design work. It does more
than replay a selected programmed behavior: the order argument bounds every
allowed seller policy, and a feasible script attains the bound. However, the
environment, intervention and adverse script are engineered. No experiment
here establishes autonomous emergence, strategic stability, human
understanding, realistic demand estimation or real-world consumer benefit.
The eight labels include equivalent calibrations and grid variants; eighty
target labels do not provide eighty independent replications.

## Current grading and next consequential question

For this narrow known-model contribution I judge numerical execution roughly
4–4.5/5, presentation clarity roughly 4/5 and originality roughly 3/5. These are
informal reviewer ranges, not the hackathon judges' scores. They concern the
narrow known-model result and developer-reviewed artifacts, not human-tested
understanding or likely competition rank. Additional parameter sweeps would
have limited value now.

My preferred next question is model misspecification: hold the deployed guard
and physical cap code fixed, lower the actual demand quality gap, and certify
how much downward error each selected target/period tolerates. The same
nominal price envelope still bounds all allowed policies; actual customer
surplus changes. Its monotonicity in the actual quality gap makes the lower
endpoint of a declared uncertainty interval decisive. Very small certified
error margins would be a valuable falsification of practical robustness,
especially for near-100% claims. This alternative-model question would require
a separate prospective protocol, not reinterpretation of this closed run.

For the specifically declared alternative where actual quality minus outside
quality falls by delta>=0 while mu and enforcement remain fixed,
`C_delta=B*mu*log(1+exp(-delta/mu)*S_nominal)` at each executed pair.
This preserves price-coordinate monotonicity, and strictly decreases welfare
with delta. The same fixed price envelope remains worst. A useful discriminating
quantity is therefore the break-even downward-error radius for each selected
period/target, compared with always-cap and the unchanged-guard floor. That
would quantify calibration fragility without assuming the alternative is a
measured real-market error distribution.

A second useful question is each seller's discounted best response to the
public adverse script with phase included in the state. It would test strategic
relevance without changing the all-policy guarantee. Unilateral MDP auditing is
already close prior work and must not be presented as a newly invented method.
Price caps and timing restrictions are also existing regulatory ideas; see
[MacKay and Weinstein, Dynamic Pricing Algorithms, Consumer Harm, and Regulatory Response](https://wustllawreview.org/dynamic-pricing-algorithms-consumer-harm-and-regulatory-response/).
The separate SPARSE_RESET_NOVELTY.md identifies additional primary reset/control
and economic-platform sources and explicitly disclaims a firstness proof.

## Presentation source review to date

I read recurring-analysis.js and RECURRING_RESULTS.md and directly checked that
all eighty derived target rows and 128 frontier records preserve the frozen
primary results. No interpretation correction was needed: differing physical
caps/old targets across grid-size labels, already-safe targets, permanent
activation for strong targets and shared-backend limitations are explicit.

I also read build-recurring-web.js and the current recurring UI sources. The
export requires all three independent receipt/output/manifest/auditor bindings
and live frozen dependencies. The game uses its own finite floor, exact
cumulative buffer, real execution count, explicit public phase and separate
manual/scripted histories. These sources make no unsupported independent-AI,
profit-optimum or continuous-to-finite certificate transfer claim. Actual
rendering and browser observations were then checked as described below.

## Final artifact and developer-QA closure

I read all four pages of the actual recurring-cap PDF and inspected all four
rendered pages. I requested two small fixes: label the shortened target value
as approximate, and include the separate `--finite` Fraction audit command.
Both were applied; I checked the revised PDF text and the changed page1/page4
renders. The accepted four-page artifact is
`output/pdf/recurring-cap-note.pdf`, SHA-256
`c7c0e309ba38599d7930933b9783e321a5b52732225837e235706d74b6957a1b`.
Its figures, complete target matrix, cap-first mathematics, numerical scopes,
prior-work positioning and limitations are legible and accurate. No claim of
general optimal control, strategic equilibrium or emergent behavior was added.
The final page1 clarification explicitly defines the old permanent-cap
percentage targets, old certified anchor floor and saved
`1e-8*max(1,requested value)` relaxation. I checked its actual text, PDF hash and
updated page1 render; it is accurate and remains readable. The other three
pages' content is unchanged.

I read RECURRING_REPLAY_QA.md and independently opened the four root-supplied
actual browser screenshots: recurring-v6-desktop, recurring-v6-narrow,
overview-v6-desktop and overview-v6-narrow. The root performed the live browser
interactions; I reviewed the resulting evidence rather than independently
repeating those interactions. It records actual desktop checks, first-cap and
later-guard rewards, asymmetric choices, separate manual/scripted histories,
undo/restart, K=1, and a K=128 target-failing case that retains its own lower
floor. Both 390px/320px CSS child pages exposed the complete selected quote
and successfully executed their first cap. The inspected portions are readable.
The larger displayed finite-game floor is explicitly scoped to that finite
choice set, not silently substituted for the continuous floor.

The QA correctly separates DOM-adapter checks from actual rendering and
developer interactions from a human study. Direct desktop width equality and
empty direct warning/error logs are recorded. Exact child width was not
available; the narrow checks are CSS iframe views, not device emulation. Two
unsourced MutationObserver wrapper errors are retained without an invented
causal explanation. This evidence supports the scoped developer-QA claim; it
does not establish exhaustive accessibility, touch usability, download behavior
or human comprehension. These limitations do not invalidate the accepted
mathematical/numerical result.
