# C3X 0.30 R21 — First-hit mask on the h4/Qd2 pair

[Protocol](C3X_030_R21_D1_MAPPED_PAIR_PROTOCOL_20261117.md) · [target freeze](../receipts/C3X_030_R21_D1_FIRST_HIT_20261117.json).

At round 1.2 from the shared question family, the mask changed the first nominated main-search probe from hit to miss in both fresh-process repeats. In both arms the same scoped child returned −59 in qsearch with adjusted depth −1, `ttMove=0`, and the qsearch hit field set to 1. This value backed up to +59 at the h4 root event inside the [49, 69] window. Both arms selected h4, used 24,010 nodes, and ended with a depth-10 upper bound of +27 cp. The entire normalized public search stream matched across arms. The only stderr differences between the two arms are the one mask message and the changed probe hit flag.

R20's Italian case shows one-hit sensitivity reaching an early root value. R21 supplies a same-method negative case on a budget-stable candidate pair. The sham's hit carries no local TT move, and both arms follow the same recorded qsearch route. These observations narrow the question of when the TT hit signal matters. They do not adjudicate the meaning of other TT hits, and they do not explain the independent conditional ranking difference after Ne7 and Qc7.
