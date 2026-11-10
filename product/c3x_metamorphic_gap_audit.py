#!/usr/bin/env python3
"""C3X 0.30/P5 — mirror metamorphic robustness of *contrastive* move gaps.

Primary owned source: Martin et al (2025), Re-evaluating Metamorphic Testing
of Chess Engines: A Replication Study, DOI 10.1016/j.infsof.2025.107679.
Their finding: transformed board finite-depth evaluations can disagree,
often due to normal search effects; violation != proof of software bug.

Here we reproduce a NARROW mirror relation, applied to two separately
forced root moves and their *contrastive gap*, not the full Martin dataset,
four relations, depth range, or statistical/threshold experiment.

python-chess board.mirror() performs color swap + vertical rank reflection
and changes side-to-move. The mapped UCI is rank-reflected, promotion
unchanged. Evaluate each action from the side who originally makes it,
so comparisons across colors have the SAME semantic root-player POV.

No target labels, prospective claims, or causal source-search attribution.
"""
import argparse
import hashlib
import json
from pathlib import Path

import chess
import chess.engine

from c3x_explain_two_moves import verify_board_and_pair,ENGINE_GIT_COMMIT

SCHEMA="c3x030-p5-mirror-metamorphic-contrastive-gap-native-v1"
MARTIN_DRIVE="https://drive.google.com/file/d/1bMl15sK_8G0h9GbuJehObn9zj8RoKKX7/view"
JACOVI_DRIVE="https://drive.google.com/file/d/11ltQLiTQxQuFiKMJb5jnVtK5U--WtNXP/view"
DEPTHS=(8,10,12)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def mirror_move(move):
    if not isinstance(move,chess.Move):
        raise ValueError("P5_HOLD_NOT_CHESS_MOVE")
    return chess.Move(chess.square_mirror(move.from_square),
                      chess.square_mirror(move.to_square),
                      promotion=move.promotion,
                      drop=move.drop)


def mirrored_pair(board,a,b):
    if not board.is_valid() or a==b or a not in board.legal_moves or b not in board.legal_moves:
        raise ValueError("P5_HOLD_ORIGINAL_PAIR_NOT_LEGAL")
    counterpart=board.mirror()
    counterpart_a,counterpart_b=mirror_move(a),mirror_move(b)
    if not counterpart.is_valid() or (counterpart_a not in counterpart.legal_moves
                                     or counterpart_b not in counterpart.legal_moves):
        raise ValueError("P5_HOLD_MIRROR_PAIR_NOT_LEGAL")
    if counterpart.mirror().fen(en_passant="fen")!=board.fen(en_passant="fen"):
        raise ValueError("P5_HOLD_DOUBLE_MIRROR_NONINVOLUTIVE")
    if (mirror_move(counterpart_a)!=a or mirror_move(counterpart_b)!=b
        or counterpart.turn==board.turn):
        raise ValueError("P5_HOLD_MOVE_PERSPECTIVE_DRIFT")
    return counterpart,counterpart_a,counterpart_b


def evaluate_forced(board,move,engine,depth):
    info=engine.analyse(board,chess.engine.Limit(depth=depth),
                        root_moves=[move],game=object(),info=chess.engine.INFO_ALL)
    if (type(info.get("depth")) is not int or info["depth"]<depth
        or type(info.get("nodes")) is not int or info["nodes"]<=0
        or not info.get("pv") or info["pv"][0]!=move or info.get("score") is None):
        raise ValueError("P5_HOLD_SOURCE_FORCED_ROOT_SEARCH")
    pov=info["score"].pov(board.turn)
    cp=pov.score()
    return {
        "root_mover_cp_or_null_mate":cp,
        "root_mover_mate_or_null":pov.mate() if pov.is_mate() else None,
        "depth":info["depth"],"nodes":info["nodes"],
        "forced_root_uci":move.uci(),
        "principal_variation_uci":[x.uci() for x in info["pv"][:6]]
    }


def relative_distance_abs(x,y):
    if x is None or y is None:
        return None
    den=abs(x)+abs(y)
    if den==0:
        return 0.0
    return abs(x-y)/den


