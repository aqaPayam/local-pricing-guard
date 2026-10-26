# Refinement Lab presentation verification

Status: presentation files and this QA note frozen after actual-data source/adapter checks and root rendered-browser checks on 26 October 2026. This note is not a human usability study or an independent scientific audit. No frozen science, previous UI, PDF or package was modified by this presentation task.

## Display and scope

New page `/refinement` compares nine saved finite grids and a separate continuous view for each of eight inherited market labels. It retains all five old target labels, their original margins and actual relaxed thresholds. Eight labels include grid variants and economically equivalent cases; they are not eight independent replications.

The page shows the old finite certificate, the new mesh's post-cap worst continuation, the range of start-specific worst values, and the validated continuous enclosure. A range across starting histories is not a confidence interval or a range across all allowed play. The largest grid is not a proof of the limit. Several scalar fixed points can persist on a finite mesh. Short values and chart positions are marked approximate; full validated enclosure strings remain in the evidence drawer. No numerical convergence-error band, exact continuous trajectory, account-backed player, API call or new learning run was created.

The nominal/effective selector changes only the continuous comparison; finite rows retain their saved effective allowance. Each grid's own permanent-cap floor is an optional moving benchmark, visually separate from the fixed old threshold. All-start failure means that a below-target continuation exists from every state; it does not mean every actual play fails. Limiting profits and a unilateral deviation gain do not establish incentive compatibility or joint-profit optimality.

## Evidence export gate

`node research/build-refinement-web.js` reads saved outputs without solving markets. Before writing, it requires both independent audits to pass; binds mesh manifest and index hashes, continuous manifest and results hashes, case hashes and both frozen source/input dependency lists; checks declared record counts and retained target identity. It refuses missing or changed evidence. It does not substitute a presentation check for either scientific audit.

The generated `research/mesh-results/web-data.json` contains 8 market records, 72 mesh cases and 16 continuous records, 393,027 bytes. Initial verified SHA-256: `dadb04261c570353a150b6307d1e8f5e0bcb32d326f05dd217f0b9464e1a6d04`. A second export using `--output .local/refinement-export-check.json` matched byte for byte on this runtime. Hash identity must be refreshed if the exporter or scientific audit receipts change before final freeze.

## Actual-module logic checks

Run from the project root:

```
node .local/refinement-display-smoke.mjs
node .local/refinement-export-smoke.mjs
```

The first runs the actual UI module with a lightweight dependency-free DOM adapter and the actual exported data. All 800 combinations passed: 8 markets × 5 original targets × 10 resolutions × 2 continuous tolerance views. It checks fixed threshold retention, selected finite values, full continuous enclosure text, absence of missing/nonfinite display values, the moving-benchmark toggle, row selection, missing-data handling and rejection of either unaudited evidence set. Deliberately unresolved presentation fixtures, including missing calculation/rounding/assumption fields, remain visible without invented values. Those fixtures are UI branch tests, not additional scientific scenarios.

The second runs the real exporter with a read-only filesystem adapter. Its successful output matches the saved export byte for byte. Six altered-evidence fixtures are rejected: mesh approval, continuous approval, mesh index bytes, continuous results bytes, frozen inherited target-input bytes and mesh-case bytes. Alterations exist only in memory; no frozen file is changed.

These are module/adapter checks. They do not verify rendered layout, browser accessibility, external-link availability or human understanding. Native dropdowns, native buttons, visible focus styles, text alongside graphics and reduced-motion styling are implemented; broad accessibility conformance and actual reduced-motion behavior are unverified.

Local HTTP checks passed for `/refinement`, `/refinement.css`, `/refinement.js`, `/refinement-data.json`, `/refinement-layout` and `/refinement-layout.css`: all returned status 200 with the expected HTML/CSS/JavaScript/JSON MIME. The direct page permits same-origin JSON access and retains self-only scripts/styles in its CSP. These response checks do not demonstrate that a browser rendered or interacted with the page.

## Rendered-browser checks

Root exercised the actual local browser page. The direct desktop page reported 1,265px client width and 1,265px scroll width. Its fixed original anchor threshold, round-trip display `72.119039682514071`, stayed unchanged while the selected view changed from 15 prices to 1,921 prices (post-cap diagnostic approximately `66.298213`) and then Continuum (floor location approximately `66.272044`). The optional own-cap checkbox added the moving comparison markers. Enter activated the focused Continuum row. Nominal/effective selection worked. The base market's 90% target was reported already guaranteed in the continuous comparison; the double-tolerance label's 90% target failed. The scale0.5 market at 1,921 prices retained two scalar fixed points and a start-worst spread approximately `0.017439`.

Root also inspected the actual `/refinement-layout` child pages at 390px and 320px CSS widths, clicked the Continuum row in both, and observed readable charts and text with no visible clipping. Exact numerical child scroll-width measurement was unavailable; there is no exact narrow-overflow claim. These are child CSS viewports, not device emulation or broad device coverage.

The direct page's warning/error log was empty during these checks. The separate wrapper log contained one unsourced `MutationObserver.observe` Node-type error at `23:06:48Z`. Its cause was not identified. Similar unsourced errors were observed in earlier developer wrappers; that does not establish a shared cause or that this error is outside the application. Wrapper interactions and the displayed children remained functional. There is no claim that every browser console was error-free.

Root saved the following actual rendered screenshots; the UI agent opened and visually inspected all three:

- `.local/refinement-v5-desktop.png`: price-interval and finite-grid comparison section, including the moving benchmark.
- `.local/refinement-v5-limit.png`: separate Continuum row and continuous-floor explanation.
- `.local/refinement-v5-narrow.png`: actual 390px and 320px child pages with Continuum selected in both.

No human comprehension study, external human playtest, broad accessibility certification or real-device test is claimed. Reduced-motion styling is present, but an actual system reduced-motion preference was not exercised. The page has no automatic animation or model player.

## Files

New presentation assets: `research/demo/refinement.html`, `refinement.css`, `refinement.js`, `refinement-layout.html`, `refinement-layout.css`. Read-only exporter: `research/build-refinement-web.js`. Portable logic checks: `.local/refinement-display-smoke.mjs` and `.local/refinement-export-smoke.mjs`. Root owns server routes and scientific figure/report work.
