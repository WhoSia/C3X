#!/usr/bin/env python3
from __future__ import annotations
import argparse,itertools,json,math
from collections import Counter,defaultdict
from pathlib import Path
import chess

FAMILIES=("T1_INTEGER_SCORECARD","T2_ORDERED_RULE_LIST","T3_SPARSE_INTERACTION_TABLE")
INDICATORS=(
"pair_consensus_orientation","preferred_move_full_agreement","median_gap_le_10","median_gap_le_25",
"max_gap_le_25","gap_dispersion_le_5","gap_dispersion_le_15","phase_RICH","phase_REDUCED",
"branching_NARROW","branching_WIDE","tactical_QUIET_SURFACE","grammar_complexity_le_1",
"chain_ATOMIC","target_atom_singleton","target_endpoint_FROM","target_polarity_GAIN","side_role_OWN",
"piece_minor","legal_delta_LOW","attack_symdiff_LOW","total_collateral_le_12","total_collateral_le_20")
GRAMMAR_COMPLEXITY={"G0_LEGACY_PHYSICAL":0,"G1_SAME_PIECE_COLLATERAL":1,
"G2_SAME_TYPE_SIDE_COLLATERAL":2,"G3_SIDE_ROLE_COLLATERAL":3,"G4_GLOBAL_COLLATERAL":4}
INTERACTIONS=(
("pair_geometry","gap_dispersion_bin"),
("phase","branching"),
("relation_atom_family","side_role"),
("grammar_complexity_bin","total_collateral_bin"),
)

def load(p):return json.loads(Path(p).read_text())

def world_rows(root):
    out=[]
    for p in Path(root).rglob("*.json"):
        try:x=load(p)
        except:continue
        if x.get("schema")=="c3x-g10-p16-router-validation-world-v1":out.append(x)
    return out

def binned(v,cuts,labels):
    for c,l in zip(cuts,labels):
        if v<=c:return l
    return labels[-1]

def attack_symdiff(base_fen,target_fen,edit):
    b=chess.Board(base_fen);q=chess.Board(target_fen)
    fr=chess.parse_square(edit[:2]);to=chess.parse_square(edit[2:])
    return len(set(b.attacks(fr)) ^ set(q.attacks(to)))

def legal_delta(base_fen,target_fen):
    return abs(chess.Board(target_fen).legal_moves.count()-chess.Board(base_fen).legal_moves.count())

def chain_sig(ch):
    return "|".join([ch["target_edit"],ch["subset_edit"],ch["sham_edit"],",".join(ch.get("target_atoms",[])),",".join(ch.get("subset_atoms",[]))])

