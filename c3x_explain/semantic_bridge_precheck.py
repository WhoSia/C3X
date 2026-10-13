"""I10-P4 high/low semantic bridge: independent BOARD PROXY PRECHECK ONLY.

Not source causal science! Reads immutable historical Ethereal P16 reference
and checks whether concept candidate board proxies are separable under
previously recorded edits. A genuine prospective C++ engine event intervention
with fresh independent labels, non-aliased SHAM and negative controls is required
before any source-to-human-chess semantic causal claim may be admitted.
"""
from __future__ import annotations
import hashlib,json
import chess

ORIGINAL_BLOB_SHA1="53765418975095ec5981da35464859e01f030902"
CONCEPT_PROBES=("moving_side_center_attacks","moving_side_king_ring_pressure","moving_side_legal_move_count")

def board_proxy(fen:str)->dict[str,int]:
    board=chess.Board(fen)
    if not board.is_valid():
        raise ValueError("SEMANTIC_BOARD_INVALID")
    own=board.turn
    rival_king=board.king(not own)
    if rival_king is None:
        raise ValueError("MISSING_RIVAL_KING")
    center=[chess.D4,chess.E4,chess.D5,chess.E5]
    king_ring=[rival_king]+list(board.attacks(rival_king))
    return {
        "moving_side_center_attacks":sum(board.is_attacked_by(own,sq) for sq in center),
        "moving_side_king_ring_pressure":sum(board.is_attacked_by(own,sq) for sq in king_ring),
        "moving_side_legal_move_count":board.legal_moves.count(),
    }

def certify_source_identity(raw:bytes)->dict:
    digest=hashlib.sha1(b"blob "+str(len(raw)).encode()+b"\0"+raw).hexdigest()
    if digest!=ORIGINAL_BLOB_SHA1:
        raise ValueError("HISTORICAL_ETHEREAL_SOURCE_BLOB_IDENTITY_MISMATCH")
    cert=json.loads(raw)
    if cert.get("engine")!="ethereal" or cert.get("replication_status")!="LOCAL_ONLY":
        raise ValueError("SOURCE_ENGINE_OR_LOCAL_SCOPE_MISMATCH")
    if cert.get("certificate_id")!="398eca8d6adf00525e6d5bf7":
        raise ValueError("WRONG_CERTIFICATE_ID")
    if cert.get("concept_label") is not None:
        raise ValueError("ORIGINAL_HAS_UNREVIEWED_CONCEPT_LABEL")
    return cert

def audit_original_historical(raw:bytes)->dict:
    c=certify_source_identity(raw)
    worlds=c["counterfactual_boards"]
    cells=c["decision_cells"]
    if set(worlds)!={"B0","TARGET","SUBSET","SHAM"}:
        raise ValueError("WORLD_SET_CHANGED")
    if set(cells)!=set(worlds):
        raise ValueError("SOURCE_CELL_WORLD_MISMATCH")
    fp={k:board_proxy(v["fen"]) for k,v in worlds.items()}
    for k,v in worlds.items():
        b=chess.Board(v["fen"])
        if not b.is_valid():
            raise ValueError("INVALID_REPLAY_BOARD")
        for move in (c["pair"]["A"]["uci"],c["pair"]["B"]["uci"]):
            if chess.Move.from_uci(move) not in b.legal_moves:
                raise ValueError("RIVAL_NOT_LEGAL_IN_ALL_WORLDS")
    original=fp["B0"]
    deltas={w:{f:fp[w][f]-original[f] for f in CONCEPT_PROBES} for w in fp if w!="B0"}
    source_events={w:cells[w]["bounds"]["LOWER"]["state"] for w in cells}
    sham_alias=worlds["SHAM"]["fen"]==worlds["SUBSET"]["fen"]
    candidates=[
        {"metric":feature,"B0":original[feature],
         "TARGET_delta":deltas["TARGET"][feature],
         "SUBSET_delta":deltas["SUBSET"][feature],
         "SHAM_delta":deltas["SHAM"][feature],
         "can_distinguish_target_from_subset_in_observed_board_proxy":
              fp["TARGET"][feature]!=fp["SUBSET"][feature]}
        for feature in CONCEPT_PROBES
    ]
    return {
      "schema":"c3x-ecl-i10-p4-historical-Ethereal-semantic-precheck-v1",
      "historical_original_git_blob_sha1":ORIGINAL_BLOB_SHA1,
      "engine":"ethereal","certificate_id":c["certificate_id"],
      "engine_source_execution_new":False,
      "historical_source_event_cells":source_events,
      "board_proxy_features":fp,"deltas_vs_B0":deltas,
      "candidate_board_proxies":candidates,
      "sham_aliases_subset_exact_board":sham_alias,
      "independent_sham_adequacy":"FAIL_ALIASED_BOARD" if sham_alias else "NOT_EVALUATED",
      "concept_label_in_original":None,
      "new_semantic_causal_certificate":None,
      "causal_semantic_claim_authorized":False,
      "concept_to_source_event_causation":"NOT_IDENTIFIED",
      "relation_to_prior_science":"DIAGNOSTIC_ONLY_UNDER_ORIGINAL_G95_P16_LOCAL_CEILING",
      "required_prospective_tests":[
        "Independent non-aliased SHAM board edit with matching edit feasibility",
        "New source-original event interventions on a preregistered distinct board set",
        "Control for legal rival move set, engine version, history, evaluation depth, seed and budget",
        "Compute causal impact of targeted original search event, not mere between-board event association",
        "Blind/independent human chess concept annotations",
        "Game/event-disjoint new board identities, confound and multiplicity analysis",
        "Negative-control synthetic concept labels and search events",
        "Causal abstraction intervention-commutation and matched rival concept effects"
      ],
    }
