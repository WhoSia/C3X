#!/usr/bin/env python3
"""C3X0.23-P1-R1: real TT FIRST source suppression, passive same-node SEE matches.

No native SEE value flip. Two frozen licensed ecologies, all eligible roles.
Preserve zero-source and censored HOLD cells. Per-role M0/M1 exact UCI
predictions already committed before these V treatment outcomes.
"""
import argparse,hashlib,json
from pathlib import Path
from collections import Counter
from c3x_018_native_TT_lineage_factorial_6_8 import play,need
from c3x_018_jan16_TT_cross_window_pair_native import RULES,mask_filters
from c3x_018_independent16_TT_value_transport_native import verified_reader_lineage
from c3x_022_P2_two_stage_exact_move_scout import native_world,source_depth_ladder
from c3x_023_P1_same_descendant_SEE_node_matcher import candidates

SOURCE_SHA="0ff43e28dcb3a5e48dea6b61e4450fc8bb9e1f96363871c33c4b73524664db61"
STAGEA_SHA="fe88afe49d7d43db7b81c37decab783f2b68311ed2ca10b6f42be4268bdb3442"
FORECAST_PATH="c3x/forecasts/c3x-023-P1-licensed-May-CC0-32game-M0-M1-literal-UCI-source-first-preTT-20261010.json"
ECOLOGIES=("may2026_broadcast","lichess_CC0_nonmate_puzzles")
WORLDS=("O","F")
ROLES=("STRICT","BROAD")
SCHEMA="c3x023-P1-R1-two-licensed-ecologies-native-TT-first-and-common-SEE-path-v1"

def frozen(path,sha):
    raw=Path(path).read_bytes()
    need(hashlib.sha256(raw).hexdigest()==sha,"P1R1_IMMUTABLE_FROZEN_SOURCE_DRIFT")
    return json.loads(raw)

def verify_precommitted_literals(source,stagea,forecasts):
    need(forecasts["status"]=="GIT_FROZEN_LITERAL_FORECASTS_BEFORE_FIRST_TT_READER_SUPPRESSION",
         "P1R1_NOT_GIT_SEALED_BEFORE_TREATMENT")
    need(forecasts["native_stageA_raw_JSON_SHA256"]==STAGEA_SHA and
         forecasts["new_licensed32_source_SHA256"]==SOURCE_SHA,"P1R1_SOURCE_FORECAST_MISMATCH")
    need(stagea["summary"]["actual_TT_FIRST_interventions"]==0
         and stagea["summary"]["actual_SEE_Boolean_interventions"]==0
         and stagea["summary"]["treatment_outcomes_seen"] is False,
         "P1R1_STAGEA_NOT_UNTREATED")
    n=0
    for eco in ECOLOGIES:
        src=source["per_ecology"][eco]["selected"]
        old=stagea["ecologies"][eco]["cases"]
        pred=forecasts["ecologies"][eco]["cases"]
        need(len(src)==len(old)==len(pred)==16,"P1R1_32_DENOMINATOR_DRIFT")
        for a,b,c in zip(src,old,pred):
            need(a["id"]==b["id"]==c["source_id"] and
                 a["source_game_sha256"]==b["source_sha256"],
                 "P1R1_SOURCE_ROW_ID_DRIFT")
            baseline={order:b["worlds"][order]["baseline_UCI"]["bestmove"] for order in WORLDS}
            need(baseline["O"]==c["baseline_O_UCI"] and
                 baseline["F"]==c["baseline_F_UCI"],"P1R1_UNSEALED_O_F_BESTMOVE")
            for order in WORLDS:
                for role in ROLES:
                    entry=b["worlds"][order]["roles"][role]
                    literal=c["first_reader_target_roles"][order+"/"+role]
                    eligible=entry["status"]=="FIRST_SOURCE_PAIR_PRE_OUTCOME"
                    need(eligible==literal["source_eligible"],
                         "P1R1_SOURCE_PAIR_MASK_NOT_FROZEN")
                    if eligible:
                        need(entry["exact_UCI"]["M0"]==literal["M0_exact_UCI"]==baseline[order]
                             and entry["exact_UCI"]["M1"]==literal["M1_exact_UCI"]==
                             baseline["F" if order=="O" else "O"],
                             "P1R1_PRECOMMITTED_LITERAL_UCI_DRIFT")
                        n+=2
                    else:
                        need(literal["M0_exact_UCI"] is None and literal["M1_exact_UCI"] is None,
                             "P1R1_MASKED_SOURCES_WITH_EXACT_PREDICTION")
    need(n==248,"P1R1_LITERALS_248_NOT_SEALED")
    return n

def cold(engine,world,clocks,order,mode,target=None,filters=None,watch=None):
    kwargs={"fen_clocks":clocks,"allow_empty_lineage":True}
    if filters is not None:kwargs["tt_reader_filters"]=filters
    if watch is not None:
        kwargs["native_use_watch"]={"key64":watch["key64"],"root_call":watch["root_call"]}
        kwargs["see_watch"]={"key64":watch["key64"],"root_call":watch["root_call"],
                            "policy":"OBS","passive_ancestry":True}
    a=play(engine,world,order,mode,target,**kwargs)
    b=play(engine,world,order,mode,target,**kwargs)
    need(a==b,"P1R1_SOURCE_DUPLICATE_COLD_MISMATCH")
    need(not any(e.get("altered") for e in a["native_see_events"]
                 if e.get("kind")=="witness"),"P1R1_SEE_SOURCE_WATCH_MUST_NOT_MUTATE")
    return a

