# Cap & Go: prospective playable recurring-cap design

Design only, 26 October 2026. This document responds to the root's request for a user-friendly game based on `SPARSE_RESET_CANDIDATE.md`, including its pending activation-time finite-horizon corollary. The root subsequently selected the inherited physical-cap family, reflected below; its generalized proof and prospective protocol remain pending. No new case computation, controller implementation, UI implementation, game session or human study was performed for this design. Build only after a prospective protocol and explicit implementation authorization. Existing pages, data, reports and packages remain unchanged.

## The game in three sentences

You control both shops in a small, fully known market. Choose any permitted price for each shop, execute both together, and try to push customer benefit toward the verified worst-case benchmark while watching each shop's profit. Every K executions, one real cap round interrupts the guard; the question is how much protection this recurring rule provides at different periods.

Working title: **Cap & Go · Two-Shop Challenge**. A “cap” is an actual price execution restriction, not deletion of memory, a reset of a learner, or a free adjustment between reward-bearing rounds.

## What the person controls

The person is a deliberate coordinator of Shop A and Shop B. Say this before play: “You choose both prices. This is a stress test, not two independent players.” Neither shop is called a hidden rival. The two choices execute atomically, and both allowed sets during a guard round depend on the previous public prices, not on edits to the other shop's current quote.

Use one predeclared finite price set per market: the inherited 61-price base mesh with the exact original physical cap price inserted under the approved near-cap priority rule. The frozen protocol removes a base quote within 1e-12 absolute price units of that cap (retaining an invalid-grid outcome if more than one is near), preserves the original cap exactly, then sorts and deduplicates exactly. This yields 61 or 62 actual choices. Record every replaced base quote and distance; this construction defines a new display game and does not alter an old grid. Every permitted grid choice remains selectable; do not reduce human choice to strategy buttons. A native range control stepping over grid indices, a searchable/selectable price list if needed, and explicit numeric price labels make the choices accessible. If a price-typing aid is provided, an off-grid or blocked price is a preview only. Offer clearly labeled permitted alternatives and require the person to choose one; do not silently round, clip or execute it.

The primary recurring intervention must reuse the exact original physical cap price for that inherited scenario. This holds the cap strength fixed while changing when it is applied. Include that cap in the finite quote set rather than silently rounding it to the nearest 61-mesh point. The potentially nonuniform 61/62-choice game recomputes its own best-profit benchmark and needs its own complete payoff, upper-map and periodic-controller audit; the older uniform61 audit is not its certificate. The original cap source, its binary64 identity, the expanded price list and actual cap index remain visible in evidence details. Continuous analysis of this same physical cap is also separate, and requires its own validated recurring-cap assumptions and certificate.

The default screen contains one market and a short set of audited periods. Market variants and target details sit behind “Change the challenge.” Retain all eight inherited scenario labels and their original five target labels, including numerical duplicates; the original 40 targets and margins stay fixed. Select the default period only after the actual data is available; choose a short, informative eligible case rather than inventing a favorable result. Changing market, period, cap definition or tolerance starts a new game. It cannot rewrite an ongoing game's rule or its comparison floor.

## A meaningful and honest challenge

Primary prompt: **“Can you get below the protected average using only allowed prices?”** Use this wording only for a finite-game, cap-first average guarantee that has actually been audited. The point is to understand a quantified protection rule; a correct certificate makes a genuine legal counterexample impossible within its assumptions. The game is not new evidence of emergent AI behavior, and a person's failure to find a counterexample does not establish the certificate.

The person tries to get close to the adverse benchmark. Track the distance from the audited worst average for the same number of executed rounds where available. Short prefixes can have a higher tight benchmark than the complete-cycle floor; do not penalize someone for the protective first round by comparing every prefix only with the infinite-cycle value. Show profit for each shop as a separate outcome. Lowest customer benefit need not maximize either profit or joint profit.

