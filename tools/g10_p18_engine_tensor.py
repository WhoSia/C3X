#!/usr/bin/env python3
from __future__ import annotations
import argparse,itertools,json
from collections import Counter,defaultdict
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))
import g10_p17_transparent_susceptibility as p17

ENGINES=("stockfish_19","berserk","ethereal")
SOURCES=("P16_SRC_TWIC_1655","P16_SRC_TWIC_1656")
INDICATORS=tuple(p17.INDICATORS)

def load(p): return json.loads(Path(p).read_text())

def literal_name(lit):
    n,v=lit
    return n if v else "NOT_"+n

def rule_name(rule):
    return " & ".join(literal_name(x) for x in rule)

def rule_ok(row,rule):
    return all(bool(row["indicators"][n])==v for n,v in rule)

def all_rules():
    lits=[(n,v) for n in INDICATORS for v in (True,False)]
    out=[(x,) for x in lits]
    for a,b in itertools.combinations(lits,2):
        if a[0]==b[0]: continue
        out.append(tuple(sorted((a,b))))
    return out

def build(pair_freeze,corpus,worlds):
    pf=load(pair_freeze);corp=load(corpus)
    meta={f"p16:{z['source_id']}:{z['trajectory_hash'][:12]}":z for z in corp["positions"]}
    acc={}
    for w in p17.world_rows(worlds):
        pid=w["position_id"];pos=pf["positions"][pid]
        for policy in ("ROUTED","GLOBAL_G2"):
            ch=w["chains"].get(policy)
            if not ch:continue
            g=(p17.GRAMMAR_COMPLEXITY[w["router_grammar"]] if policy=="ROUTED" else 2)
            sig=pid+"|"+p17.chain_sig(ch)
            labels={e:(bool(w["engines"][e][policy]["supported"]) if e in w["engines"] else None) for e in ENGINES}
            if sum(v is not None for v in labels.values())<2:raise SystemExit("P18_ACTIVE_ENGINE_LT2 "+sig+" "+repr(labels))
            if sig not in acc:
                raw,ind=p17.make_features(pos,meta[pid],ch,g)
                acc[sig]={
                  "row_id":sig,"position_id":pid,"source_id":w["source_id"],
                  "chain_signature":p17.chain_sig(ch),"observed_policies":[policy],
                  "selection_grammar_complexity":g,"raw":raw,"indicators":ind,
                  "engine_survival":labels
                }
            else:
                if acc[sig]["engine_survival"]!=labels:raise SystemExit("P18_DUP_ENGINE_LABEL_CONFLICT "+sig)
                acc[sig]["observed_policies"].append(policy)
                if g<acc[sig]["selection_grammar_complexity"]:
                    acc[sig]["selection_grammar_complexity"]=g
                    raw,ind=p17.make_features(pos,meta[pid],ch,g)
                    acc[sig]["raw"]=raw;acc[sig]["indicators"]=ind
    rows=sorted(acc.values(),key=lambda r:r["row_id"])
    for r in rows:
        vals=[v for v in r["engine_survival"].values() if v is not None]
        r["active_engine_count"]=len(vals)
        r["support_count"]=sum(vals)
        r["aggregate_ge2"]=r["support_count"]>=2
        r["support_class"]=(
          "UNIVERSAL_SURVIVAL" if vals and all(vals) else
          "PARTIAL_SUPPORT" if r["support_count"]>=1 else
          "UNIVERSAL_FAILURE"
        )
    return rows

def rate(xs):return None if not xs else sum(xs)/len(xs)

