#!/usr/bin/env python3
"""Strict reproducible cross-season C3X 0.14 chess operator transport audit.

S29 discovery 40 roots and source-frozen S28 64 roots with sham-verified native
five-arm SF16 interventions. Test post-hoc law-majority predictions honestly,
identity overlaps and 2x2 root bestmove nonmonotone arm patterns.
"""
from __future__ import annotations
import argparse,collections,hashlib,json
from pathlib import Path

DISCOVERY="336d9fcd5d5023a73824dc95b9399570b2786bfcb527dd2e1a42b6471a6a7374"
TRANSFER="86bcbaa3e5e974834b35c35e387b1255e6369ca708c65f8d260d44faa359acd9"
S29_SOURCE="cfb2c4b0631959cfcdd5bf1eb098f7b41c40468a7b22e434e95ef8936cc43ead"
S28_SOURCE="1152473ed8d8793361f922434c75c7da2b9a58e0aa68a59466fc65179d6ac5e4"
TARGETS=[
 ("PAWN","QUEEN","DIAGONAL","ZERO",False),
 ("PAWN","QUEEN","FILE","NONZERO",False),
 ("ROOK","QUEEN","DIAGONAL","ZERO",False),
 ("PAWN","ROOK","FILE","NONZERO",False)]
ARMS=("SEE_UNMASK","WQ_OWN","WQ_ENEMY","WQ_BOTH")
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def require(c,m):
    if not c:raise RuntimeError(m)
