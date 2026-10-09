#!/usr/bin/env python3
"""C3X0.14 season-disjoint TCEC S28 native SF16 pin-operator transfer.

Original S29 40-world five-arm 11-response signatures DISCLOSED and frozen
before *any* source-native S28 evaluation. Source-only frozen 64 original
S28 legal histories; original unpatched OFF reference and 5 surgical arms.
No king-pin legal move generator modification. Root pin causality NOT proven.
"""
from __future__ import annotations
import argparse,collections,hashlib,json
from pathlib import Path
from c3x_014_official_pin_NNUE_vs_classic_phenotype_court import native

SOURCE_SHA="1152473ed8d8793361f922434c75c7da2b9a58e0aa68a59466fc65179d6ac5e4"
DISCOVERY_S29={
 "0000":22,"0001":2,"0010":2,"0011":1,"0100":1,"0101":1,
 "1000":2,"1001":2,"1011":1,"1101":1,"1111":5}
MODES={"OFF":0,"SEE_UNMASK":1,"WQ_OWN":2,"WQ_ENEMY":4,"WQ_BOTH":6}
INVERSE_MAP={"SEE_UNMASK":"SEE_unmask_fired","WQ_OWN":"WQ_own_skip_fired","WQ_ENEMY":"WQ_enemy_skip_fired"}
SUBTYPES=[
 ("PAWN","QUEEN","DIAGONAL","ZERO",False),
 ("PAWN","QUEEN","FILE","NONZERO",False),
 ("ROOK","QUEEN","DIAGONAL","ZERO",False),
 ("PAWN","ROOK","FILE","NONZERO",False)
]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def insist(x,msg):
    if not x:raise RuntimeError(msg)
def plain(v):return {k:z for k,z in v.items() if k not in ("native_pin_trace","pin_causal_intervention")}
def tkey(law):
    return (law["pinned_piece"],law["pinning_piece"],law["axis"],
            law["legal_pinned_piece_mobility"],law["can_legally_capture_pinner"])
