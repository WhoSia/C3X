#!/usr/bin/env python3
"""C3X021 P1-R1 full64 native second-consumer probes for all 31 March roles.

No target choice depends on this rerun: selected pairs and baseline UCI
come from SHA-frozen P1 March court. A reader-block, key hit, and native
eval/cutoff consumption are three DISTINCT kinds of evidence.
"""
import argparse,hashlib,json
from pathlib import Path
from c3x_018_native_TT_lineage_factorial_6_8 import play,need
from c3x_018_independent16_TT_value_transport_native import canonical_engine_world
from c3x_018_chess_clock_factorial_original_history_native import game_clocks
from c3x_018_jan16_TT_cross_window_pair_native import RULES,mask_filters

SOURCE_SHA="d79e48633be2b683176f1a6d4650aeea1b7584f11c85c2349a5bddda113febee"
P1_SHA="5ee15c3ec48be0042a9bb0ae7566808737f56e7568c2b29d43f00ae64afcb259"
ROLES=("STRICT","BROAD")
USE_SITES=("main","qsearch","main_cutoff","qsearch_cutoff")
FLIP_GROUP=((4,"BROAD"),(9,"STRICT"))

def checked(path,sha):
    raw=Path(path).read_bytes()
    need(hashlib.sha256(raw).hexdigest()==sha,
         "C3X021_R1_FROZEN_SHA_"+Path(path).name)
    return json.loads(raw)

def actual_use_analysis(x,physical,watch):
    probes=x["watched_tt_probes"]
    uses=x["native_tt_value_uses"]
    need(not any(e.get("kind")=="censored" for e in probes),
         "WATCHED_FULL64_PROBE_CENSORED")
    need(not any(e.get("kind")=="censored" for e in uses),
         "WATCHED_NATIVE_USE_CENSORED")
    need(all(p.get("key64")==watch["key64"]
             and p.get("root_call")==watch["root_call"] for p in probes),
         "WRONG_NATIVE_PROBE_SOURCE_KEY")
    actual=[e for e in uses if e.get("kind")=="used"]
    need(all(e.get("site") in USE_SITES and
             e.get("key64")==watch["key64"] and
             e.get("root_call")==watch["root_call"] and
             e.get("full64_match")==1 for e in actual),
         "WRONG_NATIVE_USE_SOURCE_OR_SITE")
    hits=[p for p in probes if p.get("kind")=="probe" and
          p.get("tt_hit")==1]
    full=[p for p in hits if p.get("shadow_full64_match")==1
           and p.get("tt_slot")==physical["slot"]]
    need(not actual or full,
         "NATIVE_USE_WITHOUT_MATCHING_FULL64_PHYSICAL_PROBE")
    return {
        "watched_root_call":watch["root_call"],
        "watched_full64_key":str(watch["key64"]),
        "probe_records":len(probes),
        "physical_TT_hits":len(hits),
        "live_full64_shadow_hits":len(full),
        "native_eval_assignment_events":sum(e["site"] in ("main","qsearch") for e in actual),
        "native_main_or_qsearch_cutoff_events":sum(e["site"] in ("main_cutoff","qsearch_cutoff") for e in actual),
        "native_use_count":len(actual),
        "native_use_events":actual,
        "probe_witnesses":probes,
        "class":"NATIVE_SCORE_OR_CUTOFF_USED" if actual else
                "FULL64_PROBE_WITH_NO_ACTUAL_NATIVE_USE" if full else
                "PROBE_WITHOUT_FULL64_SHADOW" if hits else "NO_WATCHED_HIT",
    }

def watch_cold(engine,world,clock,role,prior):
    physical=prior["source_physical"]
    root_calls=prior["source_root_calls"]
    pair={
        "physical":physical,"root_calls":root_calls,
        "root_candidate_native":prior["source_root_move_native"]
    }
    watcher={"key64":physical["key64"],"root_call":root_calls[1]}
    kwargs={"fen_clocks":clock,
            "tt_reader_filters":mask_filters(RULES[role],pair,"FIRST"),
            "probe_watch":watcher,
            "native_use_watch":watcher}
    a=play(engine,world,"F","V",physical,**kwargs)
    b=play(engine,world,"F","V",physical,**kwargs)
    need(a==b,"WATCH_COLD_REPEAT")
    need(a["UCI"]==prior["V"]["UCI"],"ORIGINAL_MARCH_V_SIX_FIELD_DRIFT")
    blocks=[e for e in a["blocks"] if e["kind"]=="reader_block"]
    need(len(blocks)==prior["actual_reader_block_count"],
         "ORIGINAL_SOURCE_FIRST_READER_CONTACT_DRIFT")
    need(all(e["root_call"]==root_calls[0] and
             all(e[field]==physical[field] for field in ("key64","slot","epoch"))
             for e in blocks),"ORIGINAL_FIRST_PHYSICAL_READER_IDENTITY_DRIFT")
    evidence=actual_use_analysis(a,physical,watcher)
    evidence["matched_first_reader_block_count"]=len(blocks)
    evidence["V_core"]=a["UCI"]
    evidence["root_event_count"]=len(a["root_events"])
    evidence["original_final_bestmove_changed"]=prior["categorical_F_V_bestmove_changed"]
    evidence["cold_repeat"]=True
    return evidence

