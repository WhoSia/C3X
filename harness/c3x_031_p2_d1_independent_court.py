"""C3X 0.31 P2-D1: independent SHA-bound 78-native-search, 156-log audit.

Data are retrospective 7-case depth tests selected AFTER original P2 results.
This verifier performs zero new chess searches; it checks raw logs and
preserves the distinction between a changed move and the same original pair.
"""
from __future__ import annotations
from collections import Counter
import argparse
import hashlib
import json
from pathlib import Path
import re

FULL_JSON_SHA = "e2a56d69342fbe60a522f62b69ca01c08446008c482a571b8dc0a47e5ba95f90"
FULL_LOGS_ZIP_SHA = "e45dca037f748a06e5043194de397ca26659af726c174a9505f097a5566202bc"
P2_PRECONTACT_JSON_SHA = "17915c7d9ae56dd950cd026d07a4917a414213415ea3b28af256b305eb8ad146"
P2_TREATED_JSON_SHA = "69904f920c21844f2a2f278f6332b7c8fdc9857a821c33fdc0f29dfa56aaf09f"


def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def require(value,why):
    if not value:
        raise ValueError(why)

def normalize(raw):
    return [re.sub(r"\b(?:time|nps) \d+ ?", "",s)
            for s in raw.decode().splitlines() if s.startswith(("info depth ","bestmove "))]

