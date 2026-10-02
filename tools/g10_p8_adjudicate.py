#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,itertools,math
from pathlib import Path
from c3x_g10.morphism_grammar import development_adjudication,morphism_witness

def load(p):return json.loads(Path(p).read_text())
def exact_one_sided(k,n):
    if n<=0:return 1.0
    return sum(math.comb(n,i) for i in range(k,n+1))/(2**n)
def family_map(current,ecology):
    d=development_adjudication(ecology);dev={c["id"]:c for c in ecology["certificates"]}
    families={f"orbit-{i}":part for i,part in enumerate(d["orbit_partition"]) if len(part)>=2}
    out=[]
    for c in current:
        matches=[]
        for fid,members in families.items():
            witnesses=[]
            for mid in members:
                w=morphism_witness(c,dev[mid])
                if w["isomorphic"]:witnesses.append({"member":mid,"witness":w})
                else:
                    w2=morphism_witness(dev[mid],c)
                    if w2["isomorphic"]:witnesses.append({"member":mid,"witness":w2})
            if witnesses:matches.append({"family_id":fid,"development_members":members,"witnesses":witnesses})
        out.append({"certificate_id":c["certificate_id"],"position_id":c["position_id"],"source_id":c["source_id"],"engine":c["engine"],"matches":matches})
    return out,families
def main():
    ap=argparse.ArgumentParser()
    for x in ["fresh","normalized","selection","ecology","out"]:ap.add_argument("--"+x,required=True)
    a=ap.parse_args();fresh=load(a.fresh);norm=load(a.normalized);sel=load(a.selection);eco=load(a.ecology)
    arm={}
    for z in sel["assignments"]:
        arm[z["target_position_id"]]="TARGET";arm[z["control_position_id"]]="CONTROL"
    certs=norm["certificates"]
    for c in certs:c["p8_arm"]=arm.get(c["position_id"],"UNASSIGNED")
    positive={pid for pid in arm if any(c["position_id"]==pid for c in certs)}
    pairs=[]
    t_success=c_success=to=co=both=neither=0
    for z in sel["assignments"]:
        t=z["target_position_id"] in positive;c=z["control_position_id"] in positive
        t_success+=int(t);c_success+=int(c)
        if t and c:both+=1
        elif t:to+=1
        elif c:co+=1
        else:neither+=1
        pairs.append({"source_id":z["source_id"],"target_position_id":z["target_position_id"],"control_position_id":z["control_position_id"],"target_positive":t,"control_positive":c,"match_distance":z["match_distance"]})
    n=len(pairs);disc=to+co
    acquisition={
      "pairs":n,"target_positive_positions":t_success,"control_positive_positions":c_success,
      "target_yield":t_success/n if n else 0.0,"control_yield":c_success/n if n else 0.0,
      "yield_difference":(t_success-c_success)/n if n else 0.0,
      "target_only":to,"control_only":co,"both":both,"neither":neither,
      "paired_one_sided_binomial_p":exact_one_sided(to,disc) if to>co else 1.0,
    }
    if t_success==0 and c_success==0:acq_state="NULL_YIELD_BOTH_ARMS"
    elif t_success>c_success and to>co:acq_state="TARGETED_ACQUISITION_ENRICHED"
    else:acq_state="NO_TARGETED_YIELD_ADVANTAGE"
    fmap,families=family_map(certs,eco)
    groups={}
    for row in fmap:
        for m in row["matches"]:
            groups.setdefault(m["family_id"],[]).append({**row,"match":m})
    admitted=[]
    for fid,rows in groups.items():
        sources={r["source_id"] for r in rows};engines={r["engine"] for r in rows}
        nonidentity=any(any(w["witness"]["minimal_generators"] for w in r["match"]["witnesses"]) for r in rows)
        if {"P8_SRC_TWIC_1657","P8_SRC_TWIC_1658"}<=sources and len(engines)>=2 and nonidentity:
            admitted.append({"family_id":fid,"sources":sorted(sources),"engines":sorted(engines),"members":rows})
    firewall=(
      sel.get("chain_qualification_opened") is False and sel.get("factorial_outcomes_opened") is False
      and sel.get("certificate_outcomes_opened") is False and not sel.get("forbidden_outcomes_consulted")
    )
    if not firewall:verdict="FAIL_SELECTION_BIAS_FIREWALL"
    elif not sel.get("support_pass"):verdict="HOLD_ORBIT_TARGET_SUPPORT_INSUFFICIENT"
    elif admitted:verdict="PASS_EMPIRICAL_MECHANISM_FAMILY_ADMITTED"
    elif acq_state=="NULL_YIELD_BOTH_ARMS":verdict="NULL_YIELD_BOTH_ARMS"
    elif acq_state=="TARGETED_ACQUISITION_ENRICHED":verdict="PASS_TARGETED_ACQUISITION_ENRICHED_NO_FAMILY"
    else:verdict="PASS_NO_TARGETED_YIELD_ADVANTAGE"
    out={
      "schema":"c3x-g10-p8-court-v1","verdict":verdict,"acquisition_state":acq_state,
      "selection_bias_firewall_pass":firewall,"selection_support_pass":sel.get("support_pass"),
      "acquisition":acquisition,"matched_pairs":pairs,
      "complete_local_certificate_count":len(certs),
      "certificates_by_arm":{"TARGET":sum(c["p8_arm"]=="TARGET" for c in certs),"CONTROL":sum(c["p8_arm"]=="CONTROL" for c in certs)},
      "family_membership":fmap,"admitted_mechanism_families":admitted,
      "p7_nontrivial_families":families,
      "p7_grammar":["C","S","E"],"unlicensed_generators":["G","U"],
      "transportable_pattern_instantiated":False,
      "authority_ceiling":["At most MECHANISM_FAMILY_CANDIDATE","No transportable law","No objective chess truth or human cognition/utility claim"]
    }
    Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print("G10_P8_VERDICT",verdict,"target",t_success,"control",c_success,"certs",len(certs),"families",len(admitted))
if __name__=="__main__":main()
