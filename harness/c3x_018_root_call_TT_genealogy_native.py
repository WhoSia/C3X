#!/usr/bin/env python3
"""C3X 0.18 within-arm root call, candidate and TT cutoff genealogy court.

Pairs root-local candidate return evidence with within-arm TT cutoff ancestry.
A join on root_call and root_move is descriptive only; it does not prove that
one TT event causes candidate return or any O/F cross-arm event identity.
"""
import argparse,hashlib,json
from pathlib import Path
from collections import Counter,defaultdict
from c3x_018_native_TT_lineage_factorial_6_8 import play,need
from c3x_018_TT_writer_dose_6_8 import TARGETS

def summarize(x):
    roots=x["root_events"]
    need(roots,"ROOT_EVENTS_ABSENT")
    need(len(roots)<4096,"ROOT_TRACE_CENSORED")
    need(all("root_call" in r and "trial" in r for r in roots),"ROOT_TRIAL_ID_MISSING")
    need(all("root_call" in e and "root_move" in e for e in x["consumer_records"]),
         "TT_ANCESTRY_FIELD_MISSING")
    calls=defaultdict(lambda:{"windows":[],"candidates":[],"after_sort":[],"tt":Counter(),"first_move":None})
    for e in roots:
        call=e["root_call"]
        if e["kind"]=="window_enter":
            calls[call]["windows"].append({
              "depth":e["depth"],"trial":e["trial"],"alpha":e["alpha"],
              "beta":e["beta"],"first_move":e["first_move"]})
            calls[call]["first_move"]=e["first_move"]
        elif e["kind"]=="candidate":
            calls[call]["candidates"].append({k:e[k] for k in
                ("move","child_return","alpha","beta","before","after","index")})
        elif e["kind"]=="after_sort":
            calls[call]["after_sort"].append({k:e[k] for k in
                ("first_move","first_score","alpha","beta")})
    for evt in x["consumer_records"]:
        call=evt["root_call"]
        if call in calls:
            calls[call]["tt"][str(evt["root_move"])]+=1
    return {
      "root_event_count":len(roots),
      "root_calls":[{"root_call":key,
           "windows":entry["windows"],
           "candidates":entry["candidates"],
           "after_sort":entry["after_sort"],
           "tt_consumer_count_by_root_candidate":dict(entry["tt"])}
           for key,entry in sorted(calls.items())],
      "unattributed_tt_cutoff_events":sum(
           evt["root_call"] not in calls for evt in x["consumer_records"]),
      "root_attributed_tt_cutoffs":sum(
           evt["root_call"] in calls for evt in x["consumer_records"])
    }

def main():
    p=argparse.ArgumentParser()
    for key in ("cohort","prior","patched","out"):p.add_argument("--"+key,required=True)
    a=p.parse_args()
    data=json.loads(Path(a.cohort).read_text())
    prior=json.loads(Path(a.prior).read_text())
    result={"schema":"c3x018-root-aspiration-candidate-TT-cutoff-within-arm-genealogy-v1",
            "source_sha256":hashlib.sha256(Path(a.cohort).read_bytes()).hexdigest(),
            "prior_sha256":hashlib.sha256(Path(a.prior).read_bytes()).hexdigest(),
            "cases":[]}
    for case_id in (6,8):
        world=data["selected"][case_id-1]
        orig=prior["worlds"][case_id-1]["cells"]
        row={"id":case_id,"arms":{}}
        for root_mode,ttmode,dose in (("O","OBS",0),("F","OBS",0),("Z","OBS",0),
                                       ("F","W",2),("F","W",22 if case_id==6 else 2)):
            key=f"{root_mode}_{ttmode}_{dose}"
            target=TARGETS[case_id] if ttmode=="W" else None
            one=play(a.patched,world,root_mode,ttmode,target,
                     writer_budget=dose if ttmode=="W" else None)
            two=play(a.patched,world,root_mode,ttmode,target,
                     writer_budget=dose if ttmode=="W" else None)
            need(one==two,f"COLD_REPLAY_{case_id}_{key}")
            if ttmode=="OBS":
                need(one["UCI"]==orig[root_mode]["UCI"],
                     f"PASSIVE_OBSERVER_DRIFT_{case_id}_{key}")
            row["arms"][key]={"UCI":one["UCI"],
                    "TT_writer_block_count":one["lineage_summary"]["writer_block"],
                    "TT_cutoff_count":one["lineage_summary"]["consumer_reached"],
                    "within_arm":summarize(one)}
            print("C3X018_ROOT_TT_LINEAGE",case_id,key,one["UCI"]["bestmove"],
                  len(one["root_events"]),one["lineage_summary"]["consumer_reached"],
                  flush=True)
        need(row["arms"]["O_OBS_0"]["UCI"]==row["arms"]["Z_OBS_0"]["UCI"],
             f"NO_CONTACT_CORE_{case_id}")
        result["cases"].append(row)
    result["limitations"]=[
      "Within-arm source genealogy: root-call IDs are not cross-arm causal matches",
      "Physical TT cutoff event root_move is a thread-local current root candidate, not recursive call path ID",
      "TT event associated with root candidate is neither identified causal parent nor necessity",
      "Source candidate returns may reflect alternative qsearch/eval, sorting and TT uses",
      "Only 4096 root events; reject if the limit is reached",
      "Selected cases 6,8; finite depth 12, SF16, standalone FEN",
      "No rescue in this genealogy court, no unique natural mediation"]
    Path(a.out).write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("C3X018_ROOT_ASPIRATION_TT_GENEALOGY_NATIVE_PASS",flush=True)
if __name__=="__main__":main()