def court(source,prior,engine):
    need(len(source["selected"])==len(prior["cases"])==16,
         "FULL16_SOURCE_DENOMINATOR")
    report={"schema":"c3x021-P1-R1-march16-watched-full64-TT-native-second-consumer-v1",
            "source_sha256":SOURCE_SHA,
            "parent_P1_native_sha256":P1_SHA,
            "planned_role_denominator":32,
            "watch_rule":"exact selected second root-call of first full64 physical same-writer pair",
            "cases":[]}
    for sf,frozen in zip(source["selected"],prior["cases"]):
        gid=sf["id"]
        need(gid==frozen["id"] and sf["source_game_sha256"]==frozen["source_sha"],
             "SOURCE_PROVENANCE_ALIGNMENT")
        world,_=canonical_engine_world(sf)
        clock=game_clocks(sf)
        row={"game":gid,"roles":{}}
        for role in ROLES:
            old=frozen["roles"][role]
            if old["status"]=="NO_ELIGIBLE_PHYSICAL_PAIR":
                row["roles"][role]={"class":"NO_ELIGIBLE_PHYSICAL_PAIR"}
                continue
            need(old["status"]=="ACTUAL_SOURCE_CONTACT",
                 "UNEXPECTED_ORIGINAL_NONCONTACT")
            row["roles"][role]=watch_cold(engine,world,clock,role,old)
        report["cases"].append(row)
        print("C3X021_P1_R1_WATCH",gid,
              {k:(v["class"],v.get("native_use_count",0)) for k,v in row["roles"].items()},
              flush=True)
    stats={
        "full_source_games":16,
        "role_denominator":32,
        "eligible_roles":sum(r["class"]!="NO_ELIGIBLE_PHYSICAL_PAIR"
                         for c in report["cases"] for r in c["roles"].values()),
        "roles_with_physical_probe":sum(r.get("live_full64_shadow_hits",0)>0
                         for c in report["cases"] for r in c["roles"].values()),
        "roles_with_native_eval_assignment":sum(r.get("native_eval_assignment_events",0)>0
                         for c in report["cases"] for r in c["roles"].values()),
        "roles_with_native_cutoff":sum(r.get("native_main_or_qsearch_cutoff_events",0)>0
                         for c in report["cases"] for r in c["roles"].values()),
        "historical_P1_reader_block_bestmove_flips":2,
        "observed_flipped_cases":{
            str(gid)+"_"+role:{
                "class":report["cases"][gid-1]["roles"][role]["class"],
                "native_use_count":report["cases"][gid-1]["roles"][role]["native_use_count"],
                "live_full64_shadow_hits":report["cases"][gid-1]["roles"][role]["live_full64_shadow_hits"],
            } for gid,role in FLIP_GROUP},
        "historical_F19_5":"FAIL_RETAINED",
        "historical_K4":"FAIL_0_OF_4_RETAINED",
    }
    need(stats["eligible_roles"]==31,"FROZEN_ELIGIBLE_31_DENOMINATOR")
    report["summary"]=stats
    return report

def main():
    p=argparse.ArgumentParser()
    for field in ("march","prior-native","engine","out"):
        p.add_argument("--"+field,required=True)
    a=p.parse_args()
    result=court(checked(a.march,SOURCE_SHA),
                 checked(a.prior_native,P1_SHA),a.engine)
    out=Path(a.out)
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,sort_keys=True,indent=2)+"\n")
    print("C3X021_P1_R1_FULL64_NATIVE_WATCH_VERDICT",
          json.dumps(result["summary"],sort_keys=True),flush=True)
if __name__=="__main__":main()
