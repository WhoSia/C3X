#!/usr/bin/env python3
"""C3X G9.4-P24 prospective multivariate atlas and intervention-response court."""
import argparse,csv,hashlib,itertools,json
from collections import Counter,defaultdict
from pathlib import Path
import p20_transport as p20
import p21_boundary as p21

STAGE="C3X 0.7.0-G9.4-P24"
FAMILIES=p21.CORE_FAMILIES
SQUARES=p21.CORE_SQUARES
TARGETS=p21.P20_TARGETS
HEADER=["sha","family","side","square","sf_main","sf_q","sf_qshare","berserk_main","berserk_q","berserk_qshare","ethereal_main","ethereal_q","ethereal_qshare","inanis_tt_main","inanis_pawn_q"]
LEVELS=(1,2,4,8)

def canon(o):return json.dumps(o,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()
def digest(o):return hashlib.sha256(canon(o)).hexdigest()
def seal(o):o.pop("receipt_sha256",None);o["receipt_sha256"]=digest(o);return o

def census(a):
    pool=json.loads(Path(a.pool).read_text())
    if pool.get("schema")!="c3x-p24-core-pool-v1" or pool.get("scientific_stage")!=STAGE or pool.get("engine_outcomes_consulted") is not False:raise SystemExit("P24_POOL_AUTHORITY")
    eng=p20.parse_engines(a.engine);src=[c for c in pool["candidates"] if c["material_seed_name"]==a.family]
    if len(src)!=48:raise SystemExit("P24_CENSUS_COUNT")
    rows=[]
    for i,c in enumerate(src,1):
        sh={t:p20.run_search(eng[t],c["fen"],"SHAM",a.nodes) for t in TARGETS};ina=p21.run_inanis(a.inanis,c["fen"],"SHAM",a.nodes);z=p21.feature_map(sh)
        rows.append({"candidate_sha256":c["candidate_sha256"],"material_seed_name":a.family,"side_to_move":c["side_to_move"],"square":c["square"],"vertex":c["vertex"],"fen":c["fen"],"world":c["world"],"sham":sh,"features":z,"inanis_sham":ina});print("P24_CENSUS",a.family,i,flush=True)
    out={"schema":"c3x-p24-core-census-v1","scientific_stage":STAGE,"family":a.family,"pool_sha256":pool["pool_sha256"],"selective_outcomes_consulted":False,"nodes":a.nodes,"p20_binaries":{t:{"protocol":eng[t]["protocol"],"sha256":p21.sha_file(eng[t]["path"])} for t in TARGETS},"inanis_binary_sha256":p21.sha_file(a.inanis),"rows":rows};seal(out)
    Path(a.out).parent.mkdir(parents=True,exist_ok=True);Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")

def collect(path):
    rows=[];seen=set();pb=None;ib=None;pool=None
    for p in sorted(Path(path).rglob("*.json")):
        x=json.loads(p.read_text())
        if x.get("schema")!="c3x-p24-core-census-v1" or x.get("scientific_stage")!=STAGE:continue
        if x.get("selective_outcomes_consulted") is not False or x["family"] in seen:raise SystemExit("P24_CENSUS_AUTHORITY")
        seen.add(x["family"]);rows.extend(x["rows"])
        if pb is None:pb=x["p20_binaries"];ib=x["inanis_binary_sha256"];pool=x["pool_sha256"]
        elif pb!=x["p20_binaries"] or ib!=x["inanis_binary_sha256"] or pool!=x["pool_sha256"]:raise SystemExit("P24_CENSUS_IDENTITY")
    if seen!=set(FAMILIES) or len(rows)!=384:raise SystemExit("P24_CENSUS_SET")
    return rows,pb,ib,pool

def export(a):
    rows,_,_,_=collect(a.census_dir);lines=["\t".join(HEADER)]
    for r in sorted(rows,key=lambda q:q["candidate_sha256"]):
        z=r["features"];hh=r["inanis_sham"]["engagement"]
        vals=[r["candidate_sha256"],r["material_seed_name"],r["side_to_move"],r["square"],*[format(float(z[k]),".17g") for k in p21.FEATURES],str(int(hh.get("TT_MAIN",0))),str(int(hh.get("PAWN_Q",0)))];lines.append("\t".join(vals))
    Path(a.out).write_text("\n".join(lines)+"\n");print("P24_TSV",len(rows),p21.sha_file(a.out))

def read_atlas(path):
    with open(path,newline="") as f:rows=list(csv.DictReader(f,delimiter="\t"))
    if len(rows)!=384 or len({r["sha"] for r in rows})!=384:raise SystemExit("P24_ATLAS_CARDINALITY")
    return {r["sha"]:r for r in rows}

def precommit(a):
    rows,pb,ib,pool_sha=collect(a.census_dir);by={r["candidate_sha256"]:r for r in rows};atlas=read_atlas(a.atlas)
    ar=json.loads(Path(a.atlas_receipt).read_text())
    if ar.get("schema")!="c3x-p24-atlas-v1" or ar.get("scientific_stage")!=STAGE or ar.get("outcomes_consulted") is not False or ar.get("cells")!=384:raise SystemExit("P24_ATLAS_RECEIPT")
    pool=json.loads(Path(a.pool).read_text())
    if pool.get("pool_sha256")!=pool_sha or pool.get("freshness",{}).get("generation_index_offset")!=520000:raise SystemExit("P24_POOL_JOIN")
    cells=[]
    for sha,r in by.items():
        z=atlas.get(sha)
        if z is None:raise SystemExit("P24_ATLAS_JOIN "+sha)
        cells.append({"candidate_sha256":sha,"material_seed_name":r["material_seed_name"],"side_to_move":r["side_to_move"],"square":r["square"],"vertex":r["vertex"],"fen":r["fen"],"world":r["world"],"states":{"K1":"ALL","K2":z["state2"],"K4":z["state4"],"K8":z["state8"]},"atlas":{"c_total":float(z["c_total"]),"c_q":float(z["c_q"]),"d_total":float(z["d_total"]),"d_q":float(z["d_q"]),"d_joint":float(z["d_joint"])}})
    for K,expected in ((2,12),(4,6),(8,3)):
        q=Counter((c["material_seed_name"],c["side_to_move"],c["states"][f"K{K}"]) for c in cells)
        if any(v!=expected for v in q.values()) or len(q)!=(16*K):raise SystemExit(f"P24_K{K}_QUOTA")
    out={"schema":"c3x-p24-core-precommit-v1","scientific_stage":STAGE,"selective_outcomes_consulted":False,"fresh_world_pool_sha256":pool_sha,"fresh_generation_offset":520000,"p20_binaries":pb,"inanis_binary_sha256":ib,"atlas_receipt":ar,"atlas_tsv_sha256":p21.sha_file(a.atlas),"refinement_levels":list(LEVELS),"cells":sorted(cells,key=lambda z:z["candidate_sha256"])};seal(out)
    Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n");print("P24_PRECOMMIT_PASS",out["receipt_sha256"])

def load_pre(path):
    x=json.loads(Path(path).read_text())
    if x.get("schema")!="c3x-p24-core-precommit-v1" or x.get("scientific_stage")!=STAGE or x.get("selective_outcomes_consulted") is not False:raise SystemExit("P24_PRECOMMIT_AUTHORITY")
    return x

def baseline(c,run):
    w=p20.world_value(c,run["semantic"]["bestmove"])
    if w is None:raise SystemExit("P24_WORLD_JOIN_SHAM "+c["candidate_sha256"])
    return {"receipt":run,"world":w,"action_changed":False,"fine_changed":False,"coarse_changed":False}
def arm(c,base_run,base_world,run):
    w=p20.world_value(c,run["semantic"]["bestmove"])
    if w is None:raise SystemExit("P24_WORLD_JOIN "+c["candidate_sha256"])
    return {"receipt":run,"world":w,"action_changed":run["semantic"]["bestmove"]!=base_run["semantic"]["bestmove"],"fine_changed":(w["wdl"],w["precise_dtz"])!=(base_world["wdl"],base_world["precise_dtz"]),"coarse_changed":w["wdl"]!=base_world["wdl"]}

def vertex(a):
    pre=load_pre(a.precommit);eng=p20.parse_engines(a.engine)
    for t in TARGETS:
        if p21.sha_file(eng[t]["path"])!=pre["p20_binaries"][t]["sha256"] or eng[t]["protocol"]!=pre["p20_binaries"][t]["protocol"]:raise SystemExit("P24_ENGINE_IDENTITY "+t)
    if p21.sha_file(a.inanis)!=pre["inanis_binary_sha256"]:raise SystemExit("P24_INANIS_IDENTITY")
    src=[r for r in pre["cells"] if r["material_seed_name"]==a.family]
    if len(src)!=48:raise SystemExit("P24_VERTEX_SUPPORT")
    rows=[]
    for i,c in enumerate(src,1):
        rec={k:c[k] for k in ("candidate_sha256","material_seed_name","side_to_move","square","vertex","fen","states","atlas")};rec["targets"]={}
        for t in TARGETS:
            br=p20.run_search(eng[t],c["fen"],"SHAM",a.nodes);b=baseline(c,br);arms={"00":b}
            for bits,mode in (("10","MASK_MAIN"),("01","MASK_QSEARCH"),("11","MASK_MAIN_QSEARCH"),("ALL","MASK_ALL")):
                arms[bits]=arm(c,br,b["world"],p20.run_search(eng[t],c["fen"],mode,a.nodes))
            rec["targets"][t]={"arms":arms}
        ibr=p21.run_inanis(a.inanis,c["fen"],"SHAM",a.nodes);ib=baseline(c,ibr);ia={"SHAM":ib}
        for name,mode in (("TT_MAIN","MASK_TT_MAIN"),("PAWN_Q","MASK_PAWN_Q")):
            ia[name]=arm(c,ibr,ib["world"],p21.run_inanis(a.inanis,c["fen"],mode,a.nodes))
        rec["inanis"]={"arms":ia};rows.append(rec);print("P24_VERTEX",a.family,i,c["states"]["K8"],flush=True)
    out={"schema":"c3x-p24-core-vertex-v1","scientific_stage":STAGE,"family":a.family,"precommit_receipt_sha256":pre["receipt_sha256"],"rows":rows};seal(out)
    Path(a.out).parent.mkdir(parents=True,exist_ok=True);Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n");print("P24_VERTEX_PASS",a.family,out["receipt_sha256"])

def fp(z):
    c=z["curvature"];return [c["class"],c["dominant_coordinate"],c["dominant_sign"]]
def same(v):return len({json.dumps(x,sort_keys=True) for x in v})==1

def adjudicate(a):
    pre=load_pre(a.precommit);by={}
    for p in sorted(Path(a.results).rglob("p24-core-*.json")):
        x=json.loads(p.read_text())
        if x.get("schema")!="c3x-p24-core-vertex-v1" or x.get("scientific_stage")!=STAGE or x.get("precommit_receipt_sha256")!=pre["receipt_sha256"]:continue
        if x["family"] in by:raise SystemExit("P24_RESULT_DUP")
        by[x["family"]]=x
    if set(by)!=set(FAMILIES):raise SystemExit("P24_RESULT_SET")
    court={};laws={t:{} for t in TARGETS}
    for K in LEVELS:
        sk=f"K{K}";states=sorted({r["states"][sk] for x in by.values() for r in x["rows"]})
        if len(states)!=K:raise SystemExit(f"P24_STATE_COUNT_{K}")
        fps={};compat={};strict_cells=[];natural_cells=[];recovery=[]
        for state in states:
            fps[state]={};compat[state]={}
            for t in TARGETS:
                fps[state][t]={}
                for sq,mp in SQUARES.items():
                    vres={bit:{"rows":[r for r in by[fam]["rows"] if r["states"][sk]==state]} for bit,fam in mp.items()}
                    expected=48//K
                    if any(len(vres[b]["rows"])!=expected for b in vres):raise SystemExit(f"P24_SUPPORT_K{K}_{state}_{sq}")
                    z=p20.square_analysis(vres,t);fps[state][t][sq]=fp(z)
                    if K==8:laws[t].setdefault(state,{})[sq]=fp(z)
            for sq in SQUARES:
                vals=[fps[state][t][sq] for t in TARGETS]
                if same(vals):strict_cells.append(state+"|"+sq)
                pair=[]
                for x,y in itertools.combinations(TARGETS,2):
                    # Recompute analysis objects only for inherited compatibility.
                    mp=SQUARES[sq];vx={bit:{"rows":[r for r in by[fam]["rows"] if r["states"][sk]==state]} for bit,fam in mp.items()}
                    pair.append(p20.compatible(p20.square_analysis(vx,x),p20.square_analysis(vx,y))["compatible"])
                compat[state][sq]=all(pair)
                if all(pair):natural_cells.append(state+"|"+sq)
            heavy=[fps[state][t]["HEAVY_HEAVY"] for t in TARGETS];minor=[fps[state][t]["MINOR_MINOR"] for t in TARGETS]
            if all(tuple(x)==("CURVED","QSEARCH",-1) for x in heavy) and not (same(minor) and minor[0][0]=="CURVED"):recovery.append(state)
        universal_strict=len(strict_cells)==K*2;universal_natural=len(natural_cells)==K*2
        distinct={t:len({json.dumps([fps[s][t]["HEAVY_HEAVY"],fps[s][t]["MINOR_MINOR"]],sort_keys=True) for s in states}) for t in TARGETS}
        court[sk]={"states":states,"fingerprints":fps,"strict_cells":strict_cells,"natural_cells":natural_cells,"universal_strict_architecture_invariance":universal_strict,"universal_conditional_naturality":universal_natural,"p20_relation_recovery_states":recovery,"distinct_response_laws_by_engine":distinct}
    k8=court["K8"];blocks=defaultdict(list)
    for state in k8["states"]:
        for t in TARGETS:
            sig=json.dumps([k8["fingerprints"][state][t]["HEAVY_HEAVY"],k8["fingerprints"][state][t]["MINOR_MINOR"]],sort_keys=True,separators=(",",":"))
            blocks[sig].append(t+"|"+state)
    response_blocks=sorted((sorted(v) for v in blocks.values()),key=lambda z:(len(z),z),reverse=True)
    common_states=[]
    for state in k8["states"]:
        sigs=[json.dumps([k8["fingerprints"][state][t]["HEAVY_HEAVY"],k8["fingerprints"][state][t]["MINOR_MINOR"]],sort_keys=True) for t in TARGETS]
        if len(set(sigs))==1:common_states.append(state)
    architecture_free=len(common_states)==8
    architecture_index_necessary=not architecture_free
    nonconstant=all(k8["distinct_response_laws_by_engine"][t]>1 for t in TARGETS)
    ceiling=(not any(court[f"K{K}"]["universal_strict_architecture_invariance"] for K in LEVELS) and not any(court[f"K{K}"]["universal_conditional_naturality"] for K in LEVELS) and architecture_index_necessary)
    pawnq=sum(r["inanis"]["arms"]["PAWN_Q"]["fine_changed"] for x in by.values() for r in x["rows"])
    coarse=any(r["targets"][t]["arms"][b]["coarse_changed"] for x in by.values() for r in x["rows"] for t in TARGETS for b in ("10","01","11","ALL"))
    if pawnq!=0:verdict="NEGATIVE_CONTROL_FAILURE"
    elif architecture_free:verdict="ARCHITECTURE_FREE_INTERVENTION_RESPONSE_BISIMULATION_RECONSTITUTED"
    elif ceiling and nonconstant:verdict="FROZEN_ATLAS_QUOTIENT_REFINEMENT_CEILING_REACHED__ARCHITECTURE_INDEXED_CAUSAL_LAW_CONSTITUTED"
    elif ceiling:verdict="FROZEN_ATLAS_QUOTIENT_REFINEMENT_CEILING_REACHED__NO_STABLE_LAW_CONSTITUTION"
    else:verdict="PARTIAL_ATLAS_TRANSPORT__SUCCESSOR_CONFIRMATION_REQUIRED"
    out={"schema":"c3x-p24-adjudication-v1","scientific_stage":STAGE,"precommit_receipt_sha256":pre["receipt_sha256"],"fresh_cells":384,"quotient_court":court,"k8_intervention_response_bisimulation":{"response_equivalence_blocks":response_blocks,"architecture_free_states":common_states,"architecture_free_success":architecture_free,"architecture_index_necessary":architecture_index_necessary},"quotient_refinement_ceiling":ceiling,"architecture_indexed_laws":laws,"architecture_indexed_law_nonconstant_each_engine":nonconstant,"inanis_pawn_q_negative_control":{"fine_changes":pawnq,"pass":pawnq==0},"robust_wdl_changed_any_arm":coarse,"verdict":verdict,"authority_ceiling":"fresh P24 offset-520000 pawnless core; frozen empirical-copula atlas K=1/2/4/8; Stockfish19/Berserk/Ethereal PSM_READ interventions; Inanis negative control; 80k SHAM census; 300k selective nodes; exact-world fine-value response geometry"};seal(out)
    Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n");print("P24_ADJUDICATION",verdict,"ceiling=",ceiling,"common_k8=",len(common_states),"pawnq=",pawnq)

def main():
    ap=argparse.ArgumentParser();sp=ap.add_subparsers(dest="cmd",required=True)
    p=sp.add_parser("census");p.add_argument("--pool",required=True);p.add_argument("--engine",action="append",required=True);p.add_argument("--inanis",required=True);p.add_argument("--family",choices=FAMILIES,required=True);p.add_argument("--nodes",type=int,default=80000);p.add_argument("--out",required=True);p.set_defaults(fn=census)
    p=sp.add_parser("export");p.add_argument("--census-dir",required=True);p.add_argument("--out",required=True);p.set_defaults(fn=export)
    p=sp.add_parser("precommit");p.add_argument("--census-dir",required=True);p.add_argument("--pool",required=True);p.add_argument("--atlas",required=True);p.add_argument("--atlas-receipt",required=True);p.add_argument("--out",required=True);p.set_defaults(fn=precommit)
    p=sp.add_parser("vertex");p.add_argument("--precommit",required=True);p.add_argument("--engine",action="append",required=True);p.add_argument("--inanis",required=True);p.add_argument("--family",choices=FAMILIES,required=True);p.add_argument("--nodes",type=int,default=300000);p.add_argument("--out",required=True);p.set_defaults(fn=vertex)
    p=sp.add_parser("adjudicate");p.add_argument("--precommit",required=True);p.add_argument("--results",required=True);p.add_argument("--out",required=True);p.set_defaults(fn=adjudicate)
    a=ap.parse_args();a.fn(a)
if __name__=="__main__":main()
