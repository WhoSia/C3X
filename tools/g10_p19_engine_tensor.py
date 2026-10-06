#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))
import g10_p17_transparent_susceptibility as p17

ENGINES=("stockfish_19","berserk","ethereal")
def load(p): return json.loads(Path(p).read_text())
def world_rows(root):
    out=[]
    for p in Path(root).rglob("*.json"):
        try:x=load(p)
        except:continue
        if x.get("schema")=="c3x-g10-p19-engine-support-world-v1":out.append(x)
    return out

def build(pair_freeze,corpus,worlds):
    pf=load(pair_freeze);corp=load(corpus)
    meta={f"p19:{z['source_id']}:{z['trajectory_hash'][:12]}":z for z in corp["positions"]}
    acc={}
    for w in world_rows(worlds):
        pid=w["position_id"];pos=pf["positions"][pid]
        for policy in ("ROUTED","GLOBAL_G2"):
            ch=w["chains"].get(policy)
            if not ch:continue
            g=(p17.GRAMMAR_COMPLEXITY[w["router_grammar"]] if policy=="ROUTED" else 2)
            sig=pid+"|"+p17.chain_sig(ch)
            labels={e:(bool(w["engines"][e][policy]["supported"]) if e in w["engines"] else None) for e in ENGINES}
            if sum(v is not None for v in labels.values())<2:continue
            if sig not in acc:
                raw,ind=p17.make_features(pos,meta[pid],ch,g)
                acc[sig]={"row_id":sig,"position_id":pid,"source_id":w["source_id"],
                  "chain_signature":p17.chain_sig(ch),"observed_policies":[policy],
                  "selection_grammar_complexity":g,"raw":raw,"indicators":ind,"engine_survival":labels}
            else:
                if acc[sig]["engine_survival"]!=labels:raise SystemExit("P19_DUP_ENGINE_LABEL_CONFLICT "+sig)
                acc[sig]["observed_policies"].append(policy)
                if g<acc[sig]["selection_grammar_complexity"]:
                    acc[sig]["selection_grammar_complexity"]=g
                    raw,ind=p17.make_features(pos,meta[pid],ch,g);acc[sig]["raw"]=raw;acc[sig]["indicators"]=ind
    rows=sorted(acc.values(),key=lambda r:r["row_id"])
    for r in rows:
        vals=[v for v in r["engine_survival"].values() if v is not None]
        r["active_engine_count"]=len(vals);r["support_count"]=sum(vals);r["aggregate_ge2"]=r["support_count"]>=2
    return rows

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--pair-freeze",required=True);ap.add_argument("--corpus",required=True);ap.add_argument("--worlds",required=True);ap.add_argument("--out",required=True)
    a=ap.parse_args();rows=build(a.pair_freeze,a.corpus,a.worlds)
    src=sorted({r["source_id"] for r in rows})
    out={"schema":"c3x-g10-p19-engine-tensor-v1","stage":"C3X 0.9.0-G10-P19","sources":src,"engines":list(ENGINES),
         "rows":rows,"engine_resolved_labels_opened_for_p19":True,"black_box_models_used":False}
    Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print("G10_P19_TENSOR","ROWS",len(rows),"SOURCES",src)
    print("SUPPORT",json.dumps({str(k):sum(r["support_count"]==k for r in rows) for k in range(4)},sort_keys=True))
if __name__=="__main__": main()
