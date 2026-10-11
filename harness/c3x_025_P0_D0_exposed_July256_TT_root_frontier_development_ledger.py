#!/usr/bin/env python3
"""C3X0.25-P0-D0 SHA-gated, source-true 256-game exposed July causal evidence court.
READ ONLY. Strictly descriptive historical data; no causal TT->SEE or M5 validation.
"""
import argparse,glob,hashlib,json
from collections import Counter,defaultdict
from pathlib import Path

STAGE_SHA="90bb3537f140ec7f52f8d9115add1ba88ff293705217fd75784da55343d86c65"
FORECAST_SHA="7a4c152362171c65a9417f38de89e81ab776a4c14718fbd213411c155bb4094d"
SOURCE_SHA="d2c50a1293e68c3feb8571d1ee1be6ba1a7ee539a12dd1a98378adfa9b54fb58"
SCORE_SHA="1c94973c1eaa9fca82e7a1caaaa614d4b711839df465ef7dc42e7f28fd46f7be"
SHARD_SHAS=(
"76eb58229a97cb9b39fb9b007233b2c30042b509274b866f25bf05c5aae9336e",
"68dc175dffd09bf4772918fba76a1766c70c876c98459cf5233e39b4adc1b27d",
"f3fd2097fcbb30a444c752c64ea37138a9048b1e97959042005f749ec2b9a2dc",
"4807f4dc023153a9c45b9b2891f84968f3ae61328364704780c3e8319bd43792")
REGISTRY="c3x/forecasts/c3x-024-P4-July2025-256-source-game-SHA-human-Git-seal-before-native-20261011.json"
SEAL="c3x/forecasts/c3x-024-P4-July2025-256game-1024role-six-model-literal-UCI-before-FIRST-human-Git-seal-20261011.json"
MODELS=("M0","M1","M2_depth11","M3_v1","M3_v2","M4_survivor")
ORDERS=("O","F")
ROLES=("STRICT","BROAD")

def get(path,expected):
    raw=Path(path).read_bytes()
    digest=hashlib.sha256(raw).hexdigest()
    if digest!=expected:raise ValueError("C3X025_SOURCE_OR_TREATMENT_EXACT_SHA_DRIFT:"+str(path))
    return json.loads(raw)
def tally(rows,field):
    out=defaultdict(lambda:{"eligible":0,"HOLD":0,"contact":0,"flips":0,"stable":0,
                           "M4_alt":0,"M4_alt_correct":0,"M4_alt_wrong":0,"M0_correct":0,
                           "M4_correct":0,"passive_SEE_observed_eligible":0,
                           "source_TT_value_use_recorded_eligible":0})
    for z in rows:
        value=z[field]
        k=json.dumps(value,sort_keys=True,separators=(",",":"))
        a=out[k]
        if z["status"]=="HOLD":
            a["HOLD"]+=1
            continue
        a["eligible"]+=1;a["contact"]+=int(z["contact"])
        a["flips"]+=int(z["flip"]);a["stable"]+=int(not z["flip"])
        a["M4_alt"]+=int(z["alt"])
        a["M4_alt_correct"]+=int(z["alt"] and z["M4_correct"])
        a["M4_alt_wrong"]+=int(z["alt"] and not z["M4_correct"])
        a["M0_correct"]+=int(z["M0_correct"]);a["M4_correct"]+=int(z["M4_correct"])
        a["passive_SEE_observed_eligible"]+=int(z["passive_SEE"])
        a["source_TT_value_use_recorded_eligible"]+=int(z["source_TT_use"])
    return [{"source_feature":json.loads(k),**v} for k,v in sorted(out.items())]

