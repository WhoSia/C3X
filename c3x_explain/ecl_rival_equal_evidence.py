"""P4 equal-input evaluation contract for official Queen, Cui and CCC rivals.

This DOES NOT run or represent the actual authors' models. The package only
ensures exactly the same source-derived chess facts are offered to every
future comparison arm. Full official model availability is a separate status.
"""
from __future__ import annotations
import hashlib
import json
from typing import Any
import chess

ARMS=("P3_STATIC","P4_TRAINED","QUEEN_ORIGINAL","CUI_STRATEGY","CCC_ORIGINAL")
RUNNABLE={"P3_STATIC":True,"P4_TRAINED":True,
          "QUEEN_ORIGINAL":False,"CUI_STRATEGY":False,"CCC_ORIGINAL":False}

def equal_input(source:dict[str,Any])->dict[str,Any]:
    if source.get("schema")!="c3x-ecl-i10-p4-strong-rival-equal-information-contract-v1":
        raise ValueError("RIVAL_PACKET_SOURCE_SCHEMA_INVALID")
    fen=source.get("fen")
    try:
        board=chess.Board(fen)
        if not board.is_valid():raise ValueError("INVALID_CHESS_FEN")
        played=chess.Move.from_uci(source["played_uci"])
        rival=chess.Move.from_uci(source["original_source_rival"])
        if played==rival or played not in board.legal_moves or rival not in board.legal_moves:
            raise ValueError("NOT_DISTINCT_LEGAL_ROOTS")
    except (TypeError,ValueError,KeyError) as exc:
        raise ValueError("RIVAL_PACKET_BOARD_OR_ROOT_INVALID") from exc
    candidate=source.get("source_rival_rows") or []
    if (len(candidate)!=2 or
        {r.get("uci") for r in candidate}!={played.uci(),rival.uci()} or
        candidate[0].get("rank")!=1 or candidate[1].get("rank")!=2 or
        candidate[0].get("depth") is None or
        candidate[0]["depth"]!=candidate[1].get("depth") or
        any(type(r.get("score_cp")) is not int or r.get("score_bound") for r in candidate)):
        raise ValueError("ROOT_PAIR_SOURCE_NOT_COMPARABLE")
    rows=[]
    for c in candidate:
        x=board.copy(stack=False);sans=[]
        for u in c.get("pv_uci") or []:
            try:m=chess.Move.from_uci(u)
            except ValueError:raise ValueError("BAD_PV_UCI")
            if m not in x.legal_moves:raise ValueError("BAD_PV_SOURCE_LEGALITY")
            sans.append(x.san(m));x.push(m)
        if not sans or c["pv_uci"][0]!=c["uci"]:
            raise ValueError("PV_ROOT_NOT_GROUNDED")
        rows.append({"uci":c["uci"],"san":c["san"],"rank":c["rank"],
                     "depth":c["depth"],"cp":c["score_cp"],
                     "observed_legal_pv_san":sans})
    # Deliberately omit any unverified causal 'source trace' or explanatory
    # pseudo-certificates from the neutral prompt.
    common={"schema":"c3x-ecl-i10-p4-equal-original-PGN-public-source-v1",
           "chess_board_fen":fen,
           "source_game_group":source["source_game_group"],
           "source_ply":source["original_ply"],
           "actual_played_uci":played.uci(),
           "actual_played_san":board.san(played),
           "distinct_source_rival_uci":rival.uci(),
           "source_original_engine":"ORIGINAL_SF16_PINNED_ONLY_AS_VERIFIED_BY_RUN_RECEIPT",
           "restricted_exact_root_candidate_evidence":rows,
           "recorded_evidence_claims":source.get("same_compiled_eligible_claims"),
           "available_source_mechanism_intervention_certificates":[],
           "no_objective_bestmove_proof":True,
           "no_unearned_causal_chess_concept":True,
           "applicability":"CONVENTIONAL_ENGINE_EVIDENCE_ONLY"}
    data=json.dumps(common,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()
    digest=hashlib.sha256(data).hexdigest()
    return {"schema":"c3x-ecl-i10-p4-same-evidence-competitor-registry-v1",
            "common_evidence":common,
            "common_sha256":digest,
            "arms":[
              {"name":arm,"input_sha256":digest,
               "paper_model_executed":False,
               "execution_readiness":(
                 "C3X_PILOT_ROUTER_ONLY" if RUNNABLE[arm] else
                 "REQUIRES_OFFICIAL_MODEL_AND_FAITHFUL_EQUAL_INPUT_ADAPTER"),
               "C3X_source_causal_claim_authorized":False}
              for arm in ARMS],
            "full_search_trace_equal_comparison_admissible":False,
            "reason_full_trace_not_available":"NONE_OF_THE_NATIVE_P4_PILOT_ARTIFACTS_CAPTURED_FULL_INTERNAL_SEARCH_EVENT_TRACE",
            "independent_human_result":None,
            "competitive_result":None}

def freeze_rivals(exports:list[dict[str,Any]])->dict:
    entries=[equal_input(z) for z in exports]
    if not entries:raise ValueError("NO_VALID_STRONG_COMPARISON_CASES")
    return {"schema":"c3x-ecl-i10-p4-equal-evidence-baseline-setup-v1",
            "source_scope":"SAME_SOURCE_FEN_MOVES_PVS_CPU_CP_CLAIMS_NO_CAUSAL_EVENT_TRACE",
            "registrations":entries,
            "original_Queen_run":False,"original_Cui_run":False,"original_CCC_run":False,
            "scientific_C3X_outperformance_of_original_rivals":None}