def tensor_summary(rows):
    srceng={}
    for s in SOURCES:
        srceng[s]={}
        for e in ENGINES:
            rr=[r for r in rows if r["source_id"]==s]
            ys=[int(r["engine_survival"][e]) for r in rr if r["engine_survival"][e] is not None]
            srceng[s][e]={"n":len(ys),"positive":sum(ys),"rate":rate(ys)}
    support_count=Counter(r["support_count"] for r in rows)
    pairwise={}
    for a,b in itertools.combinations(ENGINES,2):
        c=Counter()
        for r in rows:
            x,y=r["engine_survival"][a],r["engine_survival"][b]
            if x is None or y is None:continue
            c["N"]+=1;c["BOTH"]+=int(x and y);c[a+"_ONLY"]+=int(x and not y);c[b+"_ONLY"]+=int(y and not x);c["NEITHER"]+=int(not x and not y)
        pairwise[a+"__"+b]=dict(c)
    grand=rate([int(r["engine_survival"][e]) for r in rows for e in ENGINES if r["engine_survival"][e] is not None])
    source_mean={s:rate([int(r["engine_survival"][e]) for r in rows if r["source_id"]==s for e in ENGINES if r["engine_survival"][e] is not None]) for s in SOURCES}
    engine_mean={e:rate([int(r["engine_survival"][e]) for r in rows if r["engine_survival"][e] is not None]) for e in ENGINES}
    residual={}
    for s in SOURCES:
        residual[s]={}
        for e in ENGINES:
            residual[s][e]=srceng[s][e]["rate"]-source_mean[s]-engine_mean[e]+grand
    return {
      "source_engine":srceng,
      "support_count_distribution":{str(k):v for k,v in sorted(support_count.items())},
      "active_engine_count_distribution":dict(Counter(str(r["active_engine_count"]) for r in rows)),
      "support_classes":dict(Counter(r["support_class"] for r in rows)),
      "aggregate_ge2_positive":sum(r["aggregate_ge2"] for r in rows),
      "support_intersection_failures":sum((not r["aggregate_ge2"]) and r["support_count"]>=1 for r in rows),
      "universal_failures":sum(r["support_count"]==0 for r in rows),
      "universal_survivals":sum(r["support_class"]=="UNIVERSAL_SURVIVAL" for r in rows),
      "pairwise":pairwise,
      "grand_rate":grand,"source_mean":source_mean,"engine_mean":engine_mean,
      "source_engine_interaction_residual":residual
    }

def primitive_effects(rows):
    effects={}
    source_reversal=defaultdict(list)
    engine_reversal=[]
    for ind in INDICATORS:
        effects[ind]={}
        for e in ENGINES:
            effects[ind][e]={}
            signs=[]
            for s in SOURCES:
                rr=[r for r in rows if r["source_id"]==s]
                t=[r for r in rr if r["indicators"][ind]]
                f=[r for r in rr if not r["indicators"][ind]]
                rt=rate([int(r["engine_survival"][e]) for r in t if r["engine_survival"][e] is not None])
                rf=rate([int(r["engine_survival"][e]) for r in f if r["engine_survival"][e] is not None])
                d=None if rt is None or rf is None else rt-rf
                sg=None if d is None else (1 if d>1e-12 else -1 if d<-1e-12 else 0)
                effects[ind][e][s]={"true_n":len(t),"true_rate":rt,"false_n":len(f),"false_rate":rf,"delta":d,"sign":sg}
                signs.append(sg)
            if None not in signs and signs[0]*signs[1]<0:source_reversal[ind].append(e)
        for s in SOURCES:
            ss=[]
            for e in ENGINES:
                ss.append(effects[ind][e][s]["sign"])
            nz=[x for x in ss if x not in (None,0)]
            if 1 in nz and -1 in nz:engine_reversal.append({"indicator":ind,"source":s,"engine_signs":dict(zip(ENGINES,ss))})
    return {"effects":effects,"source_sign_reversal_engines":dict(source_reversal),"engine_sign_reversals":engine_reversal}

def eval_rule(rows,e,rule):
    bysrc={}
    for s in SOURCES:
        rr=[r for r in rows if r["source_id"]==s and r["engine_survival"][e] is not None]
        hit=[r for r in rr if rule_ok(r,rule)]
        pos=[r for r in rr if r["engine_survival"][e] is True]
        hp=sum(bool(r["engine_survival"][e]) for r in hit)
        rec=sum(rule_ok(r,rule) for r in pos)/len(pos) if pos else None
        bysrc[s]={
          "support":len(hit),"positive_in_rule":hp,
          "precision":hp/len(hit) if hit else None,
          "positive_total":len(pos),"recall_among_positive":rec
        }
    cov=sum(bysrc[s]["support"] for s in SOURCES)/len(rows)
    suff=all(bysrc[s]["support"]>=3 and bysrc[s]["precision"] is not None and bysrc[s]["precision"]>=0.70 for s in SOURCES) and cov>=0.15
    nec=all(bysrc[s]["support"]>=3 and bysrc[s]["recall_among_positive"] is not None and bysrc[s]["recall_among_positive"]>=0.70 for s in SOURCES)
    worstp=min((bysrc[s]["precision"] for s in SOURCES if bysrc[s]["precision"] is not None),default=-1)
    worstr=min((bysrc[s]["recall_among_positive"] for s in SOURCES if bysrc[s]["recall_among_positive"] is not None),default=-1)
    minsup=min(bysrc[s]["support"] for s in SOURCES)
    return {"rule":rule_name(rule),"literals":[{"indicator":n,"value":v} for n,v in rule],
            "by_source":bysrc,"combined_coverage":cov,"sufficient":suff,"necessary":nec,
            "worst_precision":worstp,"worst_recall":worstr,"min_support":minsup}

