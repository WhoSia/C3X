#!/usr/bin/env python3
"""C3X 0.14 actual Stockfish16 native pin source operator runtime court.

Strict side-effect sham: 160 source-frozen evaluator runs must exactly reproduce
the previous uninstrumented actual SF16 UCI score, nodes, PV, and best move.
Counters describe WHOLE SEARCH TREE, not root pin causal contribution.
"""
from __future__ import annotations
import argparse,collections,hashlib,json
from pathlib import Path
from c3x_014_official_pin_NNUE_vs_classic_phenotype_court import native
from c3x_014_pin_native_trace_fields import PIN_FIELDS

SOURCE_SHA="cfb2c4b0631959cfcdd5bf1eb098f7b41c40468a7b22e434e95ef8936cc43ead"
BASE_SHA="2eed2dc94832364345721a66608eb72360d1667c6dc763ff90b4fa6241db4084"
MODES=("NNUE","CLASSICAL")
SIGNATURE_KEYS=("legal_pinned_rejected","see_masked_recapture_episodes",
                "classical_mobility_nonzero_pin_blockers",
                "classical_WeakQueen_own_blockers",
                "classical_WeakQueen_enemy_blockers")
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def demand(x,msg):
    if not x:raise RuntimeError(msg)
def subtype(w):return json.dumps(w["source_chess_law_subtype"],sort_keys=True)
def signature(tr):return tuple(int(tr[k]>0) for k in SIGNATURE_KEYS)
def assert_sources(src,bas):
    demand(src["schema"]=="c3x-014-official-TCEC-S29-chess-law-absolute-pin-subtype-census-before-engine-scores-v1","SOURCE_SCHEMA")
    demand(src["source_only_selected_sample_size"]==40 and not src["engine_outputs_used_for_selection"],"SOURCE_NO_SCORE")
    demand(bas["schema"]=="c3x-014-source-frozen-king-absolute-pin-native-NNUE-vs-classical-phenotype-court-v1","BASE_SCHEMA")
    demand(bas["actual_native_unmodified_SF16_engine_processes"]==160 and len(bas["all_actual_source_pin_native_evaluation_cells"])==40,"BASE_160")
