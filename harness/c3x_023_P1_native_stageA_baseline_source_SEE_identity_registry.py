#!/usr/bin/env python3
"""C3X0.23-P1 new licensed May16/CC0 nonmate16 native StageA READ-ONLY.

Do NOT call V FIRST reader blocker, and do not derive any treatment outcome.
Cold twice passive O/F, physically discover STRICT/BROAD first writer-reader
witness, preregister M0 and historical failed M1 literal exact UCI. For each
source world with a STRICT source pair, passively observe first32 native SEE
events (real descendant keys/ancestors from new source-path overlay) to seed a
pre-outcome source identity registry. No graph-mediator effect inferred.
"""
import argparse,hashlib,json
from pathlib import Path
from c3x_018_native_TT_lineage_factorial_6_8 import play,need
from c3x_018_jan16_TT_cross_window_pair_native import RULES,first_pair
from c3x_022_P2_two_stage_exact_move_scout import native_world,cold,source_depth_ladder

SOURCE_SHA="0ff43e28dcb3a5e48dea6b61e4450fc8bb9e1f96363871c33c4b73524664db61"
ECOLOGIES=("may2026_broadcast","lichess_CC0_nonmate_puzzles")
WORLDS=("O","F")
ROLES=("STRICT","BROAD")
SCHEMA="c3x023-P1-licensed-May-and-CC0-stageA-untreated-native-node-SEE-rivals-v1"

def immutable(path,sha):
    raw=Path(path).read_bytes()
    need(hashlib.sha256(raw).hexdigest()==sha,"P1_NEW_LICENCED_SOURCE_SHA_DRIFT")
    return json.loads(raw)

def literal(base,other,eligible):
    if not eligible:
        return {"status":"NO_ELIGIBLE_SOURCE","M0":None,"M1":None}
    return {"status":"PRECOMMITTED_EXACT_UCI_NO_V",
            "M0":base,
            "M1":other if other!=base else base,
            "M0_predict_flip":False,
            "M1_predict_flip":other!=base}

