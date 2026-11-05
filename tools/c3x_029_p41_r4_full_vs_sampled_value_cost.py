"""P41: archive-measured full-reply vs sampled chess-value adjudication cost.

No new engine run. Figures are estimated requested native node budgets and
MUST NOT be mistaken for actual consumed nodes or accurate chess-value labels.
"""
from __future__ import annotations
import hashlib, json
from pathlib import Path

ORIGINAL_SHA="84f037f62b86a7ee34239921f609a9015a6ea8d4cdf351f41563ef78dc6dabcf"

def read_source(path):
    b=Path(path).read_bytes()
    if hashlib.sha256(b).hexdigest()!=ORIGINAL_SHA:
        raise ValueError("HOLD_ARCHIVAL_SOURCE_SHA")
    return json.loads(b)

def estimate(data,reference_nodes=96000,k_opp=3,k_own=3):
    assert data["game_events"]==8 and data["candidate_worlds"]==16
    assert reference_nodes>0 and k_opp>0 and k_own>0
    worlds=[w for c in data["cases"] for w in c["worlds"]]
    assert len(worlds)==16
    n_opp=sum(len(w["branches"]) for w in worlds)
    n_own=sum(b["own_legal_reply_count"] for w in worlds for b in w["branches"])
    expansions=sum(w["expanded_legal_moves"] for w in worlds)
    assert expansions==16+n_opp+n_own
    sample_opp=sum(min(k_opp,len(w["branches"])) for w in worlds)
    sample_own=sum(min(k_own,b["own_legal_reply_count"])
                   for w in worlds
                   for b in sorted(w["branches"],key=lambda x:x["opponent_reply"])[:k_opp])
    assert sample_own>0
    return {"status":"P41_ARCHIVAL_FEASIBILITY_NOT_CHESS_VALUE_RESULT",
       "source_games":8,"candidate_worlds":16,
       "observed_legal_opponent_replies":n_opp,
       "observed_legal_own_followups":n_own,
       "observed_legal_expansions":expansions,
       "sampled_opponent_branches":sample_opp,
       "sampled_own_followups":sample_own,
       "hypothetical_nodes_per_leaf":reference_nodes,
       "hypothetical_full_leaf_requested_nodes":n_own*reference_nodes,
       "hypothetical_sampled_leaf_requested_nodes":sample_own*reference_nodes,
       "ratio_full_over_sampled_legal_leaves":n_own/sample_own,
       "limits":["not a native engine measurement",
                 "lexicographically selected k branches are not engine ranked",
                 "sampled branches cannot establish universal all-response low regret",
                 "exposed historical eight games, not independent heldout"]}
