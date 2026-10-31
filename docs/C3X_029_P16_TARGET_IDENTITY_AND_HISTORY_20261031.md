# P16 — Fixed identity of a comparative chess claim
Scientific question: is the model being rewarded for the SAME explanatory claim after changes to legal response scope, chess history or continuation horizon?
An explanation's contrastive target is a tuple of source game, complete state/history digest, candidate set, chess property, legal opponent response scope, horizon and ruleset. Plain 'b1b4 is better' cannot identify the estimand.
P16 canonical SHA-256 fingerprint is an **identity key for declared metadata**, not a raw chess source checksum; the fields may be forged or unverified. Tests enforce that changing horizon or capture-only vs all-legal changes identity, while candidate order is invariant.
This fixes the methodological ambiguity of P11 string claim_identity under caller control; adoption into actual chess evaluation requires source legal replay and reference attachment. No native run.
