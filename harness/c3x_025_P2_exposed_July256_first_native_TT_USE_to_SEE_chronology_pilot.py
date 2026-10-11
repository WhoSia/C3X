#!/usr/bin/env python3
"""P2 exposed July TT semantic-use and original native SEE chronological source-only.
Two cold arm repeats, exact original SHA and UCI parity. No SEE changes or M5.
"""
import argparse,glob,hashlib,json
from pathlib import Path
from c3x_018_native_TT_lineage_factorial_6_8 import play
from c3x_018_jan16_TT_cross_window_pair_native import RULES,mask_filters,verify_selected_blocks
from c3x_022_P2_two_stage_exact_move_scout import native_world
from c3x_023_P1_R2_T0_chronological_post_TT_common_SEE_dev import (
    post_source_match,source_lines)
from c3x_025_P0_D0_exposed_July256_TT_root_frontier_development_ledger import (
    STAGE_SHA,FORECAST_SHA,SOURCE_SHA,SHARD_SHAS,REGISTRY,SEAL,get)
MODES=("O","F")
ROLES=("STRICT","BROAD")
SCHEMA="c3x025-P2-July256-exposed-TT-real-use-SEE-prefix-chronology-v1"
def original_targets(source,stage,forecast,shards):
    if len(shards)!=4 or len(source["selected"])!=256 or len(forecast["cases"])!=256:
        raise ValueError("P2_EXACT_ORIGINAL_256_PROVENANCE")
    original=[x for sh in shards for x in sh["all_cells"]]
    if len(original)!=256 or [x["game_id"] for x in original]!=list(range(1,257)):
        raise ValueError("P2_ORIGINAL_256_GAME_ORDER_DRIFT")
    targets=[(52,"O","STRICT"),(52,"O","BROAD")]
    first_flip=None
    for g in original:
        for x in g["roles"]:
            if x["status"]=="REAL_NATIVE_PHYSICAL_TT_FIRST" and x["actual_root_flip"] is True:
                first_flip=(g["game_id"],x["root_order"],x["role"])
                break
        if first_flip is not None:break
    if first_flip is None:raise ValueError("P2_PRIOR_96_NATIVE_ROOT_FLIPS_NOT_FOUND")
    if first_flip not in targets:targets.append(first_flip)
    for g,o,r in targets:
        src=source["selected"][g-1]
        st=stage["ecologies"]["july2025_broadcast"]["cases"][g-1]
        fc=forecast["cases"][g-1]
        role=st["worlds"][o]["roles"][r]
        if not src["source_game_sha256"]==st["source_sha256"]==fc["source_game_sha256"] or
           role["status"]!="FIRST_SOURCE_PAIR_PRE_OUTCOME":
            raise ValueError("P2_ORIGINAL_PRETREATMENT_SOURCE_ROLE_NOT_VALID")
    return targets,original
def cold(engine,board,clock,order,role,scope,treated):
    key=scope["physical"]["key64"]
    call=scope["root_calls"][0]
    kw={"fen_clocks":clock,"allow_empty_lineage":True,"ordered_source_trace":True,
        "native_use_watch":{"key64":key,"root_call":call},
        "see_watch":{"key64":key,"root_call":call,
                     "policy":"OBS","passive_ancestry":True}}
    if treated:
        target={k:scope[k] for k in ("physical","root_calls","root_candidate_native")}
        kw["tt_reader_filters"]=mask_filters(RULES[role],target,"FIRST")
    else:target=None
    args=(engine,board,order,"V" if treated else "OBS",
          scope["physical"] if treated else None)
    a=play(*args,**kw)
    b=play(*args,**kw)
    if a!=b:raise ValueError("P2_COLD_NATIVE_OPERATOR_TRACE_PARITY_DRIFT")
    if any(e.get("original")!=e.get("delivered") or e.get("altered")!=0
           for e in a["native_see_events"] if e["kind"]=="witness"):
        raise ValueError("P2_NATIVE_SEE_WAS_ACTUATED")
    if treated:
        proof=verify_selected_blocks(a,target,RULES[role],"FIRST")
        if proof["blocked"]<1:raise ValueError("P2_NATIVE_TT_FIRST_NO_SOURCE_CONTACT")
    else:
        if a["lineage_summary"]["reader_block"]!=0:
            raise ValueError("P2_OBS_ORIGINAL_TT_POLICY_NOT_PASSIVE")
    return a
