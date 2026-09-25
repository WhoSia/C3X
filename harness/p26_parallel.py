#!/usr/bin/env python3
"""Execution-only parallelization for the frozen P26 product-space field.
Splits family vertices by budget, then reconstructs byte-semantic full-family receipts
before invoking the unchanged scientific adjudicator.
"""
import argparse,json
from collections import defaultdict
from pathlib import Path
import p26_product_field as P

def vertex_budget(a):
    pre=P.load_pre(a.precommit);eng=P.p20.parse_engines(a.engine);b=int(a.budget)
    if b not in P.BUDGETS:raise SystemExit("P26P_BUDGET")
    for t in P.TARGETS:
        if P.p21.sha_file(eng[t]["path"])!=pre["p20_binaries"][t]["sha256"]:raise SystemExit("P26P_ENGINE_ID")
    src=[c for c in pre["cells"] if c["material_seed_name"]==a.family]
    if len(src)!=32:raise SystemExit(f"P26P_VERTEX_N {len(src)}")
    rows=[]
    for i,c in enumerate(src,1):
        rec={k:c[k] for k in ("candidate_sha256","material_seed_name","side_to_move","square","vertex","fen","states_by_budget")}
        rec["by_budget"]={str(b):{"targets":{}}}
        for t in P.TARGETS:
            br=P.p20.run_search(eng[t],c["fen"],"SHAM",b);base=P.baseline(c,br);arms={"00":base}
            for bits,mode in (("10","MASK_MAIN"),("01","MASK_QSEARCH"),("11","MASK_MAIN_QSEARCH"),("ALL","MASK_ALL")):
                arms[bits]=P.arm(c,br,base["world"],P.p20.run_search(eng[t],c["fen"],mode,b))
            rec["by_budget"][str(b)]["targets"][t]={"arms":arms}
        rows.append(rec);print("P26_PARALLEL_VERTEX",a.family,b,i,flush=True)
    out={"schema":"c3x-p26-vertex-budget-v1","scientific_stage":P.STAGE,"family":a.family,"budget":b,"precommit_receipt_sha256":pre["receipt_sha256"],"rows":rows};P.seal(out)
    Path(a.out).parent.mkdir(parents=True,exist_ok=True);Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")

def merge(a):
    files=sorted(Path(a.results).rglob("*.json"));parts={}
    for p in files:
        x=json.loads(p.read_text())
        if x.get("schema")!="c3x-p26-vertex-budget-v1":continue
        key=(x["family"],int(x["budget"]))
        if key in parts:raise SystemExit("P26P_DUP "+str(key))
        parts[key]=x
    expected={(f,b) for f in P.FAMILIES for b in P.BUDGETS}
    if set(parts)!=expected:raise SystemExit(f"P26P_PART_SET {len(parts)}/32")
    outdir=Path(a.out_dir);outdir.mkdir(parents=True,exist_ok=True)
    for fam in P.FAMILIES:
        prehash={parts[(fam,b)]["precommit_receipt_sha256"] for b in P.BUDGETS}
        if len(prehash)!=1:raise SystemExit("P26P_PREHASH")
        bysha={}
        for b in P.BUDGETS:
            for r in parts[(fam,b)]["rows"]:
                sha=r["candidate_sha256"]
                if sha not in bysha:
                    bysha[sha]={k:r[k] for k in ("candidate_sha256","material_seed_name","side_to_move","square","vertex","fen","states_by_budget")}
                    bysha[sha]["by_budget"]={}
                if str(b) in bysha[sha]["by_budget"]:raise SystemExit("P26P_BUDGET_DUP")
                bysha[sha]["by_budget"][str(b)]=r["by_budget"][str(b)]
        if len(bysha)!=32 or any(set(r["by_budget"])!=set(map(str,P.BUDGETS)) for r in bysha.values()):raise SystemExit("P26P_MERGE_N")
        out={"schema":"c3x-p26-vertex-v1","scientific_stage":P.STAGE,"family":fam,"precommit_receipt_sha256":next(iter(prehash)),"execution_provenance":"32-way family×budget parallel reconstruction; scientific content identical to frozen P26 vertex contract","rows":sorted(bysha.values(),key=lambda z:z["candidate_sha256"])};P.seal(out)
        (outdir/f"p26-core-{fam}.json").write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print("P26_PARALLEL_MERGE_PASS",len(parts))

def main():
    ap=argparse.ArgumentParser();sp=ap.add_subparsers(dest="cmd",required=True)
    p=sp.add_parser("vertex-budget");p.add_argument("--precommit",required=True);p.add_argument("--engine",action="append",required=True);p.add_argument("--family",choices=P.FAMILIES,required=True);p.add_argument("--budget",type=int,choices=P.BUDGETS,required=True);p.add_argument("--out",required=True);p.set_defaults(fn=vertex_budget)
    p=sp.add_parser("merge");p.add_argument("--results",required=True);p.add_argument("--out-dir",required=True);p.set_defaults(fn=merge)
    a=ap.parse_args();a.fn(a)
if __name__=="__main__":main()