def make_features(pos,meta,ch,grammar_complexity):
    views=[v for v in pos["engine_views"].values() if v.get("active")]
    gaps=[int(v["gap_cp_abs"]) for v in views if v.get("gap_cp_abs") is not None]
    prefs=[v.get("baseline_preferred") for v in views if v.get("baseline_preferred")]
    pref_count=max(Counter(prefs).values()) if prefs else 0
    dispersion=max(gaps)-min(gaps) if gaps else 99
    atoms=list(ch.get("target_atoms",[]))
    singleton=len(atoms)==1
    relation=atoms[0] if singleton else ("MULTI:"+",".join(sorted(atoms)) if atoms else "NONE")
    endpoint_from=bool(atoms) and all("_FROM_" in a for a in atoms)
    polarity_gain=bool(atoms) and all(a.endswith("_GAIN") for a in atoms)
    ld=legal_delta(meta["fen"],ch["target_fen"])
    ad=attack_symdiff(meta["fen"],ch["target_fen"],ch["target_edit"])
    total=int(ch.get("total_collateral",0))
    raw={
      "active_engine_count":len(views),"pair_support_count":int(pos["pair"]["support_count"]),
      "pair_geometry":pos.get("geometry"),"median_gap_cp":float(pos["pair"]["median_gap_cp"]),
      "max_gap_cp":int(pos["pair"]["max_gap_cp"]),"gap_dispersion_cp":dispersion,
      "preferred_move_agreement_count":pref_count,"phase":meta["context"]["phase"],
      "branching":meta["context"]["branching"],"tactical_surface":meta["context"]["tactical_surface"],
      "grammar_complexity":grammar_complexity,"chain_type":ch["type"],"target_atom_count":len(atoms),
      "deleted_atom_count":max(0,len(atoms)-len(ch.get("subset_atoms",[]))),"relation_atom_family":relation,
      "piece_type":ch.get("piece_type"),"side_role":ch.get("side_role"),
      "legal_move_delta_abs":ld,"attack_symdiff":ad,"total_collateral":total,
      "gap_dispersion_bin":binned(dispersion,[5,15,10**9],["0-5","6-15","16+"]),
      "grammar_complexity_bin":str(grammar_complexity),
      "total_collateral_bin":binned(total,[12,20,10**9],["0-12","13-20","21+"])
    }
    ind={
      "pair_consensus_orientation":raw["pair_geometry"]=="CONSENSUS_ORIENTATION",
      "preferred_move_full_agreement":pref_count==len(views) and len(views)>0,
      "median_gap_le_10":raw["median_gap_cp"]<=10,
      "median_gap_le_25":raw["median_gap_cp"]<=25,
      "max_gap_le_25":raw["max_gap_cp"]<=25,
      "gap_dispersion_le_5":dispersion<=5,
      "gap_dispersion_le_15":dispersion<=15,
      "phase_RICH":raw["phase"]=="RICH","phase_REDUCED":raw["phase"]=="REDUCED",
      "branching_NARROW":raw["branching"]=="NARROW","branching_WIDE":raw["branching"]=="WIDE",
      "tactical_QUIET_SURFACE":raw["tactical_surface"]=="QUIET_SURFACE",
      "grammar_complexity_le_1":grammar_complexity<=1,"chain_ATOMIC":raw["chain_type"]=="ATOMIC_CHAIN",
      "target_atom_singleton":singleton,"target_endpoint_FROM":endpoint_from,"target_polarity_GAIN":polarity_gain,
      "side_role_OWN":raw["side_role"]=="OWN","piece_minor":raw["piece_type"] in ("KNIGHT","BISHOP"),
      "legal_delta_LOW":ld<=2,"attack_symdiff_LOW":ad<=3,
      "total_collateral_le_12":total<=12,"total_collateral_le_20":total<=20,
    }
    return raw,{k:bool(ind[k]) for k in INDICATORS}

def build_dataset(pair_freeze,corpus,worlds):
    pf=load(pair_freeze);corp=load(corpus)
    meta={f"p16:{z['source_id']}:{z['trajectory_hash'][:12]}":z for z in corp["positions"]}
    acc={}
    for w in world_rows(worlds):
        pid=w["position_id"];pos=pf["positions"][pid]
        for policy in ("ROUTED","GLOBAL_G2"):
            ch=w["chains"].get(policy)
            if not ch:continue
            label=sum(1 for e,z in w["engines"].items() if z[policy]["supported"])>=2
            g=(GRAMMAR_COMPLEXITY[w["router_grammar"]] if policy=="ROUTED" else 2)
            sig=pid+"|"+chain_sig(ch)
            if sig not in acc:
                raw,ind=make_features(pos,meta[pid],ch,g)
                acc[sig]={"row_id":sig,"position_id":pid,"source_id":w["source_id"],"label":bool(label),
                          "observed_policies":[policy],"selection_grammar_complexity":g,
                          "chain_signature":chain_sig(ch),"raw":raw,"indicators":ind}
            else:
                if acc[sig]["label"]!=bool(label):raise SystemExit("P17_DUPLICATE_LABEL_CONFLICT "+sig)
                acc[sig]["observed_policies"].append(policy)
                if g<acc[sig]["selection_grammar_complexity"]:
                    acc[sig]["selection_grammar_complexity"]=g
                    raw,ind=make_features(pos,meta[pid],ch,g);acc[sig]["raw"]=raw;acc[sig]["indicators"]=ind
    return sorted(acc.values(),key=lambda r:r["row_id"])

def stats(rows,pred):
    admitted=[r for r in rows if pred(r)]
    pos=sum(r["label"] for r in admitted)
    return {"n":len(rows),"admitted":len(admitted),"positive":pos,
            "precision":None if not admitted else pos/len(admitted),
            "coverage":0 if not rows else len(admitted)/len(rows)}

def score(row,terms):return sum(coef for name,coef in terms if row["indicators"][name])

def best_threshold(rows,terms):
    vals=sorted({score(r,terms) for r in rows})
    best=None
    for t in vals:
        st=stats(rows,lambda r,t=t:score(r,terms)>=t)
        if st["admitted"]<3:continue
        obj=(st["precision"],st["positive"],st["admitted"],-sum(abs(c) for _,c in terms),-len(terms),-t)
        if best is None or obj>best[0]:best=(obj,t,st)
    return best

