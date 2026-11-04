#!/usr/bin/env python3
"""Compare three informational methods on original exposed 16 real game replies.

Important: 1-reply next-move accuracy and 3-reply coverage have DIFFERENT
denominators of predictions per game and are not a matched-budget win.
"""
import argparse
import hashlib
import json
from pathlib import Path

SOURCE_SHA = "6520672aabab7f525872169085f19bdd81e27a4473f0c58ba9c9aa428937104c"


def need(ok, err):
    if not ok:
        raise ValueError("C3X_P32_REPLY_COMPETITOR_" + err)


def row_views(source, experiment):
    need(source["source_game_sha256"] == experiment["game_sha256"], "SOURCE_IDENTITY")
    need(source["id"] == experiment["id"], "CASE_IDENTITY")
    plies = source["full_original_mainline_uci"]
    i = source["source_ply_before_original_move"]
    need(i + 1 < len(plies), "NO_ACTUAL_NEXT_REPLY")
    original_played = plies[i]
    actual_reply = plies[i + 1]
    need(original_played == experiment["original_move_uci"], "PLAYED_MISMATCH")
    original = [a for a in experiment["candidates"] if a["is_source_played"]]
    need(len(original) == 1 and original[0]["root_uci"] == original_played,
         "NO_UNIQUE_FORCED_PLAYED")
    a = original[0]
    pv = a["forced_root_pv_uci"]
    need(pv and pv[0] == original_played, "PV_ROOT_MISMATCH")
    predictions = [r["reply_uci"] for r in a["opponent_reply_top3"]]
    need(len(predictions) == len(set(predictions)), "DUPLICATE_REPLY")
    need(predictions, "NO_OPPONENT_REPLY")
    return {
        "id": source["id"],
        "game_sha256": source["source_game_sha256"],
        "played_move_uci": original_played,
        "actual_next_opponent_move_uci": actual_reply,
        "source_exposed": True,
        "method_A_forced_root_PV": {
            "root": original_played, "next_move_prediction": pv[1] if len(pv) > 1 else None,
            "root_score": a["forced_root_value_cp_or_mate_scaled"], "PV": pv
        },
        "method_B_simple_one_reply_plan_JSON": {
            "root": original_played, "immediate_material_delta_cp": a["immediate_material_delta_cp"],
            "best_opponent_reply_uci": a["best_opponent_reply"],
            "material_after_best_reply_cp": a["opponent_reply_top3"][0]["material_after_opponent_reply_cp"],
            "root_pov_value_after_best_reply": a["best_opponent_reply_value_cp_or_mate_scaled"]
        },
        "method_C_top3_conditional_plan": {
            "root": original_played,
            "reply_branches": [{"reply_uci":r["reply_uci"],
                                "root_pov_value_cp_or_mate_scaled":r["root_pov_cp_or_mate_scaled"],
                                "mover_next_uci":r.get("mover_followup_uci"),
                                "material_after_reply_cp":r.get("material_after_opponent_reply_cp"),
                                "material_after_mover_followup_cp":r.get("material_after_mover_followup_cp")}
                               for r in a["opponent_reply_top3"]]
        },
        "historical_response_metrics": {
            "A_forced_pv_exact_next": len(pv)>1 and pv[1] == actual_reply,
            "B_simple_plan_best_reply_exact": a["best_opponent_reply"] == actual_reply,
            "C_top3_rank_of_actual_reply": (predictions.index(actual_reply)+1
                                            if actual_reply in predictions else None),
            "C_top3_covers_actual_reply": actual_reply in predictions
        }
    }


def compare(source, original_run):
    need(original_run["source_sha256"] == SOURCE_SHA, "BAD_RUN_SOURCE_SHA")
    cases = original_run["cases"]
    old = source["selected"]
    need(len(old) == len(cases) == 16, "DENOMINATOR")
    rows = [row_views(x,y) for x,y in zip(old,cases)]
    coverage = {
        "n_original_exposed_source_games": len(rows),
        "A_forced_root_PV_one_reply_exact": sum(x["historical_response_metrics"]["A_forced_pv_exact_next"] for x in rows),
        "B_one_reply_plan_exact":sum(x["historical_response_metrics"]["B_simple_plan_best_reply_exact"] for x in rows),
        "C_three_reply_coverage":sum(x["historical_response_metrics"]["C_top3_covers_actual_reply"] for x in rows),
        "C_actual_rank_one":sum(x["historical_response_metrics"]["C_top3_rank_of_actual_reply"]==1 for x in rows),
        "C_actual_rank_two":sum(x["historical_response_metrics"]["C_top3_rank_of_actual_reply"]==2 for x in rows),
        "C_actual_rank_three":sum(x["historical_response_metrics"]["C_top3_rank_of_actual_reply"]==3 for x in rows),
        "C_actual_missing_from_top3": [x["id"] for x in rows if not x["historical_response_metrics"]["C_top3_covers_actual_reply"]],
        "strong_claim_status": "NO_MATCHED_COMPUTE_NO_INDEPENDENT_HELDOUT_NO_SUPERIORITY"
    }
    return {
        "schema":"c3x029-p32-original-human-opponent-reply-three-method-source-exposed-v1",
        "original_c3x018_source_sha256": SOURCE_SHA,
        "study_status":"historical_source_exposed_development_not_new_holdout",
        "target":"exact historical human opponent move, NOT engine best-reply truth",
        "noncomparability":"A and B predict ONE move; C covers THREE. Coverage is not an equal-cardinality accuracy, and C costs more engine search.",
        "aggregate":coverage,
        "cases":rows
    }


def main():
    p = argparse.ArgumentParser()
    for k in ("source","native","out"):
        p.add_argument("--"+k,required=True)
    a=p.parse_args()
    raw=Path(a.source).read_bytes()
    need(hashlib.sha256(raw).hexdigest()==SOURCE_SHA, "SOURCE_SHA")
    result=compare(json.loads(raw),json.loads(Path(a.native).read_bytes()))
    Path(a.out).write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n")
    print("C3X_P32_REPLY_THREE_METHODS",result["aggregate"])


if __name__=="__main__":
    main()