def verify(data,log_dir,p2_precontact,p2_treated):
    require(data["id"]=="C3X_031_P2_D1_EQUAL_DEPTH_DIAGNOSIS"
            and data["classification"]=="POST_OUTCOME_SELECTED_EXPLORATORY_NATIVE_DEPTH_RESEARCH"
            and data["seven_postselected_cases"]==7
            and data["frozen_depth_cells"]==13,
            "retrospective seven-game target/cell denominator changed")
    files={p.relative_to(log_dir).as_posix():p
           for p in Path(log_dir).rglob("*.txt")}
    require(len(files)==156, "original 78 native searches should have 156 text logs")
    by_source={x["id"]:x for x in p2_precontact["source_events"]}
    by_treat={x["id"]:x for x in p2_treated["cases"]}
    require(len(by_source)==len(by_treat)==64,"original P2 native context missing")
    counts=Counter()
    comparisons=[]
    frozen_events=set(data["frozen_seven_source_events"])
    require(len(frozen_events)==7,"duplicate source event")
    for case in data["results"]:
        ident=case["source_event_id"]
        game,group=ident.rsplit("-",1)
        require(game in by_source and game in by_treat
                and case["original_32k_bestmove"]==by_source[game]["baseline_bestmove"]
                and case["treated_32k_bestmove"]==
                    by_treat[game]["targets"][group]["arms"]["both_off"]["final_move"]
                and case["target"]==by_source[game]["targets"][group]["target"],
                "original P2 32k move pair or event was rewritten")
        require(ident in frozen_events and
                len(case["fixed_depth_cells"])==len(
                    set([case["original_32k_depth"],case["treatment_32k_depth"]])),
                "original source events/depth choices changed")
        frozen_events.remove(ident)
        cells={}
        for cell in case["fixed_depth_cells"]:
            depth=cell["depth"]
            folder=f"{ident}/depth-{depth}"
            require(depth in (case["original_32k_depth"],case["treatment_32k_depth"])
                    and depth not in cells, "unexpected or duplicated depth")
            cells[depth]=cell
            for arm in ("R31-reference","R33-off"):
                label="reference_native" if arm=="R31-reference" else "observer_disabled_native"
                r=cell[label]
                for ext in ("stdout.txt","stderr.txt"):
                    require(folder+"/"+arm+"/"+ext in files,
                            "missing historical untouched native log")
                orig_out=normalize(files[folder+"/"+arm+"/stdout.txt"].read_bytes())
                require(orig_out==r["uci"] and
                        sha(files[folder+"/"+arm+"/stderr.txt"].read_bytes())==r["stderr_sha256"],
                        "source control logs were not faithfully stored")
                require(r["best"]["move"]==orig_out[-1].split()[1],
                        "source reference best disagrees with original UCI")
                counts["native_sources"]+=1
            for treatment in ("untouched","both_off"):
                rows=cell["all_repeats"][treatment]
                require(len(rows)==2,"cold source repeat absent")
                for rep,r in enumerate(rows):
                    folder2=f"{folder}/{treatment}-{rep}"
                    out=normalize(files[folder2+"/stdout.txt"].read_bytes())
                    require(out==r["uci"]
                            and r["best"]["move"]==out[-1].split()[1]
                            and sha(files[folder2+"/stderr.txt"].read_bytes())==r["stderr_sha256"],
                            "source-intervention UCI/stderr raw artifact mismatch")
                    require(r["actual_completed_depth"]==depth,
                            "supposedly fixed-depth source arm did not complete depth")
                    if r["target_event"] is not None and r["contact_status"]=="SOURCE_TARGET_PHYSICALLY_MATCHED":
                        require(r["target_event"]["open"]==case["target"]
                                and r["target_event"]["close"]["stopped"]=="0",
                                "target identity not source-matched")
                    counts["native_sources"]+=1
                # replays were already required identical by original executor
                for field in ("best","uci","target_event","contact_status","nodes"):
                    require(rows[0][field]==rows[1][field],
                            "repeated native source outcomes changed")
            control=cell["control"]
            treated=cell["treatment"]
            require(control==cell["all_repeats"]["untouched"][0]
                    and treated==cell["all_repeats"]["both_off"][0],
                    "reported arm does not equal actual native source case")
            contact=(control["contact_status"]==treated["contact_status"]==
                     "SOURCE_TARGET_PHYSICALLY_MATCHED")
            observed=control["best"]["move"]!=treated["best"]["move"]
            if not contact:
                status="HOLD_SOURCE_CONTACT_OR_IDENTITY"
            elif observed:
                status="VALID_EQUAL_DEPTH_FINAL_CHOICE_CHANGED"
            else:
                status="VALID_EQUAL_DEPTH_NO_FINAL_CHOICE_CHANGE"
            require(cell["status"]==status and
                    cell["root_choice_changed"]==observed,
                    "source depth case published classification differs")
            counts[status]+=1
            if cell["is_original_completed_depth"]:
                original_pair=(case["original_32k_bestmove"],
                               case["treated_32k_bestmove"])
                fixed_pair=(control["best"]["move"],
                            treated["best"]["move"])
                comparisons.append({
                    "source_event":ident,
                    "full_depth":depth,
                    "status":status,
                    "exact_original_32k_pair_reproduced":original_pair==fixed_pair,
                    "original_32k_move_pair":original_pair,
                    "fixed_depth_move_pair":fixed_pair,
                    "control_nodes":control["nodes"],
                    "treated_nodes":treated["nodes"]
                })
    require(not frozen_events
            and counts["native_sources"]==78
            and len(comparisons)==7,
            "full native search denominator not reproduced")
    require(counts["VALID_EQUAL_DEPTH_FINAL_CHOICE_CHANGED"]==8
            and counts["VALID_EQUAL_DEPTH_NO_FINAL_CHOICE_CHANGE"]==4
            and counts["HOLD_SOURCE_CONTACT_OR_IDENTITY"]==1,
            "13-depth native label census mismatched")
    require(sum(r["status"]=="VALID_EQUAL_DEPTH_FINAL_CHOICE_CHANGED"
                for r in comparisons)==5,
            "exact 7-case original-depth comparison did not reproduce")
    require(sum(r["exact_original_32k_pair_reproduced"]
                for r in comparisons)==1,
            "source root pair transport claim violated")
    p=next(r for r in comparisons if r["source_event"]=="P2-028-0")
    require(p["exact_original_32k_pair_reproduced"]
            and p["control_nodes"]==35662
            and p["treated_nodes"]==36217,
            "P2-028 native root-pair and near-work witness not reproduced")
    return {
        "id":"C3X_031_P2_D1_INDEPENDENT_FULL_NATIVE_LOG_COURT",
        "evidence":"ORIGINAL_156_FILE_LOG_AUDIT_NO_NEW_NATIVE_SEARCH",
        "original_D1_full_result_json_sha256":FULL_JSON_SHA,
        "postoutcome_selected_games":7,
        "source_depth_cells":13,
        "original_native_searches":78,
        "original_log_files_rehashed":156,
        "new_searches_in_this_verifier":0,
        "complete_original_depth_root_flips":5,
        "complete_original_depth_root_same":2,
        "original_32k_exact_move_pair_reproduced":1,
        "per_case_original_depth":comparisons,
        "all_cell_statuses":dict(counts),
        "P3_candidate":"P2-028-0 source target, original fixed depth 16, exact UCI pair, original 35,662 vs 36,217 nodes",
        "claim_limit":"Postselected exploratory fixed completed depth is not matched node work, TT-history mediation, chess merit or human learning."
    }

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("source_json",type=Path)
    ap.add_argument("original_log_folder",type=Path)
    ap.add_argument("p2_precontact",type=Path)
    ap.add_argument("p2_original_treated",type=Path)
    ap.add_argument("out",type=Path)
    args=ap.parse_args()
    raw=args.source_json.read_bytes()
    require(sha(raw)==FULL_JSON_SHA,"original D1 JSON SHA mismatch")
    pre_bytes=args.p2_precontact.read_bytes()
    treated_bytes=args.p2_original_treated.read_bytes()
    require(sha(pre_bytes)==P2_PRECONTACT_JSON_SHA
            and sha(treated_bytes)==P2_TREATED_JSON_SHA,
            "original precontact or treated P2 source changed")
    result=verify(json.loads(raw),args.original_log_folder,
                  json.loads(pre_bytes),json.loads(treated_bytes))
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("P2_D1_INDEPENDENT",result["all_cell_statuses"],
          "original_pair_preserved",result["original_32k_exact_move_pair_reproduced"],
          "output_sha256",sha(args.out.read_bytes()))

if __name__=="__main__":
    main()