def fit_t1(rows):
    terms=[];current=best_threshold(rows,terms)
    if current is None:current=((0,0,0,0,0,0),0,stats(rows,lambda r:True))
    for _ in range(6):
        candidates=[]
        used={n for n,_ in terms}
        for n in INDICATORS:
            if n in used:continue
            for coef in (-2,-1,1,2):
                tt=terms+[(n,coef)];bt=best_threshold(rows,tt)
                if bt:candidates.append((bt[0],n,coef,bt[1],bt[2]))
        if not candidates:break
        candidates.sort(key=lambda x:(x[0],x[1],x[2]),reverse=True)
        obj,n,c,t,st=candidates[0]
        if obj<=current[0]:break
        terms.append((n,c));current=(obj,t,st)
    return {"family":"T1_INTEGER_SCORECARD","terms":[{"indicator":n,"coefficient":c} for n,c in terms],
            "threshold":current[1],"train":current[2],"structure":[n for n,_ in terms]}

def pred_t1(m,row):
    return score(row,[(z["indicator"],z["coefficient"]) for z in m["terms"]])>=m["threshold"]

def literals(row):
    return [(n,True) for n in INDICATORS]+[(n,False) for n in INDICATORS]

def literal_ok(row,lit):return row["indicators"][lit[0]]==lit[1]
def rule_ok(row,rule):return all(literal_ok(row,tuple(x)) for x in rule)

def all_rules():
    lits=[(n,v) for n in INDICATORS for v in (False,True)]
    one=[(x,) for x in lits]
    two=[]
    for a,b in itertools.combinations(lits,2):
        if a[0]==b[0]:continue
        two.append(tuple(sorted((a,b))))
    return one+two

RULE_LIBRARY=None
def fit_t2(rows):
    global RULE_LIBRARY
    if RULE_LIBRARY is None:RULE_LIBRARY=all_rules()
    uncovered=list(rows);rules=[]
    for _ in range(4):
        cand=[]
        for rule in RULE_LIBRARY:
            hit=[r for r in uncovered if rule_ok(r,rule)]
            if len(hit)<3:continue
            p=sum(r["label"] for r in hit);prec=p/len(hit)
            if prec<0.5:continue
            key=tuple(f"{n}={'1' if v else '0'}" for n,v in rule)
            cand.append(((prec,p,len(hit),tuple(reversed(key))),rule,hit))
        if not cand:break
        cand.sort(key=lambda x:x[0],reverse=True)
        _,rule,hit=cand[0];rules.append(rule)
        ids={r["row_id"] for r in hit};uncovered=[r for r in uncovered if r["row_id"] not in ids]
    model={"family":"T2_ORDERED_RULE_LIST",
           "rules":[[{"indicator":n,"value":v} for n,v in rule] for rule in rules],
           "structure":[[(n,v) for n,v in rule] for rule in rules]}
    model["train"]=stats(rows,lambda r:pred_t2(model,r))
    return model

def pred_t2(m,row):
    for rule in m["rules"]:
        if all(row["indicators"][z["indicator"]]==z["value"] for z in rule):return True
    return False

def interaction_cell(row,inter):return tuple(str(row["raw"][k]) for k in inter)
def fit_t3(rows):
    tabs=[]
    for inter in INTERACTIONS:
        cnt=defaultdict(lambda:[0,0])
        for r in rows:
            k=interaction_cell(r,inter);cnt[k][0]+=int(r["label"]);cnt[k][1]+=1
        good={}
        best=0
        for k,(p,n) in cnt.items():
            lap=(p+1)/(n+2)
            if n>=3 and lap>=0.5:good["|".join(k)]={"positive":p,"n":n,"laplace":lap};best=max(best,lap)
        if good:
            tabs.append({"features":list(inter),"admit_cells":good})
        if len(tabs)==2:break
    m={"family":"T3_SPARSE_INTERACTION_TABLE","tables":tabs,
       "structure":[tuple(z["features"]) for z in tabs]}
    m["train"]=stats(rows,lambda r:pred_t3(m,r))
    return m

def pred_t3(m,row):
    for tab in m["tables"]:
        k="|".join(str(row["raw"][x]) for x in tab["features"])
        if k in tab["admit_cells"]:return True
    return False

def structure(m):
    return m["structure"]

def evaluate_family(fam,train,test):
    if fam=="T1_INTEGER_SCORECARD":m=fit_t1(train);pred=pred_t1
    elif fam=="T2_ORDERED_RULE_LIST":m=fit_t2(train);pred=pred_t2
    else:m=fit_t3(train);pred=pred_t3
    return m,stats(test,lambda r:pred(m,r))

