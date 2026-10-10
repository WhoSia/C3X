#!/usr/bin/env python3
"""Posthoc development root-candidate verdict on previously frozen C3b source.
No new source targets, no M3 model validation.
"""
import argparse,json,hashlib
from pathlib import Path
import chess
from c3x_022_P2_two_stage_exact_move_scout import stockfish16_encoded_move
from c3x_023_P1_R1_licensed32_TT_FIRST_native_common_SEE_node_court import SOURCE_SHA,STAGEA_SHA,frozen
from c3x_023_P1_R2_T3_strict_SEE_TT_two_by_two_source_court import T2_JSON_SHA
from c3x_024_P2_R2_actual_ancestor_root_survival_court import audit

def summarize(raw,source):
    assert raw["source_games"]==2 and raw["arm_worlds"]==8
    cases=[];tally={}
    for c in raw["cases"]:
        gid=c["game_id"]
        src=source["per_ecology"]["may2026_broadcast"]["selected"][gid-1]
        fen=src["fen4"]
        board=chess.Board(fen+" 0 1")
        if not board.is_valid():raise ValueError("INVALID_FROZEN_MAY_SOURCE_ROOT")
        native={stockfish16_encoded_move(board,m):m.uci() for m in board.legal_moves}
        per={}
        for label,cell in c["arms"].items():
            status=cell["C3b"]["status"]
            events=cell["C3b"].get("source_events",[])
            result=cell["final_UCI"]["bestmove"]
            if status=="C2_ACTUAL_CONTINUE":
                verdict="EXACT_SEE_GUARD_CONTINUE_CONTROL"
                candidate=None
            else:
                if not events or "root_move" not in events[0]:
                    candidate=None;verdict="NO_ROOT_CANDIDATE_NATIVE_OBSERVATION_HOLD"
                else:
                    candidate=native.get(events[0]["root_move"])
                    if candidate is None:
                        verdict="ROOT_CANDIDATE_LEGAL_MAPPING_HOLD"
                    elif status=="C3B_FULL_ANCESTOR_TO_ROOT_CANDIDATE_EXECUTED":
                        verdict=("SOURCE_ROOT_CANDIDATE_REACHED_AND_FINAL_BESTMOVE"
                                 if candidate==result else
                                 "SOURCE_ROOT_CANDIDATE_REACHED_BUT_NOT_FINAL_BESTMOVE")
                    else:
                        verdict="C3B_PARTIAL_NO_FULL_ROOT_CANDIDATE_CERTIFICATE"
            footprint=[{"event":e["event"],"ply":e["ply"]} for e in events]
            row={"C3b_status":status,"root_candidate_UCI":candidate,
                 "final_bestmove_UCI":result,
                 "root_candidate_equals_final":candidate==result if candidate else None,
                 "survival_verdict":verdict,
                 "bounded_source_event_footprint":footprint if
                    status=="C3B_PARTIAL_CENSORED_OR_PATH_DIVERGED" else [],
                 "C3a":cell["C3a"]}
            tally[verdict]=tally.get(verdict,0)+1
            per[label]=row
        cases.append({"game_id":gid,"source_site":c["source_site"],
                      "root_order":c["root_order"],"role":c["role"],
                      "arms":per})
    return {"schema":"c3x024-P2-R3-posthoc-source-root-candidate-survival-v1",
            "source_games":2,"arm_worlds":8,"cold_runs":16,
            "posthoc_development_only":True,"survival_counts":tally,
            "cases":cases,"no_natural_mediation_claim":True,
            "no_original_fen_pgn_headers":True}
def main():
    p=argparse.ArgumentParser()
    for k in ("source","stagea","presealed","source-targets","engine","t3-receipt","out"):
        p.add_argument("--"+k,required=True)
    a=p.parse_args()
    src=frozen(a.source,SOURCE_SHA)
    full=audit(src,frozen(a.stagea,STAGEA_SHA),
               json.loads(Path(a.presealed).read_text()),
               frozen(a.source_targets,T2_JSON_SHA),a.engine,
               json.loads(Path(a.t3_receipt).read_text()))
    assert (full["full_ancestor_root_arms"],full["partial_or_diverged_arms"],
            full["actual_continue_arms"])==(2,2,4),"HISTORIC_C3B_CLASS_CHANGED"
    result=summarize(full,src)
    o=Path(a.out);o.parent.mkdir(parents=True,exist_ok=True)
    o.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("C3X024_P2_R3_POSTHOC_ROOT_SURVIVAL_COUNTS",result["survival_counts"],flush=True)
    print("C3X024_P2_R3_POSTHOC_PARTIAL_DIAGNOSTIC",
          {str(c["game_id"]):{k:v["bounded_source_event_footprint"]
                              for k,v in c["arms"].items()
                              if v["bounded_source_event_footprint"]}
           for c in result["cases"]},flush=True)
    print("C3X024_P2_R3_NATIVE_FULL_PRIVATE_SHA256",
          hashlib.sha256(o.read_bytes()).hexdigest(),flush=True)
if __name__=="__main__":main()