There is no global leaderboard: raw scores across different economies, periods and horizons are not directly comparable. At a session end, report the chosen rules and horizon alongside every score. A small “Explore profits instead” prompt may invite experimentation, but must not relabel the adverse-customer-benefit benchmark as a profit optimum.

If the finite protocol provides only a completed-cycle or long-run certificate, the challenge instead reads: **“Compare a complete cycle with its verified worst average.”** Score only complete cycles against that certificate. Partial-cycle averages stay visible as observations, never as a failed protection promise. The UI must not borrow the pending continuous finite-prefix corollary to upgrade an unverified finite-grid result.

## The first minute

Three short cards precede the first action:

1. **You set both prices.** Choose from the marked prices for each shop. Higher prices can reduce expected purchases; both profit and customer benefit depend on the pair.
2. **A cap really executes.** The first round is capped. It earns its own reward and establishes the first public prices. Then the guard governs the next K−1 rounds.
3. **Watch the average, not just one round.** A later round may be below the protected average. The customer-benefit buffer explains how the cap and later rounds add up.

An optional first-three-execution guide is on by default and never executes a price. It points to the cap, then the previous-price guard, then the difference between current benefit and the running average. Guidance adapts to K=1: every execution is capped, so it must not promise a guard round that never occurs. If the current data does not display a below-floor individual round, explain that possibility conditionally rather than manufacturing one.

The normal game begins before any execution with blank outcomes. No inherited price is counted as a reward. Optional old-history presets can be an advanced illustration; they do not affect the cap-first guarantee and must be labeled history, not an extra played round.

## One screen, one clear action

Use the existing warm background and orange/blue shop colors, native SVG/CSS graphics and readable text. No paid illustrations or model-generated assets are needed.

The upper strip says “Execution 1 · CAP ROUND” or “Execution 2 · GUARD ROUND,” followed by a row of K phase tiles when practical. The active tile is explicit. For long periods, show the current phase and a compact count instead of hundreds of tiny boxes. A countdown says “Cap now” or “Next cap in X executions.” In code and tests, define the count as the number of intervening guard executions before the next cap, so its text and phase are unambiguous.

Two large shop cards show the last executed price, expected purchases and that shop's profit. Next-price controls are visually separate and labeled “Not executed yet.” Beneath each control, all actual 61/62 price positions have a legible allowed/blocked pattern and an accessible text count. Orange/blue marks identify shops; shape, labels and line styles carry the same distinction without relying on color alone.

On cap rounds, a roof/bar graphic shows the common maximum price and says “Both shops can choose any grid price at or below this cap.” The cap replaces the guard for that execution. Do not silently intersect the two restrictions unless a different, separately certified protocol explicitly defines that controller.

On guard rounds, a small arrow connects “B's previous price” to A's allowed choices, and the converse for B. Plain copy explains the local rule: “Keep modeled immediate profit within the allowed loss of the best price against the other shop's previous price.” The advanced drawer can expose the exact grid benchmark, tolerance and allowance. Editing A's present proposal cannot change B's present allowed set.

The single primary button reads **“Execute both prices →”**. Before execution, a preview may show the deterministic model's expected outcomes, clearly labeled preview. That is consistent with joint human control of a known market; there is no claim of sealed independent decisions. A blocked or missing choice disables execution and explains the reason beside the affected control.

## Customer graphics and the benefit buffer

Show expected demand with baskets/customer icons divided between the shops and no purchase. An icon represents a stated number of expected purchases, with fractional or partial icons when appropriate. It is a picture of the public demand formula, not a sample of real people or an empirical demand forecast.

Three distinct metrics remain visible:

- **This round:** customer benefit and both profits from the latest executed pair.
- **Since the first cap:** cumulative customer benefit and its average over the exact executed-round count.
- **The protection promise:** the audited finite-game floor, its numerical scope and the fixed rules to which it applies.

