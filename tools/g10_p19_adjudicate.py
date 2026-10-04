#!/usr/bin/env python3
from __future__ import annotations
import argparse, json
from collections import Counter, defaultdict
from pathlib import Path

ENGINES=("stockfish_19","berserk","ethereal")
ORDER=(("stockfish_19","berserk"),("berserk","ethereal"))
RULE_MIN_SUPPORT=3
RULE_MIN_PRECISION=0.70
RULE_MIN_COVERAGE=0.15
MIN_COMMON_POOLED=10
MIN_ANTECEDENT_POS=3
MIN_COMMON_PER_SOURCE=5

def load(path):
    return json.loads(Path(path).read_text())

def phase_reduced(row):
    raw=row.get("raw",{})
    ind=row.get("indicators",{})
    if "phase_REDUCED" in ind:
        return bool(ind["phase_REDUCED"])
    return str(raw.get("phase","")).upper()=="REDUCED"

def grammar_le1(row):
    ind=row.get("indicators",{})
    if "grammar_complexity_le_1" in ind:
        return bool(ind["grammar_complexity_le_1"])
    if "grammar_complexity_le1" in ind:
        return bool(ind["grammar_complexity_le1"])
    g=row.get("selection_grammar_complexity",row.get("raw",{}).get("grammar_complexity"))
    return g is not None and float(g)<=1

def rule_hit(row):
    return grammar_le1(row) and not phase_reduced(row)

def sources(rows):
    return sorted({r["source_id"] for r in rows})

def relation(rows,a,b):
    bysrc={}
    all_common=[]
    for s in sources(rows):
        rr=[r for r in rows if r["source_id"]==s]
        common=[r for r in rr if r["engine_survival"].get(a) is not None and r["engine_survival"].get(b) is not None]
        violations=[r for r in common if r["engine_survival"][a] is True and r["engine_survival"][b] is False]
        antecedent=[r for r in common if r["engine_survival"][a] is True]
        both=[r for r in common if r["engine_survival"][a] is True and r["engine_survival"][b] is True]
        bysrc[s]={
          "common_active":len(common),"antecedent_positive":len(antecedent),"both_positive":len(both),
          "violation_count":len(violations),
          "violation_row_ids":[r.get("row_id") for r in violations]
        }
        all_common.extend(common)
    pooled_ante=[r for r in all_common if r["engine_survival"][a] is True]
    pooled_both=[r for r in all_common if r["engine_survival"][a] is True and r["engine_survival"][b] is True]
    pooled_v=[r for r in all_common if r["engine_survival"][a] is True and r["engine_survival"][b] is False]
    power=(len(all_common)>=MIN_COMMON_POOLED and len(pooled_ante)>=MIN_ANTECEDENT_POS and
           len(pooled_both)>=1 and all(v["common_active"]>=MIN_COMMON_PER_SOURCE for v in bysrc.values()))
    status=("UNDERPOWERED" if not power else "PROSPECTIVE_FALSIFIED" if pooled_v else "PROSPECTIVE_CONFIRMED")
    return {
      "relation":f"{a}_subseteq_{b}","status":status,"by_source":bysrc,
      "pooled":{"common_active":len(all_common),"antecedent_positive":len(pooled_ante),
                "both_positive":len(pooled_both),"violation_count":len(pooled_v),
                "violation_row_ids":[r.get("row_id") for r in pooled_v]}
    }

