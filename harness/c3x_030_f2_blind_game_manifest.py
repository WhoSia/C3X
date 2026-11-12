#!/usr/bin/env python3
"""C3X F2/S4H-0: prospective identity-only independent-game pilot cohort.

This tool constructs and freezes 12 deterministic LEGAL opening continuations
(4 development, 8 untouched holdout source histories) at plies 8 and 10.
These are analyst-constructed opening lines, not an independent random sample
of human games and not chess game outcomes. No engine, labels or scores.
The SHA-sealed manifest must be archived BEFORE downstream treatment results.
"""
import argparse,hashlib,json
from pathlib import Path
import chess

SCHEMA="c3x030-f2-blind-holdout-manifest-v1"
VERSION="C3X 0.30"
# Each full history is frozen here before the first independent-holdout search.
GAMES={
"dev_italian":("development","e2e4 e7e5 g1f3 b8c6 f1c4 f8c5 c2c3 g8f6 d2d3 d7d6"),
"dev_london":("development","d2d4 d7d5 c1f4 g8f6 e2e3 e7e6 g1f3 f8d6 f4g3 e8g8"),
"dev_pirc":("development","e2e4 d7d6 d2d4 g8f6 b1c3 g7g6 g1f3 f8g7 f1e2 e8g8"),
"dev_scandinavian":("development","e2e4 d7d5 e4d5 d8d5 b1c3 d5a5 d2d4 c7c6 g1f3 c8f5"),
"test_scotch":("holdout","e2e4 e7e5 g1f3 b8c6 d2d4 e5d4 f3d4 g8f6 b1c3 f8b4"),
"test_french":("holdout","e2e4 e7e6 d2d4 d7d5 b1c3 g8f6 c1g5 f8e7 e4e5 f6d7"),
"test_carokann":("holdout","e2e4 c7c6 d2d4 d7d5 b1c3 d5e4 c3e4 c8f5 e4g3 f5g6"),
"test_kingsindian":("holdout","d2d4 g8f6 c2c4 g7g6 b1c3 f8g7 e2e4 d7d6 g1f3 e8g8"),
"test_catalan":("holdout","d2d4 g8f6 c2c4 e7e6 g2g3 d7d5 f1g2 f8e7 g1f3 e8g8"),
"test_vienna":("holdout","e2e4 e7e5 b1c3 g8f6 f2f4 d7d5 f4e5 f6e4 d1f3 b8c6"),
"test_fourknights":("holdout","e2e4 e7e5 g1f3 b8c6 b1c3 g8f6 f1b5 f8b4 e1g1 e8g8"),
"test_queensindian":("holdout","d2d4 g8f6 c2c4 e7e6 g1f3 b7b6 g2g3 c8b7 f1g2 f8e7"),
}
PLIES=(8,10)

def generate():
    cases=[]
    for game,(split,moves) in sorted(GAMES.items()):
        seq=moves.split()
        if len(seq)!=10:raise ValueError("F2_HOLD_GAME_HISTORY_LENGTH:"+game)
        board=chess.Board()
        for i,move in enumerate(seq,1):
            m=chess.Move.from_uci(move)
            if m not in board.legal_moves:
                raise ValueError("F2_HOLD_ILLEGAL_OR_NONHISTORICAL_MOVE:"+game+":"+move)
            board.push(m)
            if i in PLIES:
                if not board.is_valid():raise ValueError("F2_HOLD_INVALID_POSITION")
                cases.append({"case_id":game+"_ply"+str(i),
                   "game_id":game,"split":split,"fen":board.fen(),
                   "history_uci":seq[:i]})
    if len(cases)!=24 or len({x["fen"] for x in cases})!=24:
        raise ValueError("F2_HOLD_FEN_COUNT_OR_DUPLICATE")
    if sum(c["split"]=="holdout" for c in cases)!=16:
        raise ValueError("F2_HOLD_HOLDOUT_SIZE")
    return cases

def manifest():
    cases=generate()
    return {"schema":SCHEMA,"research_version":VERSION,
        "source":"researcher-authored-deterministic-legal-opening-lines",
        "outcome_based_position_selection":False,
        "random_population_sample":False,
        "independent_game_lineages_not_independent_FEN_snapshots":True,
        "evaluation_positions_from_same_game_are_correlated":True,
        "no_evaluation_or_treatment_outcomes_in_manifest":True,
        "cases_per_game":2,"number_development_game_histories":4,
        "number_holdout_game_histories":8,
        "manifest_is_identity-only":True,
        "entries":[{k:v for k,v in case.items() if k!="split"}
                   for case in cases if case["split"]=="holdout"],
        "development_entries":[{k:v for k,v in case.items() if k!="split"}
                   for case in cases if case["split"]=="development"]}
def main():
    a=argparse.ArgumentParser();a.add_argument("--out",required=True)
    x=a.parse_args()
    data=manifest()
    dest=Path(x.out);dest.parent.mkdir(parents=True,exist_ok=True)
    raw=(json.dumps(data,indent=2,sort_keys=True,ensure_ascii=False)+"\n").encode("utf8")
    dest.write_bytes(raw)
    print("C3X_F2_S4H0_FROZEN_GAME_HISTORIES",
          "HOLDOUT",len(data["entries"]),"DEVELOPMENT",len(data["development_entries"]),
          "MANIFEST_SHA256",hashlib.sha256(raw).hexdigest(),
          "NO_ENGINE_SEARCHES",True)
if __name__=="__main__":main()
