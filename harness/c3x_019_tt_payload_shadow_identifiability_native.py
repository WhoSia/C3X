#!/usr/bin/env python3
"""C3X019 adaptive orthogonal factorization of TT payload vs writer shadow.

One original January #2 STRICT source, pinned cold SF16:
V-BOTH versus V-FIRST+PASSIVE_SECOND across NONE/SKIP/FULL/BYTES/SHADOW.
Pass/fail pertains mechanism identification, not root-choice generalization.
"""
import argparse,hashlib,json
from pathlib import Path
from c3x_018_native_TT_lineage_factorial_6_8 import play,need
from c3x_018_independent16_TT_value_transport_native import canonical_engine_world
from c3x_018_chess_clock_factorial_original_history_native import game_clocks
from c3x_018_jan16_TT_cross_window_pair_native import RULES,mask_filters

SRC_SHA="5b49818e4678c12d0e5e73eba39eff2d50742b070a0ed870cba1d3e94afe0533"
PRIOR_SHA="9d7ff1d8c5e019a5ab5b95441468da0ad49951adc756b8669db7853b82649470"
POLICIES=("NONE","SKIP","REINSTATE","BYTES_ONLY","SHADOW_ONLY")
GAME=2
SELECTOR="STRICT"

def both_policy(engine,world,clocks,pair,policy,passive):
    key=pair["physical"]["key64"]
    second=pair["root_calls"][1]
    ctrl={"key64":key,"slot":pair["physical"]["slot"],
          "epoch":pair["physical"]["epoch"],
          "first_call":pair["root_calls"][0],
          "last_call":second,"policy":policy}
    opts={"fen_clocks":clocks,"p1_writer":ctrl,
          "tt_reader_filters":mask_filters(RULES[SELECTOR],pair,"BOTH"),
          "probe_watch":{"key64":key,"root_call":second},
          "native_use_watch":{"key64":key,"root_call":second}}
    if passive:opts["passive_second_call"]=second
    x=play(engine,world,"F","V",pair["physical"],**opts)
    y=play(engine,world,"F","V",pair["physical"],**opts)
    need(x==y,"ORTHOGONAL_COLD_NONDET_"+policy+("_PASSIVE" if passive else "_BLOCK"))
    need(not any(e["kind"]=="censored" for e in x["p0_save_events"]),
         "P0_SAVE_CENSORED_"+policy)
    need(not any(e["kind"]=="censored" for e in x["native_tt_value_uses"]),
         "NATIVE_USE_CENSORED_"+policy)
    need(not any(e["kind"]=="censored" for e in x["watched_tt_probes"]),
         "TT_PROBE_CENSORED_"+policy)
    blocks=[e for e in x["blocks"] if e["kind"]=="reader_block"]
    actual=[e for e in x["native_tt_value_uses"] if e["kind"]=="used"]
    allowed=x["native_tt_source_allows"]
    write_events=x["p0_save_events"]
    selected=[e for e in write_events if e["kind"]=="writer_reinstated"]
    row={
       "policy":policy,"second_native_allowed":bool(passive),
       "UCI":x["UCI"],"V_reader_block_calls":[e["root_call"] for e in blocks],
       "V_second_root_blocked":any(e["root_call"]==pair["root_calls"][1] for e in blocks),
       "source_reader_native_allow_calls":[e["root_call"] for e in allowed],
       "actual_post_assignment_native_uses":actual,
       "actual_native_eval_use_count":len(actual),
       "physical_second_root_TT_probes":x["watched_tt_probes"],
       "shadow_last_writer_at_second_TT_probe":[
           {"epoch":e["shadow_epoch"],"serial":e["shadow_writer_serial"],
            "full64_match":e["shadow_full64_match"],"raw_depth":e["raw_depth"],
            "raw_bound":e["raw_bound"],"raw_value":e["raw_value"],
            "raw_eval":e["raw_eval"]}
           for e in x["watched_tt_probes"] if e["kind"]=="probe"],
       "raw_writer_value_snapshots_at_V_gate":[
           e for e in x["payload_witnesses"] if e["kind"]=="reader"],
       "raw_payload_witness_mismatches":[
           e for e in x["payload_witnesses"]
           if e["kind"]=="reader" and e.get("matched")==0],
       "P0_actual_save_and_P1_repair_events":write_events,
       "writer_skip_count":sum(e["kind"]=="writer_skip" for e in write_events),
       "writer_reinstated_count":len(selected),
       "writer_repair_mode_event":selected,
       "first_and_second_root_calls":pair["root_calls"]}
    return row