def law(x):return tuple(x[k] for k in ("pinned_piece","pinning_piece","axis","legal_pinned_piece_mobility","can_legally_capture_pinner"))
def signature_s29(row):return "".join("1" if row["direct_software_causal_branch_vs_OFF"][k]["bestmove_changed"] else "0" for k in ARMS)
def profile(row):return row["five_arm_chess_search_outcome_signature"]
def synergy(s):return s[1]=="0" and s[2]=="0" and s[3]=="1"
def antagonism(s):return (s[1]=="1" or s[2]=="1") and s[3]=="0"
def main():
    ap=argparse.ArgumentParser()
    for k in ("s29","s28","s29-source","s28-source","out"):ap.add_argument("--"+k,required=True)
    a=ap.parse_args()
    for field,want in [("s29",DISCOVERY),("s28",TRANSFER),("s29_source",S29_SOURCE),("s28_source",S28_SOURCE)]:
        require(sha(getattr(a,field))==want,"FROZEN_ORIGINAL_SHA_MISMATCH_"+field)
    d=json.loads(Path(a.s29).read_bytes())
    t=json.loads(Path(a.s28).read_bytes())
    so=json.loads(Path(a.s29_source).read_bytes())
    sn=json.loads(Path(a.s28_source).read_bytes())
    x=d["all_40_root_worlds_and_5_original_native_treatment_runs"]
    y=t["all_64_S28_source_new_season_native_classic_causal_five_arm_outcomes"]
    require(len(x)==40 and len(y)==64,"SOURCE_GAME_SAMPLE_COUNT")
    require(d["untreated_OFF_whole_native_search_output_and_site_counters_exact_vs_previous"]=="40/40","S29_SHAM_FAIL")
    require(t["all_64_OFF_source_unmodified_original_engine_UCI_equivalence"] and
            t["all_320_two_cold_treatment_conditions_exact"]=="320/320","S28_SHAM_FAIL")
    require(not sn["is_independent_provider"] and sn["zero_Stockfish_outputs_used_for_source_selection"],"SOURCE_DESIGN_LEAKAGE")
    byS29=collections.defaultdict(list);byS28=collections.defaultdict(list)
    for row in x:byS29[law(row["root_pin_law_subtype"])].append(signature_s29(row))
    for row in y:byS28[law(row["source_law_pin_subtype"])].append(profile(row))
    S29_full={law(json.loads(k)) for k in so["all_chess_law_subtype_frequency"]}
    S28_full={law(json.loads(k)) for k in sn["all_S28_law_feature_counts"]}
    require(len(S29_full)==31 and len(S28_full)==32,"CHESS_LAW_SOURCE_CLASS_DRIFT")
    comparison=[]
    for key in TARGETS:
        old=byS29[key];new=byS28[key]
        require(old and new,"PRIMARY_TARGET_MATCHED_GAME_SOURCE_NOT_FOUND")
        rank=collections.Counter(old)
        maj=sorted(rank.items(),key=lambda p:(-p[1],p[0]))[0][0]
        comparison.append({"law":list(key),"source_S29_n":len(old),
                           "source_S29_patterns":dict(collections.Counter(old)),
                           "S29_retrospective_most_common_pattern":maj,
                           "new_S28_n":len(new),
                           "new_S28_patterns":dict(collections.Counter(new)),
                           "exact_retrospective_law_majority_hits_in_new_S28":sum(s==maj for s in new),
                           "always_0000_null_model_hits_in_new_S28":sum(s=="0000" for s in new),
                           "S28_patterns_already_seen_in_same_S29_law_group":sum(s in set(old) for s in new)})
    # Avoid double counting two distinct historical games that reached the
    # EXACT same six-field FEN; game replicates != position replicates.
    fenGroup=collections.defaultdict(list)
    for row in y:fenGroup[row["exact_original_position_FEN"]].append(row)
    duplicated=[{"FEN":fen,"source_games":[z["source_game_id"] for z in rs],
                "profiles":[profile(z) for z in rs],
                "exact_treatment_all_arm_outputs_same":
                    all(z["all_5_arms_native_source_outcomes"]==rs[0]["all_5_arms_native_source_outcomes"]
                        for z in rs)}
                for fen,rs in fenGroup.items() if len(rs)>1]
    require(len(fenGroup)==63 and len(duplicated)==1 and
            duplicated[0]["exact_treatment_all_arm_outputs_same"],"NEW_S28_DUPLICATED_FEN_SOURCE_INTEGRITY")
    old_fn={(z["board_six_field_FEN"],z["pinned_square"]) for z in so["all_legal_pin_witnesses_source_only"]}
    new_fn={(z["board_six_field_FEN"],z["pinned_square"]) for z in sn["actual_source_only_64_chess_pin_selected_worlds"]}
    require(not(old_fn&new_fn),"LEAKING_S29_FEN_INTO_S28_SOURCE_TRANSFER")
    sh=collections.Counter(signature_s29(row) for row in x)
    th=collections.Counter(profile(row) for row in y)
    uniq=collections.Counter(profile(rs[0]) for rs in fenGroup.values())
    hit=sum(z["exact_retrospective_law_majority_hits_in_new_S28"] for z in comparison)
    null=sum(z["always_0000_null_model_hits_in_new_S28"] for z in comparison)
    exact=sum(z["S28_patterns_already_seen_in_same_S29_law_group"] for z in comparison)
    denom=sum(z["new_S28_n"] for z in comparison)
    require(denom==32 and hit==6 and null==16 and exact==9,"CHESS_TRANSFER_DIAGNOSTIC_NOT_REPRODUCED")
    out={"schema":"c3x-014-S29-discovery-S28-season-disjoint-legal-pin-contextual-operator-fiber-negative-transport-court-v1",
     "formal_research_stage":"C3X 0.14","proposed_C3X_015_NOT_OPEN":True,
     "data_integrity":{"S29_discovery_sham":"PASS","S28_native_704_pristine_sham":"PASS",
        "S29_discovery_40_JSON_SHA256":DISCOVERY,"S28_source_transfer_64_JSON_SHA256":TRANSFER,
        "S29_legal_chess_source_SHA256":S29_SOURCE,"S28_legal_chess_source_SHA256":S28_SOURCE,
        "original_game_source_season_difference":"S29 vs S28 same TCEC provider, same Stockfish16 engine",
        "shared_exact_sixfield_FEN_pinned_square_positions_between_original_S29_702_and_new_S28_64":0,
        "new_S28_distinct_source_game_ids":len({z["source_game_id"] for z in y}),
        "new_S28_distinct_sixfield_FEN":len(fenGroup),
        "S28_exact_position_replicates":duplicated},
     "chess_law_feature_ontology":{
        "source_S29_all_observed_composite_law_types":len(S29_full),
        "source_S28_all_observed_composite_law_types":len(S28_full),
        "shared_law_composites":len(S29_full&S28_full),
        "types_observed_only_in_S29":len(S29_full-S28_full),
        "types_observed_only_in_S28":len(S28_full-S29_full),
        "union_composite_types":len(S29_full|S28_full),
        "these_are_stockfish_latent_concepts":False},
     "software_intervention_bestmove_profiles":{
        "four_bit_arm_order":ARMS,"S29_original_40_source_hist":dict(sorted(sh.items())),
        "S28_64_new_game_hist":dict(sorted(th.items())),
        "S28_63_unique_FEN_hist":dict(sorted(uniq.items())),
        "seen_in_both_seasons":sorted(set(sh)&set(th)),
        "S28_only_fourbit_patterns":sorted(set(th)-set(sh)),
        "S29_only_fourbit_patterns":sorted(set(sh)-set(th)),
        "union_distinct_response_profiles":len(set(sh)|set(th)),
        "Boolean_code_branch_output_minimal_combined_WeakQueen_only_0001_or_1001":{
          "S29_game_roots":sum(n for k,n in sh.items() if synergy(k)),
          "S28_game_roots":sum(n for k,n in th.items() if synergy(k))},
        "nonmonotone_WeakQueen_arm_response_one_role_alone_but_not_both":{
          "S29_game_roots":sum(n for k,n in sh.items() if antagonism(k)),
          "S28_game_roots":sum(n for k,n in th.items() if antagonism(k))}
     },
     "repeated_S29_law_subtypes_tested_in_S28_source_season":comparison,
     "retrospective_law_only_4group_majority_prediction_on_new_S28":{
        "source_S29_law_group_majority_predictor_is_posthoc_not_preregistered":True,
        "new_S28_target_game_roots":denom,
        "S29_law_group_most_common_4bit_signature_exact_matches":hit,
        "trivial_always_0000_matches":null,
        "S28_patterns_present_somewhere_in_same_S29_law_group":exact,
        "law_majority_predictor_loses_to_trivial_no_change_baseline":hit<null},
     "scientific_claims":{
        "same_native_source_operator_intervention_arm_effect_family_detected_on_new_season":"PASS",
        "eleven_016_possible_responses_exact_law_type_mapping_transports":"FAIL_OR_WEAK, NOT STABLE",
        "true_source_game_provider_independent_transfer":"NOT TESTED",
        "new_engine_family_transfer":"NOT TESTED",
        "root_PIN_specific_causal_concept_identified":"NOT IDENTIFIED",
        "NNUE_learned_latent_tactical_concept_identified":"NOT TESTED",
        "human_faithful_explanation_benefit":"NOT TESTED"},
     "evidence_limits":[
        "S29 group majority predictor is an ex-post interpretive stress diagnostic; it was NOT precommitted as a numerical forecast before S28 results.",
        "No statistical p-values because repeated within-season engine tournament positions are not independent randomized draws.",
        "The global SEE/WeakQueen source interventions can fire in unrelated descendant search positions, not solely original pinned root piece.",
        "The exact same root FEN appears in two S28 game IDs; their measured outputs are exactly identical. Counting them as independent position replications is invalid.",
        "Operator response 4bit patterns may vary with completed search depth, alpha-beta windows, evaluation path, node counts, unrelated pieces.",
        "Four target law groups deliberately prioritised during score-blind S28 sampling, so frequency of any response across 64 is not a population prevalence.",
        "35 observed chess LAW feature tuples across two seasons are not 35 stored Stockfish NNUE features."
     ],
     "next":"Within C3X 0.14 measure POSITION/SEARCH-CONTEXT-mediators for S29/S28 same-law mismatches, stratify by actual nodes, TT window, evaluation call routing, then require independent provider or engine family and root tactical object-specific intervention before opening 0.15."}
    f=Path(a.out);f.parent.mkdir(parents=True,exist_ok=True)
    f.write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n")
    print("C3X014_CROSS_SEASON_PIN_OPERATOR_FIBER_TRANSFER_AND_NEGATIVE_COURT_VERDICT",json.dumps({
        "source_legal_law_types_union":len(S29_full|S28_full),
        "S29_40_profiles":len(sh),"S28_64_profiles":len(th),
        "observed_4bit_union":len(set(sh)|set(th)),
        "within_law_retrospective_S29_predictor":str(hit)+"/"+str(denom),
        "trivial_no_effect_baseline":str(null)+"/"+str(denom),
        "S29_set_law_profile_coverage_on_S28":str(exact)+"/"+str(denom),
        "source_overlap_exact":len(old_fn&new_fn),
        "S28_distinct_positions":len(fenGroup),
        "WQ_synergy":out["software_intervention_bestmove_profiles"]["Boolean_code_branch_output_minimal_combined_WeakQueen_only_0001_or_1001"],
        "WQ_antagonism":out["software_intervention_bestmove_profiles"]["nonmonotone_WeakQueen_arm_response_one_role_alone_but_not_both"]}),flush=True)
if __name__=="__main__":main()