def exact_block(result,source):
    blocks=[e for e in result["blocks"] if e.get("kind")=="reader_block"]
    physical=source["physical"]; calls=source["root_calls"]
    need(len(blocks)==result["lineage_summary"]["reader_block"],
         "P1R1_READER_BLOCK_COUNT_DRIFT")
    need(all(e["root_call"]==calls[0] and
             e["root_move"]==source["root_candidate_native"] and
             all(e[k]==physical[k] for k in ("key64","slot","epoch"))
             for e in blocks),"P1R1_WRONG_NATIVE_TT_PHYSICAL_WRITER_READER")
    proof=verified_reader_lineage(result)
    need(not blocks or (proof["all_valid"] and proof["count"]>=len(blocks)),
         "P1R1_WRITER_READER_SOURCE_PROOF_FAILURE")
    return blocks,proof

def scan(source,stagea,forecasts,engine):
    n_literals=verify_precommitted_literals(source,stagea,forecasts)
    out={"schema":SCHEMA,"study":"FROZEN_SOURCE_FIRST_TT_INTERVENTION_POST_PRESEALED_LITERAL_FORECAST",
         "new_licensed_source_sha256":SOURCE_SHA,
         "native_untreated_stageA_sha256":STAGEA_SHA,
         "forecasts_git_path":FORECAST_PATH,
         "frozen_pre_first_TT_UCI_literals":n_literals,
         "ecologies":{}}
    for eco in ECOLOGIES:
        results=[]
        for src,old in zip(source["per_ecology"][eco]["selected"],
                           stagea["ecologies"][eco]["cases"]):
            world,clocks,_=native_world(src)
            record={"id":src["id"],"original_source_chess_id_SHA":src["source_game_sha256"],
                    "worlds":{}}
            for order in WORLDS:
                initial=old["worlds"][order]
                model_base=initial["baseline_UCI"]
                roles={}
                # Only actual eligible roles may be treated.
                for role in ROLES:
                    target=initial["roles"][role]
                    if target["status"]!="FIRST_SOURCE_PAIR_PRE_OUTCOME":
                        roles[role]={"status":target["status"],
                                     "TT_FIRST_contact":False,
                                     "common_descendant_SEE_node":"NOT_CHECKED_NO_SOURCE_PAIR"}
                        continue
                    triple=target["physical"]
                    watch={"key64":triple["key64"],"root_call":target["root_calls"][0]}
                    pair={"physical":triple,"root_calls":target["root_calls"],
                          "root_candidate_native":target["root_candidate_native"]}
                    natural=cold(engine,world,clocks,order,"OBS",watch=watch)
                    need(natural["UCI"]==model_base and
                         natural["lineage_summary"]["reader_block"]==0,
                         "P1R1_ACTUAL_OBS_WATCH_CHANGES_FROZEN_STAGEA")
                    if role=="STRICT":
                        need(natural["native_see_events"]==
                             initial["passive_first32_SEE_events"],
                             "P1R1_SOURCE_OBS_SEE_PATH_DRIFT")
                    V=cold(engine,world,clocks,order,"V",triple,
                           filters=mask_filters(RULES[role],pair,"FIRST"),watch=watch)
                    blocks,proof=exact_block(V,target)
                    contact=bool(blocks)
                    matched=candidates(natural["native_see_events"],
                                       V["native_see_events"],contact)
                    before=source_depth_ladder(natural["root_events"])
                    after=source_depth_ladder(V["root_events"])
                    common_depths=sorted(set(before)&set(after),key=int)
                    divergent=[int(depth) for depth in common_depths
                        if before[depth]["native_leader"]!=after[depth]["native_leader"]]
                    actual=V["UCI"]["bestmove"]
                    models={m:{"exact_UCI_prediction":target["exact_UCI"][m],
                               "correct_if_contact":actual==target["exact_UCI"][m] if contact else None,
                               "predicted_flip":target["exact_UCI"][m]!=model_base["bestmove"] if contact else None}
                            for m in ("M0","M1")}
                    roles[role]={
                        "status":"SOURCE_FULL64_FIRST_READER_BLOCK_CONFIRMED" if contact else
                                 "HOLD_SOURCE_FIRST_READER_DID_NOT_FIRE",
                        "TT_FIRST_contact":contact,
                        "source_physical":triple,
                        "source_root_calls":target["root_calls"],
                        "source_root_candidate_native":target["root_candidate_native"],
                        "TT_reader_blocks":blocks,
                        "native_reader_writer_lineage_proof":proof,
                        "untreated_UCI":natural["UCI"],
                        "treated_UCI":V["UCI"],
                        "actual_bestmove_flip":actual!=model_base["bestmove"] if contact else None,
                        "M0_M1_exact_preds":models,
                        "TT_source_watched_value_uses_before":natural["native_tt_value_uses"],
                        "TT_source_watched_value_uses_after":V["native_tt_value_uses"],
                        "SEE_untreated_first32_events":natural["native_see_events"],
                        "SEE_TT_FIRST_first32_events":V["native_see_events"],
                        "common_SEE":matched,
                        "depths_common":common_depths,
                        "depths_root_leader_changed":divergent,
                        "SEE_bool_flips_performed":0,
                        "cold_repeated_every_arm":True
                    }
                record["worlds"][order]={"roles":roles}
            results.append(record)
            summary={order:{role:{
                "TT":v.get("TT_FIRST_contact"),
                "shared_unique_nodes":len(v.get("common_SEE",{}).get("matched",[])),
                "censored":v.get("common_SEE",{}).get("observed_prefix_censored"),
                "flip":v.get("actual_bestmove_flip")}
                for role,v in record["worlds"][order]["roles"].items()} for order in WORLDS}
            print("C3X023_P1_R1_NATIVE_SOURCE_MATCHED_ROOT_RESULT",eco,src["id"],summary,flush=True)
        out["ecologies"][eco]={"source_license":source["per_ecology"][eco]["source"]["license"],
                                "cases":results}
    obs=[(eco,entry["id"],order,role,x)
         for eco,group in out["ecologies"].items() for entry in group["cases"]
         for order,o in entry["worlds"].items() for role,x in o["roles"].items()]
    contacted=[x for x in obs if x[4].get("TT_FIRST_contact")]
    shared=[x for x in contacted if x[4]["common_SEE"]["matched"]]
    flipped=[x for x in contacted if x[4]["actual_bestmove_flip"]]
    no_src=[x for x in obs if not x[4].get("TT_FIRST_contact")]
    data={}
    for eco in ECOLOGIES:
        scoped=[x for x in obs if x[0]==eco]
        cc=[x for x in scoped if x[4].get("TT_FIRST_contact")]
        sh=[x for x in cc if x[4]["common_SEE"]["matched"]]
        ff=[x for x in cc if x[4]["actual_bestmove_flip"]]
        data[eco]={"contacted_source_roles":len(cc),
                   "unique_shared_SEE_node_role_cells":len(sh),
                   "unique_shared_SEE_nodes_total":sum(len(x[4]["common_SEE"]["matched"]) for x in sh),
                   "actual_final_bestmove_flipped_role_cells":len(ff),
                   "actual_final_bestmove_flipped_chess_game_units":len({x[1] for x in ff}),
                   "exact_UCI_correct_in_contact_cells":{
                       m:sum(x[4]["M0_M1_exact_preds"][m]["correct_if_contact"] for x in cc)
                       for m in ("M0","M1")},
                   "physical_role_instances_are_not_independent_chess_games":True}
    out["summary"]={
       "licensed_distinct_chess_positions":32,
       "total_possible_root_order_source_role_cells":128,
       "eligible_source_roles_preregistered":124,
       "actual_TT_FIRST_contacted_role_cells":len(contacted),
       "NO_TREATMENT_or_HOLD_or_SOURCE_FAILURE_roles":len(no_src),
       "unique_common_descendant_SEE_role_cells":len(shared),
       "unique_common_descendant_SEE_source_episodes_total":
           sum(len(x[4]["common_SEE"]["matched"]) for x in shared),
       "TT_FIRST_changed_final_UCI_role_cells":len(flipped),
       "TT_FIRST_changed_distinct_chess_game_units":len({(x[0],x[1]) for x in flipped}),
       "observed_prefix_censored_role_cells":sum(x[4]["common_SEE"]["observed_prefix_censored"] for x in contacted),
       "SEE_Boolean_interventions":0,
       "TT_score_as_eval_before_witness_cells":sum(bool(x[4]["TT_source_watched_value_uses_before"]) for x in contacted),
       "TT_score_as_eval_after_witness_cells":sum(bool(x[4]["TT_source_watched_value_uses_after"]) for x in contacted),
       "by_licensed_ecology":data,
       "NO_SOURCE_NODE_MEDIATION_CLAIM":True,
       "no_positive_M3_forecast_in_this_preseal":True}
    return out

def main():
    p=argparse.ArgumentParser()
    for key in ("source","stagea","forecasts","engine","out"):p.add_argument("--"+key,required=True)
    a=p.parse_args()
    source=frozen(a.source,SOURCE_SHA);stagea=frozen(a.stagea,STAGEA_SHA)
    fore=json.loads(Path(a.forecasts).read_bytes())
    r=scan(source,stagea,fore,a.engine)
    dest=Path(a.out);dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(json.dumps(r,ensure_ascii=False,sort_keys=True,indent=2)+"\n")
    print("C3X023_P1_R1_STRICT_SHARED_SOURCE_NODE_AND_TT_OUTCOME_SUMMARY",
          r["summary"],hashlib.sha256(dest.read_bytes()).hexdigest(),flush=True)
if __name__=="__main__":main()
