#!/usr/bin/env python3
"""C3X G9.4-P25: fresh replication, budget-atlas stability and descriptor-law court."""
import argparse,csv,hashlib,itertools,json,math
from collections import Counter,defaultdict
from pathlib import Path
import p20_transport as p20
import p21_boundary as p21

STAGE="C3X 0.7.0-G9.4-P25"
FAMILIES=p21.CORE_FAMILIES
SQUARES=p21.CORE_SQUARES
TARGETS=p21.P20_TARGETS
BUDGETS=(40000,80000,160000,300000)
CANONICAL=80000
INTERVENTION_NODES=300000
LEVELS=(1,2,4,8)
HEADER=["sha","family","side","square","sf_main","sf_q","sf_qshare","berserk_main","berserk_q","berserk_qshare","ethereal_main","ethereal_q","ethereal_qshare"]

def canon(o):return json.dumps(o,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()
def digest(o):return hashlib.sha256(canon(o)).hexdigest()
def seal(o):o.pop("receipt_sha256",None);o["receipt_sha256"]=digest(o);return o

def parse_budgets(s):
    b=tuple(int(x) for x in s.split(",") if x)
    if b!=BUDGETS:raise SystemExit(f"P25_BUDGET_CONSTITUTION {b}")
    return b

def census(a):
    pool=json.loads(Path(a.pool).read_text());budgets=parse_budgets(a.budgets)
    if pool.get("schema")!="c3x-p25-core-pool-v1" or pool.get("scientific_stage")!=STAGE or pool.get("engine_outcomes_consulted") is not False:raise SystemExit("P25_POOL_AUTHORITY")
    eng=p20.parse_engines(a.engine);src=[c for c in pool["candidates"] if c["material_seed_name"]==a.family]
    if len(src)!=48:raise SystemExit("P25_CENSUS_COUNT")
    rows=[]
    for i,c in enumerate(src,1):
        byb={}
        for b in budgets:
            sh={t:p20.run_search(eng[t],c["fen"],"SHAM",b) for t in TARGETS}
            byb[str(b)]={"sham":sh,"features":p21.feature_map(sh)}
        rows.append({"candidate_sha256":c["candidate_sha256"],"material_seed_name":a.family,"side_to_move":c["side_to_move"],"square":c["square"],"vertex":c["vertex"],"fen":c["fen"],"world":c["world"],"by_budget":byb})
        print("P25_CENSUS",a.family,i,flush=True)
    out={"schema":"c3x-p25-budget-census-v1","scientific_stage":STAGE,"family":a.family,"pool_sha256":pool["pool_sha256"],"selective_outcomes_consulted":False,"budgets":list(budgets),"p20_binaries":{t:{"protocol":eng[t]["protocol"],"sha256":p21.sha_file(eng[t]["path"])} for t in TARGETS},"rows":rows};seal(out)
    Path(a.out).parent.mkdir(parents=True,exist_ok=True);Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")

def collect(path):
    rows=[];seen=set();pb=None;pool=None
    for p in sorted(Path(path).rglob("*.json")):
        x=json.loads(p.read_text())
        if x.get("schema")!="c3x-p25-budget-census-v1" or x.get("scientific_stage")!=STAGE:continue
        if x.get("selective_outcomes_consulted") is not False or tuple(x.get("budgets",()))!=BUDGETS or x["family"] in seen:raise SystemExit("P25_CENSUS_AUTHORITY")
        seen.add(x["family"]);rows.extend(x["rows"])
        if pb is None:pb=x["p20_binaries"];pool=x["pool_sha256"]
        elif pb!=x["p20_binaries"] or pool!=x["pool_sha256"]:raise SystemExit("P25_CENSUS_IDENTITY")
    if seen!=set(FAMILIES) or len(rows)!=384:raise SystemExit("P25_CENSUS_SET")
    return rows,pb,pool

def export(a):
    b=int(a.budget)
    if b not in BUDGETS:raise SystemExit("P25_EXPORT_BUDGET")
    rows,_,_=collect(a.census_dir);lines=["\t".join(HEADER)]
    for r in sorted(rows,key=lambda q:q["candidate_sha256"]):
        z=r["by_budget"][str(b)]["features"]
        vals=[r["candidate_sha256"],r["material_seed_name"],r["side_to_move"],r["square"],*[format(float(z[k]),".17g") for k in p21.FEATURES]]
        lines.append("\t".join(vals))
    Path(a.out).write_text("\n".join(lines)+"\n");print("P25_TSV",b,len(rows),p21.sha_file(a.out))

def read_atlas(path):
    with open(path,newline="") as f:rows=list(csv.DictReader(f,delimiter="\t"))
    if len(rows)!=384 or len({r["sha"] for r in rows})!=384:raise SystemExit("P25_ATLAS_CARDINALITY")
    return {r["sha"]:r for r in rows}

def comb2(n):return n*(n-1)/2

def ari(labels_a,labels_b):
    if len(labels_a)!=len(labels_b) or len(labels_a)<2:raise ValueError("ARI support")
    ca=Counter(labels_a);cb=Counter(labels_b);joint=Counter(zip(labels_a,labels_b));n=len(labels_a)
    s=sum(comb2(v) for v in joint.values());sa=sum(comb2(v) for v in ca.values());sb=sum(comb2(v) for v in cb.values());den=comb2(n)
    expected=sa*sb/den if den else 0.0;mx=(sa+sb)/2
    return 1.0 if abs(mx-expected)<1e-15 and abs(s-mx)<1e-15 else (s-expected)/(mx-expected)

def atlas_stability(atlases):
    keys=sorted(next(iter(atlases.values())).keys());out={}
    coords=("c_total","c_q","d_total","d_q","d_joint")
    for x,y in itertools.combinations(BUDGETS,2):
        a=atlases[x];b=atlases[y];name=f"{x}__{y}"
        drift={c:sum(abs(float(a[k][c])-float(b[k][c])) for k in keys)/len(keys) for c in coords}
        agree={f"K{K}":sum(a[k][f"state{K}"]==b[k][f"state{K}"] for k in keys)/len(keys) for K in (2,4,8)}
        ar=ari([a[k]["state8"] for k in keys],[b[k]["state8"] for k in keys])
        out[name]={"coordinate_mean_absolute_drift":drift,"label_agreement":agree,"K8_adjusted_rand_index":ar}
    return out

def load_constitution(path):
    x=json.loads(Path(path).read_text())
    c=x.get("constitution",{});h=x.get("constitution_sha256")
    if c.get("schema")!="c3x-lawgen-constitution-v1" or c.get("scientific_stage")!=STAGE or c.get("selective_outcomes_consulted") is not False:raise SystemExit("P25_LAWGEN_AUTHORITY")
    if digest(c)!=h:raise SystemExit("P25_LAWGEN_HASH")
    return x

def precommit(a):
    lawgen=load_constitution(a.constitution);constitution=lawgen["constitution"]
    rows,pb,pool_sha=collect(a.census_dir);by={r["candidate_sha256"]:r for r in rows}
    pool=json.loads(Path(a.pool).read_text())
    if pool.get("pool_sha256")!=pool_sha or pool.get("freshness",{}).get("generation_index_offset")!=620000:raise SystemExit("P25_POOL_JOIN")
    expected_bins={e["id"]:e["binary_sha256"] for e in constitution["engines"]}
    if {t:pb[t]["sha256"] for t in TARGETS}!=expected_bins:raise SystemExit("P25_BINARY_SPEC_MISMATCH")
    atlases={};receipts={}
    for b in BUDGETS:
        ap=Path(a.atlas_dir)/f"p25-atlas-{b}.tsv";rp=Path(a.atlas_dir)/f"p25-atlas-{b}-receipt.json"
        atlases[b]=read_atlas(ap);receipts[b]=json.loads(rp.read_text())
        r=receipts[b]
        if r.get("schema")!="c3x-p24-atlas-v1" or r.get("outcomes_consulted") is not False or r.get("cells")!=384:raise SystemExit("P25_ATLAS_RECEIPT")
    stability=atlas_stability(atlases);canonical=atlases[CANONICAL];cells=[]
    for sha,r in by.items():
        z=canonical[sha]
        budget_states={str(b):{"K2":atlases[b][sha]["state2"],"K4":atlases[b][sha]["state4"],"K8":atlases[b][sha]["state8"]} for b in BUDGETS}
        cells.append({"candidate_sha256":sha,"material_seed_name":r["material_seed_name"],"side_to_move":r["side_to_move"],"square":r["square"],"vertex":r["vertex"],"fen":r["fen"],"world":r["world"],"states":{"K1":"ALL","K2":z["state2"],"K4":z["state4"],"K8":z["state8"]},"budget_states":budget_states,"atlas":{"c_total":float(z["c_total"]),"c_q":float(z["c_q"]),"d_total":float(z["d_total"]),"d_q":float(z["d_q"]),"d_joint":float(z["d_joint"])}})
    for K,expected in ((2,12),(4,6),(8,3)):
        q=Counter((c["material_seed_name"],c["side_to_move"],c["states"][f"K{K}"]) for c in cells)
        if any(v!=expected for v in q.values()) or len(q)!=(16*K):raise SystemExit(f"P25_K{K}_QUOTA")
    out={"schema":"c3x-p25-precommit-v1","scientific_stage":STAGE,"selective_outcomes_consulted":False,"lawgen_constitution_sha256":lawgen["constitution_sha256"],"fresh_world_pool_sha256":pool_sha,"fresh_generation_offset":620000,"p20_binaries":pb,"budgets":list(BUDGETS),"canonical_atlas_nodes":CANONICAL,"selective_intervention_nodes":INTERVENTION_NODES,"atlas_receipts":receipts,"atlas_tsv_sha256":{str(b):p21.sha_file(Path(a.atlas_dir)/f"p25-atlas-{b}.tsv") for b in BUDGETS},"budget_stability":stability,"descriptor_authority":constitution["descriptor_authority"],"engine_descriptors":{e["id"]:e["descriptor"] for e in constitution["engines"]},"cells":sorted(cells,key=lambda z:z["candidate_sha256"])};seal(out)
    Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n");print("P25_PRECOMMIT_PASS",out["receipt_sha256"])

def load_pre(path):
    x=json.loads(Path(path).read_text())
    if x.get("schema")!="c3x-p25-precommit-v1" or x.get("scientific_stage")!=STAGE or x.get("selective_outcomes_consulted") is not False:raise SystemExit("P25_PRECOMMIT_AUTHORITY")
    y=dict(x);h=y.pop("receipt_sha256",None)
    if digest(y)!=h:raise SystemExit("P25_PRECOMMIT_HASH")
    return x

def baseline(c,run):
    w=p20.world_value(c,run["semantic"]["bestmove"])
    if w is None:raise SystemExit("P25_WORLD_JOIN_SHAM "+c["candidate_sha256"])
    return {"receipt":run,"world":w,"action_changed":False,"fine_changed":False,"coarse_changed":False}
def arm(c,base_run,base_world,run):
    w=p20.world_value(c,run["semantic"]["bestmove"])
    if w is None:raise SystemExit("P25_WORLD_JOIN "+c["candidate_sha256"])
    return {"receipt":run,"world":w,"action_changed":run["semantic"]["bestmove"]!=base_run["semantic"]["bestmove"],"fine_changed":(w["wdl"],w["precise_dtz"])!=(base_world["wdl"],base_world["precise_dtz"]),"coarse_changed":w["wdl"]!=base_world["wdl"]}

def vertex(a):
    pre=load_pre(a.precommit);eng=p20.parse_engines(a.engine)
    for t in TARGETS:
        if p21.sha_file(eng[t]["path"])!=pre["p20_binaries"][t]["sha256"] or eng[t]["protocol"]!=pre["p20_binaries"][t]["protocol"]:raise SystemExit("P25_ENGINE_IDENTITY "+t)
    src=[r for r in pre["cells"] if r["material_seed_name"]==a.family]
    if len(src)!=48:raise SystemExit("P25_VERTEX_SUPPORT")
    rows=[]
    for i,c in enumerate(src,1):
        rec={k:c[k] for k in ("candidate_sha256","material_seed_name","side_to_move","square","vertex","fen","states","atlas")};rec["targets"]={}
        for t in TARGETS:
            br=p20.run_search(eng[t],c["fen"],"SHAM",INTERVENTION_NODES);b=baseline(c,br);arms={"00":b}
            for bits,mode in (("10","MASK_MAIN"),("01","MASK_QSEARCH"),("11","MASK_MAIN_QSEARCH"),("ALL","MASK_ALL")):
                arms[bits]=arm(c,br,b["world"],p20.run_search(eng[t],c["fen"],mode,INTERVENTION_NODES))
            rec["targets"][t]={"arms":arms}
        rows.append(rec);print("P25_VERTEX",a.family,i,c["states"]["K8"],flush=True)
    out={"schema":"c3x-p25-vertex-v1","scientific_stage":STAGE,"family":a.family,"precommit_receipt_sha256":pre["receipt_sha256"],"rows":rows};seal(out)
    Path(a.out).parent.mkdir(parents=True,exist_ok=True);Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n");print("P25_VERTEX_PASS",a.family,out["receipt_sha256"])

def fp(z):
    c=z["curvature"];return [c["class"],c["dominant_coordinate"],c["dominant_sign"]]
def same(v):return len({json.dumps(x,sort_keys=True) for x in v})==1

def law_signature(fps,engine,states):
    return [[s,sq,fps[s][engine][sq]] for s in states for sq in ("HEAVY_HEAVY","MINOR_MINOR")]

def descriptor_compression(pre,signatures):
    desc=pre["engine_descriptors"];subsets=pre["descriptor_authority"]["candidate_subsets_in_test_order"]
    tested=[];minimal=None;sufficient=[]
    for subset in subsets:
        groups=defaultdict(list)
        for e in TARGETS:
            key=tuple(json.dumps(desc[e][c],sort_keys=True) for c in subset);groups[key].append(e)
        ok=True
        for members in groups.values():
            if len({json.dumps(signatures[e],sort_keys=True,separators=(",",":")) for e in members})>1:ok=False;break
        rec={"coordinates":subset,"descriptor_groups":sorted(sorted(v) for v in groups.values()),"sufficient_on_frozen_engine_set":ok}
        tested.append(rec)
        if ok:
            if minimal is None:minimal=len(subset)
            if len(subset)==minimal:sufficient.append(rec)
    law_groups=defaultdict(list)
    for e in TARGETS:law_groups[json.dumps(signatures[e],sort_keys=True,separators=(",",":"))].append(e)
    return {"observed_law_equivalence_partition":sorted(sorted(v) for v in law_groups.values()),"minimal_descriptor_cardinality":minimal,"minimal_sufficient_subsets":sufficient,"all_tested_subsets":tested,"one_coordinate_identified":minimal==1,"identification_ceiling":pre["descriptor_authority"]["identification_ceiling"]}

def adjudicate(a):
    pre=load_pre(a.precommit);by={}
    for p in sorted(Path(a.results).rglob("p25-core-*.json")):
        x=json.loads(p.read_text())
        if x.get("schema")!="c3x-p25-vertex-v1" or x.get("scientific_stage")!=STAGE or x.get("precommit_receipt_sha256")!=pre["receipt_sha256"]:continue
        if x["family"] in by:raise SystemExit("P25_RESULT_DUP")
        by[x["family"]]=x
    if set(by)!=set(FAMILIES):raise SystemExit("P25_RESULT_SET")
    court={}
    for K in LEVELS:
        sk=f"K{K}";states=sorted({r["states"][sk] for x in by.values() for r in x["rows"]})
        if len(states)!=K:raise SystemExit(f"P25_STATE_COUNT_{K}")
        fps={};strict_cells=[];natural_cells=[]
        for state in states:
            fps[state]={}
            for t in TARGETS:
                fps[state][t]={}
                for sq,mp in SQUARES.items():
                    vres={bit:{"rows":[r for r in by[fam]["rows"] if r["states"][sk]==state]} for bit,fam in mp.items()}
                    expected=48//K
                    if any(len(vres[b]["rows"])!=expected for b in vres):raise SystemExit(f"P25_SUPPORT_K{K}_{state}_{sq}")
                    fps[state][t][sq]=fp(p20.square_analysis(vres,t))
            for sq,mp in SQUARES.items():
                vals=[fps[state][t][sq] for t in TARGETS]
                if same(vals):strict_cells.append(state+"|"+sq)
                vres={bit:{"rows":[r for r in by[fam]["rows"] if r["states"][sk]==state]} for bit,fam in mp.items()}
                pair=[p20.compatible(p20.square_analysis(vres,x),p20.square_analysis(vres,y))["compatible"] for x,y in itertools.combinations(TARGETS,2)]
                if all(pair):natural_cells.append(state+"|"+sq)
        distinct={t:len({json.dumps([fps[s][t]["HEAVY_HEAVY"],fps[s][t]["MINOR_MINOR"]],sort_keys=True) for s in states}) for t in TARGETS}
        court[sk]={"states":states,"fingerprints":fps,"strict_cells":strict_cells,"natural_cells":natural_cells,"universal_strict_architecture_invariance":len(strict_cells)==K*2,"universal_conditional_naturality":len(natural_cells)==K*2,"distinct_response_laws_by_engine":distinct}
    k8=court["K8"];common=[]
    for s in k8["states"]:
        sigs=[[k8["fingerprints"][s][t]["HEAVY_HEAVY"],k8["fingerprints"][s][t]["MINOR_MINOR"]] for t in TARGETS]
        if same(sigs):common.append(s)
    signatures={t:law_signature(k8["fingerprints"],t,k8["states"]) for t in TARGETS}
    compression=descriptor_compression(pre,signatures)
    nonconstant=all(k8["distinct_response_laws_by_engine"][t]>1 for t in TARGETS)
    replication=(len(common)==0 and nonconstant)
    if replication and compression["minimal_descriptor_cardinality"] is not None:
        verdict="FRESH_ARCHITECTURE_INDEX_REPLICATED__BUDGET_ATLAS_MEASURED__FROZEN_DESCRIPTOR_MORPHISM_IDENTIFIED"
    elif replication:
        verdict="FRESH_ARCHITECTURE_INDEX_REPLICATED__BUDGET_ATLAS_MEASURED__DESCRIPTOR_IDENTIFICATION_UNDERDETERMINED"
    else:
        verdict="P25_REPLICATION_NOT_CONFIRMED__DESCRIPTOR_COURT_REMAINS_DESCRIPTIVE"
    out={"schema":"c3x-p25-adjudication-v1","scientific_stage":STAGE,"precommit_receipt_sha256":pre["receipt_sha256"],"budget_stability":pre["budget_stability"],"court":court,"architecture_free_k8_states":common,"architecture_index_replication":replication,"architecture_indexed_law_nonconstant_each_engine":nonconstant,"full_k8_law_signatures":signatures,"descriptor_compression":compression,"verdict":verdict,"claim_ceiling":["Budget stability is reported descriptively across the four frozen node budgets; no post-outcome threshold defines success.","Descriptor sufficiency is finite-set descriptive sufficiency over Stockfish 19, Berserk and Ethereal, not population-level causal identification.","Intervention-response bisimulation remains a finite frozen intervention-algebra notion, not full engine dynamical bisimulation."]};seal(out)
    Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n");print("P25_ADJUDICATION",verdict,out["receipt_sha256"])

def main():
    ap=argparse.ArgumentParser();sp=ap.add_subparsers(dest="cmd",required=True)
    p=sp.add_parser("census");p.add_argument("--pool",required=True);p.add_argument("--engine",action="append",required=True);p.add_argument("--family",required=True);p.add_argument("--budgets",required=True);p.add_argument("--out",required=True);p.set_defaults(fn=census)
    p=sp.add_parser("export");p.add_argument("--census-dir",required=True);p.add_argument("--budget",required=True);p.add_argument("--out",required=True);p.set_defaults(fn=export)
    p=sp.add_parser("precommit");p.add_argument("--census-dir",required=True);p.add_argument("--pool",required=True);p.add_argument("--constitution",required=True);p.add_argument("--atlas-dir",required=True);p.add_argument("--out",required=True);p.set_defaults(fn=precommit)
    p=sp.add_parser("vertex");p.add_argument("--precommit",required=True);p.add_argument("--engine",action="append",required=True);p.add_argument("--family",required=True);p.add_argument("--out",required=True);p.set_defaults(fn=vertex)
    p=sp.add_parser("adjudicate");p.add_argument("--precommit",required=True);p.add_argument("--results",required=True);p.add_argument("--out",required=True);p.set_defaults(fn=adjudicate)
    a=ap.parse_args();a.fn(a)

if __name__=="__main__":main()
