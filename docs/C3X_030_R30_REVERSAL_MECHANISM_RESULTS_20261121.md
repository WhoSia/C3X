# C3X 0.30 R30 — Why the same scout return can precede a different root choice

The new rule nominated a move hint for both exposed R29 depth-reversal
fixtures. In R29-020, the first reply changed but the child returned
−107 in both arms. In R29-031, probe 233 was within the scout of Kg7
in attempt 14. The full hint mask leaves the first reply Bc6 and
the scout return 1947 intact. The next cast of the search is the
full-window PV re-search. The verified child-to-root links are:

| Arm | Scout | Later PV child return | Kg7 root value vs active alpha −1951 | Final root recommendation |
| --- | ---: | ---: | ---: | --- |
| Sham | 1947 | 1934 | −1934, takes lead | g5 |
| Main picker argument only | 1947 | 1934 | −1934, takes lead | g5 |
| Singular verification only | 1947 | 1957 | −1957, does not take lead | g5 |
| Picker argument and singular verification | 1947 | 1957 | −1957, does not take lead | g5 |
| Entire effective hint | 1947 | 1952 | −1952, does not take lead | Rb2 |
| Restore | 1947 | 1934 | −1934, takes lead | g5 |

The joint arm was added after observing the separated arms and then
specified before running. The window bounds above are native values,
not exact centipawn comparisons between g5 and Rb2. Disabling
singular verification suffices to change whether Kg7 takes the lead
in the same attempt. That route, even alongside the main picker,
does not reproduce the final recommendation change caused by masking
the whole hint. Under the whole hint mask, the next PV probe saw
stored depth 10; the other arms saw 12. This is an observed difference
after treatment. It does not identify the causal contribution of
the depth field. The whole hint also participates in reduction and
other engine logic.

The follow-up experiment should trace writes between the scout and
PV re-search, then selectively intervene on the recorded value,
depth or bound at the PV consumer with entry identity controls.
This complements the new-cohort coverage test. For the human study,
a same-text plus public iteration panel is an informative additional
comparison before attributing an effect to access to native evidence.
The current experiment contains no participant outcomes.

Six arms including restore, and the original executable were checked
against the frozen probe signature and public output. A fresh
replay of the final experiment reproduced its result bytes,
SHA-256 `58ddc61bec7c03636cb2a1f5fef8c61f2a5e473e0189706ba3fed3349220a6e2`.
[Native and source logs](https://drive.google.com/file/d/1LTpp63sSAYx6Euw09LxyLJ6TsljQPcIN/view).