def audit(stage,forecast,shards,score,registry,seal):
    if stage["source_sha256"]!=SOURCE_SHA or stage["schema"]!="c3x024-P4-July2025-256game-preFIRST-untreated-source-genealogy-v1" or stage["TT_or_SEE_treatment_executed"] is not False:
        raise ValueError("C3X025_STAGEA_NOT_ORIGINAL_NO_FIRST")
    if forecast["schema"]!="c3x024-P4-July2025-256-source-only-untreated-six-model-exact-UCI-FORECAST-NO-TREATMENT-v1" or forecast["TT_FIRST_interventions_seen"]!=0 or forecast["SEE_boolean_interventions_seen"]!=0:
        raise ValueError("C3X025_FORECAST_NOT_ORIGINAL_PREFIRST")
    if registry["source_game_count"]!=256 or registry["source_only_derived_JSON_SHA256"]!=SOURCE_SHA:
        raise ValueError("C3X025_FROZEN_256_SOURCE_SHA_LOCK_MISSING")
    if seal["stageA_untreated_raw_SHA256"]!=STAGE_SHA or seal["forecast_raw_SHA256"]!=FORECAST_SHA or seal["source_JSON_SHA256"]!=SOURCE_SHA or seal["phase"]!="BEFORE_ANY_JULY_NATIVE_TT_FIRST_TREATED_OUTCOME":
        raise ValueError("C3X025_HUMAN_LITERAL_PRE_FIRST_CHAIN_MISMATCH")
    if score["schema"]!="c3x024-P4-July2025-256-game-prospective-after-human-Git-presealed-six-models-v1" or score["original_literally_Git_sealed_predictions_SHA256"]!=FORECAST_SHA:
        raise ValueError("C3X025_P4_PROSPECTIVE_NEGATIVE_OUTCOME_INVALID")
    if len(shards)!=4 or any(v["shard"]!=i or v["case_range"]!=[i*64+1,(i+1)*64] or
         v["model_forecast_source_SHA256"]!=FORECAST_SHA or v["untreated_stageA_SHA256"]!=STAGE_SHA or
         v["treated_SEE_Boolean_flips"]!=0 for i,v in enumerate(shards)):
        raise ValueError("C3X025_FOUR_EXACT_TREATED_SOURCE_SHARDS_MISSING")
    cases=stage["ecologies"]["july2025_broadcast"]["cases"]
    forecast_cases=forecast["cases"]
    human_rows=seal["ordered_games_literal_rows"]
    actual=[c for sh in shards for c in sh["all_cells"]]
    scored=score["source_only_deidentified_game_results"]
    if not(len(cases)==len(actual)==len(forecast_cases)==len(human_rows)==len(scored)==256):
        raise ValueError("C3X025_SOURCE_256_DENOMINATOR_MISMATCH")
    rows=[];games=[];first_flip_development_samples=[];dev_case52=None
    seen_hold=seen_contact=seen_flip=seen_alternative=0;correct_m0=correct_m4=0
    for i,(ca,fo,human,act,sc) in enumerate(zip(cases,forecast_cases,human_rows,actual,scored),1):
        frozen_sha=registry["ordered_selected_source_game_sha256"][i-1]
        if ca["id"]!=i or ca["source_sha256"]!=frozen_sha or fo["game_id"]!=i or fo["source_game_sha256"]!=frozen_sha or human[0]!=i or human[1]!=frozen_sha or act["game_id"]!=i or sc["game_id"]!=i:
            raise ValueError("C3X025_GAME_SOURCE_SHA_OR_SEQUENCE_DRIFT")
        if len(act["roles"])!=4 or len(human[2])!=4:
            raise ValueError("C3X025_MISSING_NESTED_ROLE")
        m0game=m4game=flip_game=contact_game=0
        O=ca["worlds"]["O"]["baseline_UCI"]["bestmove"]
        F=ca["worlds"]["F"]["baseline_UCI"]["bestmove"]
        for k,(order,role) in enumerate((o,r) for o in ORDERS for r in ROLES):
            ref=ca["worlds"][order];src=ref["roles"][role]
            pred=fo["root_orders"][order][role];observed=act["roles"][k]
            h=human[2][k]
            if observed["root_order"]!=order or observed["role"]!=role or
               h!=[order,role,pred["status"],*(pred[x] for x in MODELS),
                   int(pred["M3_v1_trigger"]),int(pred["M3_v2_trigger"]),
                   int(pred["M4_trigger"]),pred["M4_reason"]]:
                raise ValueError("C3X025_EXACT_SIX_MODEL_PREFIRST_LITERAL_DRIFT")
            if ref["source_trace_censored"] and src["status"]=="FIRST_SOURCE_PAIR_PRE_OUTCOME":
                raise ValueError("C3X025_CENSORED_SOURCE_CANNOT_BE_TREATED")
            hold=src["status"]!="FIRST_SOURCE_PAIR_PRE_OUTCOME"
            if hold!=(observed["status"]=="PRESEALED_INELIGIBLE_NO_FIRST_READER"):
                raise ValueError("C3X025_PRESEALED_HOLD_TREATMENT_LEAK")
            if hold:
                seen_hold+=1
                if observed["treated_bestmove"] is not None or observed["cold_pairs_checked"]!=0:
                    raise ValueError("C3X025_HOLD_TREATED")
                rows.append({"game_id":i,"order":order,"role":role,"status":"HOLD",
                   "source_trace_censored":ref["source_trace_censored"],
                   "root_O_F_disagree":O!=F,
                   "native_source_reason":src["status"],"contact":False,"flip":False,
                   "M0_correct":False,"M4_correct":False,"alt":False,
                   "passive_SEE":False,"source_TT_use":False})
                continue
            if observed["status"]!="REAL_NATIVE_PHYSICAL_TT_FIRST" or not observed["source_TT_first_contact"] or observed["cold_pairs_checked"]!=2:
                raise ValueError("C3X025_NATIVE_REAL_FIRST_MUST_BE_OBSERVED_FOR_ALL_ELIGIBLE")
            if observed["sham_bestmove"]!=ref["baseline_UCI"]["bestmove"] or observed["predicted"]["M0"]!=pred["M0"] or observed["predicted"]["M4_survivor"]!=pred["M4_survivor"]:
                raise ValueError("C3X025_ORIGINAL_SHAM_UCI_PRESALE_DRIFT")
            if int(observed["correct"]["M0"])!=int(observed["treated_bestmove"]==pred["M0"]) or int(observed["correct"]["M4_survivor"])!=int(observed["treated_bestmove"]==pred["M4_survivor"]):
                raise ValueError("C3X025_ORIGINAL_SCORE_EXACT_UCI_INCONSISTENT")
            seen_contact+=1
            flip=observed["actual_root_flip"] is True
            alt=pred["M4_survivor"]!=pred["M0"]
            seen_flip+=int(flip);seen_alternative+=int(alt)
            m0=int(observed["correct"]["M0"]);m4=int(observed["correct"]["M4_survivor"])
            correct_m0+=m0;correct_m4+=m4;m0game+=m0;m4game+=m4
            flip_game+=int(flip);contact_game+=1
            depths=pred.get("depth8to11_original_same_order_UCI",{})
            ladder=[depths.get(str(d)) for d in (8,9,10,11)]
            seen_ladders=[v for v in ladder if v is not None]
            base=pred["M0"]
            d11=depths.get("11")
            tt_native=src.get("root_candidate_native")
            leader12=ref["depth_leaders"].get("12",{}).get("native_leader")
            value_uses=ref.get("passive_native_TT_value_use_witnesses",[])
            see=[e for e in ref["passive_first32_SEE_events"] if e["kind"]=="witness"]
            evidence={"game_id":i,"order":order,"role":role,"status":"ELIGIBLE",
               "root_O_F_disagree":O!=F,
               "target_matches_depth12_leader":(tt_native==leader12 if tt_native is not None and leader12 is not None else None),
               "depth11_vs_12_disagree":d11!=base if d11 is not None else None,
               "same_order_prior_depth11_support":(sum(x==d11 for x in seen_ladders[:3]) if d11 is not None else None),
               "same_order_depth8to11_observed":len(seen_ladders),
               "M4_original_rule_reason":pred["M4_reason"],
               "source_trace_censored":ref["source_trace_censored"],
               "passive_SEE_prefix_censored":ref["passive_SEE_witness_censored"],
               "source_SEE_witness_count":len(see),
               "source_TT_value_use_witness_count":len(value_uses),
               "source_native_first_blocks":observed["selected_native_reader_blocks"],
               "source_physical_writer_integrity_verified":bool(observed["source_physical_writer_integrity"]),
               "contact":True,"flip":flip,"alt":alt,
               "M0_correct":bool(m0),"M4_correct":bool(m4),
               "passive_SEE":bool(see),"source_TT_use":bool(value_uses)}
            rows.append(evidence)
            if alt:
                dev_case52={"game_id":i,"order":order,"role":role,
                    "M0_UCI":base,"M4_UCI":pred["M4_survivor"],
                    "actual_final_UCI":observed["treated_bestmove"],"observed_original_untreated_UCI":observed["sham_bestmove"],
                    "M4_rule":pred["M4_reason"],"original_O_vs_F_untreated_disagree":O!=F,
                    "source_native_target_matches_depth12":evidence["target_matches_depth12_leader"],
                    "same_order_untreated_depth_leaders_8_to_11":depths,
                    "depth11_support_8_to_10":evidence["same_order_prior_depth11_support"],
                    "original_source_SEE_witness_count":len(see),
                    "source_TT_value_use_witness_count":len(value_uses),
                    "original_source_SEE_censored":ref["passive_SEE_witness_censored"],
                    "original_opposite_F_trace_censored":ca["worlds"]["F" if order=="O" else "O"]["source_trace_censored"],
                    "first_selected_native_reader_block_count":observed["selected_native_reader_blocks"],
                    "final_root_flip":flip,"claim":"DEVELOPMENT_ONLY_OBSERVED_SWITCH_WRONG_NOT_CAUSAL_MEDIATOR"}
            if flip and len(first_flip_development_samples)<12:
                first_flip_development_samples.append({"game_id":i,"order":order,"role":role,
                    "sham_UCI":observed["sham_bestmove"],"treated_UCI":observed["treated_bestmove"],
                    "M4_UCI":pred["M4_survivor"],"source_order_disagree":O!=F,
                    "passive_SEE_prefix_censored":ref["passive_SEE_witness_censored"],
                    "source_TT_value_use_witness_count":len(value_uses)})
        if sc["contact_role_cells"]!=contact_game or sc["root_bestmove_flips"]!=flip_game or
           sc["correct_role_counts"]["M0"]!=m0game or sc["correct_role_counts"]["M4_survivor"]!=m4game:
            raise ValueError("C3X025_MERGED_P4_GAME_SCORE_NOT_REPRODUCED")
        games.append({"game_id":i,"role_contacts":contact_game,"flip_roles":flip_game,
                      "M0_correct":m0game,"M4_correct":m4game,"source_O_F_untreated_disagree":O!=F})
    if (seen_hold,seen_contact,seen_flip,correct_m0,correct_m4,seen_alternative)!=(12,1012,96,916,915,1):
        raise ValueError("C3X025_ORIGINAL_256_NEGATIVE_FACTS_NOT_REPRODUCED")
    if len([g for g in games if g["flip_roles"]>0])!=48:
        raise ValueError("C3X025_48_DISTINCT_CHANGED_GAMES_DRIFT")
    if dev_case52 is None or (dev_case52["game_id"],dev_case52["order"],dev_case52["role"],
          dev_case52["M0_UCI"],dev_case52["M4_UCI"],dev_case52["actual_final_UCI"])!=(52,"O","STRICT","a6d3","d7d5","a6d3"):
        raise ValueError("C3X025_SINGLE_M4_FALSE_POSITIVE_CHANGED_AFTER_TREATMENT")
    useful=[x for x in rows if x["status"]=="ELIGIBLE"]
    source_true_TT_value_use_groups=Counter(k for x in useful for k in [("recorded" if x["source_TT_use"] else "not_recorded")])
    by_group={field:tally(rows,field) for field in
            ("order","role","root_O_F_disagree","target_matches_depth12_leader",
             "depth11_vs_12_disagree","passive_SEE_prefix_censored",
             "source_trace_censored","same_order_prior_depth11_support",
             "M4_original_rule_reason","source_TT_use","passive_SEE")}
    within_game=Counter(x["flip_roles"] for x in games)
    source_all=[x for x in rows if x["status"]=="ELIGIBLE" and x["flip"]]
    return {
      "schema":"c3x025-P0-D0-exposed-July256-TT-and-root-frontier-development-ledger-v1",
      "science_scope":"EXPOSED_DEVELOPMENT_ONLY__NOT_NEW_MODEL_VALIDATION__NOT_NATURAL_TT_SEE_MEDIATION",
      "original_sources":{"game_hash_id_registry":REGISTRY,"StageA_SHA256":STAGE_SHA,
         "forecast_original_SHA256":FORECAST_SHA,"all1024_human_Git_literal_seal":SEAL,
         "score_original_SHA256":SCORE_SHA,"shard_original_sha256":list(SHARD_SHAS)},
      "denominators":{"source_games":256,"root_worlds":512,"nested_role_cells":1024,
         "actual_source_physically_contacted":seen_contact,"prior_HOLD":seen_hold,
         "NO_CONTACT_HOLD":0,"physical_root_flip_roles":seen_flip,
         "distinct_changed_source_games":48,
         "unselected_root_flips_missed_by_M4":len([x for x in source_all if not x["alt"]]),
         "M4_changed_and_wrong":1,"M4_correct":correct_m4,"M0_correct":correct_m0},
      "per_original_game_flip_role_count":{str(k):v for k,v in sorted(within_game.items())},
      "source_observational_crosstabs":by_group,
      "single_precommitted_M4_false_positive":dev_case52,
      "lowest_game_id_first_twelve_root_flip_examples":first_flip_development_samples,
      "evidence_identification_limits":{
         "E0_physical_first_reader":"PROVEN_BY_TREATED_SHARD_NATIVE_CONTACT",
         "E1_actual_semantic_TT_value_use_after_treatment":"NOT_CERTIFIED_BY_P4_TREATED_PACKET",
         "E2_common_full_computational_state_after_treatment":"NOT_CERTIFIED",
         "E3_natural_SEE_activation_change_after_TT":"NOT_CERTIFIED",
         "E4_native_branch_admission_and_first_divergence":"NOT_CERTIFIED",
         "E5_complete_source_ancestor_return":"NOT_CERTIFIED",
         "E6_native_root_terminal_bestmove":"OBSERVED",
         "passive_stageA_TT_use_records":"OBSERVATIONAL_OLD_WORLD_ONLY_NOT_INTERVENTION_MEDIATION",
         "passive_stageA_SEE_prefix":"BOUNDED_32_EVENTS_PER_WORLD__CENSORED_NE_ABSENT",
         "fully_identified_natural_TT_to_SEE_to_root_mediation_paths":0,
         "fully_identified_natural_TT_to_SEE_to_root_mediation_paths_interpretation":"ZERO_CERTIFIED_BY_THIS_DATA__NOT_PROOF_NATURAL_MEDIATION_ABSENT",
         "next_required_source_instrument":"TIMEORDERED_TT_SEMANTIC_USE__EXACT_NODE_SEARCH_STATE__SEE_BRANCH__ANCESTOR_ROOT_COMPETITION"},
      "statistical_claim":"DESCRIPTION_ONLY. Conditional cells within games/events, not independent samples or a predictive model. No p-values or posthoc M5 score.",
      "source_rights":"Derived original Lichess 2025-07 broadcast CC BY-SA4 with attribution. No original full PGNs/FEN, player/event labels, source native keys or modified GPL engine binary.",
      "no_original_game_move_history_or_player_metadata":True
    }
