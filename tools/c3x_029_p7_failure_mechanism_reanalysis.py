"""C3X 0.29-P7: reproduce arithmetic and mechanism falsifiers from original repo receipts.

Run inside WhoSia/C3X checkout:
  python tools/c3x_029_p7_failure_mechanism_reanalysis.py

This is READ-ONLY evidence reanalysis, not a fresh native Stockfish trial or
305-param model retraining. Fail-closed original source paths are required.
"""
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
P = {
    "K4": "c3x/receipts/c3x-019-feb-four-single-return-restoration-root-choice-null-and-beta-rescue-20261010.json",
    "B": "c3x/receipts/c3x-020-B-native-minimal-second-return-root-choice-rescue-20261010.json",
    "C": "c3x/receipts/c3x-020-C-native-alpha-gate-discontinuity-game3-six-target-20261010.json",
    "TWIC": "c3x/receipts/c3x-022-P2-TWIC-puzzle32-stageB-literal-UCI-falsification-and-depth-20261010.json",
    "MLP": "c3x/receipts/c3x-explain-i10-p5-2026-olympiad-original-native305-and-semantic-boundary-20261013.json"
}
def load():
    return {k:json.loads((ROOT / f).read_text(encoding="utf-8")) for k,f in P.items()}
def court(d):
    k,b,c,t,m=(d[z] for z in ("K4","B","C","TWIC","MLP"))
    ck=k["cases"]
    assert len(ck)==4 and k["verdicts"]["K4_FINAL_ROOT_RESCUE"]=="FAIL_0_OF_4"
    assert all(v["REPAIR_return"]==v["F_return"] and v["REPAIR_bestmove"]==v["FIRST_bestmove"]!=v["F_bestmove"] for v in ck)
    bb=b["case3"]; ca=c["case3"]
    assert bb["UCI_bestmove"]["SECOND_ONLY"]==bb["UCI_bestmove"]["F"]
    assert bb["UCI_bestmove"]["A0"]==bb["UCI_bestmove"]["FIRST"]
    assert bb["score_cp"]["FIRST"]==bb["score_cp"]["SECOND_ONLY"]
    assert bb["child_return_gate"]["FIRST_return"]>bb["child_return_gate"]["alpha"]
    assert bb["child_return_gate"]["F_return"]<=bb["child_return_gate"]["alpha"]
    alpha=ca["alpha"]; ladder=ca["points"]
    assert len(ladder)==6
    assert all((x["value"]>alpha)==bool(x["gate"]) for x in ladder)
    assert set(x["bestmove"] for x in ladder if not x["gate"])=={ca["F_bestmove"]}
    assert set(x["bestmove"] for x in ladder if x["gate"])=={ca["V_bestmove"]}
    assert any(x["value"]==alpha for x in ladder) and any(x["value"]==alpha+1 for x in ladder)
    tw=t["per_ecology"]["twic"]; cm=tw["flip_confusion"]
    n=tw["eligible_and_delivered_physical_first_reader_role_cells"]
    assert sum(cm.values())==n==64
    assert cm["TP"]+cm["FN"]==tw["actual_flip_role_cells"]
    assert cm["TP"]+cm["FP"]==tw["predicted_flip_role_cells"]
    assert cm["TN"]+tw["specific_move_exact_when_actual_flip"]==tw["literal_post_intervention_UCI_exact_matches"]
    third=[x for x in t["distinct_mechanisms"] if "Third" in x.get("interpretation","") or "third" in x.get("interpretation","")]
    assert {x["twic_game"] for x in third}>={4,10}
    ml=m["tiny_model"]; p=ml["training_actual_human_reply_matches_source_pv"]/ml["training_labeled_positions"]
    y=ml["testing_actual_human_reply_matches_source_pv"]
    nt=ml["testing_labeled_positions"]
    constant=(y*(1-p)**2+(nt-y)*p**2)/nt
    seen=ml["eval_305param_UNCALIBRATED_brier"]
    assert abs(constant-ml["eval_constant_training_prevalence_brier"])<1e-12
    assert seen>constant
    return {
      "status":"RECOMPUTED_ARCHIVED_EVIDENCE_NOT_NATIVE_RERUN",
      "K4":{"return_restored":len(ck),"bestmove_restored":sum(x["REPAIR_bestmove"]==x["F_bestmove"] for x in ck)},
      "game3":{"first_return_fail_but_second_return_rescues":True,"alpha":alpha,
        "one_cp_boundary":[alpha,alpha+1],
        "first_nodes":bb["nodes"]["FIRST"],"second_nodes":bb["nodes"]["SECOND_ONLY"],
        "first_and_second_same_reported_cp":True},
      "TWIC":{"eligible_role_cells":n,"flip_detection_accuracy":(cm["TP"]+cm["TN"])/n,
        "exact_move_accuracy":tw["literal_post_intervention_UCI_exact_matches"]/n,
        "nochange_baseline_accuracy":tw["no_flip_majority_exact_matches"]/n,
        "binary_precision":cm["TP"]/(cm["TP"]+cm["FP"]),
        "actual_flips":cm["TP"]+cm["FN"],
        "true_flip_exact_UCI_correct":tw["specific_move_exact_when_actual_flip"],
        "observed_third_move_games":sorted({x["twic_game"] for x in third})},
      "MLP":{"train_probability":p,"test_empirical_rate":y/nt,
        "baseline_brier_recomputed":constant,"model_brier_archived":seen,
        "difference":seen-constant,
        "parameters_per_training_row":ml["trainable_scalars"]/ml["training_labeled_positions"],
        "per_example_weights_and_scores_replayed":False},
      "limits":["TWIC roles share 16 games; not independent n=64 games",
        "305 individual fitted predictions not in receipt",
        "0.20-B/C one postselected development game",
        "No novel native or transfer experiment in this read-only computation"]}
if __name__=="__main__":
    print(json.dumps(court(load()),ensure_ascii=False,indent=2,sort_keys=True))
