# Independent review: demand calibration under frozen enforcement

Status: theory, prospective primary implementation, complete numerical audit,
derived numerical presentation, final PDF and scoped actual developer browser
checks accepted. Review closed; no additional scientific execution is implied.
Earlier frozen studies and delivery archives remain unchanged.

## Is the question meaningful?

It tests a precise missing assumption in the previous known-model guarantee:
the actual demand calibration can differ from the nominal model used by an
externally enforced action filter. The nominal guard, price domain, physical
cap, public clock and all original absolute welfare targets stay fixed.
Inside product quality falls by d*mu; outside quality and mu stay fixed.
This is a useful conditional calibration-reserve study.

Its interpretation must remain narrow. Reducing product quality directly
reduces customer surplus at the same prices. Keeping an almost-100% absolute
old target then produces small error tolerance mechanically. A failed target
does not demonstrate sellers gaming the mechanism, new autonomous collusion,
extra harm caused by a cap, or empirical demand uncertainty. The study does
not certify an action filter that recomputes its eligibility from an unknown
true model. The externally deployed nominal filter is deliberately frozen.

## Theory and prospective review

I wrote the prospective MODEL_MISSPEC_THEORY.md and protocol before new case
execution; root independently reviewed and accepted them. With nominal price
signal S, actual surplus is B*mu*log(1+exp(-d)*S). It is decreasing in both prices
and d. Therefore the same nominal top-price path attains every actual phase's
minimum, and a lower-quality endpoint certifies the entire declared interval
of fixed unknown d. This is neither an expected risk nor a confidence interval.

The cap-first finite-average proof remains valid because rewards along that
price orbit still descend. The unchanged nominal contraction gives a valid
uniform geometric tail; it does not assert that its excess shrinks with d.
Stationary crossing radii have an independent closed form. Finite-period
crossings have independently signed lower/upper displacements. All claims
retain the old fixed F-delta thresholds, including their original numerical
margin; no easier actual-market benchmark is substituted.

I reviewed misspec-study.py and all synthetic tests before freeze. Three
execution/claim gates were requested and fixed prospectively: a mismatch with
the closed d=0 period selection must be a retained unresolved failure; missing
pre-case target inputs must retain started/failure journals and all planned
slots; partial journal/record/completion outputs must block a new run. The
seventeen primary synthetic tests were independently rerun successfully.
They include signed padded stationary brackets, toy exact/uncertain zero
boundaries, empty safe sets, censoring, tails, phase-prefix reasoning, retained
duplicates and all three execution safeguards.

The primary source/input manifest was frozen before cases:
`ee02db992869d3fe41ac6e0b5f02a747f67d57293db7cd0c232ab69bba3eed07`.
The completed results hash is
`71d940c1ed4f3fe816c5b5dd4446d0ae5a2805cf2bf7426358800692b1e09ac3`.
All sixteen model semantics completed in 94.376 seconds with a final frozen
dependency recheck. The largest after-model RSS sample was 58,863,616 bytes,
not a continuously measured peak. No new learning, seller model/API calls,
purchases, external data or submission occurred.

## Independent audit and actual coverage

The new auditor imports no primary misspecification functions. It reuses the
frozen independent 130-digit arithmetic/model backend and evaluates actual
surplus using the algebraically separate exp(x+d) denominator. It separately
checks stationary closed forms, welfare signs at radius endpoints, price-tail
bounds, fixed prior policy choices, every reserve level and every robust
period's safe/failing endpoints. Old enforcement/cap/target identities and
closed audit/source/input hashes are checked transitively. The same standard
Decimal backend is shared; this is not formally verified arithmetic or an
independent transcendental library.

The complete audit passed 40,598 checks, covering sixteen model records,
eighty target labels, 240 retained policy slots, 960 reserve-level rows and
320 robust-period comparisons. Fifty-four policy slots are explicit duplicates.
All eighty d=0 selections reproduce the closed study. There are 174 certified
crossing radii and 66 already-failing-at-zero slots, whose safe nonnegative sets
are correctly empty. There are no actual unresolved/censored radius/model rows.
The robust-period statuses are 50 no-recurring-cap rows, 182 exact largest
periods and 88 fixed-family-infeasible rows across the two semantics/four levels.
These counts are not independent experimental samples or hypothesis tests.

Five deliberate actual-evidence corruptions were rejected: nominal enforcement
constant, displacement units, old target scaling, radius bracket and claimed
maximal period. Four independent synthetic audit tests also passed, including
separately evaluated high-precision scalar references, an explicit long toy
orbit/tail, signed root/period boundary failures and a synthetic full primary
certificate with independent corruptions. Tests may use primary code to
construct toy fixtures; the auditor calculation code itself does not import it.

The final independent auditor source hash is
`efbc8c30e5981863d4298b9a4bf945ade642413e566df9bdee9618ee8119eb08`.
The passed certificate is misspec-results/independent-audit.json and binds
the exact manifest/results and frozen arithmetic-backend hashes.

## Actual scientific result and its limits

