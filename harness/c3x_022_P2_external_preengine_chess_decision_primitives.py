#!/usr/bin/env python3
"""Freeze ALL standard-chess legal root decision primitives BEFORE any native O/F scout."""
import argparse,hashlib,json
from pathlib import Path
import chess
from c3x_021_P1_atomic_decision_transition_graph import profile

SOURCE_SHA="ebe6648f43f64c6f31e0d547845bec3d87c663093fd68298acf2ebe4c0287554"
ECOLOGIES=("twic","lichess_puzzles")

def prepare(source):
    if source.get("phase")!="ENGINE_BLIND_SOURCE_FREEZE_NO_TT_FORECAST_OUTCOME":
        raise ValueError("P2_SOURCE_PHASE_NOT_BLIND")
    if source.get("selected_count")!=32:
        raise ValueError("P2_SOURCE_NOT_32")
    result={"schema":"c3x022-P2-pre-native-TWIC-puzzle-standard-chess-all-legal-primitives-v1",
            "source_sha256":SOURCE_SHA,
            "phase":"ALL_LEGAL_BOARD_TRANSITIONS_FROZEN_BEFORE_NATIVE_O_F",
            "ecologies":{}}
    seen=set()
    for eco in ECOLOGIES:
        rows=source["ecologies"][eco]["selected"]
        if len(rows)!=16 or [x["id"] for x in rows]!=list(range(1,17)):
            raise ValueError("P2_ECOLOGY_DENOMINATOR")
        out=[]
        for row in rows:
            fen=row["fen4"]
            if fen in seen:
                raise ValueError("P2_CROSS_ECOLOGY_FEN_COLLISION")
            seen.add(fen)
            b=chess.Board(fen+" "+str(row["source_halfmove_clock"])+" "+str(row["source_fullmove_number"]))
            m=profile(b)
            if m["legal_root_move_count"]!=row["source_root_legal_count"]:
                raise ValueError("P2_LEGAL_CHESS_ROOT_COUNT_DRIFT")
            if row["played_legal_move_uci"] not in {x["move"] for x in m["moves"]}:
                raise ValueError("P2_SOURCE_PLAYED_OR_PUZZLE_MOVE_NOT_LEGAL")
            out.append({"id":row["id"],"source_game_sha256":row["source_game_sha256"],
                        "profile":m})
        result["ecologies"][eco]={"selected":out,"all_legal_root_moves":sum(len(r["profile"]["moves"]) for r in out)}
    result["summary"]={"source_positions":32,
                       "all_legal_chess_root_actions":sum(x["all_legal_root_moves"] for x in result["ecologies"].values()),
                       "worlds_never_engine_evaluated":True,
                       "no_source_label_treated_as_native_score":True}
    return result

def main():
    p=argparse.ArgumentParser()
    for field in ("source","out"):p.add_argument("--"+field,required=True)
    args=p.parse_args()
    raw=Path(args.source).read_bytes()
    if hashlib.sha256(raw).hexdigest()!=SOURCE_SHA:raise ValueError("P2_NEW_SOURCE_SHA_DRIFT")
    report=prepare(json.loads(raw))
    out=Path(args.out);out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(report,sort_keys=True,indent=2,ensure_ascii=False)+"\n")
    print("C3X022_P2_TWO_ECOLOGIES_ALL_LEGAL_ACTIONS_SEALED",
          report["summary"],hashlib.sha256(out.read_bytes()).hexdigest(),flush=True)
if __name__=="__main__":main()
