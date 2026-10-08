#!/usr/bin/env python3
"""P8-R4: legal opponent reply sensitivity on ALL frozen P8 born/not-born roots."""
import argparse,hashlib,json
from pathlib import Path
import chess,chess.engine

ETH_PIN="0e47e9b67f345c75eb965d9fb3e2493b6a11d09a"

def sign(x):return (x>0)-(x<0)

def choose_replies(exe,board):
    """Opponent is to move. Two independent selector processes with depth6."""
    def once():
        with chess.engine.SimpleEngine.popen_uci(exe,timeout=40) as e:
            if not {"Hash","Threads","MultiPV"}.issubset(e.options):
                return {"status":"HOLD_UCI_CONTROL_UNAVAILABLE"}
            e.configure({"Threads":1,"Hash":16})
            rows=e.analyse(board,chess.engine.Limit(depth=6),multipv=2)
        scored=[]
        for row in (rows if isinstance(rows,list) else [rows]):
            pv=row.get("pv",[])
            val=row.get("score")
            cp=val.pov(board.turn).score(mate_score=None) if val else None
            if pv and cp is not None and row.get("depth")==6 and pv[0] in board.legal_moves:
                scored.append({"reply":pv[0].uci(),"cp_opponent":cp,"depth":6})
        return {"status":"SELECTOR_CP_RESULT","choices":scored}
    repeats=[once(),once()]
    if any(r["status"]!="SELECTOR_CP_RESULT" or len(r["choices"])!=2 for r in repeats):
        return {"status":"HOLD_SELECTOR_MISSING_TWO_COMPLETE_REPLIES","trials":repeats}
    if repeats[0]["choices"]!=repeats[1]["choices"]:
        return {"status":"HOLD_SELECTOR_COLD_REPEAT_DRIFT","trials":repeats}
    a,b=repeats[0]["choices"]
    if a["reply"]==b["reply"]:
        return {"status":"HOLD_DUPLICATE_REPLY","trials":repeats}
    if a["cp_opponent"]<b["cp_opponent"]:
        return {"status":"HOLD_SELECTOR_ORDER_INCONSISTENT","trials":repeats}
    delta=a["cp_opponent"]-b["cp_opponent"]
    return {"status":"TWO_COLD_REPLIES_SUPPORTED" if delta<=100 else "HOLD_SECOND_REPLY_NOT_PLAUSIBLE",
            "strong":a["reply"],"rival":b["reply"],
            "selector_cp_gap":delta,"trials":repeats}

def assess_leaf(exe,board,original_side):
    """Evaluate AFTER two plies in original mover score POV, depth10."""
    def once():
        with chess.engine.SimpleEngine.popen_uci(exe,timeout=55) as e:
            if not {"Hash","Threads"}.issubset(e.options):
                return {"status":"HOLD_UCI_CONTROL_UNAVAILABLE"}
            e.configure({"Threads":1,"Hash":16})
            info=e.analyse(board,chess.engine.Limit(depth=10))
        val=info.get("score")
        cp=val.pov(original_side).score(mate_score=None) if val else None
        if cp is None or info.get("depth")!=10:
            return {"status":"HOLD_MATE_OR_DEPTH","depth":info.get("depth")}
        return {"status":"COMPLETE_DEPTH10_CP_ONLY","cp_root_side":cp,
                "pv":[x.uci() for x in info.get("pv",[])[:8]],
                "nodes":info.get("nodes")}
    trials=[once(),once()]
    exact=all(x["status"]=="COMPLETE_DEPTH10_CP_ONLY" for x in trials)
    exact=exact and trials[0]["cp_root_side"]==trials[1]["cp_root_side"]
    return {"status":"EXACT_REPEAT_ROOT_SIDE_CP" if exact else "HOLD_DEPTH10_CP_REPLICA",
            "cp":trials[0]["cp_root_side"] if exact else None,"trials":trials}

