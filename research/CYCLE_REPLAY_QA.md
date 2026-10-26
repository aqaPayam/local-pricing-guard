# Stress Lab display verification

**FROZEN:** presentation source, derived display data and this verification record are closed after the CSP-compatible SVG meter fix and the root's refreshed desktop check. Remaining limitations below are retained explicitly.

The separate `/stress` page displays the frozen coordinated finite-grid audit. It is not an additional research experiment, independent-player game, new training run, or human comprehension study. Existing human-game assets, scientific source files, archived v2 report and v2 package were not changed by this work.

## Display and interaction design

- Three steps explain rule selection, move checks and outcomes. CSS storefronts show both executed prices, expected purchases, customer benefit and each seller's profit. Native SVG charts distinguish entry from repetition and completed moves from saved future previews.
- Market, rule, objective and start are separate controls: eight markets, three rules, two objectives, competitive/high anchors, saved public terminal states, and a clearly distinguished global-envelope start on an optimal loop.
- Every selected witness happens to be a one-state repeating loop. The page calls it a constant pair; repetition is not additional experimental evidence. If the selected pair also belongs to the independently computed finite-grid Nash set, this is explicitly stated.
- Replay earns only destination-state rewards. The starting public price pair earns nothing. “Next 10,” Back, Restart, paused-by-default playback, and a focusable keyboard-control panel are provided; playback stops after 12 additional moves and the display caps at 200 moves.
- Manual coordinator mode knowingly gives one person control of both shops. Only the current permitted grid points are offered; both prices execute together. A manual path does not become an optimized or learned finding. The earlier continuous-price human challenge remains linked separately.
- Guard checks compare immediate profit with the grid best response to the rival's **previous** price. Actual profits are at the simultaneously executed destination pair. Fixed-cap explanation identifies nearest-grid rounding. Acceptance is mechanically assured by choosing permitted actions and is never labeled customer safety.
- Infinite-average objective intervals, numerical gaps, the structural finite-horizon customer-benefit floor, and model assumptions remain separate. Displayed intervals round outward and lower floors round down. Finite learned averages are labeled as a different quantity, with repeated seed/condition observations acknowledged.
- Mobile breakpoints, keyboard focus styles and reduced-motion styling are implemented. This implementation statement is not evidence of a completed browser accessibility audit.

## Completed checks

1. `node --check research/demo/stress.js` passed.
2. `node research/build-cycle-web.js` exported 24 cases and confirmed the saved independent audit is passed. The exporter checks all case hashes against the frozen index, grid structure, connected entry paths, every displayed allowed transition, loop closure, payoff consistency and witness means inside their numerical objective intervals. It does not rerun or replace the independent scientific auditor.
3. Rebuilding to `.local/cycle-web-rebuild.json` produced byte-identical display data. Current display JSON is 4,495,849 bytes; SHA-256 `ca43abccdd7f040dce69a02260e6018fbd80aab9965fc5b7a98ce37fdf7e1e84`.
4. A lightweight DOM-adapter smoke script at `.local/stress-display-smoke.mjs` loaded the real display module and frozen JSON. It exercised all 24 cases / 48 objective cells / 546 displayed start choices, ten moves each (5,460 saved moves), without malformed numeric renderings. The longest displayed entry path is four moves; every displayed loop has length one, so these checks reach repetition for every start. It also checked initial reward exclusion, exact first destination reward, Back to the unexecuted starting state, manual allowed-quote execution, manual reward rendering and manual undo. The adapter verifies display logic; it is **not a browser or layout engine**.
5. Live localhost HTTP checks returned 200 for `/stress`, `/stress.js`, `/stress.css`, and `/cycle-data.json`, with correct HTML, JavaScript, CSS and JSON MIME types. The page retains self-only scripts/styles and same-origin evidence loading. Demand meters use SVG attributes, with no inline styles that conflict with that policy. This checks serving and source compatibility, not rendered interaction.
6. The independent referee read the HTML, display logic and exporter. The scientific labels were accepted, with its requested change from “exact finite grid” to “finite grid · numerical bounds” applied. The referee separately reported that browser access was unavailable.
7. Direct recomputation from frozen reward tables checked all 928 displayed guard shortfall comparisons across entry and closed-loop edges: no displayed selected quote exceeds its stated tolerance.

## Actual browser developer checks

The display subagent and referee initially had empty browser inventories (`apps: []`, `browsers: []`). The root agent subsequently restored its own in-app browser surface and performed these real interactions on the served page. These are developer checks, not human playtesting or evidence of newcomer comprehension.

- Desktop: a 1066 CSS-pixel viewport reported matching document client/scroll widths of 1055 at the inspected initial state. The first high-start guard move executed 1.660 / 1.660 with customer benefit 54.329. The competitive start after ten moves showed customer benefit 72.119 and one permitted price per shop.
- Keyboard: focused replay controls responded to Left/Right stepping and Space Play/Pause; playback was started and paused through keyboard and button controls. Timer interval accuracy was not measured. Manual coordination executed A 1.699 / B 1.660, customer benefit 52.686 and profits 28.325 / 31.241; both local checks passed. Back returned to zero completed moves with blank earned rewards. The root repeated the asymmetric manual execution after the final refresh with the same valid results.
- Narrow layout: actual `/stress` pages loaded in **390px and 320px CSS child viewports**, and Next was clicked in both. The inspected storefronts, outcome metrics and permitted-price cards were readable, with no visible horizontal overflow in the captured stage. These were responsive child viewports, not device emulation. Numeric child-document scroll-width measurement was unsupported, so no numeric mobile overflow assertion is made.
- Both final screenshots, `.local/stress-v3-desktop.png` and `.local/stress-v3-narrow.png`, follow the SVG demand-meter CSP fix. The root overwrote the original desktop capture after a fresh reload. This subagent also opened the supplied images for visual inspection.

Direct page console logs were empty during the root's initial check and again on the fresh final direct-page reload. A separate narrow-layout wrapper reported a MutationObserver error with no source URL; its origin was not established and the Stress Lab source contains no MutationObserver. This wrapper message is not attributed to the application without source evidence.

Downloaded replay file operation, a full accessibility audit, device/browser coverage and rendered reduced-motion behavior have not been verified. The responsive stage checks do not establish human comprehension or comprehensive coverage of every control and chart on every narrow viewport. Scientific certificate validation remains separate from all presentation checks.
