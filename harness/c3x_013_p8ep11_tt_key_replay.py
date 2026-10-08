#!/usr/bin/env python3
"""EP11 actual Stockfish16 TT fingerprint and same-source keyed replay court."""
from __future__ import annotations
import argparse,hashlib,json,os,re,subprocess
from pathlib import Path
import chess

FEN="2rq1rk1/p4ppp/bp1bnn2/3pN3/2pP3P/1P2PPP1/PB2NRB1/R2Q2K1 w - - 1 17"
ORDERS=(("f3f4","g3g4"),("g3g4","f3f4"))
DEPTHS=(8,12)
FROZEN_MAIN_ORDINAL=32
ABSENT_KEY="ffffffffffffffff"

def measure(binary, depth, order, site="NONE", ordinal=0, key=None, ply=None, node_depth=None):
    board=chess.Board(FEN)
    assert board.is_valid() and board.turn==chess.WHITE
    assert all(chess.Move.from_uci(m) in board.legal_moves for m in order)
    env=dict(os.environ,C3X_P8_EP9_BLOCK_CUTOFF="OFF",
             C3X_P8_EP10_SITE=site,C3X_P8_EP10_ORDINAL=str(ordinal))
    for k in ("C3X_P8_EP11_TARGET_KEY","C3X_P8_EP11_TARGET_SITE","C3X_P8_EP11_TARGET_PLY","C3X_P8_EP11_TARGET_DEPTH"):
        env.pop(k,None)
    if key is not None:
        assert site=="NONE" and ordinal==0 and ply is not None and node_depth is not None
        env.update(C3X_P8_EP11_TARGET_KEY=key,C3X_P8_EP11_TARGET_SITE="MAIN",
                   C3X_P8_EP11_TARGET_PLY=str(ply),C3X_P8_EP11_TARGET_DEPTH=str(node_depth))
    lines=[]
    with subprocess.Popen([str(binary)],stdin=subprocess.PIPE,stdout=subprocess.PIPE,
         stderr=subprocess.STDOUT,text=True,bufsize=1,env=env) as p:
        def send(*z):
            p.stdin.write("\n".join(z)+"\n")
            p.stdin.flush()
        def wait(prefix):
            for _ in range(100000):
                x=p.stdout.readline()
                if not x:raise RuntimeError(f"UCI EOF waiting {prefix}: {lines[-12:]}")
                lines.append(x.rstrip())
                if x.startswith(prefix):return
            raise RuntimeError("UCI unbounded lines")
        send("uci");wait("uciok")
        send("setoption name Threads value 1","setoption name Hash value 16",
             "setoption name MultiPV value 2","ucinewgame","isready")
        wait("readyok")
        send("position fen "+FEN,"go depth "+str(depth)+" searchmoves "+" ".join(order))
        wait("bestmove ");send("quit")
        assert p.wait(timeout=10)==0
    infos={}
    for x in lines:
        if not (x.startswith("info depth ") and " multipv " in x and " pv " in x):continue
        md=re.search(r"\bdepth (\d+)",x)
        if not md or int(md.group(1))!=depth:continue
        mat=re.search(r"\bscore (cp|mate) (-?\d+)",x)
        if not mat:continue
        rank=int(re.search(r"\bmultipv (\d+)",x).group(1))
        pv=x.split(" pv ",1)[1].split()
        infos[rank]={"root_move":pv[0],"score_kind":mat.group(1),
                     "score_white_cp":int(mat.group(2)) if mat.group(1)=="cp" else None,
                     "score_mate":int(mat.group(2)) if mat.group(1)=="mate" else None,
                     "nodes":int(re.search(r"\bnodes (\d+)",x).group(1)),
                     "pv":pv[:12]}
    if set(infos)!={1,2} or {v["root_move"] for v in infos.values()}!=set(order):
        raise ValueError("Missing legal root MultiPV lines "+str(infos))
    best=[x.split()[1] for x in lines if x.startswith("bestmove ")]
    assert best==[infos[1]["root_move"]]
    records={}
    for prefix in ("c3x_p8_ep10","c3x_p8_ep11"):
        matching=[x for x in lines if x.startswith("info string "+prefix+" ")]
        if len(matching)>1:raise ValueError("Duplicate "+prefix)
        if matching:
            vals=matching[0].split(" fen=",1)
            parts=vals[0].split()[3:]
            # Some fields intentionally serialized in hex; preserve as str.
            fields=dict(q.split("=",1) for q in parts)
            obj={k:(v if k.endswith("_hex") else int(v)) for k,v in fields.items()}
            if len(vals)>1:obj["fen"]=vals[1]
            records[prefix]=obj
    if site=="MAIN" and ordinal==32:
        assert records["c3x_p8_ep10"]["blocked"]==1
    if key is not None:
        assert "c3x_p8_ep11" in records
    vals={v["root_move"]:v for v in infos.values()}
    gap=(vals["f3f4"]["score_white_cp"]-vals["g3g4"]["score_white_cp"]
         if all(v["score_white_cp"] is not None for v in vals.values()) else None)
    return {"bestmove":best[0],"ranked_pvs":infos,"signed_pair_gap_white_cp":gap,
            "native_records":records}