def pilot(source,stage,forecast,shards,engine):
    targets,original=original_targets(source,stage,forecast,shards)
    cases=[]
    for gid,order,role in targets:
        raw=source["selected"][gid-1]
        ref=stage["ecologies"]["july2025_broadcast"]["cases"][gid-1]
        predicted=forecast["cases"][gid-1]["root_orders"][order][role]
        old=ref["worlds"][order]
        scope=old["roles"][role]
        original_role=next(x for x in original[gid-1]["roles"] if
                          x["root_order"]==order and x["role"]==role)
        board,clock,_=native_world({**raw,"source_root_legal_count":raw["root_legal_move_count"]})
        try:
            obs=cold(engine,board,clock,order,role,scope,False)
            treated=cold(engine,board,clock,order,role,scope,True)
        except RuntimeError as exc:
            if str(exc)=="C3X018_PHYSICAL_COURT_TRACE_CENSORED":
                cases.append({"game_id":gid,"order":order,"role":role,
                   "status":"HOLD_EXACT_NATIVE_TT_30000_LOG_CENSORED",
                   "not_replaced_by_other_case":True})
                continue
            raise
        if obs["UCI"]!=old["baseline_UCI"]:
            raise ValueError("P2_ORIGINAL_BASELINE_NATIVE_UCI_REPLAY_MISMATCH")
        if treated["UCI"]["bestmove"]!=original_role["treated_bestmove"] or
           bool(treated["UCI"]["bestmove"]!=obs["UCI"]["bestmove"])!=bool(original_role["actual_root_flip"]):
            raise ValueError("P2_ORIGINAL_NATIVE_TT_FIRST_OUTCOME_REPLAY_MISMATCH")
        if obs["UCI"]["bestmove"]!=predicted["M0"]:
            raise ValueError("P2_HUMAN_GIT_ORIGINAL_LITERAL_M0_CHANGED")
        if original_role["cold_pairs_checked"]!=2 or not original_role["source_TT_first_contact"]:
            raise ValueError("P2_SOURCE_REAL_TT_FIRST_NOT_AUDITED")
        source_use=[a for kind in ("used","main_cutoff","qsearch_cutoff")
                    for a in source_lines(obs,"TT_value_used",kind,scope)]
        blocks=source_lines(treated,"physical_TT","reader_block",scope)
        native_match=post_source_match(obs,treated,scope)
        match={"status":native_match["status"],
               "strict_post_source_matches":native_match["strict_post_source_matches"],
               "post_event_sites":native_match.get("post_event_sites",{}),
               "pre_or_other_shared_source_events":native_match.get("preceding_or_unqualified_shared_events",0),
               "original_prefix_censored":native_match.get("source_prefix_censored",False)}
        if len(blocks)<1:
            raise ValueError("P2_NATIVE_SELECTED_FIRST_SOURCE_BLOCK_NOT_ON_CHRONOLOGICAL_TRACE")
        see_obs=[x for x in obs["native_see_events"] if x["kind"]=="witness"]
        see_treated=[x for x in treated["native_see_events"] if x["kind"]=="witness"]
        row={
            "game_id":gid,"order":order,"role":role,
            "status":"EXPOSED_NATIVE_TT_CHRONOLOGY_WITNESSED_WITHOUT_FULL_STATE",
            "original_model_M0":predicted["M0"],
            "original_model_M4":predicted["M4_survivor"],
            "original_OBS_UCI":obs["UCI"]["bestmove"],
            "original_TT_FIRST_UCI":treated["UCI"]["bestmove"],
            "original_root_flip":original_role["actual_root_flip"],
            "native_original_real_TT_semantic_use_events":len(source_use),
            "native_physical_first_reader_blocks":len(blocks),
            "native_untreated_SEE_prefix_calls":len(see_obs),
            "native_treated_SEE_prefix_calls":len(see_treated),
            "native_original_SEE_prefix_censored":any(e["kind"]=="censored" for e in obs["native_see_events"]),
            "native_treated_SEE_prefix_censored":any(e["kind"]=="censored" for e in treated["native_see_events"]),
            "post_native_use_and_physical_FIRST_common_source_SEE":match,
            "full_search_state_same":"NOT_INSTRUMENTED_IN_THE_2025_JULY_P4_ORIGINAL_OVERLAY",
            "actual_branch_prune_continue":"NOT_INSTRUMENTED",
            "child_parent_ancestor_value_chain":"NOT_INSTRUMENTED",
            "natural_TT_SEE_mediation_proven":False
        }
        cases.append(row)
        print("C3X025_P2_EXPOSED_JULY_NATIVE_TT_SEE_CHRONOLOGY",
              {k:row[k] for k in ("game_id","order","role","original_root_flip",
               "native_original_real_TT_semantic_use_events",
               "native_physical_first_reader_blocks",
               "native_untreated_SEE_prefix_calls",
               "native_treated_SEE_prefix_calls",
               "post_native_use_and_physical_FIRST_common_source_SEE")},flush=True)
    return {
      "schema":SCHEMA,"scientific_status":"EXPOSED_DEVELOPMENT_ONLY_NO_NEW_HELDOUT_PROSPECTIVE",
      "source_original_JSON_SHA256":SOURCE_SHA,
      "source_original_untreated_stageA_SHA256":STAGE_SHA,
      "source_original_six_model_forecast_SHA256":FORECAST_SHA,
      "original_four_native_shard_SHA256":list(SHARD_SHAS),
      "pilot_target_count":len(targets),
      "cold_repeats_per_TT_policy_arm":2,
      "target_definition":"case52 O STRICT M4 false positive; case52 O BROAD same-world control; lexicographic original first actual root-flip role",
      "study_cases":cases,
      "all_P4_original_outcomes_preserved":True,
      "proves_natural_TT_SEE_root_mediation":False,
      "missing_E2_to_E5_full_causal_chain":"FULL_SEARCH_STATE_AND_BRANCH_ADMISSION_AND_ANCESTOR_RETURN_NOT_CAPTURED",
      "source_SEE_unchanged_native_boolean":True,
      "TT_original_and_V_mode_traces_passive_except_original_physical_TT_FIRST":True,
      "rights":"Lichess July2025 official broadcast CC BY-SA4, original full PGN/FEN/player names, raw TT position keys/path and GPL modified binary NOT distributed."
    }
def main():
    ap=argparse.ArgumentParser()
    for k in ("source","stagea","forecast","shards","engine","out"):
        ap.add_argument("--"+k,required=True)
    a=ap.parse_args()
    source=get(a.source,SOURCE_SHA);stage=get(a.stagea,STAGE_SHA);forecast=get(a.forecast,FORECAST_SHA)
    paths=sorted(glob.glob(str(Path(a.shards)/"C3X024_P4_TREATED_SHARD_*.json")))
    if len(paths)!=4:raise ValueError("P2_EXACT_FOUR_ORIGINAL_SHARDS_MISSING")
    shards=[get(p,SHARD_SHAS[i]) for i,p in enumerate(paths)]
    out=pilot(source,stage,forecast,shards,a.engine)
    p=Path(a.out);p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print("C3X025_P2_JULY256_EXPOSED_NATIVE_TT_USE_SEE_PILOT_SUMMARY",
          [(z["game_id"],z["order"],z["role"],z["status"]) for z in out["study_cases"]],flush=True)
    print("C3X025_P2_JULY256_EXPOSED_FULL_DERIVED_JSON_SHA256",
          hashlib.sha256(p.read_bytes()).hexdigest(),flush=True)
if __name__=="__main__":main()