def main():
    ap=argparse.ArgumentParser()
    for field in ("source","original-engine","treated-engine","out"):
        ap.add_argument("--"+field,required=True)
    a=ap.parse_args()
    insist(sha(a.source)==SOURCE_SHA,"S28_PROSPECTIVE_SOURCE_ONLY_FROZEN64_SHA_MISMATCH")
    data=json.loads(Path(a.source).read_bytes())
    worlds=data["actual_source_only_64_chess_pin_selected_worlds"]
    insist(len(worlds)==64 and data["source_game_distinctness"]==64
           and data["zero_Stockfish_outputs_used_for_source_selection"],"S28_SOURCE_GATE_NOT_SCORE_BLIND")
    source_game_ids=[x["game_index"] for x in worlds]
    insist(len(set(source_game_ids))==64,"FROZEN_S28_64_GAME_INDEPENDENCE_MISMATCH")
    out=[]
    for i,w in enumerate(worlds,1):
        # Genuine original Stockfish16 binary, no C3X instrumentation/logic.
        clean=native(a.original_engine,w["source_game_history_uci"],w["pinned_square"],"CLASSICAL")
        arms={}
        for name,tag in MODES.items():
            pair=[native(a.treated_engine,w["source_game_history_uci"],
                w["pinned_square"],"CLASSICAL",
                capture_pin_trace=True,pin_intervention=name)
                for _ in range(2)]
            insist(pair[0]==pair[1],"S28_SF16_SOURCE_ARM_COLD_DRIFT_"+str(i)+"_"+name)
            p=pair[0]
            fire=p["pin_causal_intervention"]
            insist(fire["mode"]==tag,"S28_CAUSAL_ARM_ID_MISMATCH_"+name)
            if name=="OFF":
                insist(plain(p)==clean,"S28_SOURCE_UNPATCHED_STOCKFISH16_SHAM_MISMATCH")
                insist(all(fire[x]==0 for x in ("SEE_unmask_fired","WQ_own_skip_fired","WQ_enemy_skip_fired")),
                    "S28_OFF_ARM_ACTUALLY_MUTATED")
            if name=="SEE_UNMASK":insist(fire["WQ_own_skip_fired"]==fire["WQ_enemy_skip_fired"]==0,"SEE_WQ_CROSS_ARM")
            if name=="WQ_OWN":insist(fire["SEE_unmask_fired"]==fire["WQ_enemy_skip_fired"]==0,"OWN_WQ_CROSS_ARM")
            if name=="WQ_ENEMY":insist(fire["SEE_unmask_fired"]==fire["WQ_own_skip_fired"]==0,"ENEMY_WQ_CROSS_ARM")
            if name=="WQ_BOTH":insist(fire["SEE_unmask_fired"]==0,"BOTH_SEE_CROSS_ARM")
            arms[name]=p
        base=arms["OFF"]
        changes={}
        for name in list(MODES)[1:]:
            r=arms[name];fire=r["pin_causal_intervention"]
            actual_fired=(fire[INVERSE_MAP[name]] if name in INVERSE_MAP else fire["WQ_own_skip_fired"]+fire["WQ_enemy_skip_fired"])
            modified={k:bool(r[k]!=base[k]) for k in
                      ("bestmove","score_kind","score_flag","value_root_stm","nodes","pv")}
            if actual_fired==0:
                insist(not any(modified.values()),"S28_SOURCE_EVENT_NOT_FIRED_YET_UCI_CHANGED_"+name)
            changes[name]={
               "fired":actual_fired,"bestmove_changed":modified["bestmove"],
               "score_changed":any(modified[k] for k in ("score_kind","score_flag","value_root_stm")),
               "nodes_changed":modified["nodes"],"PV_changed":modified["pv"],
               "original_bestmove":base["bestmove"],"treated_bestmove":r["bestmove"],
               "original_score":base["value_root_stm"],"treated_score":r["value_root_stm"]}
        sig="".join("1" if changes[name]["bestmove_changed"] else "0"
                    for name in ("SEE_UNMASK","WQ_OWN","WQ_ENEMY","WQ_BOTH"))
        row={"source_season":28,"source_game_id":w["game_index"],
            "source_round":w["source_round"],
            "source_law_pin_subtype":w["source_chess_law_subtype"],
            "exact_original_position_FEN":w["board_six_field_FEN"],
            "source_original_full_history_uci":w["source_game_history_uci"],
            "exact_root_pinned_square":w["pinned_square"],
            "five_arm_chess_search_outcome_signature":sig,
            "native_direct_source_operator_firing_and_root_effect":changes,
            "all_5_arms_native_source_outcomes":arms,
            "original_unpatched_SF16_OFF_verified":True,
            "S28_source_game_selection_used_SF16_scores":False}
        out.append(row)
        print("C3X014_SOURCE_DISJOINT_S28_NATIVE_PIN_CAUSAL_WORLD",i,
              "original_game",w["game_index"],
              "law",tkey(w["source_chess_law_subtype"]),
              "sig",sig,
              "fire",dict((k,v["fired"]) for k,v in changes.items()),flush=True)
    hist=collections.Counter(r["five_arm_chess_search_outcome_signature"] for r in out)
    seen=set(DISCOVERY_S29);new=set(hist)-seen
    target_detail=[]
    for j,k in enumerate(SUBTYPES,1):
        subset=[r for r in out if tkey(r["source_law_pin_subtype"])==k]
        target_detail.append({"prior_014_S29_target_index":j,"law_type":k,
            "observed_S28_game_roots":len(subset),
            "nonzero_root_bestmove_any_arm":sum(r["five_arm_chess_search_outcome_signature"]!="0000" for r in subset),
            "S28_root_response_signatures":dict(collections.Counter(r["five_arm_chess_search_outcome_signature"] for r in subset)),
            "S29_original_40_worlds_have_same_law_type":True,
            "new_source_phenotypic_response_not_root_PIN_subtype_certified":True})
    summary={}
    for arm in ("SEE_UNMASK","WQ_OWN","WQ_ENEMY","WQ_BOTH"):
        f=[r["native_direct_source_operator_firing_and_root_effect"][arm] for r in out]
        summary[arm]={"actual_source_native_treatments_with_firing":sum(z["fired"]>0 for z in f),
             "actual_source_native_firing_events":sum(z["fired"] for z in f),
             "bestmove_changed":sum(z["bestmove_changed"] for z in f),
             "score_changed":sum(z["score_changed"] for z in f),
             "nodes_changed":sum(z["nodes_changed"] for z in f),
             "PV_changed":sum(z["PV_changed"] for z in f),
             "nonfired_strict_negative_control_worlds":sum(z["fired"]==0 for z in f)}
    claim={
       "schema":"c3x-014-sf16-S28-season-disjoint-64-pin-law-root-five-arm-causal-software-sensitivity-transfer-v1",
       "formal_study":"C3X 0.14","proposed_015_NOT_OPEN":True,
       "independent_source_season":28,"same_TCEC_provider_as_discovery_S29":True,
       "frozen_source_S28_json_SHA256":SOURCE_SHA,
       "source_selected_before_S28_engine_outputs":True,
       "official_native_SF16_commit":"68e1e9b3811e16cad014b590d7443b9063b3eb52",
       "actual_native_uninstrumented_stockfish_OFF_reference_processes":64,
       "actual_native_five_arm_Cplusplus_source_modified_engine_processes":640,
       "sum_actual_SF16_processes":704,
       "distinct_root_source_games":64,
       "all_64_OFF_source_unmodified_original_engine_UCI_equivalence":True,
       "all_320_two_cold_treatment_conditions_exact":"320/320",
       "zero_fire_any_UCI_change_falsifier_gated":True,
       "modified_chess_legality":False,
       "discovering_S29_patterns":"AFTER they were frozen before this S28 trial",
       "prespecified_original_S29_fourbit_bestmove_response_profile_counts":DISCOVERY_S29,
       "actual_S28_all_fourbit_bestmove_profile_counts":dict(sorted(hist.items())),
       "original_S29_profile_set_size":len(seen),
       "S28_profiles_already_seen_in_S29":sorted(set(hist)&seen),
       "S28_profiles_NOT_seen_in_S29":sorted(new),
       "total_distinct_S28_profiles":len(hist),
       "S28_root_worlds_with_any_direct_source_operator_root_bestmove_effect":sum(r["five_arm_chess_search_outcome_signature"]!="0000" for r in out),
       "S28_roles_together_alter_bestmove_but_each_alone_does_not":sum(
           r["five_arm_chess_search_outcome_signature"][1:]== "001" for r in out),
       "prespecified_four_S29_pin_law_groups_tested_on_new_S28_games":target_detail,
       "actual_engine_branch_treatment_results":summary,
       "all_64_S28_source_new_season_native_classic_causal_five_arm_outcomes":out,
       "P1_procedurally_sealed_holdout_examined":False,
       "claim_11_latent_pin_strategic_concepts":False,
       "claim_isolated_root_pin_causality":False,
       "claim_proven_provider_or_new_engine_transport":False,
       "scope_limits":[
         "A new season of TCEC is source GAME disjoint from Season29 but uses same provider, environment and engine. This is partial seasonal transport.",
         "Source-only S28 roots were selected with source-side quotas on the four previously discovered repeated law types, not through engine outcome selection.",
         "Entire search SEE and WeakQueen code intervention may fire on many descendant positions unrelated to root pinned piece. New season replication is evidence of software sensitivity type transfer, not chess root pin causal mediation.",
         "Same legal subtype root worlds differ in many other board properties, pawn structures, material, king exposure, move ordering and search nodes.",
         "An output pattern is not an individual NNUE latent unit, strategy category or proof of faithful explanations.",
         "Cold repeats are technical reproducibility not 640 independent games.",
         "All source code original GPL and unpatched native binary baseline must be archived and cross-checked."
       ]}
    dst=Path(a.out);dst.parent.mkdir(parents=True,exist_ok=True)
    dst.write_text(json.dumps(claim,ensure_ascii=False,indent=2)+"\n")
    print("C3X014_SEASON_DISJOINT_S28_REAL_SF16_FIVE_ARM_TRANSFER_COURT_VERDICT",json.dumps({
         "season":28,"root_games":64,"SF16_native_engine_processes":704,
         "all_320_treatment_pairs":"PASS","all_64_unmodified_OFF_shams":"PASS",
         "profiles_S29":len(seen),"profiles_S28":len(hist),
         "shared_patterns":sorted(set(hist)&seen),
         "new_patterns":sorted(new),
         "S28_hist":dict(hist),
         "source_operator_arm_summary":summary,
         "four_prespecified_law_groups":target_detail}),flush=True)
if __name__=="__main__":main()
