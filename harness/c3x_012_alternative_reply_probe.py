#!/usr/bin/env python3
"""Six-source alternative-opponent-reply probe; developmental only, not causal."""
import argparse
import hashlib
import json
from pathlib import Path
import chess
import chess.engine

def cold(exe, board, perspective):
    with chess.engine.SimpleEngine.popen_uci(exe,timeout=20) as eng:
        eng.configure({"Threads":1,"Hash":16})
        r=eng.analyse(board,chess.engine.Limit(nodes=30000))
    value=r["score"].pov(perspective).score(mate_score=None)
    return {"cp_original_mover":value,"depth":r.get("depth"),
            "nodes":r.get("nodes"),
            "pv":[m.uci() for m in r.get("pv",[])[:6]]}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--qualification",required=True)
    p.add_argument("--output",required=True)
    p.add_argument("--engine",default="/usr/games/stockfish")
    a=p.parse_args()
    path=Path(a.qualification)
    q=json.loads(path.read_text())
    assert q["schema"]=="c3x-012-six-source-development-qualification-v1"
    out={"schema":"c3x-012-alternative-reply-development-v1",
         "status":"DEVELOPMENT_ONLY_ALTERNATIVE_REPLY_NOT_CAUSAL_EXPLANATION",
         "qualification_sha256":hashlib.sha256(path.read_bytes()).hexdigest(),
         "selection":"LEXICAL_FIRST_AND_MEDIAN_LEGAL_OPPONENT_REPLIES_PER_CANDIDATE_BEFORE_SCORE",
         "claim_authority":False,"worlds":[]}
    for source in q["worlds"]:
        row={"source_id":source["source_id"]}
        pair=source.get("selected_pair")
        if not pair:
            row["status"]="HOLD_NO_QUALIFIED_PAIR"
            out["worlds"].append(row)
            continue
        board=chess.Board(source["fen"])
        root_turn=board.turn
        branches={}
        for move_uci in (pair["a"],pair["b"]):
            candidate=chess.Move.from_uci(move_uci)
            if candidate not in board.legal_moves:
                raise ValueError("ROOT_PAIR_ILLEGAL")
            after=board.copy(stack=False)
            after.push(candidate)
            replies=sorted(after.legal_moves,key=lambda m:m.uci())
            if len(replies)<2:
                branches[move_uci]={"status":"HOLD_REPLY_BREADTH"}
                continue
            frozen={"lex_first":replies[0],"lex_median":replies[len(replies)//2]}
            branch={}
            for name,reply in frozen.items():
                leaf=after.copy(stack=False)
                leaf.push(reply)
                scores=[cold(a.engine,leaf,root_turn) for _ in range(2)]
                branch[name]={"opponent_reply":reply.uci(),
                              "fen_after_candidate_reply":leaf.fen(en_passant="fen"),
                              "score_repeats":scores,
                              "exact_repeat":scores[0]["cp_original_mover"] is not None
                                  and scores[0]["cp_original_mover"]==scores[1]["cp_original_mover"]}
            branches[move_uci]=branch
        row["pair"]=pair
        row["branches"]=branches
        row["status"]="ALTERNATIVE_REPLY_VALUES_OBSERVED_DEV_ONLY"
        out["worlds"].append(row)
    out["counts"]={x:sum(y["status"]==x for y in out["worlds"])
                   for x in sorted({y["status"] for y in out["worlds"]})}
    Path(a.output).write_text(json.dumps(out,indent=2)+"\n")
    print("C3X_012_RIVAL_REPLY_COUNTS",out["counts"])
    print("C3X_012_CAUSAL_AUTHORITY",False)

if __name__=="__main__":
    main()
