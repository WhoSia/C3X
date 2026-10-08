#!/usr/bin/env python3
"""P8-R3 retrospective adversarial chess concept signs and collateral changes.

This explicitly is post-outcome exploratory, not prospectively falsified science.
"""
import argparse,hashlib,json
from collections import defaultdict
from pathlib import Path
import chess
from c3x_explain.concepts import candidate_delta
from harness.c3x_013_p6r1_birth_rival_support import births

def sign(x):return (x>0)-(x<0)

def audit(case):
    board=chess.Board(case["root_fen"])
    assert board.is_valid()
    p=case["pair_true_false"]
    a,b=[chess.Move.from_uci(p[z]) for z in ("a","b")]
    assert a in board.legal_moves and b in board.legal_moves
    newborn=births(board,a)
    assert newborn and not births(board,b)
    assert newborn==case["newly_passed_pawns"]
    own="white" if board.turn else "black"
    own_birth=sum(z["color"]==own for z in newborn)
    opp_birth=sum(z["color"]!=own for z in newborn)
    pred=1 if own_birth and not opp_birth else (-1 if opp_birth and not own_birth else None)
    features=candidate_delta(board,a,b)
    delta=features["played_minus_alternative"]
    feature_other={k:v for k,v in delta.items()
                   if k not in ("own_passed_pawn_count","opp_passed_pawn_count")}
    engines={}
    for name in ("Stockfish","Ethereal_classical"):
        values=[case["engine_panels"][name][str(d)]["gap_true_minus_false_cp"]
                for d in (8,12,16)]
        valid=all(v is not None for v in values)
        one_sign=valid and len(set(sign(v) for v in values))==1 and sign(values[0])!=0
        engines[name]={"gaps_true_minus_false":values,"stable":one_sign,
                       "sign":sign(values[0]) if one_sign else None,
                       "naive_prediction_matched":pred==sign(values[0]) if one_sign and pred is not None else None}
    return {"broadcast":case["broadcast"],"game_url":case["game_url"],
            "source_rank":case["source_rank"],"ply":case["ply"],"pair":p,
            "original_side":own,"newborn":newborn,
            "own_birth_count":own_birth,"opponent_birth_count":opp_birth,
            "naive_own_benefits_opponent_harms_sign":pred,
            "feature_changes":delta,"other_monitored_feature_changes":feature_other,
            "geometry_differs_other_than_pawn_status":a.from_square!=b.from_square,
            "engines":engines,"causal_concept_mediation":False}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--p8r2-result",required=True)
    p.add_argument("--out",required=True)
    a=p.parse_args()
    raw=Path(a.p8r2_result).read_bytes()
    d=json.loads(raw)
    assert d["schema"]=="c3x-013-p8-r2-frozen-birth-two-engine-v1"
    assert d["counts"]["pairs_original"]==8
    rows=[audit(q) for q in d["results"]]
    assert len(rows)==8
    # Multiplicity across source groups and root comparisons cannot be ignored.
    by_group=defaultdict(list)
    for row in rows:
        by_group[row["broadcast"]].append(row)
    group_scores={k:{"pair_count":len(v),"all_naive_concordant_both_engines":all(
        x["engines"]["Stockfish"]["naive_prediction_matched"] is True and
        x["engines"]["Ethereal_classical"]["naive_prediction_matched"] is True for x in v),
         "any_counterexample":any(
             x["engines"]["Stockfish"]["naive_prediction_matched"] is False or
             x["engines"]["Ethereal_classical"]["naive_prediction_matched"] is False for x in v)}
        for k,v in by_group.items()}
    out={"schema":"c3x-013-p8-r3-retrospective-concept-rival-v1",
         "status":"RETROSPECTIVE_AFTER_P8R2_OUTCOME_NOT_CONFIRMATORY",
         "origin_P8R2_sha256":hashlib.sha256(raw).hexdigest(),
         "source_group_denominator":32,"support_group_count":len(by_group),
         "observed_pair_rows":len(rows),
         "original_side_own_birth_pairs":sum(x["own_birth_count"]>0 and x["opponent_birth_count"]==0 for x in rows),
         "opponent_birth_pairs":sum(x["opponent_birth_count"]>0 and x["own_birth_count"]==0 for x in rows),
         "naive_rule_testable":sum(x["naive_own_benefits_opponent_harms_sign"] is not None for x in rows),
         "naive_rule_agreements_at_stockfish_depth16":sum(
             x["engines"]["Stockfish"]["naive_prediction_matched"] is True for x in rows),
         "naive_rule_counterexamples_at_stockfish_depth16":sum(
             x["engines"]["Stockfish"]["naive_prediction_matched"] is False for x in rows),
         "monitored_non_passed_feature_counterexamples":sum(
             bool(x["other_monitored_feature_changes"]) for x in rows),
         "group_level":group_scores,
         "rows":rows,
         "no_causal_mechanism_identified":True,
         "human_outcome_measured":False,"C3X_014":"CANDIDATE_ONLY_NO_NAME"}
    Path(a.out).parent.mkdir(parents=True,exist_ok=True)
    Path(a.out).write_text(json.dumps(out,indent=2,ensure_ascii=False)+"\n")
    print("P8R3_ADVERSARIAL_CONCEPT_RULE",out["naive_rule_agreements_at_stockfish_depth16"],
          "/",out["naive_rule_testable"],"counterexamples",out["naive_rule_counterexamples_at_stockfish_depth16"])
    print("P8R3_CONFOUNDING_FEATURE_PAIRS",out["monitored_non_passed_feature_counterexamples"])
    assert len(rows)==8 and len(by_group)==4
    assert out["no_causal_mechanism_identified"]
if __name__=="__main__":main()