def main():
    p=argparse.ArgumentParser()
    for name in ("source","prior","engine","out"):p.add_argument("--"+name,required=True)
    a=p.parse_args()
    raw=Path(a.source).read_bytes();prev=Path(a.prior).read_bytes()
    need(hashlib.sha256(raw).hexdigest()==SRC_SHA,"JANUARY_SOURCE_DRIFT")
    need(hashlib.sha256(prev).hexdigest()==PRIOR_SHA,"JANUARY_INDEPENDENT_NATIVE_DRIFT")
    source=json.loads(raw)["selected"][GAME-1]
    prior=json.loads(prev)["cases"][GAME-1]
    need(source["id"]==prior["id"]==GAME and prior["status"]=="VALID","CASE_ID")
    pair=prior["selectors"][SELECTOR]["selected_passive_pair"]
    need(pair["root_calls"]==[4,5] and pair["physical"]==
         {"key64":10822490400377030283,"slot":0,"epoch":1},
         "ORIGINAL_FIXED_PAIR_CHANGED")
    world,_=canonical_engine_world(source)
    clocks=game_clocks(source)
    output={"schema":"c3x019-source-orthogonal-native-10byte-TT-payload-versus-shadow-writer-and-true-use-v1",
        "classification":"ADAPTIVE_SINGLE_JANUARY_SOURCE_IDENTIFIABILITY_TEST",
        "source_sha256":SRC_SHA,"independent_prior_sha256":PRIOR_SHA,
        "source_game_id":2,"selection_rule":"STRICT",
        "fixed_physical_target":pair["physical"],"root_calls":pair["root_calls"],
        "source_clock":list(clocks),"arms":{}}
    baseline=play(a.engine,world,"F","OBS",fen_clocks=clocks)
    again=play(a.engine,world,"F","OBS",fen_clocks=clocks)
    need(baseline==again,"COLD_SOURCE_F")
    need(baseline["UCI"]==prior["controls"]["F"],"SOURCE_F_UCI_CHANGED")
    output["F_UCI"]=baseline["UCI"]
    for policy in POLICIES:
        for passive in (False,True):
            label=policy+("_NATIVE_SECOND" if passive else "_V_BOTH")
            row=both_policy(a.engine,world,clocks,pair,policy,passive)
            output["arms"][label]=row
            print("C3X019_RAW_SHADOW_FACTOR",label,
                "V_calls",row["V_reader_block_calls"],
                "native_use",row["actual_native_eval_use_count"],
                "probe_versions",[(e["epoch"],e["raw_depth"]) for e in
                    row["shadow_last_writer_at_second_TT_probe"]],
                "mismatch",len(row["raw_payload_witness_mismatches"]),
                "bestmove",row["UCI"]["bestmove"],flush=True)
    none=output["arms"]["NONE_V_BOTH"]
    full=output["arms"]["REINSTATE_V_BOTH"]
    shadow=output["arms"]["SHADOW_ONLY_V_BOTH"]
    by=output["arms"]["BYTES_ONLY_V_BOTH"]
    skipped=output["arms"]["SKIP_V_BOTH"]
    second=pair["root_calls"][1]
    def present(row,epoch,depth):
        return any(e["epoch"]==epoch and e["raw_depth"]==depth and
                   e["full64_match"]==1 for e in row["shadow_last_writer_at_second_TT_probe"])
    for label in ("NONE_V_BOTH","NONE_NATIVE_SECOND"):
        need(output["arms"][label]["UCI"]==prior["selectors"][SELECTOR]["arms"]["BOTH"]["UCI"],
             "REPLAY_UNMODIFIED_JANUARY_"+label)
    need(none["V_reader_block_calls"]==[pair["root_calls"][0]],"NATIVE_FIRST_BLOCK_REPLAY")
    need(full["V_reader_block_calls"]==[4,5] and skipped["V_reader_block_calls"]==[4,5],
         "PREVIOUS_FULL_OR_SKIP_REPLAY")
    rules={
      "ID0_NONINTERFERENCE":"PASS",
      "ID1_FACTOR_CONTACT":"PASS" if (
        skipped["writer_skip_count"]==1 and all(
        output["arms"][n+"_V_BOTH"]["writer_reinstated_count"]==1 for n in
        ("REINSTATE","BYTES_ONLY","SHADOW_ONLY"))) else "NOT_TESTED",
      "ID2_SHADOW_ONLY_TAUTOLOGY":"PASS_TRAP_CONFIRMED" if (
        shadow["V_second_root_blocked"] and
        bool(shadow["raw_payload_witness_mismatches"]) and present(shadow,1,1)
        ) else "FAIL_PREDICTION",
      "ID3_BYTES_ONLY_DISTINCTION":"PASS_CONVERSE_TRAP_CONFIRMED" if (
        not by["V_second_root_blocked"] and present(by,2,0)
        ) else "FAIL_PREDICTION",
      "ID4_INDEPENDENT_NATIVE_USE":"PASS" if all(
        not r["V_second_root_blocked"]
        for name,r in output["arms"].items() if name.endswith("_NATIVE_SECOND")
        ) else "FAIL",
      "ID5_NEGATIVE_SHAM":"NOT_TESTED_EXPLICIT_WRITER_DECOY_IN_PREVIOUS_P0P1_ONLY"}
    # The "passive" second root branch might not satisfy old shadow target;
    # actual assignment observer still independently records native use.
    output["summary"]={
        "arms":len(output["arms"]),"cold_duplicates_per_arm":2,
        "original_native_bestmove":baseline["UCI"]["bestmove"],
        "second_targeted_call":second,
        "policy_block_at_second":{
           name:output["arms"][name+"_V_BOTH"]["V_second_root_blocked"]
           for name in POLICIES},
        "policy_actual_native_value_use_at_second":{
           name:output["arms"][name+"_NATIVE_SECOND"]["actual_native_eval_use_count"]
           for name in POLICIES},
        **rules}
    output["limits"]=[
        "Single adaptively selected January source case, not independent blind data",
        "SHADOW_ONLY is a deliberately inconsistent shadow/native state, not a physically natural trajectory",
        "The V source reader_block proves an eligible value was BLOCKED, not actually used",
        "Actual native eval assignment after source V guard is independently recorded",
        "Partial restoration intentionally allows physical bytes and shadow epoch to disagree",
        "No categorical bestmove mediation established even when native consumer available"]
    out=Path(a.out);out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(output,indent=2,sort_keys=True)+"\n")
    print("C3X019_ORTHOGONAL_WRITER_IDENTITY_NATIVE_RESULT",
          json.dumps(output["summary"],sort_keys=True),flush=True)
if __name__=="__main__":main()
