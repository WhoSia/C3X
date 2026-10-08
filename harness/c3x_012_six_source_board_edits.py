#!/usr/bin/env python3
"""Frozen-pair edited-board contrasts: developer diagnostic, not causal mediation."""
import argparse
import hashlib
import json
from pathlib import Path

import chess
import chess.engine

def cheb(a,b):
    return max(abs(chess.square_file(a)-chess.square_file(b)),
               abs(chess.square_rank(a)-chess.square_rank(b)))

def vect(board,sq,pair):
    targets=[chess.Move.from_uci(m) for m in (pair["a"],pair["b"])]
    att=board.attacks(sq)
    return [int(v in att) for move in targets for v in (move.from_square,move.to_square)]

def candidates(board,pair):
    protected={v for u in (pair["a"],pair["b"]) for v in
               (chess.parse_square(u[:2]),chess.parse_square(u[2:4]))}
    possible={}
    for src,p in sorted(board.piece_map().items()):
        if p.piece_type not in (chess.KNIGHT,chess.BISHOP,chess.QUEEN) or src in protected:continue
        prior=vect(board,src,pair)
        for dst in sorted(board.attacks(src)):
            if dst in protected or board.piece_at(dst) or cheb(src,dst)>2:continue
            after=board.copy(stack=False)
            after.remove_piece_at(src)
            after.set_piece_at(dst,p)
            if not after.is_valid() or after.is_check():continue
            if any(chess.Move.from_uci(u) not in after.legal_moves for u in (pair["a"],pair["b"])):continue
            legal_delta=after.legal_moves.count()-board.legal_moves.count()
            attack_delta=len(set(board.attacks(src))^set(after.attacks(dst)))
            if abs(legal_delta)>6 or attack_delta>10:continue
            changed=vect(after,dst,pair)!=prior
            key=(src,cheb(src,dst))
            possible.setdefault(key,[]).append({
                "from":chess.square_name(src),"to":chess.square_name(dst),
                "fen":after.fen(en_passant="fen"),"changed":changed,
                "relation_before":prior,"relation_after":vect(after,dst,pair),
                "legal_move_delta":legal_delta,"attack_set_diff":attack_delta})
    matched=[]
    for key,items in possible.items():
        for target in (x for x in items if x["changed"]):
            for sham in (x for x in items if not x["changed"]):
                matched.append((key[0],target["to"],sham["to"],target,sham))
    if not matched:return None
    _,_,_,target,sham=min(matched,key=lambda x:x[:3])
    return {"TARGET":target,"SHAM":sham}

def score(exe,fen,pair):
    b=chess.Board(fen)
    roots=[chess.Move.from_uci(pair[k]) for k in ("a","b")]
    if any(m not in b.legal_moves for m in roots):return {"status":"ILLEGAL_PAIR"}
    with chess.engine.SimpleEngine.popen_uci(exe,timeout=20) as engine:
        engine.configure({"Threads":1,"Hash":16})
        res=engine.analyse(b,chess.engine.Limit(nodes=80000),multipv=2,root_moves=roots)
    by_move={}
    for r in res:
        if not r.get("pv") or not r.get("score"):continue
        cp=r["score"].pov(b.turn).score(mate_score=None)
        if cp is not None:
            by_move[r["pv"][0].uci()]={"cp":cp,"depth":r.get("depth"),"pv":[x.uci() for x in r["pv"][:8]]}
    a,b=by_move.get(pair["a"]),by_move.get(pair["b"])
    if not a or not b:return {"status":"HOLD_MISSING_CP_OR_MATE","raw":by_move}
    if a["depth"] is None or a["depth"]!=b["depth"]:
        return {"status":"HOLD_DEPTH_MISMATCH","raw":by_move}
    return {"status":"SYNTACTICALLY_COMPARABLE_CP_ONLY","depth":a["depth"],
            "a_cp":a["cp"],"b_cp":b["cp"],"delta_cp":a["cp"]-b["cp"],"raw":by_move}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--qualification",required=True)
    p.add_argument("--output",required=True)
    p.add_argument("--engine",default="/usr/games/stockfish")
    a=p.parse_args()
    source=Path(a.qualification)
    q=json.loads(source.read_text())
    assert q["schema"]=="c3x-012-six-source-development-qualification-v1"
    out={"schema":"c3x-012-six-source-board-edit-contrast-v1",
         "source_qualification_sha256":hashlib.sha256(source.read_bytes()).hexdigest(),
         "status":"POST_PILOT_FIXED_DEPTH12_DEVELOPMENT_NOT_MECHANISM_IDENTIFICATION",
         "measurement_method_change":"FROZEN_AFTER_OBSERVING_FAILED_NODES_MULTIPV_DEPTH_MISMATCH",
         "science_claim_permission":False,
         "worlds":[],"explanation_authority":False}
    for w in q["worlds"]:
        row={"source_id":w["source_id"],"source_fen_sha256":w.get("fen_sha256")}
        pair=w.get("selected_pair")
        if not pair or not w.get("fen"):
            row["status"]="HOLD_NO_QUALIFIED_PAIR"
        else:
            try:
                board=chess.Board(w["fen"])
                edits=candidates(board,pair)
                if edits is None:
                    row["status"]="HOLD_NO_MATCHED_LEGAL_TARGET_SHAM"
                else:
                    row["pair"]=pair
                    row["frozen_edit_family"]=edits
                    worlds={"B0":w["fen"],"TARGET":edits["TARGET"]["fen"],
                            "SHAM":edits["SHAM"]["fen"]}
                    row["measured"]={label:[score(a.engine,fen,pair) for _ in range(2)]
                                     for label,fen in worlds.items()}
                    if all(all(t["status"]=="SYNTACTICALLY_COMPARABLE_CP_ONLY"
                               for t in trials) for trials in row["measured"].values()):
                        contrast=[row["measured"]["TARGET"][i]["delta_cp"]-
                                  row["measured"]["SHAM"][i]["delta_cp"] for i in range(2)]
                        row["contrast_target_minus_sham_cp"]=contrast
                        row["status"]="BOARD_CONTRAST_OBSERVED_NOT_MEDIATOR"
                    else:row["status"]="HOLD_INCOMPARABLE_SCORE"
            except Exception as exc:
                row.update({"status":"EXECUTION_HOLD","error_type":type(exc).__name__,
                            "error":str(exc)[:190]})
        out["worlds"].append(row)
    out["counts"]={x:sum(w["status"]==x for w in out["worlds"])
                   for x in sorted({w["status"] for w in out["worlds"]})}
    Path(a.output).write_text(json.dumps(out,indent=2)+"\n")
    print("C3X_012_CHESS_BOARD_CONTRAST_COUNTS",out["counts"])
    print("C3X_012_HUMAN_STRATEGY_AUTHORITY",False)
    if any(w["status"]=="EXECUTION_HOLD" for w in out["worlds"]):
        raise SystemExit("SOURCE_INTEGRITY_HOLD_DO_NOT_PROMOTE")

if __name__=="__main__":
    main()