For the base15 effective model's old 95% target, the previously selected K=4
policy tolerates a downward quality displacement of approximately d=0.0069632.
Permanent activation of the same physical cap tolerates approximately
d=0.153462. These are taste-scale units: physical quality falls by d*mu, not by
d percent. The predeclared uncertainty levels d_bar=0,0.001,0.01,0.05 require
largest robust periods 4,4,3,2 respectively, with all original absolute target
values retained. This gives a concrete frequency-versus-calibration-reserve
comparison within the same physical-cap family.

For the old 95% target, the eight effective selected-policy crossing radii
approximately range from 0.000716154 to 0.0519766. The half-tolerance label's
nominal K=10 selection must reduce to K=9 at the smallest declared positive
bound d_bar=0.001. This shows why a maximal nominal period should not be sold
as a demand-calibration guarantee.

Every relaxed 100% target becomes infeasible for this fixed-cap family already
at d_bar=0.001. Its permanent-cap crossing radii are approximately
1.85e-8–4.43e-8 taste-scale units. This magnitude largely reflects the original
1e-8 target relaxation. It is an expected fixed-target reserve effect, not a
new emergent failure mechanism or evidence for such precise real calibration.
The unknown-error levels are illustrative assumptions without empirical
probabilities. Different cap levels, uncertain enforcement, other demand
families, uncertain taste scale and strategic stability remain unexamined.

The work improves execution and exposes an important limitation in what a
known-model certificate promises. It adds no general-purpose robust shield or
learning algorithm. My current informal execution judgment is 4–4.5/5 and
originality about 3/5 for the combined narrow research program, and clarity
about 4/5 after the actual note, figures and scoped interface checks. These are not
the hackathon judges' scores or a ranking prediction.

## Derived presentation and PDF review

I read the descriptive analysis and its complete findings, the hash-gated
presentation exporter and the uncertainty-page sources. I independently
matched all 240 compact radius source records, 960 surplus/reserve/status
rows and 320 robust-period source records against the accepted raw results.
No numeric/status drift occurred. The findings retain empty safe sets,
duplicates, fixed old thresholds, illustrative uncertainty assumptions and
the distinction between original timing and a newly selected robust clock.
The exporter re-generates the descriptive adapter read-only and byte-matches
the saved summary in addition to checking audit/source/input identities.

I read all three pages of the actual calibration PDF and inspected every
rendered page. The initial version had overlapping0/.001 axis labels,
an overlaid legend hiding the bottom radius row, and an undefined A. I
requested fixes; all were applied. The accepted three-page file is
`output/pdf/demand-calibration-note.pdf`, SHA-256
`b1cd60eca9f8fa3ecd6a5a8ab23b5ef4c4f116af17bbe75dc2d5f25d4b406ad7`.
All three revised page renders were inspected. The four equally spaced
uncertainty positions are explicitly categorical, connecting lines are only
visual guides, both legends are outside their data, and A/B plus the inherited
cap premise are defined. The paper's positive/negative results, narrow
uncertainty scope and mechanical near-100% explanation are accurate.

I checked the Hartline, Wang and Zhang(2025) reference against its primary
[arXiv record and paper](https://arxiv.org/html/2501.09740v1). It concerns
pessimistic calibrated-regret auditing and unknown-cost integrity, not this
fixed-action-map quality-shift certificate. The note correctly labels it as
a different certificate and asserts no new general auditing method.

The uncertainty UI keeps actual product quality separate from deployed
enforcement, uses taste-scale units and approximate display values, preserves
small positive radii in scientific notation, and makes empty/zero/unresolved
statuses distinct. It does not alter the older finite game. These source and
adapter observations are not a substitute for actual browser readability or
human comprehension evidence.

## Final interface closure

The root agent performed the actual desktop and 390/320 CSS child-page
interactions recorded in MISSPEC_REPLAY_QA.md. I independently inspected both
final screenshots and their scientific labels; I did not repeat the root's
browser interactions. The base 95% example retains the same absolute threshold,
separates the below-target original K=4 policy from the newly selected K=3,
and shows permanent activation separately. Small positive 100%-target radii
remain scientific-notation values rather than being mislabeled zero. The
three policy labels and values remain readable in the inspected narrow views.

The root measured direct desktop scroll/client widths of 1265/1265, exercised
the declared buttons, keyboard and navigation, and captured empty direct-page
warning/error logs. Exact child widths were unavailable. One unsourced wrapper
MutationObserver TypeError remains disclosed without a causal attribution.
These developer checks are not a human pilot, device-emulation study,
accessibility certification or download verification. The final presentation
QA source hash is
`a76bf468778664cdc4faca2a8f725ccd8ba506e4e59ed2445425aef1614c8bb0`.
The 320-view adapter checks and fifteen altered-evidence rejections add
presentation/evidence-gating coverage, not behavioral research observations.

The accepted PDF remains the b1cd60ec-prefixed full hash above. No numerical
blocker remains within this fixed-demand-shift, fixed-enforcement scope.
The next consequential question is the individual incentive to follow the
adverse script; additional calibrated grids would add less information.
