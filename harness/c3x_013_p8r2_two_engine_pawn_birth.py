#!/usr/bin/env python3
"""P8-R2: eight frozen legal pawn-birth toggles vs control across two engine lineages.

No source rescue, no concept mediation certificate, no C3X 0.14 opening.
"""
import argparse,hashlib,json
from pathlib import Path
import chess
from harness.c3x_013_p8e1_pinned_ethereal import observe,sign
from harness.c3x_013_p7r1_tactical_support import hazard
from harness.c3x_013_p6r1_birth_rival_support import births

DIGEST="c5a18fdb71f752d37ceae740990937499d95c5dc6bf7981e7c672fdfeef659de"
DEPTHS=(8,12,16)

def classify_source(raw):
    q=json.loads(raw)
    assert q["schema"]=="c3x-013-p8-r1-source-only-phase-positivity-v1"
    assert q["fresh_frozen_group_count"]==32 and q["new_group_digest"]==DIGEST
    rows=[]
    for item in q["records"]:
        for ply in ("32","64","80"):
            w=item["worlds"][ply]
            if w["status"]!="CHESS_RULE_PAIR_SUPPORT_ONLY":
                continue
            board=chess.Board(w["fen"])
            for pair in w["pre_engine_birth_pair_examples"]:
                true=pair["birth_true_root"]
                false=pair["birth_false_root"]
                a,b=[chess.Move.from_uci(x) for x in (true,false)]
                assert a in board.legal_moves and b in board.legal_moves
                assert hazard(board,a)==hazard(board,b)
                assert not pair["same_from_square"]
                ba,bb=births(board,a),births(board,b)
                assert ba and not bb
                rows.append({"broadcast":item["broadcast"],"source_rank":item["source_rank"],
                             "game_url":item["game_url"],"raw_source_game_sha256":item["source_game_sha256"],
                             "ply":int(ply),"root_fen":w["fen"],
                             "root_fen_sha256":hashlib.sha256(w["fen"].encode()).hexdigest(),
                             "pair_true_false":{"a":true,"b":false},
                             "newly_passed_pawns":ba,
                             "original_move_hazard":hazard(board,a)})
    # R1 had 4+3+1 matched pairs in 4 broadcast groups; no relabeling or replacements.
    assert len(rows)==8
    assert len({r["broadcast"] for r in rows})==4
    return q,rows

def panel(exe,board,pair):
    out={}
    for depth in DEPTHS:
        trials=[observe(exe,board,pair,depth) for _ in (1,2)]
        exact=all(x["status"]=="CP_DIRECTION_ONLY" for x in trials) and (
            trials[0]["gap_cp"]==trials[1]["gap_cp"])
        val=trials[0].get("gap_cp") if exact else None
        out[str(depth)]={"trials":trials,"exact_repeat":exact,
                         "gap_true_minus_false_cp":val,
                         "direction":sign(val) if val is not None else None,
                         "within_50_engine_local":abs(val)<=50 if val is not None else None}
    usable=all(x["exact_repeat"] for x in out.values())
    dirs=[x["direction"] for x in out.values()]
    out["all_depth_same_nonzero_sign"]=usable and len(set(dirs))==1 and dirs[0]!=0
    out["all_depth_engine_local_under50"]=usable and all(
        x["within_50_engine_local"] for x in (out[str(k)] for k in DEPTHS))
    return out

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--p8-source",required=True)
    ap.add_argument("--stockfish",default="/usr/games/stockfish")
    ap.add_argument("--ethereal",required=True)
    ap.add_argument("--out",required=True)
    args=ap.parse_args()
    raw=Path(args.p8_source).read_bytes()
    source,records=classify_source(raw)
    output={"schema":"c3x-013-p8-r2-frozen-birth-two-engine-v1",
            "status":"DEVELOPMENT_CROSS_ENGINE_CHESS_CONCEPT_TOGGLE_NOT_CAUSAL",
            "original_p8_r1_sha256":hashlib.sha256(raw).hexdigest(),
            "original_sampled_groups":32,
            "matched_groups":4,"frozen_birth_toggle_pairs":8,
            "ethereal_source_commit":"0e47e9b67f345c75eb965d9fb3e2493b6a11d09a",
            "engine_binary_sha256":{"Stockfish":hashlib.sha256(Path(args.stockfish).read_bytes()).hexdigest(),
                                    "Ethereal_classical":hashlib.sha256(Path(args.ethereal).read_bytes()).hexdigest()},
            "results":[],"source_clusters_are_not_independent_engines":True,
            "causal_chess_concept_certificate":None,
            "C3X_014":"CANDIDATE_NO_TITLE_UNOPENED"}
    for case in records:
        board=chess.Board(case["root_fen"])
        pair=case["pair_true_false"]
        obj={**case,"engine_panels":{
            "Stockfish":panel(args.stockfish,board,pair),
            "Ethereal_classical":panel(args.ethereal,board,pair)}}
        ep=obj["engine_panels"]
        obj["same_direction_at_every_depth"]=all(
            ep["Stockfish"][str(d)]["direction"]==ep["Ethereal_classical"][str(d)]["direction"]
            and ep["Stockfish"][str(d)]["direction"] not in (None,0)
            for d in DEPTHS)
        obj["repeated_by_both_engines"]=all(
            ep[name][str(d)]["exact_repeat"]
            for name in ep for d in DEPTHS)
        obj["status"]=("TWO_ENGINE_ROOT_RESULTS_ONLY" if obj["repeated_by_both_engines"]
                       else "HOLD_MATE_PV_OR_REPEAT")
        output["results"].append(obj)
    output["counts"]={
        "pairs_original":8,
        "pairs_both_engine_all_depth_repeat":sum(x["repeated_by_both_engines"] for x in output["results"]),
        "pairs_both_engine_all_depth_sign_concordant":sum(x["same_direction_at_every_depth"] for x in output["results"]),
        "pairs_both_engines_individually_sign_stable":sum(
            all(x["engine_panels"][name]["all_depth_same_nonzero_sign"]
                for name in ("Stockfish","Ethereal_classical")) for x in output["results"]),
        "pairs_stockfish_all_depth_50cp":sum(x["engine_panels"]["Stockfish"]["all_depth_engine_local_under50"] for x in output["results"]),
        "pairs_ethereal_all_depth_50cp_uncalibrated":sum(x["engine_panels"]["Ethereal_classical"]["all_depth_engine_local_under50"] for x in output["results"])
    }
    Path(args.out).parent.mkdir(parents=True,exist_ok=True)
    Path(args.out).write_text(json.dumps(output,indent=2)+"\n")
    print("P8R2_TWO_ENGINE_BIRTH_ROOT_COUNTS",output["counts"])
    assert len(output["results"])==8 and output["original_sampled_groups"]==32
    assert output["causal_chess_concept_certificate"] is None
if __name__=="__main__":
    main()
