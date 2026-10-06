#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,itertools
from pathlib import Path

ENGINES=("stockfish_19","berserk","ethereal")
ORDER=(("stockfish_19","berserk"),("berserk","ethereal"))
RULE_MIN_SUPPORT=3
RULE_MIN_PRECISION=0.70
RULE_MIN_COVERAGE=0.15
MIN_COMMON_POOLED=10
MIN_ANTECEDENT_POS=3
MIN_COMMON_PER_SOURCE=5

def load(path): return json.loads(Path(path).read_text())
def phase_reduced(row):
    ind=row.get("indicators",{}); raw=row.get("raw",{})
    if "phase_REDUCED" in ind:return bool(ind["phase_REDUCED"])
    return str(raw.get("phase","")).upper()=="REDUCED"
def grammar_le1(row):
    ind=row.get("indicators",{})
    if "grammar_complexity_le_1" in ind:return bool(ind["grammar_complexity_le_1"])
    g=row.get("selection_grammar_complexity",row.get("raw",{}).get("grammar_complexity"))
    return g is not None and float(g)<=1
def rule_hit(row): return grammar_le1(row) and not phase_reduced(row)
def sources(rows): return sorted({r["source_id"] for r in rows})

def relation(rows,a,b):
    bysrc={};all_common=[]
    for s in sources(rows):
        common=[r for r in rows if r["source_id"]==s and r["engine_survival"].get(a) is not None and r["engine_survival"].get(b) is not None]
        violations=[r for r in common if r["engine_survival"][a] is True and r["engine_survival"][b] is False]
        antecedent=[r for r in common if r["engine_survival"][a] is True]
        both=[r for r in common if r["engine_survival"][a] is True and r["engine_survival"][b] is True]
        bysrc[s]={"common_active":len(common),"antecedent_positive":len(antecedent),"both_positive":len(both),
                  "violation_count":len(violations),"violation_row_ids":[r.get("row_id") for r in violations]}
        all_common.extend(common)
    ante=[r for r in all_common if r["engine_survival"][a] is True]
    both=[r for r in all_common if r["engine_survival"][a] is True and r["engine_survival"][b] is True]
    viol=[r for r in all_common if r["engine_survival"][a] is True and r["engine_survival"][b] is False]
    power=(len(all_common)>=MIN_COMMON_POOLED and len(ante)>=MIN_ANTECEDENT_POS and len(both)>=1 and
           all(v["common_active"]>=MIN_COMMON_PER_SOURCE for v in bysrc.values()))
    status="UNDERPOWERED" if not power else "PROSPECTIVE_FALSIFIED" if viol else "PROSPECTIVE_CONFIRMED"
    return {"relation":f"{a}_subseteq_{b}","status":status,"by_source":bysrc,
      "pooled":{"common_active":len(all_common),"antecedent_positive":len(ante),"both_positive":len(both),
                "violation_count":len(viol),"violation_row_ids":[r.get("row_id") for r in viol]}}

def ferrers(rows):
    pair={}
    any_obstruction=False
    witnesses=[]
    for a,b in itertools.combinations(ENGINES,2):
        common=[r for r in rows if r["engine_survival"].get(a) is not None and r["engine_survival"].get(b) is not None]
        a_only=[r for r in common if r["engine_survival"][a] is True and r["engine_survival"][b] is False]
        b_only=[r for r in common if r["engine_survival"][a] is False and r["engine_survival"][b] is True]
        incomparable=bool(a_only and b_only)
        pair[f"{a}__{b}"]={"common_active":len(common),"a_only":len(a_only),"b_only":len(b_only),
          "neighborhoods_incomparable":incomparable,
          "a_only_row_ids":[r["row_id"] for r in a_only],"b_only_row_ids":[r["row_id"] for r in b_only]}
        if incomparable:
            any_obstruction=True
            witnesses.append({"engine_pair":[a,b],"row_x":a_only[0]["row_id"],"row_y":b_only[0]["row_id"],
                              "pattern":"INDUCED_2K2_NEIGHBORHOOD_OBSTRUCTION"})
    return {"status":"NON_FERRERS_OBSTRUCTION_FOUND" if any_obstruction else "FERRERS_COMPATIBLE_ON_OBSERVED_COMMON_ACTIVITY",
            "pair_diagnostics":pair,"obstruction_witnesses":witnesses,
            "authority":"SECONDARY_DEMOTION_ONLY_ORDER_FREE_DIAGNOSTIC"}

