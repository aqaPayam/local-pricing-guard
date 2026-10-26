# What this comparison means

Two shops learn to set prices to increase their own profit. Customers can buy
from either shop or buy nothing. We calculate customer benefit from the same
fixed market model in both versions.

Both versions begin with one real price cap. After that, one version keeps a
guard that limits which prices each shop may choose. The other permits every
price on the original game board. Both shops receive the same learning time,
memory size and paired random streams. We repeat the comparison for twelve
fixed seeds, including any result that goes against our expectations.

The question is whether the guard changes what these learners do under this
budget. We are not assuming that high prices prove collusion, or that a guard
that works in this game will work in every market.

When you open the replay, the shops have already finished learning. One click
runs one more market round using their saved policies. The prices shown at the
start are remembered history; they have not earned new money or customer
benefit. Undo and restart return to that same saved situation. They do not
train the shops again or insert another starting cap.

The replay shows what you have executed so far. The eventual-cycle result
describes the complete repeating pattern reached by the frozen shops. The
training-window result describes their last period of learning, when they
still explored. These can differ without a calculation error.

Static benchmark prices add context. A pure Nash pair is a simultaneous price
pair at which neither shop can improve its one-round profit by changing alone.
A joint-profit maximum is a pair giving the shops the largest total one-round
profit on this board. We retain every tied pair and explicitly say if no pure
Nash pair exists. These benchmarks do not certify an equilibrium of the
learned, history-dependent policies.

The results page must show all twelve comparisons, explain its difference
direction, and keep missing results visible. A positive customer-benefit
difference means the full-grid version benefited customers more; a negative
one means the guarded version did. Neither direction is selected in advance
as the answer we want.