def test_trace(t):
    demand(set(t)==set(PIN_FIELDS),"NATIVE_PIN_FIELD_SCHEMA")
    demand(all(isinstance(v,int) and v>=0 for v in t.values()),"INVALID_SOURCE_COUNTERS")
    demand(t["legal_pinned_aligned"]+t["legal_pinned_rejected"]==t["legal_pinned_tests"],"NATIVE_LEGAL_GUARD_PARTITION")
    demand(t["legal_pinned_tests"]<=t["legal_normal_tests"],"LEGAL_PIN_EXCEEDS_TOTAL")
    demand(t["see_masked_recapture_episodes"]<=t["see_pinners_guard"],"SEE_MASK_OVERCOUNT")
    demand(t["see_masked_attackers"]>=t["see_masked_recapture_episodes"],"SEE_MASK_ATTACKER_LOST")
    demand(t["classical_mobility_nonzero_pin_blockers"]<=t["classical_mobility_calls"],"MOBILITY_CALL_SITES")
    demand(t["classical_mobility_pin_blocker_piece_count"]>=t["classical_mobility_nonzero_pin_blockers"],"MOBILITY_PIN_BLOCKERS")
    demand(t["classical_WeakQueen_hits"]<=t["classical_WeakQueen_tests"],"WEAKQUEEN_HIT_OVERFLOW")
    demand(t["classical_WeakQueen_own_blockers"]+t["classical_WeakQueen_enemy_blockers"]>=t["classical_WeakQueen_hits"],"WEAKQUEEN_RAY_ROLE_ACCOUNTING")
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source",required=True)
    p.add_argument("--prior-160",required=True)
    p.add_argument("--engine",required=True)
    p.add_argument("--out",required=True)
    a=p.parse_args()
    demand(sha(a.source)==SOURCE_SHA,"FROZEN_40_CHESS_PIN_SHA")
    demand(sha(a.prior_160)==BASE_SHA,"PRIOR_NATIVE_160_SHA")
    src=json.loads(Path(a.source).read_bytes())
    baseline=json.loads(Path(a.prior_160).read_bytes())
    assert_sources(src,baseline)
    rows=[]
    originals=baseline["all_actual_source_pin_native_evaluation_cells"]
    worlds=src["source_only_selected_witnesses"]
    for index,(w,old) in enumerate(zip(worlds,originals),1):
        for k,v in (("source_game_index","game_index"),("source_original_FEN","board_six_field_FEN"),("pinned_square","pinned_square")):
            demand(old[k]==w[v],"CROSS_ARTIFACT_SOURCE_ROW_MISMATCH_"+k)
        results={}
        for mode in MODES:
            probes=[native(a.engine,w["source_game_history_uci"],w["pinned_square"],mode,True) for cold in (1,2)]
            demand(probes[0]==probes[1],"NATIVE_PIN_TRACE_COLD_DRIFT_"+str(index)+"_"+mode)
            native_result=probes[0]
            test_trace(native_result["native_pin_trace"])
            stripped={k:v for k,v in native_result.items() if k!="native_pin_trace"}
            if stripped!=old["nnue_and_classical"][mode]:
                differences={k:{"prior":old["nnue_and_classical"][mode].get(k),"new":stripped.get(k)}
                    for k in set(stripped)|set(old["nnue_and_classical"][mode])
                    if stripped.get(k)!=old["nnue_and_classical"][mode].get(k)}
                print("C3X014_PIN_BASELINE_DRIFT",index,mode,json.dumps(differences,sort_keys=True),flush=True)
                raise RuntimeError("INSTRUMENTATION_CHANGED_ACTUAL_SF16_UCI_RESULTS")
            results[mode]=native_result
        law=subtype(w)
        row={"source_game_index":w["game_index"],"source_round":w["source_round"],
             "source_legal_FEN":w["board_six_field_FEN"],
             "source_pin_square":w["pinned_square"],"source_pin_legal_subtype":w["source_chess_law_subtype"],
             "source_game_history_uci":w["source_game_history_uci"],
             "root_pin_law_features":{
                  "legal_moves":w["pinned_piece_legal_moves_count"],
                  "pseudolegal_moves":w["pinned_piece_pseudolegal_moves_count"],
                  "pinner_capture":w["pinned_piece_can_legally_capture_pinner"]},
             "source_law_subtype_key":law,
             "original_nnue_vs_classical_root_move_diff":
                  old["bestmove_changed_between_evaluation_implementations"],
             "native_runtime_by_mode":results,
             "whole_tree_operation_presence_by_mode":{
                   m:{k:int(results[m]["native_pin_trace"][k]>0) for k in SIGNATURE_KEYS} for m in MODES},
             "whole_tree_operation_per_1000_search_nodes_by_mode":{
                   m:{k:round(1000*results[m]["native_pin_trace"][k]/max(1,results[m]["nodes"]),3)
                      for k in PIN_FIELDS} for m in MODES},
             "operation_grain":"whole tree, not a causal attribution to the root pinned piece"}
        rows.append(row)
        print("C3X014_NATIVE_PIN_OPERATOR_REAL",index,
              "source_game",w["game_index"],"pinned",w["pinned_piece"],
              "NNUE_signature",signature(results["NNUE"]["native_pin_trace"]),
              "CLASSICAL_signature",signature(results["CLASSICAL"]["native_pin_trace"]),
              "NNUE_root",results["NNUE"]["bestmove"],
              "CLASSICAL_root",results["CLASSICAL"]["bestmove"],flush=True)
    grouped=collections.defaultdict(list)
    for row in rows:grouped[row["source_law_subtype_key"]].append(row)
    repeated={k:r for k,r in grouped.items() if len(r)>1}
    demand(len(grouped)==30 and len(repeated)==4 and sum(map(len,repeated.values()))==14,
           "FROZEN_40_REPEATED_SUBTYPE_GEOMETRY_DRIFT")
    comparisons={}
    for group,lst in repeated.items():
        demand(len({r["source_game_index"] for r in lst})==len(lst),"REPEATED_GAMES_ARE_NOT_DISJOINT")
        sby_mode={mode:{
            "binary_operational_signatures":list(sorted({signature(row["native_runtime_by_mode"][mode]["native_pin_trace"]) for row in lst})),
            "distinct_binary_signature_count":
                len({signature(row["native_runtime_by_mode"][mode]["native_pin_trace"]) for row in lst}),
            "root_moves_differ_between_source_positions":
                len({row["native_runtime_by_mode"][mode]["bestmove"] for row in lst})>1,
            "seen_masked_SEE_cases":sum(row["native_runtime_by_mode"][mode]["native_pin_trace"]["see_masked_recapture_episodes"]>0 for row in lst),
            "seen_WeakQueen_cases":sum(row["native_runtime_by_mode"][mode]["native_pin_trace"]["classical_WeakQueen_hits"]>0 for row in lst)}
            for mode in MODES}
        comparisons[group]={"different_source_games":len(lst),"game_ids":[r["source_game_index"] for r in lst],
            "modes":sby_mode,
            "compared_object":"whole searched tree; classification of root pin cause NOT identified"}
    alln={k:sum(row["native_runtime_by_mode"]["NNUE"]["native_pin_trace"][k] for row in rows) for k in PIN_FIELDS}
    allc={k:sum(row["native_runtime_by_mode"]["CLASSICAL"]["native_pin_trace"][k] for row in rows) for k in PIN_FIELDS}
    f={
      "schema":"c3x-014-genuine-SF16-pin-legality-SEE-mobility-WeakQueen-runtime-branches-frozen40-v1",
      "formal_research_unit":"C3X 0.14","internal_checkpoint_not_formal_P_substage":True,
      "source_only_40_sha256":SOURCE_SHA,"untouched_native_160_baseline_sha256":BASE_SHA,
      "native_instrumented_binary_sha256":sha(a.engine),
      "source_game_groups":len({r["source_game_index"] for r in rows}),
      "frozen_source_pin_worlds":40,"engine_evaluation_arms":list(MODES),
      "native_instrumented_SF16_processes":160,"cold_repeats_per_arm":2,
      "exact_match_against_prior_unmodified_SF16_UCI_cells":80,
      "identical_full_native_trace_cold_pairs":80,
      "observed_law_subtype_keys":len(grouped),
      "repeated_legal_law_subtype_groups":len(repeated),
      "eligible_repeated_game_source_cases":14,
      "whole_search_tree_totals":{"NNUE":alln,"CLASSICAL":allc},
      "within_same_chess_law_subtype_operative_signature_cases":comparisons,
      "within_repeated_law_groups_where_native_binary_tree_signature_differs":{
          mode:sum(z["modes"][mode]["distinct_binary_signature_count"]>1 for z in comparisons.values())
          for mode in MODES},
      "per_40_source_root_case_exact_output_and_trace":rows,
      "sealed_P1_four_case_games_accessed":False,
      "native_branch_observation_verified":True,
      "causal_root_pin_subtype_identified":False,
      "stockfish_learned_latent_pin_subtype_identified":False,
      "scientific_limits":[
        "Direct source-native counters are real executed conditions but aggregate ALL explored search nodes, not events necessarily caused by this particular ROOT pinned square.",
        "40 source-selected pin worlds comprise 30 distinct law subtype tuples; only four repeated groups (14 positions) allow source-game-distinct within-law comparison.",
        "Original Stockfish16 C++ classic mobility and WeakQueen only used in classic evaluator mode. NNUE internal features are not instrumented here.",
        "Search tree/node count differs between NNUE and CLASSICAL and across source positions; differences in tree signatures are NOT isolated pin causal mediators.",
        "Even an observed same-law different search signature can reflect other position features, not necessarily a distinct built-in strategy category.",
        "Cold repeats verify technical determinism, NOT 160 independent source games.",
        "Cross-source prospective chess-concept generality and faithful human explanation remain HOLD."
      ]}
    out=Path(a.out);out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(f,ensure_ascii=False,indent=2)+"\n")
    print("C3X014_SF16_PIN_NATIVE_BRANCH_COURT_VERDICT",json.dumps({
      "worlds":40,"new_engine_processes":160,"prior_exact_UCI_cells":80,
      "cold_native_trace_exact":80,"repeated_law_groups":len(repeated),
      "eligible_same_law_positions":14,"within_law_tree_signature_diverse":f["within_repeated_law_groups_where_native_binary_tree_signature_differs"],
      "NNUE_site_totals":alln,"CLASSICAL_site_totals":allc}),flush=True)
if __name__=="__main__":main()
