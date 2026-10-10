#!/usr/bin/env python3
"""Engine-free chess move transition census for 0.22 April16, before native search."""
import argparse
import hashlib
import json
from pathlib import Path
import chess
from c3x_021_P1_atomic_decision_transition_graph import profile

APRIL_SHA="0e5516fc0cd49203bf7cc366f4133d6c9b20a2f21de0667468f121e398d2fa93"

def build(source):
    selected=source["selected"]
    if (source["phase"]!="SOURCE_ONLY_BEFORE_APRIL_NATIVE_OUTCOMES"
        or len(selected)!=16 or [x["id"] for x in selected]!=list(range(1,17))):
        raise ValueError("BAD_APRIL_SOURCE_PRENATIVE_DENOMINATOR")
    if len({r["fen4"] for r in selected})!=16:
        raise ValueError("DUPLICATE_APRIL_FEN4")
    positions=[]
    for row in selected:
        board=chess.Board(row["fen4"]+" 0 1")
        p=profile(board)
        if p["legal_root_move_count"]!=row["source_root_legal_count"]:
            raise ValueError("APRIL_LEGAL_ROOT_CENSUS_DRIFT")
        if row["played_legal_move_uci"] not in {m["move"] for m in p["moves"]}:
            raise ValueError("APRIL_SELECTED_PLAYED_MOVE_ILLEGAL")
        positions.append({"id":row["id"],
                          "game_sha256":row["source_game_sha256"],
                          "played":row["played_legal_move_uci"],
                          "profile":p})
    return {
        "schema":"c3x022-P0-april16-source-only-all-legal-root-decision-primitives-v1",
        "phase":"SOURCE_ONLY_COMPLETE_BEFORE_NATIVE_EXAMINATION",
        "april_source_sha256":APRIL_SHA,
        "chess_standard_not_atomic_variant":True,
        "all_source_games":len(positions),
        "all_legal_root_moves":sum(len(x["profile"]["moves"]) for x in positions),
        "positions":positions,
        "usage":"Join only by SHA-frozen game ID and legal chess UCI move after native observation; never infer engine causal valuation from geometry."
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--april",required=True)
    p.add_argument("--out",required=True)
    args=p.parse_args()
    raw=Path(args.april).read_bytes()
    if hashlib.sha256(raw).hexdigest()!=APRIL_SHA:
        raise ValueError("APRIL_ENGINEBLIND_SOURCE_SHA_CHANGED")
    report=build(json.loads(raw))
    out=Path(args.out);out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(report,sort_keys=True,indent=2,ensure_ascii=False)+"\n")
    print("C3X022_APRIL16_ALL_LEGAL_CHESS_PRIMITIVES_SEALED",
          report["all_source_games"],report["all_legal_root_moves"],
          hashlib.sha256(out.read_bytes()).hexdigest(),flush=True)
if __name__=="__main__":main()
