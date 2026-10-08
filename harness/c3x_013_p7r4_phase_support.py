#!/usr/bin/env python3
"""Exploratory P7-R4 phase-dependent pair support; same 32 frozen broadcast groups."""
import argparse,hashlib,io,json
from pathlib import Path
import chess,chess.pgn
from harness.c3x_013_p7r1_tactical_support import freeze_source,census

LANDMARKS=(32,64,80)
def one_game(item):
    row={"broadcast":item["broadcast"],"game_url":item["game_url"],
         "source_game_sha256":item["sha"],"landmarks":{}}
    game=chess.pgn.read_game(io.StringIO(item["raw"].decode("utf-8","replace")))
    if not game or game.errors:
        row["status"]="HOLD_GAME_PARSER_OR_VARIANT"
        return row
    b=game.board()
    if not b.is_valid():
        row["status"]="HOLD_START_POSITION"
        return row
    moves=list(game.mainline_moves())
    row["total_ply_in_game"]=len(moves)
    by={}
    for ply in LANDMARKS:
        if len(moves)<ply:
            by[str(ply)]={"status":"HOLD_GAME_END_BEFORE_LANDMARK"}
            continue
        target=chess.Board(game.board().fen())
        # Python-chess uses the exact PGN starting board; do not assume standard if PGN FEN exists.
        target=game.board()
        bad=False
        for m in moves[:ply]:
            if m not in target.legal_moves:
                bad=True;break
            target.push(m)
        if bad or not target.is_valid():
            by[str(ply)]={"status":"HOLD_ILLEGAL_OR_INVALID_LANDMARK"}
            continue
        if target.is_game_over():
            by[str(ply)]={"status":"HOLD_TERMINAL_AT_LANDMARK"}
            continue
        audited=census(target)
        counts=audited["counts"]
        by[str(ply)]={"status":"LEGAL_TACTICAL_SUPPORT",
                       "fen4_sha256":hashlib.sha256(
                           " ".join(target.fen(en_passant="fen").split()[:4]).encode()).hexdigest(),
                       "legal_root_count":audited["legal_root_count"],
                       "matched_birth_pairs":counts["passed_birth_toggling_in_matched"],
                       "strict_birth_pairs":counts["passed_birth_toggling_in_strict"],
                       "matched_any":bool(counts["passed_birth_toggling_in_matched"]),
                       "strict_any":bool(counts["passed_birth_toggling_in_strict"]),
                       "same_origin_tactical_pairs":counts["matched_and_same_origin"],
                       "tactical_pairs":counts["matched_legal_immediate_recapture"]}
    row["landmarks"]=by
    row["status"]="PARTIAL_OR_COMPLETE_LEGAL_PLY_COURT"
    return row

def summary(rows, groups):
    out={}
    for ply in LANDMARKS:
        good=[r["landmarks"][str(ply)] for r in groups
              if r.get("status")=="PARTIAL_OR_COMPLETE_LEGAL_PLY_COURT"
              and r["landmarks"].get(str(ply),{}).get("status")=="LEGAL_TACTICAL_SUPPORT"]
        out[str(ply)]={"eligible_groups":len(good),
                       "groups_with_matched_birth":sum(x["matched_any"] for x in good),
                       "groups_with_strict_birth":sum(x["strict_any"] for x in good),
                       "matched_birth_pairs":sum(x["matched_birth_pairs"] for x in good),
                       "strict_birth_pairs":sum(x["strict_birth_pairs"] for x in good)}
    return out

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source",required=True)
    p.add_argument("--output",required=True)
    args=p.parse_args()
    earlier,selected=freeze_source(args.source)
    assert len(earlier)==16 and len(selected)==32
    rows=[one_game(z) for z in selected]
    long80=[r for r in rows
            if r.get("status")=="PARTIAL_OR_COMPLETE_LEGAL_PLY_COURT"
            and r["landmarks"].get("80",{}).get("status")=="LEGAL_TACTICAL_SUPPORT"]
    result={"schema":"c3x-013-p7-r4-phase-conditioned-birth-support-v1",
            "stage":"C3X 0.13 P7 exploratory after observed P7-R1 ply32",
            "original_source_sha256":hashlib.sha256(Path(args.source).read_bytes()).hexdigest(),
            "frozen_group_count":32,"landmarks_halfmoves":list(LANDMARKS),
            "all_groups_per_landmark":summary(rows,rows),
            "ply80_survivor_group_count":len(long80),
            "within_ply80_survivors_paired_landmarks":summary(rows,long80),
            "source_holds":[{"broadcast":r["broadcast"],"status":r["status"]}
                            for r in rows if r["status"]!="PARTIAL_OR_COMPLETE_LEGAL_PLY_COURT"],
            "records":rows,
            "selection_bias_warning":"Ply80 subgroup selected by completed game duration. Pair counts within a game are dependent; no general population phase prevalence or causal move preference is inferred.",
            "engine_scores":None,"causal_strategic_authority":False,
            "0_14":"UNOPENED_CANDIDATE_ONLY"}
    Path(args.output).parent.mkdir(parents=True,exist_ok=True)
    Path(args.output).write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n")
    print("P7R4_PHASE_ALL",result["all_groups_per_landmark"])
    print("P7R4_PHASE_PAIRED80",result["within_ply80_survivors_paired_landmarks"])
    assert len(rows)==32 and result["engine_scores"] is None
if __name__=="__main__":main()