def ethereal_rule(rows):
    bysrc={}
    total_support=0
    total_rows=len(rows)
    statuses=[]
    counterexamples=[]
    for s in sources(rows):
        active=[r for r in rows if r["source_id"]==s and r["engine_survival"].get("ethereal") is not None]
        hit=[r for r in active if rule_hit(r)]
        pos=sum(r["engine_survival"]["ethereal"] is True for r in hit)
        precision=(pos/len(hit)) if hit else None
        bad=[r for r in hit if r["engine_survival"]["ethereal"] is False]
        counterexamples += [r.get("row_id") for r in bad]
        ok=len(hit)>=RULE_MIN_SUPPORT and precision is not None and precision>=RULE_MIN_PRECISION
        statuses.append(ok)
        bysrc[s]={"active":len(active),"rule_support":len(hit),"positive":pos,"precision":precision,
                  "counterexample_row_ids":[r.get("row_id") for r in bad]}
        total_support+=len(hit)
    coverage=(total_support/total_rows) if total_rows else 0.0
    power=all(v["rule_support"]>=RULE_MIN_SUPPORT for v in bysrc.values()) and coverage>=RULE_MIN_COVERAGE
    status=("UNDERPOWERED" if not power else "PROSPECTIVE_CONFIRMED" if all(statuses) else "PROSPECTIVE_FALSIFIED")
    return {"rule":"grammar_complexity_le_1 AND phase_NOT_REDUCED","status":status,
            "by_source":bysrc,"combined_coverage":coverage,"counterexample_row_ids":counterexamples}

def adjudicate(rows):
    rels=[relation(rows,a,b) for a,b in ORDER]
    h1="PROSPECTIVE_CONFIRMED" if all(x["status"]=="PROSPECTIVE_CONFIRMED" for x in rels) else (
       "UNDERPOWERED" if any(x["status"]=="UNDERPOWERED" for x in rels) else "PROSPECTIVE_FALSIFIED")
    h2=ethereal_rule(rows)
    primary=[h1,h2["status"]]
    if all(x=="PROSPECTIVE_CONFIRMED" for x in primary): verdict="PASS"
    elif all(x=="PROSPECTIVE_FALSIFIED" for x in primary): verdict="FAIL"
    elif any(x=="UNDERPOWERED" for x in primary): verdict="HOLD"
    else: verdict="PARTIAL_PASS"
    evidence=[]
    for x in rels:
        evidence.append({"claim_type":"ENGINE_SURVIVAL_INCLUSION","engine_relation":x["relation"],
                         "source_id":"POOLED_FRESH_SOURCES","witness_rows":x["pooled"]["both_positive"],
                         "counterexample_rows":x["pooled"]["violation_row_ids"],"authority_level":x["status"]})
    evidence.append({"claim_type":"ETHEREAL_RULE_REPLICATION","engine_relation":"ethereal",
                     "source_id":"POOLED_FRESH_SOURCES","witness_rows":sum(v["positive"] for v in h2["by_source"].values()),
                     "counterexample_rows":h2["counterexample_row_ids"],"authority_level":h2["status"]})
    return {"schema":"c3x-g10-p19-adjudication-v1","verdict":verdict,"H1_partial_order":h1,
            "relations":rels,"H2_ethereal_rule":h2,"evidence_graph":evidence,
            "black_box_models_used":False}

def selftest():
    rows=[]
    for s in ("FRESH_A","FRESH_B"):
        for i in range(6):
            rows.append({"row_id":f"{s}:{i}","source_id":s,"selection_grammar_complexity":1,
                         "raw":{"phase":"OPENING"},"indicators":{},
                         "engine_survival":{"stockfish_19": i<3,"berserk": i<4,"ethereal": i<5}})
    out=adjudicate(rows)
    assert out["H1_partial_order"]=="PROSPECTIVE_CONFIRMED"
    assert out["H2_ethereal_rule"]=="PROSPECTIVE_CONFIRMED"
    bad=json.loads(json.dumps(rows))
    bad[0]["engine_survival"]["berserk"]=False
    out2=adjudicate(bad)
    assert out2["relations"][0]["status"]=="PROSPECTIVE_FALSIFIED"
    print("G10_P19_SELFTEST_PASS",out["verdict"],out2["verdict"])

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--tensor")
    ap.add_argument("--out")
    ap.add_argument("--selftest",action="store_true")
    a=ap.parse_args()
    if a.selftest:
        selftest(); return
    if not a.tensor or not a.out:
        raise SystemExit("--tensor and --out required unless --selftest")
    t=load(a.tensor)
    rows=t.get("rows",t)
    out=adjudicate(rows)
    Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print("G10_P19_VERDICT",out["verdict"],"H1",out["H1_partial_order"],"H2",out["H2_ethereal_rule"]["status"])

if __name__=="__main__":
    main()