def main():
    p=argparse.ArgumentParser()
    for q in ("stagea","forecast","score","shard-dir","out"):p.add_argument("--"+q,required=True)
    a=p.parse_args()
    stage=get(a.stagea,STAGE_SHA);forecast=get(a.forecast,FORECAST_SHA)
    score=get(a.score,SCORE_SHA)
    paths=sorted(glob.glob(str(Path(a.shard_dir)/"C3X024_P4_TREATED_SHARD_*.json")))
    if len(paths)!=4:raise ValueError("C3X025_MISSING_HISTORIC_JULY_SHARDS")
    shards=[get(f,SHARD_SHAS[i]) for i,f in enumerate(paths)]
    reg=json.loads(Path(REGISTRY).read_text());seal=json.loads(Path(SEAL).read_text())
    result=audit(stage,forecast,shards,score,reg,seal)
    out=Path(a.out);out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,sort_keys=True,indent=2)+"\n")
    print("C3X025_P0_D0_DEV_ONLY_256_SOURCE_ROLES",result["denominators"],flush=True)
    print("C3X025_P0_D0_M4_ONE_FALSE_POSITIVE_DEV",result["single_precommitted_M4_false_positive"],flush=True)
    print("C3X025_P0_D0_FLIP_PER_GAME_DISTRIBUTION",result["per_original_game_flip_role_count"],flush=True)
    print("C3X025_P0_D0_GROUPS_SOURCE_ONLY",
          {k:len(v) for k,v in result["source_observational_crosstabs"].items()},flush=True)
    print("C3X025_P0_D0_FULL_DERIVED_DEVELOPMENT_JSON_SHA256",
          hashlib.sha256(out.read_bytes()).hexdigest(),flush=True)
if __name__=="__main__":main()