def trace(model,row):
    if model["family"]=="T1_INTEGER_SCORECARD":
        parts=[];total=0
        for z in model["terms"]:
            on=row["indicators"][z["indicator"]];v=z["coefficient"] if on else 0;total+=v
            parts.append({"indicator":z["indicator"],"value":on,"coefficient":z["coefficient"],"contribution":v})
        return {"score":total,"threshold":model["threshold"],"terms":parts,"admit":total>=model["threshold"]}
    if model["family"]=="T2_ORDERED_RULE_LIST":
        for i,rule in enumerate(model["rules"]):
            fire=all(row["indicators"][z["indicator"]]==z["value"] for z in rule)
            if fire:return {"fired_rule":i,"rule":rule,"admit":True}
        return {"fired_rule":None,"admit":False,"reason":"default_abstain"}
    cells=[]
    for t in model["tables"]:
        k="|".join(str(row["raw"][x]) for x in t["features"])
        cells.append({"features":t["features"],"cell":k,"training_cell":t["admit_cells"].get(k)})
    return {"cells":cells,"admit":any(c["training_cell"] is not None for c in cells)}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--pair-freeze",required=True);ap.add_argument("--corpus",required=True);ap.add_argument("--worlds",required=True)
    ap.add_argument("--dataset-out",required=True);ap.add_argument("--out",required=True)
    a=ap.parse_args()
    rows=build_dataset(a.pair_freeze,a.corpus,a.worlds)
    Path(a.dataset_out).write_text(json.dumps({"schema":"c3x-g10-p17-development-table-v1","rows":rows},indent=2,sort_keys=True)+"\n")
    sources=sorted({r["source_id"] for r in rows})
    if sources!=["P16_SRC_TWIC_1655","P16_SRC_TWIC_1656"]:raise SystemExit("P17_SOURCE_SET "+repr(sources))
    famres={}
    selected=None
    for fam in FAMILIES:
        folds=[]
        models=[]
        for trsrc,tesrc in ((sources[0],sources[1]),(sources[1],sources[0])):
            tr=[r for r in rows if r["source_id"]==trsrc];te=[r for r in rows if r["source_id"]==tesrc]
            m,st=evaluate_family(fam,tr,te);models.append(m)
            folds.append({"train_source":trsrc,"test_source":tesrc,"model":m,"test":st})
        same=structure(models[0])==structure(models[1])
        admitted=sum(f["test"]["admitted"] for f in folds);n=sum(f["test"]["n"] for f in folds)
        gate=(same and all(f["test"]["precision"] is not None and f["test"]["precision"]>=0.5 and f["test"]["admitted"]>=3 for f in folds)
              and (admitted/n if n else 0)>=0.20
              and all(f["test"]["precision"]>=0.21428571428571427 for f in folds))
        famres[fam]={"folds":folds,"structure_identical":same,"combined_coverage":admitted/n if n else 0,"gate_pass":gate}
        if selected is None and gate:selected=fam
    verdict="PASS_TRANSPARENT_SUSCEPTIBILITY_FAMILY_LEAVE_SOURCE_OUT" if selected else "HOLD_NO_TRANSPARENT_FAMILY_CALIBRATES"
    # freeze deploy model on all development data only if family selected, using that family's deterministic fitter
    deploy=None
    if selected:
        if selected=="T1_INTEGER_SCORECARD":deploy=fit_t1(rows)
        elif selected=="T2_ORDERED_RULE_LIST":deploy=fit_t2(rows)
        else:deploy=fit_t3(rows)
    out={"schema":"c3x-g10-p17-transparent-susceptibility-v1","verdict":verdict,
         "development_rows":len(rows),"sources":sources,
         "positive_rows":sum(r["label"] for r in rows),"families":famres,
         "selected_family":selected,"deploy_model":deploy,
         "black_box_models_used":False,
         "fresh_confirmation_open_authorized":bool(selected)}
    Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print("G10_P17_TRANSPARENT",verdict,"ROWS",len(rows),"POS",out["positive_rows"],"SELECTED",selected)
    for fam in FAMILIES:
        z=famres[fam]
        print("FAMILY",fam,"STRUCT",z["structure_identical"],"COVERAGE",z["combined_coverage"],"PASS",z["gate_pass"])
        for f in z["folds"]:print("FOLD",f["train_source"],"->",f["test_source"],f["test"],"STRUCTURE",structure(f["model"]))
    if deploy:
        print("DEPLOY",json.dumps(deploy,sort_keys=True))
if __name__=="__main__":main()