def rule_search(rows):
    rules=all_rules()
    out={}
    sufficient_by_engine={};necessary_by_engine={}
    for e in ENGINES:
        ev=[eval_rule(rows,e,r) for r in rules]
        suff=[x for x in ev if x["sufficient"]]
        nec=[x for x in ev if x["necessary"]]
        suff.sort(key=lambda x:(len(x["literals"]),-x["worst_precision"],-x["min_support"],x["rule"]))
        nec.sort(key=lambda x:(len(x["literals"]),-x["worst_recall"],-x["min_support"],x["rule"]))
        sufficient_by_engine[e]=[x["rule"] for x in suff]
        necessary_by_engine[e]=[x["rule"] for x in nec]
        out[e]={"best_sufficient":suff[0] if suff else None,"best_necessary":nec[0] if nec else None,
                "sufficient_rule_count":len(suff),"necessary_rule_count":len(nec)}
    common_suff=defaultdict(list);common_nec=defaultdict(list)
    for e,xs in sufficient_by_engine.items():
        for r in xs:common_suff[r].append(e)
    for e,xs in necessary_by_engine.items():
        for r in xs:common_nec[r].append(e)
    common_suff={r:es for r,es in common_suff.items() if len(es)>=2}
    common_nec={r:es for r,es in common_nec.items() if len(es)>=2}
    return {"by_engine":out,"common_sufficient_rules":common_suff,"common_necessary_rules":common_nec}

def verdict(summary,rules):
    common=bool(rules["common_sufficient_rules"] or rules["common_necessary_rules"])
    any_engine=any(z["sufficient_rule_count"] or z["necessary_rule_count"] for z in rules["by_engine"].values())
    if common:return "PASS_ENGINE_RESOLVED_COMMON_TRANSPARENT_RULE"
    if any_engine:return "PASS_ENGINE_SPECIFIC_RULES_CROSS_ENGINE_OBSTRUCTION"
    if summary["support_intersection_failures"]>0:return "PASS_SUPPORT_INTERSECTION_DECOMPOSITION_NO_RULE"
    return "HOLD_ENGINE_RESOLVED_SUPPORT_TOO_SPARSE"

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--pair-freeze",required=True);ap.add_argument("--corpus",required=True);ap.add_argument("--worlds",required=True)
    ap.add_argument("--tensor-out",required=True);ap.add_argument("--out",required=True)
    a=ap.parse_args()
    rows=build(a.pair_freeze,a.corpus,a.worlds)
    tensor={"schema":"c3x-g10-p18-engine-tensor-v1","rows":rows,
            "engine_resolved_labels_opened_for_p18":True,"black_box_models_used":False}
    Path(a.tensor_out).write_text(json.dumps(tensor,indent=2,sort_keys=True)+"\n")
    summary=tensor_summary(rows);prim=primitive_effects(rows);rules=rule_search(rows);v=verdict(summary,rules)
    out={"schema":"c3x-g10-p18-engine-resolved-analysis-v1","verdict":v,
         "unique_chain_rows":len(rows),"engine_tensor_cells":len(rows)*len(ENGINES),
         "engines":list(ENGINES),"sources":list(SOURCES),"tensor_summary":summary,
         "primitive_analysis":prim,"transparent_rule_search":rules,
         "black_box_models_used":False,"fresh_confirmation_opened":False}
    Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print("G10_P18_ENGINE_TENSOR",v,"ROWS",len(rows),"CELLS",len(rows)*3)
    print("SUPPORT",json.dumps(summary["support_count_distribution"],sort_keys=True),
          "INTERSECTION_FAIL",summary["support_intersection_failures"],
          "UNIVERSAL_FAIL",summary["universal_failures"],"UNIVERSAL_SURVIVE",summary["universal_survivals"])
    print("SOURCE_ENGINE",json.dumps(summary["source_engine"],sort_keys=True))
    print("PAIRWISE",json.dumps(summary["pairwise"],sort_keys=True))
    print("RESIDUAL",json.dumps(summary["source_engine_interaction_residual"],sort_keys=True))
    print("SOURCE_REVERSAL",json.dumps(prim["source_sign_reversal_engines"],sort_keys=True))
    print("ENGINE_REVERSAL_COUNT",len(prim["engine_sign_reversals"]))
    print("RULES",json.dumps(rules["by_engine"],sort_keys=True))
    print("COMMON_SUFF",json.dumps(rules["common_sufficient_rules"],sort_keys=True))
    print("COMMON_NEC",json.dumps(rules["common_necessary_rules"],sort_keys=True))
if __name__=="__main__":main()