def effects(x):
    return {k:x[k] for k in ("bestmove","ranked_pvs","signed_pair_gap_white_cp")}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--ep10",required=True)
    p.add_argument("--ep11",required=True)
    p.add_argument("--output",required=True)
    a=p.parse_args()
    cells=[]
    for order in ORDERS:
        for depth in DEPTHS:
            for repetition in (1,2):
                before=measure(a.ep10,depth,order)
                sham=measure(a.ep11,depth,order)
                ordinal10=measure(a.ep10,depth,order,site="MAIN",ordinal=32)
                ordinal11=measure(a.ep11,depth,order,site="MAIN",ordinal=32)
                same_sham=effects(before)==effects(sham)
                same_ordinal=effects(ordinal10)==effects(ordinal11)
                e=ordinal11["native_records"]["c3x_p8_ep11"]
                assert e["selected"]==1 and e["actual_site"]==1 and e["actual_ordinal"]==32
                cells.append({"order":list(order),"depth":depth,"cold_repeat":repetition,
                    "old_none":before,"new_none":sham,"old_ordinal32":ordinal10,
                    "new_ordinal32":ordinal11,"sham_equivalent":same_sham,
                    "ordinal_intervention_equivalent":same_ordinal})
                print("EP11_CONTEXT_ORDINAL_SHAM",depth,order,repetition,
                      "none",same_sham,"ordinal",same_ordinal,
                      "tt_key",e["actual_key_hex"],"FEN",e.get("fen",""),flush=True)
    # Stage two: commit to the first original-order depth-12 event key and node coordinates.
    witness=next(x for x in cells if x["depth"]==12 and x["cold_repeat"]==1 and tuple(x["order"])==ORDERS[0])
    found=witness["new_ordinal32"]["native_records"]["c3x_p8_ep11"]
    key=found["actual_key_hex"]
    ply=found["actual_ply"]
    node_depth=found["actual_depth"]
    board_fen=found["fen"]
    if not chess.Board(board_fen).is_valid():
        raise ValueError("Actual engine event position FEN is not a legal chess board")
    if key==ABSENT_KEY:
        raise ValueError("Pre-fixed negative control key collides with discovery key")
    for item in cells:
        depth=item["depth"];order=tuple(item["order"])
        keyed=measure(a.ep11,depth,order,key=key,ply=ply,node_depth=node_depth)
        negative=measure(a.ep11,depth,order,key=ABSENT_KEY,ply=ply,node_depth=node_depth)
        k=keyed["native_records"]["c3x_p8_ep11"]
        n=negative["native_records"]["c3x_p8_ep11"]
        item["fixed_signature_replay"]=keyed
        item["impossible_key_control"]=negative
        item["impossible_key_control_pass"]=n["selected"]==0 and effects(negative)==effects(item["new_none"])
        item["signature_replay_matches_original_ordinal_effect"]=effects(keyed)==effects(item["new_ordinal32"])
        item["native_selected_full_position_same_as_anchor"]=k["selected"]==1 and k.get("fen")==board_fen and k["actual_key_hex"]==key
        item["native_selected_tt_entry_metadata_same_as_anchor"]=k["selected"]==1 and all(
            k[f]==found[f] for f in ("actual_tt_bound","actual_tt_depth","actual_rule50","actual_alpha","actual_beta","actual_value"))
        print("EP11_KEYED_REPLAY",depth,order,item["cold_repeat"],
              "blocked",k["selected"],"ordinal",k["actual_ordinal"],
              "matches_ordinal_output",item["signature_replay_matches_original_ordinal_effect"],
              "same_fen",item["native_selected_full_position_same_as_anchor"],flush=True)
    gates=all(z["sham_equivalent"] and z["ordinal_intervention_equivalent"]
              and z["impossible_key_control_pass"] for z in cells)
    depth12=[x for x in cells if x["depth"]==12]
    depth8=[x for x in cells if x["depth"]==8]
    panel={"schema":"c3x-013-p8ep11-tt-key-fen-context-replay-v1",
        "status":"NATIVE_TT_POSITION_PROVENANCE_TEST__SAME_GAME__NO_CHESS_CONCEPT_CERTIFICATE",
        "upstream_source":"official Stockfish sf_16 pinned commit 68e1e9b3811e16cad014b590d7443b9063b3eb52",
        "original_game":"CECLUB Primera Division Linares, reused P7 and P8 research",
        "source_fen":FEN,"preexisting_root_pair":["f3f4","g3g4"],
        "frozen_orders":[list(x) for x in ORDERS],
        "frozen_depths":list(DEPTHS),"cold_repeats_per_order_depth":2,
        "event_discovery_condition":"the first original-order depth12 MAIN ordinal32 run in this grid",
        "event_anchor":{"key_hex":key,"native_event":found,"node_full_fen":board_fen,
                        "node_ply":ply,"node_depth":node_depth},
        "negative_selector_key_hex":ABSENT_KEY,
        "controls_all_pass":gates,
        "same_exact_position_depth12_count":sum(x["native_selected_full_position_same_as_anchor"] for x in depth12),
        "keyed_replay_equals_ordinal_intervention_depth12_count":sum(x["signature_replay_matches_original_ordinal_effect"] for x in depth12),
        "keyed_replay_equals_ordinal_intervention_depth8_count":sum(x["signature_replay_matches_original_ordinal_effect"] for x in depth8),
        "cells":cells,
        "limitations":["key+FEN can identify position within this Stockfish binary, not TT-entry age/history","same source, same game, post-discovery target signature; not independent validation","search path and node counts may differ after one intervention","repeated tests are deterministic restarts, not multiple independent chess games",
                       "not a semantic chess feature and does not warrant human strategic commentary causal certificate"],
        "chess_concept_caused_preference":False,
        "C3X_014":"UNOPENED_UNNAMED"}
    output=Path(a.output);output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(panel,indent=2)+"\n")
    print("EP11_CONTEXT_RESULT",json.dumps({"controls":gates,
           "depth12_position_equal":panel["same_exact_position_depth12_count"],
           "depth12_output_equal":panel["keyed_replay_equals_ordinal_intervention_depth12_count"]}),flush=True)
    if not gates:raise SystemExit("EP11_SHAM_OR_NEGATIVE_CONTROL_INVALID")

if __name__=="__main__":main()
