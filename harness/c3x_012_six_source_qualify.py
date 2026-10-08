#!/usr/bin/env python3
"""Six-source C3X 0.12 developmental preference qualification. No causal claims."""
import argparse
import hashlib
import json
from pathlib import Path

import chess
import chess.engine

def cold(exe, board, nodes, only=None):
    with chess.engine.SimpleEngine.popen_uci(exe, timeout=20) as eng:
        eng.configure({"Threads": 1, "Hash": 16})
        kw = {"root_moves": [only]} if only else {}
        result = eng.analyse(board, chess.engine.Limit(nodes=nodes), **kw)
    if not result.get("pv"):
        return None
    score = result.get("score")
    cp = score.pov(board.turn).score(mate_score=None) if score else None
    if cp is None:
        return None
    return {"uci":result["pv"][0].uci(), "cp":cp, "depth":result.get("depth"),
            "nodes":result.get("nodes")}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--input", required=True)
    p.add_argument("--output", required=True)
    p.add_argument("--engine", default="/usr/games/stockfish")
    a=p.parse_args()
    source=Path(a.input)
    doc=json.loads(source.read_text())
    assert doc["schema"]=="c3x-012-preoutcome-six-source-world-snapshot-v1"
    out={"schema":"c3x-012-six-source-development-qualification-v1",
         "status":"DEVELOPMENT_ONLY_NOT_SCIENTIFIC_CONFIRMATION",
         "source_snapshot_sha256":hashlib.sha256(source.read_bytes()).hexdigest(),
         "engine_binary_sha256":hashlib.sha256(Path(a.engine).read_bytes()).hexdigest(),
         "worlds":[],"no_causal_explanation_authorized":True}
    for seed in doc["sources"]:
        w={"source_id":seed["source_id"],"original_pgn_sha256":seed["full_pgn_sha256"],
           "source_game_norm_sha256":seed["normalized_first_game_sha256"],
           "status":"PREQUALIFICATION"}
        try:
            board=chess.Board()
            for san in seed["san_first32"]:
                board.push_san(san)
            if len(board.move_stack)!=32 or not board.is_valid() or board.is_game_over():
                raise ValueError("BAD_SOURCE_POSITION")
            w["fen"]=board.fen(en_passant="fen")
            w["fen_sha256"]=hashlib.sha256(w["fen"].encode()).hexdigest()
            w["side_to_move"]="WHITE" if board.turn else "BLACK"
            cold10=[]
            for move in sorted(board.legal_moves,key=lambda m:m.uci()):
                r=cold(a.engine,board,10000,only=move)
                if r and r["uci"]==move.uci():
                    cold10.append(r)
            top=sorted(cold10,key=lambda r:(-r["cp"],r["uci"]))[:8]
            stable=[]
            for item in top:
                move=chess.Move.from_uci(item["uci"])
                z=[cold(a.engine,board,30000,only=move) for _ in range(2)]
                if all(x is not None for x in z) and z[0]["cp"]==z[1]["cp"]:
                    stable.append({"uci":item["uci"],"cp":z[0]["cp"],
                                   "independent_cp":[x["cp"] for x in z]})
            context=cold(a.engine,board,80000)
            best=context["uci"] if context else None
            choices=[]
            anchor=next((x for x in stable if x["uci"]==best),None)
            if anchor:
                for x in stable:
                    if x["uci"]==best: continue
                    gap=abs(anchor["cp"]-x["cp"])
                    if gap<=50:
                        choices.append({"a":min(best,x["uci"]),"b":max(best,x["uci"]),
                                        "cold_gap_cp":gap})
            choices.sort(key=lambda x:(x["cold_gap_cp"],x["a"],x["b"]))
            w.update({"legal_root_move_count":board.legal_moves.count(),
                      "cold10_nonmate_usable":len(cold10),
                      "top8":[x["uci"] for x in top],
                      "stable30k":stable,
                      "contextual80k":context,
                      "selected_pair":choices[0] if choices else None,
                      "status":"PAIR_FROZEN_DEV_ONLY" if choices else "HOLD_NO_STABLE_PAIR"})
        except Exception as exc:
            w.update({"status":"EXECUTION_HOLD","exception_type":type(exc).__name__,
                      "exception_summary":str(exc)[:160]})
        out["worlds"].append(w)
    out["counts"]={s:sum(w["status"]==s for w in out["worlds"])
                   for s in sorted({w["status"] for w in out["worlds"]})}
    Path(a.output).parent.mkdir(parents=True,exist_ok=True)
    Path(a.output).write_text(json.dumps(out,indent=2)+"\n")
    print("C3X_012_QUALIFICATION_COUNTS",out["counts"])
    print("C3X_012_SOURCES",[(w["source_id"],w["status"]) for w in out["worlds"]])
    if any(w["status"]=="EXECUTION_HOLD" for w in out["worlds"]):
        raise SystemExit("SOURCE_OR_EXECUTION_HOLD_REQUIRES_DIAGNOSTIC")

if __name__=="__main__":
    main()