def test_one(original,stockfish,ethereal):
    board=chess.Board(original["root_fen"])
    roots={k:chess.Move.from_uci(original["pair_true_false"][k]) for k in ("a","b")}
    assert board.is_valid() and all(m in board.legal_moves for m in roots.values())
    out={"broadcast":original["broadcast"],"game_url":original["game_url"],
         "ply":original["ply"],"root_fen_sha256":original["root_fen_sha256"],
         "pair":original["pair_true_false"],"born":original["newly_passed_pawns"],
         "reply_selection":{},"conditional_evaluations":{}}
    branches={}
    for side,move in roots.items():
        successor=board.copy(stack=False);successor.push(move)
        chosen=choose_replies(ethereal,successor)
        out["reply_selection"][side]=chosen
        if chosen["status"]!="TWO_COLD_REPLIES_SUPPORTED":
            out["status"]="HOLD_NO_TWO_PLAUSIBLE_OPPONENT_REPLIES"
            return out
        branches[side]={}
        for name in ("strong","rival"):
            b=successor.copy(stack=False)
            reply=chess.Move.from_uci(chosen[name])
            assert reply in b.legal_moves
            b.push(reply)
            assert b.is_valid()
            branches[side][name]=b
    for engine_name,exe in (("Stockfish",stockfish),("Ethereal_classical",ethereal)):
        scored={}
        for side in ("a","b"):
            for reply_class in ("strong","rival"):
                key=side+"_"+reply_class
                scored[key]=assess_leaf(exe,branches[side][reply_class],board.turn)
        out["conditional_evaluations"][engine_name]=scored
    out["direction_matrices"]={}
    for engine_name,values in out["conditional_evaluations"].items():
        deltas={}
        for a_reply in ("strong","rival"):
            for b_reply in ("strong","rival"):
                l=values["a_"+a_reply]["cp"];r=values["b_"+b_reply]["cp"]
                deltas[a_reply+"_vs_"+b_reply]=l-r if l is not None and r is not None else None
        ok=all(x is not None for x in deltas.values())
        signs={sign(x) for x in deltas.values()} if ok else set()
        out["direction_matrices"][engine_name]={
            "gaps_cp_original_mover":deltas,
            "all_four_comparable":ok,
            "any_nonzero_direction_reversal":bool(ok and (1 in signs and -1 in signs))}
    out["status"]="EVALUATED_CONDITIONAL_LEGAL_REPLY_MATRIX" if all(
        z["all_four_comparable"] for z in out["direction_matrices"].values()) else "HOLD_REPLY_LEAF_SCORE"
    return out

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--p8r2-source",required=True)
    p.add_argument("--stockfish",default="/usr/games/stockfish")
    p.add_argument("--ethereal",required=True)
    p.add_argument("--out",required=True)
    a=p.parse_args()
    raw=Path(a.p8r2_source).read_bytes()
    parent=json.loads(raw)
    assert parent["schema"]=="c3x-013-p8-r2-frozen-birth-two-engine-v1"
    assert len(parent["results"])==8 and parent["original_sampled_groups"]==32
    rows=[]
    for item in parent["results"]:
        try:
            rows.append(test_one(item,a.stockfish,a.ethereal))
        except Exception as exc:
            rows.append({"broadcast":item["broadcast"],
                         "status":"EXECUTION_HOLD","error_type":type(exc).__name__,
                         "error_excerpt":str(exc)[:250]})
    counts={s:sum(r["status"]==s for r in rows) for s in sorted(set(r["status"] for r in rows))}
    complete=[x for x in rows if x["status"]=="EVALUATED_CONDITIONAL_LEGAL_REPLY_MATRIX"]
    out={"schema":"c3x-013-p8-r4-opponent-reply-conditional-matrix-v1",
         "stage":"C3X 0.13 P8-R4 POST-OUTCOME DEVELOPMENT",
         "parent_p8r2_sha256":hashlib.sha256(raw).hexdigest(),
         "ethereal_source_pin":ETH_PIN,
         "engine_binary_sha256":{"Stockfish":hashlib.sha256(Path(a.stockfish).read_bytes()).hexdigest(),
                                 "Ethereal":hashlib.sha256(Path(a.ethereal).read_bytes()).hexdigest()},
         "source_cohort_denominator":32,"frozen_pawn_birth_root_pairs":8,
         "support_counts":counts,
         "reply_matrix_complete_groups":len({z["broadcast"] for z in complete}),
         "Stockfish_conditional_reversal_pairs":sum(
             x["direction_matrices"]["Stockfish"]["any_nonzero_direction_reversal"] for x in complete),
         "Ethereal_conditional_reversal_pairs":sum(
             x["direction_matrices"]["Ethereal_classical"]["any_nonzero_direction_reversal"] for x in complete),
         "records":rows,
         "no_randomized_replies":True,"no_identified_causal_concept":True,
         "C3X_014":"CANDIDATE_ONLY_NO_TITLE"}
    Path(a.out).parent.mkdir(parents=True,exist_ok=True)
    Path(a.out).write_text(json.dumps(out,indent=2)+"\n")
    print("P8R4_LEGAL_OPPONENT_REPLY_SUPPORT",counts)
    print("P8R4_CONDITIONAL_REVERSALS",out["Stockfish_conditional_reversal_pairs"],
          out["Ethereal_conditional_reversal_pairs"])
    assert len(rows)==8 and out["source_cohort_denominator"]==32
    if "EXECUTION_HOLD" in counts:raise SystemExit("EXECUTION_HOLD_SEE_RAW_ARTIFACT")
if __name__=="__main__":main()
