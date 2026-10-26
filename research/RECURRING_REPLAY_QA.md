# Cap & Go and the Market Lab front door: presentation checks

Status: actual-data source/adapter checks passed after all three required independent audits passed and the root authorized the run. Root rendered-browser checks below are complete within their stated scope. Presentation files and this note are now frozen after screenshot inspection. No human validation is claimed.

## Ownership and scope

New front-door assets: `research/demo/overview.html`, `overview.css`, `overview.js`. New human-game assets: `research/demo/recurring.html`, `recurring.css`, `recurring.js`. The root owns `research/recurring-game.js`, numerical engines, frozen scientific outputs, server integration and report. Older labs/routes/reports are preserved.

The front door offers Start -> Play -> Evidence. Its shop graphics and phase example are explicitly schematic, with no fabricated outcome values. Old labs are grouped by question and their historical scopes remain distinct. Navigation works natively; no player or scientific calculation exists in the front-door module.

The playable page delegates permitted sets, all rewards, phase transitions, averages, exact buffers and matching finite-horizon benchmark to the root-owned finite controller. It neither recomputes masks/floors nor uses a model player. Human mode controls both shops knowingly. Scripted highest-permitted-price mode has a separate controller and ledger. The cap replaces the guard on the first actual execution and every declared period thereafter; previous history earns zero reward.

The protection floor is the new finite numerical game's own audited activation-prefix floor. Its exact rational arithmetic concerns saved binary64 reward weights and numerical masks, not exact-real logit formulas. The same physical cap's continuous result has separate provenance. Target comparisons retain original thresholds and margins. Cap activation frequency and observed cap count are not quote-change frequency or a general economic cost.

## Evidence gate and actual-data adapter checks

`research/build-recurring-web.js` is a read-only adapter. It requires all three receipts: finite numerical audit, independent finite rational audit, and continuous recurring-cap audit. It verifies manifest/index/results links, live auditor hashes, frozen source/input hashes, case hashes, cap identity, declared periods and original target identity before writing. Missing or changed evidence must halt the export; no fabricated fallback is allowed. Long continuous orbit/search traces are omitted from the display summary, while the full authoritative results remain bound by their SHA-256.

`.local/recurring-display-smoke.mjs` passed using the actual export, actual UI and root-owned finite controller, with a lightweight DOM adapter. It checked 320 initial target views (8 markets x 8 periods x 5 labels), 2,104 automated invocations of human-mode execution controls and 2,040 explicitly scripted benchmark executions. These are developer tests, not actual human play. Checks covered cap boundaries and K=1, zero initial rewards, matching displayed outcomes, exact engine buffer flags, separate manual/scripted ledgers, asymmetric saved records, undo/restart, blocked choices and unavailable/malformed evidence. The adapter binds the module import to the real portable engine; it does not fabricate an economic engine.

`.local/recurring-export-smoke.mjs` also passed. It produced byte-identical output through the real exporter and rejected nine in-memory evidence alterations: all three approvals, finite index/case, continuous results, inherited targets, finite controller and live auditor. No frozen file was changed. A separate export to `.local/recurring-export-check.json` matched byte for byte. The display file contains 8 markets, 64 finite period certificates and 16 continuous summaries; 3,610,973 bytes, SHA-256 `f2777c1e3f51abdeebd029842083c9e42c80b6ffda5ac28b22b46f1493ad5f01`.

These adapter checks are not browser, layout, accessibility or human-comprehension validation. Actual desktop/narrow browser observations, screenshot paths, unsupported measurements and console limitations are recorded below. No human pilot or playtest result is claimed.


The separate `recurring-layout.html/css` and `overview-layout.html/css` developer wrappers are ready for 390px/320px actual child-page checks. They are not device emulation. Their routes are integrated and the root observations are recorded below.


## Root actual rendered-browser observations (26 October 2026 local date)

Direct Cap & Go and Start pages were inspected in the in-app browser at 1,265 CSS pixels. For both, document scroll width equaled client width 1,265; no horizontal overflow was measured. Both direct pages had empty captured warning/error logs. The reviewed desktop screenshots are .local/recurring-v6-desktop.png and .local/overview-v6-desktop.png. This is developer QA, not a human play sample.

The default is the base market, K=4 and fixed original 95% target. Before any execution, purchases/profits/benefit/averages are absent and cap count is 0/0. The first actual highest-pair cap produced CS 72.119040 and profit 22.020401 per shop, then three guard executions were shown before the next cap. Four highest-pair executions produced finite average 69.116587 and nonnegative zero display buffer, while the last round CS 67.271 was lower. Undo restored three completed executions so the next execution (4) could use a different asymmetric choice, with distinct profits and a higher average. A separate benchmark cycle preserved a distinct scripted ledger; returning to manual mode preserved its different average. K=1 executed a real cap every round. Restart restored zero executions and absent averages.

In the doubled-tolerance market, K=128 explicitly failed the unchanged95% target while keeping its lower own finite floor. A full 128-execution scripted cycle showed average 64.855986, individual last-round 64.753 and nonnegative floor buffer; it did not relabel the original target as protected. No account-backed or model game-player experiment was run: these were deterministic interface checks against already accepted evidence.

Actual child pages were inspected in the 390/320 CSS iframe wrappers. Both native jump links reached price choices. Both widths displayed the full selected quote after controls were stacked to one column. Both then executed the first cap and visibly advanced to execution 2, with 3 guard executions before the next cap, identical checked CS/profits and enabled undo. The screenshots .local/recurring-v6-narrow.png and .local/overview-v6-narrow.png record inspected layouts. The play heading was reduced to 42px at narrow widths. No visible overlap/clipping was found in these inspected portions. Exact child scroll-width measurement is unavailable through the current browser API; no claim of device emulation, exhaustive accessibility, human comprehension or touch usability follows.

The recurring wrapper logged two unsourced MutationObserver.observe TypeErrors during inspection (23:38:22 and 23:39:32 UTC), also seen on earlier script-free developer wrappers. Their origin was not attributed; direct game/Start warning/error logs were empty and both child executions succeeded. The unresolved wrapper-console limitation remains disclosed.


The UI agent opened and visually inspected all four supplied actual screenshots before this presentation freeze. Root also independently exercised the UI. These developer observations do not imply that any external human understood the rules. Saving was checked through a local Blob/download adapter, not an actual browser download; broad accessibility and real-device behavior remain unverified. The final narrow CSS and jump-link observations above supersede the earlier pre-fix layouts.
