#!/usr/bin/env python3
"""R48: frozen new-development-cohort source intervention, not H transport.
All 128 target slots retained, 126 physical targets x 2 arms x 2 repeats.
No adaptive selection; no claims of independent strategy or learner effects.
"""
import argparse
from collections import Counter,defaultdict
import json
from pathlib import Path
from c3x_031_r47_frozen_discovery import load_frozen,sha,require,CENSUS,BIN,NET
from c3x_030_r33_gate_panel import trial,select
from c3x_031_p2_treatment import matched
DISCOVERY="e82dd21d7c7b22b04c74c3719f8c63aadb3cff0b950e31eded6f4353ba755341"

def main():
    p=argparse.ArgumentParser()
    for k in ("census","discovery","folder","patch","net","out","receipt"):p.add_argument(k,type=Path)
    a=p.parse_args()
    require(sha(a.discovery.read_bytes())==DISCOVERY,"discovery drift")
    require(sha(a.patch.read_bytes())==BIN and sha(a.net.read_bytes())==NET,"native identity")
    d=json.loads(a.discovery.read_text())
    require(d["source_census_sha256"]==CENSUS and d["control_searches"]==192 and d["treatment_searches"]==0
            and d["target_statuses"]=={"FROZEN_UNTREATED":126,"NO_ELIGIBLE_EVENT":2},"preoutcome gate")
    cases=load_frozen(a.census,a.folder)
    require(len(cases)==len(d["cases"])==64,"denominator")
    results=[];searches=0
    for case,frozen in zip(cases,d["cases"]):
        ident=case["id"]
        require(all(case[k]==frozen[k] for k in ("id","ordinal","game_sha256","board_sha256","macro_family","ply")),"case identity")
        base=trial(a,case,ident+"/fresh-baseline",binary=a.patch,observer=True)
        searches+=1
        require(base["proof"]["best"]["move"]==frozen["baseline_best"] and len(base["events"])==frozen["event_count"],"untreated drift")
        selection=select(base["events"])
        row={"id":ident,"family":case["macro_family"],"baseline_best":frozen["baseline_best"],"targets":{}}
        for group in ("0","1"):
            t=frozen["targets"][group]
            if t["status"]=="NO_ELIGIBLE_EVENT":
                require(group not in selection,"no-event drift")
                row["targets"][group]={"status":"NO_ELIGIBLE_EVENT"}
                continue
            require(t["status"]=="FROZEN_UNTREATED" and selection[group]["open"]==t["target"],"nomination drift")
            target=t["target"];arms={}
            for label,skip in (("sham",False),("both",True)):
                reps=[]
                for rep in (0,1):
                    x=trial(a,case,ident+f"/{group}/{label}-{rep}",binary=a.patch,observer=True,
                            target=int(target["event"]),skip_f=skip,skip_n=skip)
                    searches+=1
                    e=matched(x["events"],target)
                    require(e["close"]["skip_f"]==e["close"]["skip_n"]==str(int(skip)),"physical activation")
                    if not skip:
                        require(x["uci"]==base["uci"] and x["proof"]==base["proof"],"sham drift")
                    reps.append({"event":e,"proof":x["proof"],"uci":x["uci"],"trace":x["trace"]})
                require(all(reps[0][k]==reps[1][k] for k in ("event","proof","uci")),"repeat drift")
                v=reps[0];best=v["proof"]["best"];end=v["event"]["close"]
                arms[label]={"best":best,"child_return":end["value"],"stopped":end["stopped"]=="1",
                             "replies":int(end["replies"]),"trace_sha256":[z["trace"] for z in reps]}
            observable=not any(x["stopped"] for x in arms.values())
            flip=arms["sham"]["best"]["move"]!=arms["both"]["best"]["move"]
            row["targets"][group]={"status":"OBSERVED" if observable else "STOPPED_CENSORED",
                 "flip":flip if observable else None,"same_completed_depth":arms["sham"]["best"]["completed"]==arms["both"]["best"]["completed"],
                 "arms":arms}
        results.append(row)
        print("R48_CASE",ident,json.dumps({k:{"status":v["status"],"flip":v.get("flip")} for k,v in row["targets"].items()}),flush=True)
    require(searches==568,"search denominator")
    targets=[v for r in results for v in r["targets"].values()]
    statuses=Counter(x["status"] for x in targets)
    observed=[x for x in targets if x["status"]=="OBSERVED"]
    flips=[x for x in observed if x["flip"]]
    by_family=defaultdict(lambda:{"games":0,"observed_targets":0,"flips":0})
    for r in results:
        f=by_family[r["family"]];f["games"]+=1
        for x in r["targets"].values():
            f["observed_targets"]+=x["status"]=="OBSERVED"
            f["flips"]+=x.get("flip") is True
    summary={"discovery_sha256":DISCOVERY,"source_census_sha256":CENSUS,"games":64,"families":24,
             "native_searches":searches,"slots":128,"statuses":dict(statuses),"observed_flips":len(flips),
             "same_depth_flips":sum(x["same_completed_depth"] for x in flips),
             "per_family":dict(by_family),"scope":"new development cohort; same finite node budget; only source early-exit intervention, not H transport, no universal independence claim"}
    a.receipt.parent.mkdir(parents=True,exist_ok=True)
    a.receipt.write_text(json.dumps({**summary,"cases":results},indent=2,sort_keys=True)+"\n")
    print("R48_AGGREGATE",json.dumps(summary,sort_keys=True),flush=True)
    print("R48_RECEIPT_SHA",sha(a.receipt.read_bytes()),flush=True)
if __name__=="__main__":main()