For an audited cap-first prefix guarantee with usable lower floor L, the protected buffer at execution T is cumulative benefit minus T×L. Label it **“Benefit above the protected average”**, with a zero baseline. It is not cash transferred to customers or a budget authorizing real-world harm. One round's contribution can be negative while the cumulative protected buffer stays nonnegative.

If a desired policy target F is also shown, keep a separate target marker and status. Do not use F in the protected-buffer calculation unless it is actually certified for this period. A period can have a valid own floor below the desired target; mark “This period does not certify your selected target,” rather than falsely saying the controller has no certificate. A target already met by the unmodified guard should not imply that recurring caps are necessary.

Numerical comparison follows the actual finite certificate. Rounded visible numbers must not determine pass/fail. Prefer stored reward enclosures and conservative accumulation for the bounded session; if only a binary64 numerical certificate is available, label that scope and apply its declared comparison rule. An apparent inconsistency pauses the claim and offers a local record; it does not trigger an “exploit discovered” victory screen.

## Strategies and the optional fixed benchmark

Offer explanation buttons that fill two choices but never execute them:

- **Highest permitted prices:** “Try the most expensive allowed pair. This is the audited adverse customer-benefit benchmark only where the finite audit establishes that fact; it is not necessarily the best profit strategy.”
- **Best immediate responses:** “Choose each shop's best price against the other's previous public price. This maximizes that local benchmark, not total future profit.” On a cap round, any suggestion must remain within the cap and say what objective it optimizes there.
- **Try an asymmetric pair:** “Give the shops different allowed prices and see how purchases and profits divide.” Do not imply that symmetry or asymmetry has a universal advantage.

A separate **“Watch the fixed benchmark”** mode replays only the audited top-choice path for the selected finite controller, if such a path is certified. It is explicitly a deterministic script. Offer one step and one complete cycle, with no automatic animation by default. If playback is added, provide pause, speed controls and reduced-motion support. Human mode and benchmark mode have separate ledgers and clear labels; the script does not secretly take over a human shop.

An overlay compares outcomes at the same execution count, phase, period and market. Do not describe a stored script as a learned adversary, an LLM, emergent collusion, an equilibrium or a general optimum. No chat, Codex account, external model endpoint or paid API may act as a game player.

## End of a short session

Prefer a few complete cycles with the actual horizon stated, and let the person continue manually. A short default is selected after the approved period set is known. Do not stop a long-period session at an arbitrary round and call its partial cycle the complete-cycle result.

The wrap-up contains the two price traces, cap-round markers, customer benefit and the two profit traces, with a compact ledger beneath. It answers:

1. Which rule and period did you use, and how many actual cap rounds occurred?
2. What were your customer-benefit average, both profits and gap from the matching audited adverse benchmark?
3. What does this finite model establish, and what remains outside its scope?

Cap activation frequency is 1/K over complete cycles. The observed finite-session fraction also depends on its length and start phase; show the actual cap count/T separately. Neither quantity is the fraction of quotes changed: people may voluntarily choose below the cap. Do not claim a correction rate or economic intervention cost without a defined counterfactual and data.

“Try another period” starts a new clearly labeled session. “Save my game” downloads a local record of configuration, evidence hashes, quoted/executed grid indices, phases, rewards and numerical comparisons. No automatic upload or fabricated playtest data is needed. An explicit reset/undo restores both phase and previous public prices and never leaves accumulated rewards from an undone move.

## Finite game and continuous certificate are separate

The main play badge says **“[actual quote count]-price game · [actual finite numerical certificate scope]”**. An optional evidence card says **“Continuous analysis: a separate result.”** It explains that continuous prices and the finite 61/62-choice game remain different objects, even when the exact physical cap price is held fixed. Show continuous findings only once their own prospective recurring-cap protocol and audit pass; the current continuous unchanged-guard audit cannot certify a new recurring intervention.