def ethereal_rule(rows):
    bysrc={};total_support=0;counterexamples=[];ok_sources=[]
    reduced_by_source={s:0 for s in sources(rows)}
    nonreduced_by_source={s:0 for s in sources(rows)}
    for s in sources(rows):
        active=[r for r in rows if r["source_id"]==s and r["engine_survival"].get("ethereal") is not None]
        reduced_by_source[s]=sum(phase_reduced(r) for r in active)
        nonreduced_by_source[s]=sum(not phase_reduced(r) for r in active)
        hit=[r for r in active if rule_hit(r)]
        pos=sum(r["engine_survival"]["ethereal"] is True for r in hit)
        precision=pos/len(hit) if hit else None
        bad=[r for r in hit if r["engine_survival"]["ethereal"] is False]
        counterexamples += [r["row_id"] for r in bad]
        ok=len(hit)>=RULE_MIN_SUPPORT and precision is not None and precision>=RULE_MIN_PRECISION
        ok_sources.append(ok)
        bysrc[s]={"active":len(active),"rule_support":len(hit),"positive":pos,"precision":precision,
                  "counterexample_row_ids":[r["row_id"] for r in bad],
                  "reduced_active":reduced_by_source[s],"nonreduced_active":nonreduced_by_source[s]}
        total_support+=len(hit)
    coverage=total_support/len(rows) if rows else 0.0
    power=all(v["rule_support"]>=RULE_MIN_SUPPORT for v in bysrc.values()) and coverage>=RULE_MIN_COVERAGE
    phase_contrast=all(reduced_by_source[s]>0 and nonreduced_by_source[s]>0 for s in bysrc)
    if not power: status="UNDERPOWERED"
    elif not all(ok_sources): status="PROSPECTIVE_FALSIFIED"
    elif phase_contrast: status="PROSPECTIVE_CONFIRMED"
    else: status="PROSPECTIVE_CONFIRMED_DOMAIN_RESTRICTED"
    return {"rule":"grammar_complexity_le_1 AND phase_NOT_REDUCED","status":status,"by_source":bysrc,
      "combined_coverage":coverage,"counterexample_row_ids":counterexamples,
      "phase_literal_contrast_tested":phase_contrast,
      "authority_note":None if phase_contrast else "Fresh bank contains no within-source REDUCED/non-REDUCED contrast; sufficiency is only confirmed on the observed non-REDUCED domain."}

def adjudicate(rows):
    rels=[relation(rows,a,b) for a,b in ORDER]
    h1="PROSPECTIVE_CONFIRMED" if all(x["status"]=="PROSPECTIVE_CONFIRMED" for x in rels) else (
       "UNDERPOWERED" if any(x["status"]=="UNDERPOWERED" for x in rels) else "PROSPECTIVE_FALSIFIED")
    h2=ethereal_rule(rows);f=ferrers(rows)
    if h1=="PROSPECTIVE_CONFIRMED" and h2["status"]=="PROSPECTIVE_CONFIRMED": verdict="PASS"
    elif h1=="PROSPECTIVE_FALSIFIED" and h2["status"]=="PROSPECTIVE_FALSIFIED": verdict="FAIL"
    elif h1=="UNDERPOWERED" or h2["status"]=="UNDERPOWERED": verdict="HOLD"
    else: verdict="PARTIAL_PASS"
    evidence=[]
    for x in rels:
        evidence.append({"claim_type":"ENGINE_SURVIVAL_INCLUSION","engine_relation":x["relation"],
          "source_id":"POOLED_FRESH_SOURCES","witness_rows":x["pooled"]["both_positive"],
          "counterexample_rows":x["pooled"]["violation_row_ids"],"authority_level":x["status"]})
    evidence.append({"claim_type":"ETHEREAL_RULE_REPLICATION","engine_relation":"ethereal",
      "source_id":"POOLED_FRESH_SOURCES","witness_rows":sum(v["positive"] for v in h2["by_source"].values()),
      "counterexample_rows":h2["counterexample_row_ids"],"authority_level":h2["status"]})
    return {"schema":"c3x-g10-p19-adjudication-v2","stage":"C3X 0.9.0-G10-P19","verdict":verdict,
      "H1_partial_order":h1,"relations":rels,"H2_ethereal_rule":h2,"ferrers_diagnostic":f,
      "evidence_graph":evidence,"black_box_models_used":False}

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--tensor",required=True);ap.add_argument("--out",required=True)
    a=ap.parse_args();t=load(a.tensor);rows=t.get("rows",t);out=adjudicate(rows)
    Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print("G10_P19_VERDICT",out["verdict"],"H1",out["H1_partial_order"],"H2",out["H2_ethereal_rule"]["status"],"FERRERS",out["ferrers_diagnostic"]["status"])
if __name__=="__main__": main()
