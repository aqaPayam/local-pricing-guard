# First-visit usability review

Source-only review, 26 October 2026, of `demo/overview.html`,
`demo/reference.html`, `demo/reference.js` and `REFERENCE_PLAIN_LANGUAGE.md`.
No actual outcomes, Q or computed anchors were opened. No device, browser
rendering or person was tested. These are three bounded recommendations for a
new delivery version; they do not authorize changing frozen prior UI or science.

1. **Say what the visitor controls before offering destinations.** The Start
   page currently presents several challenges and comparisons together; the
   reference page says "Watch both saved worlds" but its main action says "Run
   one round." A newcomer may expect to choose prices there. Use two clear
   entry choices on the new landing surface: **"Play: choose the prices"** and
   **"Watch: compare shops that already learned."** Under the second, say:
   "You control the playback. The saved shops choose their prices." Keep the
   two-shop versus one-shop choice inside the Play path, with a short statement
   of whether the person controls both shops or faces a saved rival. This makes
   manual play and frozen replay distinct without adding technical explanation.

2. **Introduce the cap and guard through the two panels before the clock.**
   The first reference explanation foregrounds "full original price grid,"
   allocated memory and clock labels. Those are controls for researchers, but
   they do not yet explain the visitor's question. Put this short introduction
   above the replay: "Both versions began with one price ceiling. Afterwards,
   the left shops kept a rule restricting their choices; the right shops could
   choose any price on the same board. Watch what this changes for customers."
   Keep the existing guard definition available in a nearby "What does the
   guard allow?" disclosure, since it is a profit-based rule, not a second price
   ceiling. Label the panels **"Guard stays on"** and **"Guard removed after
   the first cap."** Move memory/clock details into the existing evidence
   disclosure. The explanation must still say this replay starts after learning
   and does not execute a new initial cap.

3. **Make one playback action and its result unmistakable.** Keep the existing
   desktop controls and mobile replay bar, using the same primary label:
   **"Watch both: 1 round."** Use **"Undo 1 round"** and **"Start replay again"**;
   leave the twenty-round action secondary. Show the first-click instruction
   beside the button: "Click once, then compare customer benefit below." Rename
   the three benefit readouts **"This round," "Average since you started,"** and
   **"Average over the complete repeating pattern."** Explain customer benefit
   once in ordinary language as the modeled value customers receive beyond
   what they pay. Beside the difference, say **"Positive: removing the guard
   helped customers. Negative: keeping the guard helped customers."** Keep all
   twelve rows, missing states and signs. The selector can display "Example 1
   of 12" while retaining the seed ID in smaller provenance text. The fixed
   first example and scientific comparisons must remain unchanged.

The existing mobile bar, undo/restart behavior, no-new-earnings initial state,
separate training disclosure and visible limitations are useful foundations.
These recommendations change the order and wording of the introduction and
actions, rather than adding a tutorial or another game. `REFERENCE_PLAIN_LANGUAGE.md`
already contains the needed explanations; bring its short role and replay
sentences into the first interaction. A later browser check can verify that the
primary action and both panels are usable at narrow widths. It would not, by
itself, establish human comprehension or a human-data result.