def case_analysis(fen,ua,ub,engine,case_id):
    board,ma,mb=verify_board_and_pair(fen,ua,ub)
    mirrored,ca,cb=mirrored_pair(board,ma,mb)
    data={
        "case_id":case_id,
        "original_fen":board.fen(en_passant="fen"),
        "mirror_fen":mirrored.fen(en_passant="fen"),
        "original_root_candidates":[ma.uci(),mb.uci()],
        "mirrored_candidates":[ca.uci(),cb.uci()],
        "mapping":"python_chess_board_mirror_color_swap_vertical_rank",
        "same_semantic_root_player_perspective":True,
        "per_depth":{}
    }
    for depth in DEPTHS:
        original_a=evaluate_forced(board,ma,engine,depth)
        original_b=evaluate_forced(board,mb,engine,depth)
        mirrored_a=evaluate_forced(mirrored,ca,engine,depth)
        mirrored_b=evaluate_forced(mirrored,cb,engine,depth)
        rows={
            "original_a":original_a,"original_b":original_b,
            "mirrored_a":mirrored_a,"mirrored_b":mirrored_b
        }
        vals={name:r["root_mover_cp_or_null_mate"] for name,r in rows.items()}
        if all(x is not None for x in vals.values()):
            original_gap=vals["original_a"]-vals["original_b"]
            mirror_gap=vals["mirrored_a"]-vals["mirrored_b"]
            gap_delta=mirror_gap-original_gap
            sign_flip=(original_gap*mirror_gap<0)
            abs_disagreement=abs(gap_delta)
            relative=relative_distance_abs(original_gap,mirror_gap)
            direct_action_deltas={
                "candidate_a":vals["mirrored_a"]-vals["original_a"],
                "candidate_b":vals["mirrored_b"]-vals["original_b"],
            }
        else:
            original_gap=mirror_gap=gap_delta=abs_disagreement=relative=sign_flip=None
            direct_action_deltas=None
        data["per_depth"][str(depth)]={
            "forced_root_measurements":rows,
            "original_A_minus_B_cp_or_null":original_gap,
            "mirrored_A_minus_B_cp_or_null":mirror_gap,
            "mirrored_gap_minus_original_gap_cp_or_null":gap_delta,
            "absolute_gap_disagreement_cp_or_null":abs_disagreement,
            "martin_relative_distance_over_two_gaps_or_null":relative,
            "strict_opposite_sign_or_null":sign_flip,
            "original_action_score_mirror_deltas_or_null":direct_action_deltas,
            "four_real_source_queries":True,
            "total_actual_source_nodes":sum(r["nodes"] for r in rows.values()),
            "finite_search_not_proof_of_engine_bug":True,
        }
    return data


def predeclared_cases():
    """Two fixed historical-independent positions, preselected before engine."""
    start=chess.Board()
    mid=chess.Board()
    for u in ("e2e4","e7e5","g1f3","b8c6"):
        mid.push_uci(u)
    return (
        ("canonical_initial_e4_vs_d4",start.fen(en_passant="fen"),"e2e4","d2d4"),
        ("short_opening_history_Bc4_vs_d4",mid.fen(en_passant="fen"),"f1c4","d2d4"),
    )


def run(engine):
    cases=[case_analysis(fen,a,b,engine,case_id)
           for case_id,fen,a,b in predeclared_cases()]
    total_queries=len(cases)*len(DEPTHS)*4
    if len(cases)!=2 or total_queries!=24:
        raise ValueError("P5_HOLD_24_ORIGINAL_SOURCE_QUERIES")
    return {
        "schema":SCHEMA,"source":"Stockfish16 classical",
        "native_source_commit":ENGINE_GIT_COMMIT,
        "previous_historical_postselection_used":False,
        "case_selection_is_fixed_and_not_prospective_benchmark":True,
        "original_primary_metamorphic_replication":MARTIN_DRIVE,
        "faithfulness_framework_original_primary":JACOVI_DRIVE,
        "scope":"mirror relation on forced-root contrastive gaps, two boards x two actions x two symmetries x three depths",
        "no_bug_claim_from_any_finite_depth_disagreement":True,
        "no_source_decision_causality_established":True,
        "no_exact_full_original_martin_replication":True,
        "number_of_real_engine_forced_root_queries":total_queries,
        "cases":cases
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--engine",required=True)
    p.add_argument("--out",required=True)
    a=p.parse_args()
    with chess.engine.SimpleEngine.popen_uci(a.engine,timeout=120) as engine:
        if ("stockfish" not in engine.id.get("name","").lower()
            or not {"Threads","Hash","Use NNUE"}.issubset(engine.options)):
            raise ValueError("P5_HOLD_NOT_ORIGINAL_STOCKFISH")
        engine.configure({"Threads":1,"Hash":16,"Use NNUE":False})
        data=run(engine)
    data["source_binary_sha256"]=sha(a.engine)
    file=Path(a.out)
    file.parent.mkdir(parents=True,exist_ok=True)
    file.write_text(json.dumps(data,ensure_ascii=False,indent=2,sort_keys=True,
                               allow_nan=False)+"\n",encoding="utf-8")
    for case in data["cases"]:
        print("C3X_P5_ACTUAL_METAMORPHIC_RESULTS",case["case_id"],{
            depth:{k:case["per_depth"][depth][k] for k in
                   ("original_A_minus_B_cp_or_null",
                    "mirrored_A_minus_B_cp_or_null",
                    "mirrored_gap_minus_original_gap_cp_or_null",
                    "strict_opposite_sign_or_null")}
            for depth in map(str,DEPTHS)},flush=True)
    print("C3X_P5_ACTUAL_24_FORCED_SOURCE_SHA",sha(file),flush=True)


if __name__=="__main__":
    main()