def stageA(source,engine):
    need(source["schema"]=="c3x023-P1-licensed-independent-May-broadcast-and-disjoint-CC0-nonmate-puzzles-v1","WRONG_NEW_SOURCE")
    need(source["phase"]=="SOURCE_ONLY__NO_ENGINE_OR_NATIVE_RESULT_YET","SOURCE_WAS_NOT_ENGINE_BLIND")
    outcome={"schema":SCHEMA,"phase":"NEW_P1_STAGE_A_ONLY_WITH_NO_INTERVENTION",
             "source_sha256":SOURCE_SHA,"ecologies":{}}
    for eco in ECOLOGIES:
        new_rows=source["per_ecology"][eco]["selected"]
        need(len(new_rows)==16 and [x["id"] for x in new_rows]==list(range(1,17)),"P1_NEW16_FIXED")
        records=[]
        for record in new_rows:
            world,clocks,_=native_world(record)
            baseline={};candidates={};discovery_lengths={}
            for order in WORLDS:
                obs=cold(engine,world,clocks,order)
                discovery=cold(engine,world,clocks,order,discovery=True)
                need(obs["UCI"]==discovery["UCI"],"P1_READONLY_DISCOVERY_CHANGED_BASELINE")
                ev=[x for x in discovery["payload_witnesses"] if x["kind"]=="discovery"]
                need(len(ev)<=2048,"P1_SOURCE_DISCOVERY_OVER_LIMIT")
                baseline[order]=obs
                candidates[order]={r:first_pair(ev,RULES[r]) for r in ROLES}
                discovery_lengths[order]=len(ev)
            old={w:baseline[w]["UCI"]["bestmove"] for w in WORLDS}
            entry={"id":record["id"],"source_sha256":record["source_game_sha256"],
                   "source_puzzle_id":record.get("source_puzzle_id"),
                   "root_F_input_is_original_game_or_puzzle_solution":True,
                   "worlds":{}}
            for order in WORLDS:
                targets={}
                for role in ROLES:
                    pair=candidates[order][role]
                    if pair is None:
                        targets[role]={"status":"HOLD_CENSORED_UNKNOWN" if discovery_lengths[order]==2048 else "NO_ELIGIBLE_SOURCE",
                                       "physical":None,
                                       "exact_UCI":literal(old[order],old["F" if order=="O" else "O"],False)}
                    else:
                        targets[role]={"status":"FIRST_SOURCE_PAIR_PRE_OUTCOME",
                                       "physical":pair["physical"],
                                       "root_calls":pair["root_calls"],
                                       "root_candidate_native":pair["root_candidate_native"],
                                       "source_indices":pair["indices"],
                                       "exact_UCI":literal(old[order],old["F" if order=="O" else "O"],True)}
                strict=targets["STRICT"]
                watch_events=[];partial=False; native_use=[]
                if strict["status"]=="FIRST_SOURCE_PAIR_PRE_OUTCOME":
                    w={"key64":strict["physical"]["key64"],
                       "root_call":strict["root_calls"][0],
                       "policy":"OBS","passive_ancestry":True}
                    kw={"fen_clocks":clocks,"allow_empty_lineage":True,"see_watch":w,
                        "native_use_watch":{"key64":w["key64"],"root_call":w["root_call"]}}
                    x=play(engine,world,order,"OBS",**kw)
                    y=play(engine,world,order,"OBS",**kw)
                    need(x==y,"P1_PATH_READONLY_COLD_REPRO")
                    need(x["UCI"]==baseline[order]["UCI"],"P1_NODE_PATH_WATCH_INTERFERED")
                    need(x["lineage_summary"]["reader_block"]==0,"P1_STAGEA_READER_BLOCK_FORBIDDEN")
                    watch_events=x["native_see_events"]
                    partial=any(e["kind"]=="censored" for e in watch_events)
                    need(all(e.get("original")==e.get("delivered") and e.get("altered")==0
                             for e in watch_events if e["kind"]=="witness"),
                         "P1_SEE_WATCH_MODIFIED_RETURN")
                    need(all("path_hash" in e and "parent_key64" in e and
                             "path_length" in e and e["path_length"]>0
                             for e in watch_events if e["kind"]=="witness"),
                         "P1_NATIVE_POSITION_ANCESTOR_MISSING")
                    native_use=x["native_tt_value_uses"]
                entry["worlds"][order]={
                  "baseline_UCI":baseline[order]["UCI"],
                  "depth_leaders":source_depth_ladder(baseline[order]["root_events"]),
                  "roles":targets,
                  "passive_first32_SEE_events":watch_events,
                  "passive_SEE_witness_censored":partial,
                  "passive_native_TT_value_use_witnesses":native_use,
                  "path_observer_changed_sixfield_UCI":False}
            records.append(entry)
            print("C3X023_P1_NEW_NATIVE_BASELINE_SOURCE_REGISTRATION",eco,record["id"],
                  "O_F_disagree",old["O"]!=old["F"],
                  "strict_sites",{w:len(entry["worlds"][w]["passive_first32_SEE_events"])
                                  for w in WORLDS},flush=True)
        outcome["ecologies"][eco]={"license":source["per_ecology"][eco]["source"]["license"],
                                    "cases":records}
    rows=[(ec,c,o,r,x) for ec,v in outcome["ecologies"].items()
          for c in v["cases"] for o,w in c["worlds"].items()
          for r,x in w["roles"].items()]
    eligible=[x for x in rows if x[4]["status"]=="FIRST_SOURCE_PAIR_PRE_OUTCOME"]
    outcome["summary"]={"distinct_source_boards":32,"world_count":64,"potential_role_cells":128,
     "eligible_source_first_reader_role_cells":len(eligible),
     "literal_forecast_UCI_strings":len(eligible)*2,
     "O_F_baselines_differ_games_by_ecology":{
       ec:sum(c["worlds"]["O"]["baseline_UCI"]["bestmove"]!=
              c["worlds"]["F"]["baseline_UCI"]["bestmove"]
              for c in v["cases"]) for ec,v in outcome["ecologies"].items()},
     "passive_SEE_root_worlds_with_true_source_event":
        sum(bool(c["worlds"][o]["passive_first32_SEE_events"])
            for v in outcome["ecologies"].values() for c in v["cases"] for o in WORLDS),
     "native_SEE_first32_events_observed":
        sum(sum(e["kind"]=="witness" for e in c["worlds"][o]["passive_first32_SEE_events"])
            for v in outcome["ecologies"].values() for c in v["cases"] for o in WORLDS),
     "actual_TT_FIRST_interventions":0,"actual_SEE_Boolean_interventions":0,
     "treatment_outcomes_seen":False,
     "mechanism_identification":"PRE_OUTCOME_SOURCE_PATH_WITNESSES_ONLY_NOT_TT_V_ARM_ALIGNED"}
    return outcome

def main():
    p=argparse.ArgumentParser()
    for field in ("source","engine","out"):p.add_argument("--"+field,required=True)
    a=p.parse_args()
    x=stageA(immutable(a.source,SOURCE_SHA),a.engine)
    out=Path(a.out);out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(x,sort_keys=True,indent=2,ensure_ascii=False)+"\n")
    print("C3X023_P1_NATIVE_NO_TREATMENT_SOURCE_REGISTRY",x["summary"],
          hashlib.sha256(out.read_bytes()).hexdigest(),flush=True)
if __name__=="__main__":main()
