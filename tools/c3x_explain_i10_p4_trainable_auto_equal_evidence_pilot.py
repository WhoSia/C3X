"""Native-source game-disjoint *proxy-task* tiny model training/evaluation.

Two previously exposed games are intentionally split by WHOLE GAME.
No external teacher text, no real Queen/Cui/CCC inference, no human labels.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from c3x_explain.ecl_auto import run_auto
from c3x_explain.ecl_tiny_selector import train,weak_proxy_examples,benchmark,select,QUESTIONS
from tools.c3x_explain_i10_p1_historical_cases import CASES

def evidence_export(row:dict,game_id:str)->dict:
    e=row["ecl"]
    return {
       "schema":"c3x-ecl-i10-p4-strong-rival-equal-information-contract-v1",
       "source_game_group":game_id,
       "original_ply":row["ply"],"fen":row["source_fen"],
       "played_uci":e["played_uci"],
       "original_source_rival":row["source_rival"],
       "source_rival_rows":row["source_evidence"],
       "C3X_evidence_atom_refs":[a["atom_ids"] for a in e["claims"]],
       "same_compiled_eligible_claims":[
           {k:c[k] for k in ("claim_id","kind","text_ko","atom_ids","authority")}
           for c in e["claims"]],
       "known_scopes":["ENGINE_RANKING_AT_RECORDED_DEPTH_ONLY","SINGLE_REPLAYED_ENGINE_LINE_ONLY"],
       "tested_model_implementations":{"P3_STATIC":"EXECUTED","P4_TRAINED_LINEAR":"EXECUTED",
                                      "QUEEN":"NOT_EXECUTED","CUI":"NOT_EXECUTED","CCC":"NOT_EXECUTED"},
       "model_input_policy":"BOTH_PUBLIC_ENGINE_EVIDENCE_EQUAL_AND_ORIGINAL_FULL_TRACE_EQUAL_ARMS_REQUIRED_FOR_CLAIMS",
       "engine_search_tree_raw_original":"NOT_CAPTURED_BEYOND_RECORDED_MULTIPV",
       "human_utility":None,
       "causal_source_event_certs":[],
       "benchmark_requires_real_models":True
    }

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--engine",required=True)
    ap.add_argument("--out-dir",required=True)
    ap.add_argument("--moments",type=int,default=5)
    ap.add_argument("--scout-depth",type=int,default=9)
    ap.add_argument("--pair-depth",type=int,default=12)
    args=ap.parse_args()
    root=Path(args.out_dir);root.mkdir(parents=True,exist_ok=True)
    results=[]
    for case in CASES:
        x=run_auto(case["pgn"],args.engine,max_moments=args.moments,min_ply=10,
            scout_depth=args.scout_depth,pair_depth=args.pair_depth,
            disable_nnue=True,question="ENGINE_PREFERENCE")
        x["source_game_id"]=case["id"]
        (root/f"preoutcome-{case['id']}.json").write_text(json.dumps(x,indent=2,ensure_ascii=False)+"\n")
        results.append(x)
    tr,te=results
    train_packets=[r["ecl"] for r in tr["result_rows"] if r["selection"]["decision"]=="EMIT_BOUNDED_CONVENTIONAL"]
    test_rows=[r for r in te["result_rows"] if r["selection"]["decision"]=="EMIT_BOUNDED_CONVENTIONAL"]
    test_packets=[r["ecl"] for r in test_rows]
    if not train_packets or not test_packets:
        raise ValueError("NOT_ENOUGH_ADMITTED_GAME_DISJOINT_SOURCE_EVIDENCE")
    proxy=weak_proxy_examples(train_packets,CASES[0]["id"])
    model=train(proxy,epochs=100,rate=0.35)
    report=benchmark(test_packets,model,CASES[1]["id"])
    report["model_training_game"]=CASES[0]["id"]
    report["eval_game"]=CASES[1]["id"]
    report["training_weak_proxy_examples"]=len(proxy)
    report["development_preexposed_not_independent_sample"]=True
    report["train_automatic_decisions_emitted"]=tr["emitted"]
    report["train_automatic_source_attempts"]=tr["attempted"]
    report["eval_automatic_decisions_emitted"]=te["emitted"]
    report["eval_automatic_source_attempts"]=te["attempted"]
    report["train_eligible_count"]=tr["preselection"]["eligible_count"]
    report["eval_eligible_count"]=te["preselection"]["eligible_count"]
    report["historical_p3_default_short_game_auto_emit"]=0
    report["historical_p3_default_short_game_auto_attempted"]=3
    report["historical_p3_comparison_directly_equivalent"]=False
    report["methodological_warning"]="Question-type weak-proxy match, not chess pedagogy or model choice accuracy"
    (root/"tiny-model-trained-game-A.json").write_text(json.dumps(model,indent=2)+"\n")
    (root/"tiny-model-game-disjoint-proxy-comparison.json").write_text(json.dumps(report,indent=2)+"\n")
    exports=[evidence_export(r,CASES[1]["id"]) for r in test_rows]
    (root/"strong-rivals-equal-evidence-NOT-RUN.json").write_text(json.dumps(exports,indent=2,ensure_ascii=False)+"\n")
    baseline=report["proxy_comparison"]["P3_STATIC_TOP_PRIORITY_BASELINE"]
    learned=report["proxy_comparison"]["P4_TRAINED_9_PARAMETER_PROXY_SELECTOR"]
    print("I10_P4_GAME_GROUP_SPLIT",len(train_packets),len(test_packets),
          "P3_PROXY",baseline,"P4_PROXY",learned)
    print("I10_P4_SOURCE_COVERAGE",
          tr["emitted"],tr["attempted"],tr["preselection"]["eligible_count"],
          te["emitted"],te["attempted"],te["preselection"]["eligible_count"])
    print("I10_P4_ACTUAL_QUEEN_CUI_CCC_EXECUTED",False)
    print("I10_P4_HUMAN_UTILITY_OBSERVED",False)

if __name__=="__main__":main()