The pending generalized continuous activation-time corollary concerns a declared physical cap and its stated order/contraction conditions, including its relation to the guard’s fixed point. It does not automatically certify a discretized upper map or the expanded nonuniform price set. The finite audit must check whatever order, tightness and prefix conditions the game uses. If those fail or remain unresolved, retain that outcome and downgrade the display, rather than selecting another favorable case without disclosure.

## A coherent front door: Start → Play → Evidence

The many historical labs now represent different questions and can confuse a newcomer. Add a new landing page first at `/start`; do not delete or silently rewrite an old lab. A later authorized homepage change can make this the front door while preserving the original handover game at an explicit historical route such as `/handover` and retaining its frozen source and downloadable versions.

The new top navigation has three primary destinations:

| Destination | What a newcomer sees |
|---|---|
| **Start** | A one-minute explanation: local profit checks can allow poor customer outcomes; a one-time cap and a recurring cap answer different protection questions. Three illustrated steps and one primary “Play the two-shop challenge” button. |
| **Play** | The new human-controlled finite sparse-cap game, one default market and simple period selection. “Original single-shop game” is a secondary link, accurately described as a different continuous game. |
| **Evidence** | Latest reviewed question, theorem/assumption summary, finite and continuous certificate scopes, reproducibility/downloads and reviewer limitations. Historical study pages are grouped by question rather than presented as equally current results. |

Evidence can group the preserved labs as “Learned behavior” (`/study`), “Worst permitted continuations” (`/stress`), “One real handover cap” (`/activation`), and “Price precision” (`/refinement`). Earlier scripted handover/benchmark pages remain under an “Earlier demonstrations” drawer with their original limitations. The new game is an explanation layer over verified evidence; it is not a replacement for the paper or audit.

A later shared header or banner on old pages would require explicit permission to change those frozen presentation files. Until then, route/landing work alone can provide the new hierarchy. Avoid a new menu containing every old route, or several competing “latest findings” buttons that lead to different generations of the study.

## Data contract and build gate

Before implementation, agree a read-only web export containing the actual evidence identity, finite market/expanded-price-set/cap specification, phase convention, grid price array, allowed guard sets, reward table, permitted periods and per-period certificate. Each period record should distinguish its infinite/complete-cycle floor, whether every cap-first finite prefix is certified, the stored adverse cycle and any finite-horizon benchmark used for scoring. Target comparisons and their margins must be retained, including failures and unresolved values. Continuous records have separate provenance and audit status.

The exporter must verify passed audits and live hashes before emitting playable scientific claims. The UI cannot silently fall back to handcrafted example numbers when evidence is absent. A non-scientific empty tutorial can explain the controls, but it must not impersonate an actual market or carry a protection badge.

A forward protocol should also fix session length, maximum supported period, deterministic reward precision, comparison rules, cap/guard priority, whether histories can be changed, and which conditions certify the activation-prefix guarantee. These are implementation choices with mathematical consequences; resolve them before a playable build, not after a favorable screen recording.

## Verification and usability plan

Once authorized, check actual engine/controller behavior at cap boundaries, K=1, first cap, both lagged firm indices, every legal quote pair, invalid/off-grid input, undo/restart and period changes. Compare stored benchmark replay and cumulative rewards with audited records. Verify all scope downgrades for missing/failed/unresolved certificates and mismatched hashes. A deliberately mutated presentation fixture can test rejection, but is not a scientific result.

Use source/DOM-adapter checks for real module state handling, then actual desktop and narrow rendered-browser checks. Exercise native keyboard price choice, focus order, both shop controls, phase countdown, commit/reveal, exact ledger values, saving and readable 390px/320px layouts. Check motion preferences if playback exists. Record unsupported measurements, direct versus wrapper console observations, and screenshots honestly.

The primary comprehension questions for a later consenting human pilot are: “Who chooses the two prices?”, “Is this round a cap or guard?”, “Is the promise about this round or an average?”, and “Is the continuous certificate the certificate of this game?” Those are prospective checks. No human validation or comprehension success is claimed now.
