# Activation Lab verification

**FROZEN:** source, deterministic display data, display-logic checks, root actual browser observations and this presentation verification record are closed. Remaining limitations below are retained explicitly. This is the separate `/activation` page. It does not change the earlier game, Stress Lab, guard, market, checkpoints, target protocol or frozen scientific results.

## What the interface presents

The three-stage diagram distinguishes inherited public history, one **actual capped execution**, and all later executions under the original guard. Rewards are earned at newly executed prices; the old public pair earns no extra reward. The cap's possible outcomes are independent of that old history.

All eight markets and five predeclared target labels remain selectable, including numerically duplicate labels. The requested value F, numerical allowance δ, and actual threshold F−δ are separate and available at full double precision. Approximate headline values are identified as approximate. Certificate intervals round outward and lower guaranteed floors round down.

The price-pair heatmap colors every guard state as certified safe, admitting a below-target tail, or numerically unresolved. The full selected common-prefix rectangle is outlined. The certificate covers **every pair** in that rectangle, while the chosen pair and replay are explicitly illustrations. The largest cap is optimal only among the tested symmetric common-prefix caps; no arbitrary-controller optimality is claimed.

First-execution customer surplus and both individual/joint profits are displayed as full ranges over all cap outcomes. There is no fabricated distribution or typical outcome. Per-pair execution values are separately labeled. The saved guard entry path and repeating pair/cycle use the already audited destination rewards and permitted transitions.

All-state impossibility is separated from an empty numerical safe set with possible ambiguity. A witnessed lower continuation does not mean every actual play is bad. Already-safe targets are labeled as already meeting the target, so they are not counted as a repair. Long-run numerical certificates are explicitly distinguished from per-round and target-specific finite-horizon guarantees. No independent learning, stable collusion, continuous-price result or human validation is inferred.

## Completed reproducible checks

- `node --check research/demo/activation.js` and `node --check research/build-handover-web.js` pass.
- `node research/build-handover-web.js` exports the real eight markets / 40 labels. It checks inherited frozen hashes, target arithmetic, initializer rectangles, all 2,432 displayed state tails and 8,071 entry/loop transitions, plus their witness means. This presentation check does not replace the independent scientific auditor.
- Rebuilding with `node research/build-handover-web.js --output .local/handover-web-rebuild.json` produced byte-identical data. JSON: 1,387,061 bytes; SHA-256 `9d2077fb501a1030fe1e3aefe8ba07895408fd4830a55ef2a5442eeb7c73947b`.
- The dependency-free, portable smoke harness `.local/handover-display-smoke.mjs` loads the actual module and actual display JSON with a lightweight DOM adapter. It passes all 40 target labels, 69 available initializer supports, 138 corner-pair illustrations and 1,518 executions. It checks cap-before-guard timing, initial reward exclusion, actual destination rewards, arrival at saved constant guard tails, asymmetric firm-index labels, undo, focused-panel keyboard handlers, outside-rectangle rejection, legal map selection and missing-data handling. It is **not a browser or layout engine**. Command: `node .local/handover-display-smoke.mjs` from the extracted project root.
- The independent referee read the actual exporter, HTML and display logic and reported no scientific source blocker, including the scope/rounding/timing distinctions above.
- Actual localhost HTTP checks returned 200 and the correct MIME type for `/activation`, `/activation.js`, `/activation.css`, and `/handover-data.json`. The page has self-only scripts/styles and same-origin evidence loading. There are no inline styles or event handlers requiring a weaker policy. This is a serving/source check, not a rendered-browser claim.

## Browser developer verification

The display subagent's browser inventory remained unavailable. The root agent used its restored actual browser surface and reported the following served-page checks; these observations are separate from the DOM adapter:

- Default base/near-Nash target: old-history consumer surplus and profits were blank. One cap execution followed by ten guard moves showed “1 capped execution + 10 guard moves,” prices 1.466 / 1.466, customer benefit 72.12 and profits 22.02 / 22.02. The local checks explicitly referenced the previous rival price.
- Asymmetric illustrative indices A=0/B=1: the first capped execution showed customer benefit 74.02 and profits 21.85 / 20.41. Keyboard Right moved to 1.466 / 1.466 under the guard, with A having one permitted quote and B two, matching the asymmetric previous-rival indices. Keyboard Left twice returned to zero executions and blank rewards.
- Base 31-price market / 95% target / largest certified cap: five initial prices per shop and 25 possible pairs; ceiling 1.500; 25 safe grid states and 936 states admitting lower continuations; displayed whole-rectangle interval 68.960916–68.960917.
- Demand scale 0.5 / 100% target: largest certified prefix unavailable; all 225 states admit below-target continuations, and all four possible outcomes of the existing cap admit such continuations. The UI presented the all-state impossibility with the explicit worst-case scope.

The root then completed actual layout checks:

- The direct desktop page reported matching client/scroll widths of 1265 / 1265 at the inspected state.
- The separate script-free wrapper `research/demo/activation-layout.html` and `activation-layout.css` embedded actual `/activation` documents in 390px and 320px CSS child viewports. The root inspected the real maps, certificate text and shop graphics and successfully clicked the cap-execution button in both narrow documents. No horizontal clipping was visible in the inspected views. Exact child scroll-width measurement was unavailable, so this is not a numeric mobile-overflow assertion or device emulation.
- Final screenshots are `.local/activation-v4-desktop.png`, `.local/activation-v4-narrow-controls.png` and `.local/activation-v4-narrow-map.png`. This subagent opened and visually inspected all three supplied images; the narrow map shows the selected four-cell rectangle and the controls show the completed one-round cap execution.
- Direct `/activation` warning/error logs were empty. The narrow wrapper log contained one unsourced `MutationObserver.observe` Node TypeError at 22:45:27 UTC. Its origin is unresolved; neither the new page nor script-free wrapper contains MutationObserver source. This wrapper error is retained as a limitation and is not silently reclassified as an application error or dismissed as harmless. The observed page interactions remained functional.

The interface intentionally has manual stepping only; there is no autoplay interval to validate. These are developer logic/browser checks, not a human usability or comprehension study. A broad assistive-technology audit, rendered reduced-motion checks and wider device/browser coverage have not been performed.
