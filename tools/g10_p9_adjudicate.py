#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, math
from pathlib import Path

def load(p): return json.loads(Path(p).read_text())

def exact_one_sided(k,n):
    if n<=0:return 1.0
    return sum(math.comb(n,i) for i in range(k,n+1))/(2**n)

def main():
    ap=argparse.ArgumentParser()
    for x in ["normalized","census","out"]: ap.add_argument("--"+x,required=True)
    a=ap.parse_args();norm=load(a.normalized);sel=load(a.census)
    arm={}
    for z in sel["assignments"]:
        arm[z["target_position_id"]]="TARGET";arm[z["control_position_id"]]="CONTROL"
    certs=norm["certificates"]
    positive={c["position_id"] for c in certs if c["position_id"] in arm}
    pairs=[];ts=cs=to=co=both=neither=0
    by_source={}
    for z in sel["assignments"]:
        t=z["target_position_id"] in positive;c=z["control_position_id"] in positive
        ts+=int(t);cs+=int(c)
        if t and c:both+=1
        elif t:to+=1
        elif c:co+=1
        else:neither+=1
        s=by_source.setdefault(z["source_id"],{"pairs":0,"target_positive":0,"control_positive":0,"target_only":0,"control_only":0})
        s["pairs"]+=1;s["target_positive"]+=int(t);s["control_positive"]+=int(c)
        if t and not c:s["target_only"]+=1
        if c and not t:s["control_only"]+=1
        pairs.append({"source_id":z["source_id"],"target_position_id":z["target_position_id"],"control_position_id":z["control_position_id"],"target_positive":t,"control_positive":c,"match_distance":z["match_distance"]})
    n=len(pairs);disc=to+co
    acq={"pairs":n,"target_positive_positions":ts,"control_positive_positions":cs,
         "target_yield":ts/n if n else 0.0,"control_yield":cs/n if n else 0.0,
         "yield_difference":(ts-cs)/n if n else 0.0,"target_only":to,"control_only":co,
         "both":both,"neither":neither,
         "paired_one_sided_binomial_p":exact_one_sided(to,disc) if to>co else 1.0}
    by_engine={}
    for c in certs:
        a0=arm.get(c["position_id"],"UNASSIGNED")
        e=by_engine.setdefault(c["engine"],{"TARGET":0,"CONTROL":0,"UNASSIGNED":0})
        e[a0]+=1
    firewall=(sel.get("firewall_pass") is True and sel.get("forbidden_outcomes_consulted")==[]
              and sel.get("chain_qualification_opened") is False and sel.get("factorial_outcomes_opened") is False
              and sel.get("certificate_outcomes_opened") is False and sel.get("family_admission_opened") is False)
    if not firewall: verdict="FAIL_PREOUTCOME_FIREWALL"
    elif ts==0 and cs==0: verdict="NULL_CERTIFICATE_YIELD_BOTH_ARMS"
    elif ts>cs and to>co: verdict="PASS_GRADED_RECOVERABILITY_ENRICHED"
    else: verdict="PASS_GRADED_SELECTOR_DISCRIMINATIVE_NO_YIELD_ENRICHMENT"
    out={"schema":"c3x-g10-p9-experiment-v1","verdict":verdict,"preoutcome_verdict":sel["verdict"],
         "preoutcome_firewall_pass":firewall,"acquisition":acq,"matched_pairs":pairs,
         "source_enrichment":by_source,"engine_certificate_counts":by_engine,
         "complete_local_certificate_count":len(certs),
         "certificates_by_arm":{"TARGET":sum(arm.get(c["position_id"])=="TARGET" for c in certs),
                                "CONTROL":sum(arm.get(c["position_id"])=="CONTROL" for c in certs)},
         "mechanism_family_admission_opened":False,"transportable_pattern_instantiated":False,
         "authority_ceiling":["Graded recoverability/acquisition evidence only","No mechanism-family admission","No transportable law","No objective chess truth or human cognition/utility claim"]}
    Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print("G10_P9_FINAL",verdict,"target",ts,"control",cs,"certs",len(certs))

if __name__=="__main__": main()
