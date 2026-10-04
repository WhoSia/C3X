#!/usr/bin/env python3
from __future__ import annotations
import argparse,itertools,json
from collections import defaultdict
from pathlib import Path

ENGINES=("stockfish_19","berserk","ethereal")
SOURCES=("P16_SRC_TWIC_1655","P16_SRC_TWIC_1656")

def load(p):return json.loads(Path(p).read_text())

def rule_ok(row,lits):
    return all(bool(row["indicators"][z["indicator"]])==bool(z["value"]) for z in lits)

def nontrivial_rule(rows,engine,rule):
    per={}
    valid=True
    for s in SOURCES:
        rr=[r for r in rows if r["source_id"]==s and r["engine_survival"].get(engine) is not None]
        hit=[r for r in rr if rule_ok(r,rule["literals"])]
        miss=[r for r in rr if not rule_ok(r,rule["literals"])]
        hp=sum(bool(r["engine_survival"][engine]) for r in hit)
        mp=sum(bool(r["engine_survival"][engine]) for r in miss)
        hrate=hp/len(hit) if hit else None
        mrate=mp/len(miss) if miss else None
        exclusion=len(miss)/len(rr) if rr else 0
        # Demotion-only nontriviality: the rule must actually partition each source.
        cell_ok=len(hit)>=3 and len(miss)>=2 and exclusion>=0.15
        valid=valid and cell_ok
        per[s]={"eligible":len(rr),"hit_n":len(hit),"miss_n":len(miss),
                "hit_positive":hp,"miss_positive":mp,"hit_rate":hrate,"miss_rate":mrate,
                "exclusion_fraction":exclusion,"partition_nontrivial":cell_ok}
    return {"rule":rule["rule"],"engine":engine,"by_source":per,"nontrivial_partition":valid}

def nesting(rows,a,b):
    # A <= B means no row with A survival and B failure among jointly active rows.
    bysource={};tot={"n":0,"violations":0,"both":0,"a_only":0,"b_only":0,"neither":0}
    for s in SOURCES:
        c={"n":0,"violations":0,"both":0,"a_only":0,"b_only":0,"neither":0}
        for r in rows:
            if r["source_id"]!=s:continue
            x=r["engine_survival"].get(a);y=r["engine_survival"].get(b)
            if x is None or y is None:continue
            c["n"]+=1
            if x and y:c["both"]+=1
            elif x and not y:c["a_only"]+=1;c["violations"]+=1
            elif y and not x:c["b_only"]+=1
            else:c["neither"]+=1
        bysource[s]=c
        for k in tot:tot[k]+=c[k]
    return {"weaker":a,"stronger":b,"interpretation":f"{a} survival subset of {b} survival",
            "by_source":bysource,"combined":tot,
            "exact_zero_violation_both_sources":all(bysource[s]["n"]>=3 and bysource[s]["violations"]==0 for s in SOURCES)}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--tensor",required=True);ap.add_argument("--analysis",required=True);ap.add_argument("--out",required=True)
    a=ap.parse_args()
    tensor=load(a.tensor);analysis=load(a.analysis);rows=tensor["rows"]
    # Audit only rules already admitted by the frozen primary analysis. Never search for new rules.
    audits=[]
    for e,z in analysis["transparent_rule_search"]["by_engine"].items():
        for key in ("best_necessary","best_sufficient"):
            r=z.get(key)
            if r:audits.append({"kind":key,**nontrivial_rule(rows,e,r)})
    common_rules=set(analysis["transparent_rule_search"]["common_necessary_rules"]) | set(analysis["transparent_rule_search"]["common_sufficient_rules"])
    common_audit={}
    for rn in sorted(common_rules):
        engines=set(analysis["transparent_rule_search"]["common_necessary_rules"].get(rn,[])) | set(analysis["transparent_rule_search"]["common_sufficient_rules"].get(rn,[]))
        exemplar=None
        for e,z in analysis["transparent_rule_search"]["by_engine"].items():
            for key in ("best_necessary","best_sufficient"):
                r=z.get(key)
                if r and r["rule"]==rn:exemplar=r
        if exemplar is None:
            # reconstruct literals from a matching rule is intentionally forbidden; mark unavailable rather than invent.
            common_audit[rn]={"engines":sorted(engines),"audited":False,"reason":"not a best-rule exemplar; no post-hoc rule reconstruction"}
        else:
            per=[nontrivial_rule(rows,e,exemplar) for e in sorted(engines)]
            common_audit[rn]={"engines":sorted(engines),"audited":True,"per_engine":per,
                              "all_engines_nontrivial":all(x["nontrivial_partition"] for x in per)}
    nest=[]
    for a0,b0 in itertools.permutations(ENGINES,2):
        nest.append(nesting(rows,a0,b0))
    exact=[x for x in nest if x["exact_zero_violation_both_sources"]]
    # Candidate order is descriptive only: choose longest exact relation chain, no authority promotion.
    exact_pairs={(x["weaker"],x["stronger"]) for x in exact}
    chains=[]
    for order in itertools.permutations(ENGINES):
        if (order[0],order[1]) in exact_pairs and (order[1],order[2]) in exact_pairs:
            chains.append(order)
    best_suff={e:z.get("best_sufficient") for e,z in analysis["transparent_rule_search"]["by_engine"].items()}
    nontrivial_suff=[]
    for x in audits:
        if x["kind"]=="best_sufficient" and x["nontrivial_partition"]:nontrivial_suff.append(x["engine"])
    out={
      "schema":"c3x-g10-p18-demotion-audit-v1","status":"POST_PRIMARY_DEMOTION_ONLY",
      "can_strengthen_primary":False,
      "primary_verdict":analysis["verdict"],
      "best_rule_nontriviality":audits,
      "common_rule_nontriviality":common_audit,
      "nontrivial_sufficient_engines":sorted(nontrivial_suff),
      "nesting_tests":nest,
      "exact_zero_violation_relations":[{"weaker":x["weaker"],"stronger":x["stronger"],"combined":x["combined"],"by_source":x["by_source"]} for x in exact],
      "exact_three_engine_orders":[list(x) for x in chains],
      "nesting_authority":"DESCRIPTIVE_CANDIDATE_ONLY_POSTHOC_ORDER_SEARCH",
      "demoted_verdict":(
        "PASS_ENGINE_SPECIFIC_RULES_CROSS_ENGINE_OBSTRUCTION" if nontrivial_suff
        else "PASS_SUPPORT_INTERSECTION_DECOMPOSITION_NO_RULE"
      ),
      "interpretation":[
        "Common necessary rules from the primary search are not automatically law-like; high-prevalence design predicates can create degenerate necessity.",
        "Only already-selected best rules are eligible for nontriviality audit; the audit cannot discover a new rule.",
        "Exact engine-survival nesting is descriptive because engine order was not prospectively specified; it requires future confirmation before transport authority."
      ]
    }
    Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print("G10_P18_DEMOTION_AUDIT",out["demoted_verdict"])
    print("NONTRIVIAL_SUFF",out["nontrivial_sufficient_engines"])
    for x in audits:print("RULE",x["kind"],x["engine"],x["rule"],"NONTRIVIAL",x["nontrivial_partition"],x["by_source"])
    print("EXACT_REL",[(x["weaker"],x["stronger"],x["combined"]["n"],x["combined"]["violations"]) for x in exact])
    print("ORDERS",out["exact_three_engine_orders"])
if __name__=="__main__":main()
