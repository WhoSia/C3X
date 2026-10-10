#!/usr/bin/env python3
"""Read-only exact native SEE target transfer from T1, BEFORE actuator.

Result eligible if first real native matched SEE call is quiet/qsearch pruning,
exact same actual search state and path in TT-original and TT-FIRST, post
source TT actual use and physical block. No treatment code executed here.
"""
import argparse,hashlib,json
from pathlib import Path

T1_SHA="6c0440693c83ba0cd219d396b7d1cb2cdd14e3324f0c0f77485edf1df288c0a8"
SOURCE_SHA="0ff43e28dcb3a5e48dea6b61e4450fc8bb9e1f96363871c33c4b73524664db61"
DECIDED=((1,"O","STRICT"),(11,"F","STRICT"),(12,"F","STRICT"),(2,"O","STRICT"))
SCHEMA="c3x023-P1-R2-T2-preactuation-four-May-source-exact-native-SEE-targets-v1"
SITES=("quiet_prune","qsearch_prune")

def prepare(content):
    if content["schema"]!="c3x023-P1-R2-T1-native-same-search-state-SEE-after-TT-source-v1":
        raise ValueError("T2_T1_RESULT_INVALID")
    if content["new_licensed_source_sha256"]!=SOURCE_SHA:
        raise ValueError("T2_SOURCE_CHESS32_NOT_FROZEN")
    lookup={(c["source_id"],c["root_order"],c["source_role"]):c
            for c in content["cases"]}
    if len(lookup)!=6:raise ValueError("T2_DEVELOPMENT_CASE_COUNT_DRIFT")
    records=[]
    for key in DECIDED:
        c=lookup[key];p=c["causal_observational_state_classification"]
        matches=[e for e in p.get("exact_state_events",[]) if e["site"] in SITES
                 and e["actual_source_TT_score_used_before_SEE"] is True
                 and e["actual_selected_TT_first_reader_blocked_before_SEE"] is True
                 and e["original_native_SEE_Boolean"] in (0,1)]
        matches.sort(key=lambda x:(x["t1_source_line_ordinal_original"],
                                   x["t1_source_line_ordinal_TT_FIRST"]))
        target=None
        if matches:
            m=matches[0];st=m["native_search_state"]
            target={"key64":m["key64"],"parent_key64":m["parent_key64"],
                    "t1_path":m["t1_exact_ancestor_path"],"root_call":m["source_root_call"],
                    "root_move":m["source_root_move"],"move":m["move"],
                    "site":m["site"],"threshold":m["threshold"],
                    "original_SEE_Boolean":m["original_native_SEE_Boolean"],
                    **{k:st[k] for k in ("t1_ply","t1_depth","t1_alpha",
                                         "t1_beta","t1_pv","t1_qsearch",
                                         "t1_rule50","t1_occupied_present",
                                         "t1_occupied_out")},
                    "source_first_observed_line":m["t1_source_line_ordinal_original"],
                    "source_TT_FIRST_observed_line":m["t1_source_line_ordinal_TT_FIRST"]}
            if target["t1_path"].split(",")[-1]!=str(target["key64"]):
                raise ValueError("T2_ANCESTRY_TRAJECTORY_DOES_NOT_END_AT_TARGET")
        records.append({"game_id":key[0],"root_order":key[1],"source_role":key[2],
            "known_R1_final_move_changed":bool(c["actual_terminal_bestmove_flipped"]),
            "source_prep_status":"EXACT_TARGET_PRESEALED_READY" if target else
                "HOLD_NO_QUIET_QSEARCH_MATCH_IN_FIRST32_PREFIX",
            "source_exact_pruning_SEE_target":target,
            "total_T1_matched_source_states":len(p.get("exact_state_events",[])),
            "eligible_quiet_qsearch_state_count":len(matches)})
    return {"schema":SCHEMA,"phase":"PRE_ACTUATOR_SOURCE_LITERAL_TARGETS",
            "method":"deterministically earliest T1 common exact native quiet/qsearch pruning SEE site",
            "original_licensed32_source_sha256":SOURCE_SHA,
            "original_T1_raw_full_SHA256":T1_SHA,
            "prior_mechanism_precommit":"c3x/ontology/c3x-023-P1-R2-T2-preactuation-exact-source-SEE-target-selection-rule.md",
            "cases":records,
            "summary":{"fixed_development_games":len(DECIDED),
                "target_exact_node_ready":sum(r["source_exact_pruning_SEE_target"] is not None for r in records),
                "target_scope_HOLD":sum(r["source_exact_pruning_SEE_target"] is None for r in records),
                "source_T2_Boolean_interventions_performed":0,
                "source_history_score_use_and_physical_TT_FIRST_precede_target":True,
                "four_cases_selected_retrospectively_after_R1":True,
                "has_no_original_full_PGN":True}}

def main():
    p=argparse.ArgumentParser();p.add_argument("--t1",required=True);p.add_argument("--out",required=True)
    q=p.parse_args();raw=Path(q.t1).read_bytes()
    if hashlib.sha256(raw).hexdigest()!=T1_SHA:
        raise ValueError("T2_T1_NATIVE_UNTREATED_RAW_REPLAY_SHA_NOT_EQUAL")
    d=prepare(json.loads(raw));out=Path(q.out);out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(d,sort_keys=True,indent=2)+"\n")
    print("C3X023_T2_PRE_ACTUATOR_SOURCE_SIGNATURES_FROZEN",d["summary"],
          hashlib.sha256(out.read_bytes()).hexdigest(),flush=True)
if __name__=="__main__":main()
