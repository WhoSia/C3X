#!/usr/bin/env python3
"""C3X G9.4-P26: architecture×budget product-space causal-law field."""
import argparse,csv,hashlib,itertools,json
from collections import Counter,defaultdict
from pathlib import Path
import p20_transport as p20
import p21_boundary as p21

STAGE="C3X 0.7.0-G9.4-P26"
FAMILIES=p21.CORE_FAMILIES;SQUARES=p21.CORE_SQUARES;TARGETS=p21.P20_TARGETS
BUDGETS=(40000,80000,160000,300000);ANCHOR=80000
HEADER=["sha","family","side","square","sf_main","sf_q","sf_qshare","berserk_main","berserk_q","berserk_qshare","ethereal_main","ethereal_q","ethereal_qshare"]

def canon(o):return json.dumps(o,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()
def digest(o):return hashlib.sha256(canon(o)).hexdigest()
def seal(o):o.pop("receipt_sha256",None);o["receipt_sha256"]=digest(o);return o

def census(a):
    pool=json.loads(Path(a.pool).read_text())
    if pool.get("schema")!="c3x-p26-core-pool-v1" or pool.get("scientific_stage")!=STAGE or pool.get("engine_outcomes_consulted") is not False:raise SystemExit("P26_POOL_AUTHORITY")
    eng=p20.parse_engines(a.engine);src=[c for c in pool["candidates"] if c["material_seed_name"]==a.family]
    if len(src)!=48:raise SystemExit("P26_CENSUS_COUNT")
    rows=[]
    for i,c in enumerate(src,1):
        by={}
        for b in BUDGETS:
            sh={t:p20.run_search(eng[t],c["fen"],"SHAM",b) for t in TARGETS}
            by[str(b)]={"sham":sh,"features":p21.feature_map(sh)}
        rows.append({"candidate_sha256":c["candidate_sha256"],"material_seed_name":a.family,"side_to_move":c["side_to_move"],"square":c["square"],"vertex":c["vertex"],"fen":c["fen"],"world":c["world"],"by_budget":by})
        print("P26_CENSUS",a.family,i,flush=True)
    out={"schema":"c3x-p26-budget-census-v1","scientific_stage":STAGE,"family":a.family,"pool_sha256":pool["pool_sha256"],"selective_outcomes_consulted":False,"budgets":list(BUDGETS),"p20_binaries":{t:{"protocol":eng[t]["protocol"],"sha256":p21.sha_file(eng[t]["path"])} for t in TARGETS},"rows":rows};seal(out)
    Path(a.out).parent.mkdir(parents=True,exist_ok=True);Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")

def collect(path):
    rows=[];seen=set();bins=None;pool=None
    for p in sorted(Path(path).rglob("*.json")):
        x=json.loads(p.read_text())
        if x.get("schema")!="c3x-p26-budget-census-v1":continue
        if x.get("scientific_stage")!=STAGE or x.get("selective_outcomes_consulted") is not False or tuple(x["budgets"])!=BUDGETS or x["family"] in seen:raise SystemExit("P26_CENSUS_AUTHORITY")
        seen.add(x["family"]);rows.extend(x["rows"])
        if bins is None:bins=x["p20_binaries"];pool=x["pool_sha256"]
        elif bins!=x["p20_binaries"] or pool!=x["pool_sha256"]:raise SystemExit("P26_CENSUS_IDENTITY")
    if seen!=set(FAMILIES) or len(rows)!=384:raise SystemExit("P26_CENSUS_SET")
    return rows,bins,pool

def export(a):
    b=int(a.budget)
    if b not in BUDGETS:raise SystemExit("P26_BUDGET")
    rows,_,_=collect(a.census_dir);lines=["\t".join(HEADER)]
    for r in sorted(rows,key=lambda x:x["candidate_sha256"]):
        z=r["by_budget"][str(b)]["features"]
        lines.append("\t".join([r["candidate_sha256"],r["material_seed_name"],r["side_to_move"],r["square"],*[format(float(z[k]),".17g") for k in p21.FEATURES]]))
    Path(a.out).write_text("\n".join(lines)+"\n")

def read_atlas(p):
    with open(p,newline="") as f:rows=list(csv.DictReader(f,delimiter="\t"))
    if len(rows)!=384:raise SystemExit("P26_ATLAS_N")
    return {r["sha"]:r for r in rows}

def best_perm(src,anchor):
    labels=sorted({r["state8"] for r in src.values()});alabs=sorted({r["state8"] for r in anchor.values()})
    if len(labels)!=8 or len(alabs)!=8:raise SystemExit("P26_STATE_LABELS")
    table=Counter((src[k]["state8"],anchor[k]["state8"]) for k in anchor)
    best=None
    for perm in itertools.permutations(alabs):
        mp=dict(zip(labels,perm));score=sum(table[(s,mp[s])] for s in labels)
        key=(-score,tuple(perm))
        if best is None or key<best[0]:best=(key,mp,score)
    return best[1],best[2]/len(anchor)

def select_support(rows,atlases,maps):
    bysha={r["candidate_sha256"]:r for r in rows};anchor=atlases[ANCHOR];selected=[]
    for fam in FAMILIES:
      for side in ("WHITE","BLACK"):
        strata=defaultdict(list)
        for sha,r in bysha.items():
            if r["material_seed_name"]==fam and r["side_to_move"]==side:strata[anchor[sha]["state8"]].append(sha)
        labs=sorted(strata)
        if len(labs)!=8 or any(len(strata[s])!=3 for s in labs):raise SystemExit("P26_ANCHOR_BALANCE")
        choices=[sorted(strata[s]) for s in labs] # omit one from each 3
        best=None
        for omitted in itertools.product(*choices):
            omit=set(omitted);keep=[x for s in labs for x in strata[s] if x not in omit]
            counts=Counter()
            for sha in keep:
                for b in BUDGETS:
                    counts[(b,maps[b][atlases[b][sha]["state8"]])]+=1
            mn=min(counts[(b,s)] for b in BUDGETS for s in labs)
            sq=sum((counts[(b,s)]-2)**2 for b in BUDGETS for s in labs)
            key=(-mn,sq,tuple(omitted))
            if best is None or key<best[0]:best=(key,keep,mn,sq)
        if best[2]<1:raise SystemExit("P26_SUPPORT_GATE")
        selected.extend(best[1])
    if len(selected)!=256 or len(set(selected))!=256:raise SystemExit("P26_SELECTION_N")
    return selected

def load_constitution(p):
    x=json.loads(Path(p).read_text());c=x.get("constitution",{})
    if c.get("schema")!="c3x-lawgen-constitution-v2" or c.get("scientific_stage")!=STAGE or c.get("selective_outcomes_consulted") is not False:raise SystemExit("P26_LAWGEN")
    if digest(c)!=x.get("constitution_sha256"):raise SystemExit("P26_LAWGEN_HASH")
    return x

def precommit(a):
    law=load_constitution(a.constitution);rows,bins,poolsha=collect(a.census_dir)
    pool=json.loads(Path(a.pool).read_text())
    if pool.get("pool_sha256")!=poolsha or pool.get("freshness",{}).get("generation_index_offset")!=720000:raise SystemExit("P26_POOL_JOIN")
    atlases={b:read_atlas(Path(a.atlas_dir)/f"p26-atlas-{b}.tsv") for b in BUDGETS}
    maps={ANCHOR:{s:s for s in sorted({r["state8"] for r in atlases[ANCHOR].values()})}};overlap={str(ANCHOR):1.0}
    for b in BUDGETS:
        if b==ANCHOR:continue
        maps[b],overlap[str(b)]=best_perm(atlases[b],atlases[ANCHOR])
    chosen=select_support(rows,atlases,maps);by={r["candidate_sha256"]:r for r in rows};cells=[]
    for sha in chosen:
        r=by[sha]
        states={str(b):{"raw":atlases[b][sha]["state8"],"mapped":maps[b][atlases[b][sha]["state8"]]} for b in BUDGETS}
        cells.append({"candidate_sha256":sha,"material_seed_name":r["material_seed_name"],"side_to_move":r["side_to_move"],"square":r["square"],"vertex":r["vertex"],"fen":r["fen"],"world":r["world"],"states_by_budget":states})
    # hard support gate: one selected cell per family×side×budget×mapped state
    q=Counter((c["material_seed_name"],c["side_to_move"],b,c["states_by_budget"][str(b)]["mapped"]) for c in cells for b in BUDGETS)
    if min(q.values())<1 or len(q)!=8*2*4*8:raise SystemExit("P26_MAPPED_SUPPORT")
    out={"schema":"c3x-p26-precommit-v1","scientific_stage":STAGE,"selective_outcomes_consulted":False,"lawgen_constitution_sha256":law["constitution_sha256"],"fresh_world_pool_sha256":poolsha,"fresh_generation_offset":720000,"p20_binaries":bins,"budgets":list(BUDGETS),"anchor_budget":ANCHOR,"state_correspondence":{"capacity":"permutation_only","maps_to_anchor":{str(b):maps[b] for b in BUDGETS},"anchor_overlap_accuracy":overlap,"cycle_consistent_by_construction":True},"selection":{"cells":256,"rule":"omit-one-per-anchor-state exhaustive support optimization independently within family×side","mapped_support_min":min(q.values())},"descriptor_authority":law["constitution"]["descriptor_authority"],"product_space":law["constitution"]["product_space"],"cells":sorted(cells,key=lambda z:z["candidate_sha256"])};seal(out)
    # round-trip identity required
    Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n");check=json.loads(Path(a.out).read_text());h=check.pop("receipt_sha256")
    if digest(check)!=h:raise SystemExit("P26_PRECOMMIT_ROUNDTRIP")
    print("P26_PRECOMMIT_PASS",out["receipt_sha256"],overlap,min(q.values()))

def load_pre(p):
    x=json.loads(Path(p).read_text())
    if x.get("schema")!="c3x-p26-precommit-v1" or x.get("scientific_stage")!=STAGE or x.get("selective_outcomes_consulted") is not False:raise SystemExit("P26_PRE_AUTH")
    y=dict(x);h=y.pop("receipt_sha256")
    if digest(y)!=h:raise SystemExit("P26_PRE_HASH")
    return x

def baseline(c,run):
    w=p20.world_value(c,run["semantic"]["bestmove"])
    if w is None:raise SystemExit("P26_WORLD_SHAM")
    return {"receipt":run,"world":w,"action_changed":False,"fine_changed":False,"coarse_changed":False}
def arm(c,br,bw,run):
    w=p20.world_value(c,run["semantic"]["bestmove"])
    if w is None:raise SystemExit("P26_WORLD_ARM")
    return {"receipt":run,"world":w,"action_changed":run["semantic"]["bestmove"]!=br["semantic"]["bestmove"],"fine_changed":(w["wdl"],w["precise_dtz"])!=(bw["wdl"],bw["precise_dtz"]),"coarse_changed":w["wdl"]!=bw["wdl"]}

def vertex(a):
    pre=load_pre(a.precommit);eng=p20.parse_engines(a.engine)
    for t in TARGETS:
        if p21.sha_file(eng[t]["path"])!=pre["p20_binaries"][t]["sha256"]:raise SystemExit("P26_ENGINE_ID")
    src=[c for c in pre["cells"] if c["material_seed_name"]==a.family]
    if len(src)!=32:raise SystemExit(f"P26_VERTEX_N {len(src)}")
    rows=[]
    for i,c in enumerate(src,1):
        rec={k:c[k] for k in ("candidate_sha256","material_seed_name","side_to_move","square","vertex","fen","states_by_budget")};rec["by_budget"]={}
        for b in BUDGETS:
            rec["by_budget"][str(b)]={"targets":{}}
            for t in TARGETS:
                br=p20.run_search(eng[t],c["fen"],"SHAM",b);base=baseline(c,br);arms={"00":base}
                for bits,mode in (("10","MASK_MAIN"),("01","MASK_QSEARCH"),("11","MASK_MAIN_QSEARCH"),("ALL","MASK_ALL")):
                    arms[bits]=arm(c,br,base["world"],p20.run_search(eng[t],c["fen"],mode,b))
                rec["by_budget"][str(b)]["targets"][t]={"arms":arms}
        rows.append(rec);print("P26_VERTEX",a.family,i,flush=True)
    out={"schema":"c3x-p26-vertex-v1","scientific_stage":STAGE,"family":a.family,"precommit_receipt_sha256":pre["receipt_sha256"],"rows":rows};seal(out)
    Path(a.out).parent.mkdir(parents=True,exist_ok=True);Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")

def fp(z):
    c=z["curvature"];return [c["class"],c["dominant_coordinate"],c["dominant_sign"]]
def same(xs):return len({json.dumps(x,sort_keys=True) for x in xs})==1

def adjudicate(a):
    pre=load_pre(a.precommit);by={}
    for p in sorted(Path(a.results).rglob("*.json")):
        x=json.loads(p.read_text())
        if x.get("schema")!="c3x-p26-vertex-v1":continue
        if x.get("precommit_receipt_sha256")!=pre["receipt_sha256"] or x["family"] in by:raise SystemExit("P26_RESULT_AUTH")
        by[x["family"]]=x
    if set(by)!=set(FAMILIES):raise SystemExit("P26_RESULT_SET")
    states=sorted({c["states_by_budget"][str(ANCHOR)]["mapped"] for c in pre["cells"]})
    fps={};support={}
    for b in BUDGETS:
      fps[str(b)]={};support[str(b)]={}
      for s in states:
        fps[str(b)][s]={};support[str(b)][s]={}
        for sq,mp in SQUARES.items():
          fps[str(b)][s][sq]={};support[str(b)][s][sq]={}
          for t in TARGETS:
            raw={}
            for bit,fam in mp.items():
                rows=[]
                for r in by[fam]["rows"]:
                    if r["states_by_budget"][str(b)]["mapped"]==s:
                        rows.append((r["candidate_sha256"],{"targets":{t:r["by_budget"][str(b)]["targets"][t]}}))
                rows.sort(key=lambda z:z[0]);raw[bit]=rows;support[str(b)][s][sq][fam]=len(rows)
            m=min(len(raw[bit]) for bit in ("00","10","01","11"))
            if m<2:raise SystemExit(f"P26_EQUALIZED_SUPPORT {b} {s} {sq} {t} {m}")
            vres={bit:{"rows":[x[1] for x in raw[bit][:m]]} for bit in ("00","10","01","11")}
            fps[str(b)][s][sq][t]=fp(p20.square_analysis(vres,t))
    architecture_cells=0;total_cells=0
    for b in BUDGETS:
      for s in states:
       for sq in SQUARES:
        total_cells+=1
        if same([fps[str(b)][s][sq][t] for t in TARGETS]):architecture_cells+=1
    budget_cells=0;budget_total=0
    trajectories={}
    for t in TARGETS:
      trajectories[t]={}
      for s in states:
       trajectories[t][s]={}
       for sq in SQUARES:
        vals=[fps[str(b)][s][sq][t] for b in BUDGETS];trajectories[t][s][sq]=dict(zip(map(str,BUDGETS),vals))
        budget_total+=1
        if same(vals):budget_cells+=1
    arch_removable=architecture_cells==total_cells
    budget_removable=budget_cells==budget_total
    product=arch_removable and budget_removable
    if product:verdict="ARCHITECTURE_AND_BUDGET_INDICES_REMOVABLE_UNDER_FROZEN_CORRESPONDENCE"
    elif not arch_removable and not budget_removable:verdict="ARCHITECTURE_BUDGET_PRODUCT_FIELD_REQUIRED_UNDER_FROZEN_CORRESPONDENCE"
    elif not arch_removable:verdict="ARCHITECTURE_INDEX_REQUIRED_BUDGET_INDEX_REMOVABLE"
    else:verdict="BUDGET_INDEX_REQUIRED_ARCHITECTURE_INDEX_REMOVABLE"
    out={"schema":"c3x-p26-adjudication-v1","scientific_stage":STAGE,"precommit_receipt_sha256":pre["receipt_sha256"],"state_correspondence":pre["state_correspondence"],"selected_cells":len(pre["cells"]),"fingerprints":fps,"support":support,"architecture_index":{"removable":arch_removable,"invariant_cells":architecture_cells,"total_cells":total_cells},"budget_index":{"removable":budget_removable,"stable_engine_state_square_trajectories":budget_cells,"total_trajectories":budget_total},"product_space_transport":product,"field_trajectories":trajectories,"descriptor_intervention_feasibility":pre["descriptor_authority"],"verdict":verdict,"authority_ceiling":"fresh P26 worlds; finite-permutation cross-budget correspondence; four node budgets; three admitted engines; source-level P20 intervention algebra"};seal(out)
    Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print("P26_ADJUDICATION",verdict,"arch",architecture_cells,total_cells,"budget",budget_cells,budget_total)

def main():
    ap=argparse.ArgumentParser();sp=ap.add_subparsers(dest="cmd",required=True)
    p=sp.add_parser("census");p.add_argument("--pool",required=True);p.add_argument("--engine",action="append",required=True);p.add_argument("--family",choices=FAMILIES,required=True);p.add_argument("--out",required=True);p.set_defaults(fn=census)
    p=sp.add_parser("export");p.add_argument("--census-dir",required=True);p.add_argument("--budget",required=True);p.add_argument("--out",required=True);p.set_defaults(fn=export)
    p=sp.add_parser("precommit")
    for k in ("census_dir","pool","constitution","atlas_dir","out"):p.add_argument("--"+k.replace("_","-"),required=True)
    p.set_defaults(fn=precommit)
    p=sp.add_parser("vertex");p.add_argument("--precommit",required=True);p.add_argument("--engine",action="append",required=True);p.add_argument("--family",choices=FAMILIES,required=True);p.add_argument("--out",required=True);p.set_defaults(fn=vertex)
    p=sp.add_parser("adjudicate");p.add_argument("--precommit",required=True);p.add_argument("--results",required=True);p.add_argument("--out",required=True);p.set_defaults(fn=adjudicate)
    a=ap.parse_args();a.fn(a)
if __name__=="__main__":main()
