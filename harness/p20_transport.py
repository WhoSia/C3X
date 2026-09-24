#!/usr/bin/env python3
import argparse,hashlib,itertools,json,os,re,subprocess
from collections import Counter,defaultdict
from pathlib import Path

TARGETS=("stockfish_19","berserk","ethereal")
FAMILIES=("KQQvKQ","KQRvKQ","KQQvKR","KQRvKR","KRBvKB","KRNvKB","KRBvKN","KRNvKN")
SQUARES={
 "HEAVY_HEAVY":{"00":"KQQvKQ","10":"KQRvKQ","01":"KQQvKR","11":"KQRvKR"},
 "MINOR_MINOR":{"00":"KRBvKB","10":"KRNvKB","01":"KRBvKN","11":"KRNvKN"}
}
ARMS={"00":"SHAM","10":"MASK_MAIN","01":"MASK_QSEARCH","11":"MASK_MAIN_QSEARCH","ALL":"MASK_ALL"}
CENSUS_NODES=80000
INTERVENTION_NODES=300000

def canon(o): return json.dumps(o,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()
def sha_obj(o): return hashlib.sha256(canon(o)).hexdigest()
def sha_file(p):
    h=hashlib.sha256()
    with open(p,"rb") as f:
        for c in iter(lambda:f.read(1<<20),b""): h.update(c)
    return h.hexdigest()

def parse_engines(items):
    out={}
    for x in items:
        parts=x.split(",",2)
        if len(parts)!=3: raise SystemExit("--engine label,protocol,path")
        label,protocol,path=parts
        if label in out: raise SystemExit("DUP_ENGINE "+label)
        if protocol not in ("env","stockfish_uci"): raise SystemExit("BAD_PROTOCOL "+protocol)
        out[label]={"protocol":protocol,"path":path}
    if set(out)!=set(TARGETS): raise SystemExit(f"ENGINE_SET {sorted(out)}")
    return out

def read_until(p,pred,limit=100000):
    lines=[]
    while len(lines)<limit:
        x=p.stdout.readline()
        if x=="": break
        x=x.rstrip("\n"); lines.append(x)
        if pred(x): break
    return lines

def has_option(text,name):
    return re.search(r"^option name "+re.escape(name)+r"(?: |$)",text,re.M) is not None

def run_search(spec,fen,mode,nodes):
    env=os.environ.copy()
    if spec["protocol"]=="env":
        env["C3X_PSM_MODE"]=mode
    else:
        env.pop("C3X_PSM_MODE",None)
    p=subprocess.Popen([spec["path"]],stdin=subprocess.PIPE,stdout=subprocess.PIPE,
                       stderr=subprocess.STDOUT,text=True,bufsize=1,env=env)
    p.stdin.write("uci\n");p.stdin.flush()
    pre=read_until(p,lambda x:x.strip()=="uciok")
    if not any(x.strip()=="uciok" for x in pre):
        p.kill(); raise RuntimeError("UCI_OK_MISSING\n"+"\n".join(pre[-80:]))
    opts="\n".join(pre)
    cmds=[]
    if spec["protocol"]=="stockfish_uci":
        if not has_option(opts,"C3X_TTReadMode") or not has_option(opts,"C3X_Telemetry"):
            p.kill(); raise RuntimeError("STOCKFISH_C3X_SURFACE_MISSING")
        cmds += [f"setoption name C3X_TTReadMode value {mode}",
                 "setoption name C3X_Telemetry value true"]
    if has_option(opts,"Threads"): cmds.append("setoption name Threads value 1")
    if has_option(opts,"Hash"): cmds.append("setoption name Hash value 64")
    if has_option(opts,"SyzygyProbeLimit"): cmds.append("setoption name SyzygyProbeLimit value 0")
    if has_option(opts,"UCI_ShowWDL"): cmds.append("setoption name UCI_ShowWDL value true")
    if has_option(opts,"Clear Hash"): cmds.append("setoption name Clear Hash")
    cmds += ["isready",f"position fen {fen}",f"go nodes {nodes}"]
    for c in cmds: p.stdin.write(c+"\n")
    p.stdin.flush()
    lines=pre+read_until(p,lambda x:x.startswith("bestmove "))
    p.terminate()
    try: rest,_=p.communicate(timeout=4)
    except subprocess.TimeoutExpired:
        p.kill(); rest,_=p.communicate(timeout=4)
    if rest: lines.extend(rest.splitlines())
    if not any(x.strip()=="readyok" for x in lines):
        raise RuntimeError("READY_OK_MISSING")
    best=next((x for x in reversed(lines) if x.startswith("bestmove ")),None)
    infos=[x for x in lines if x.startswith("info ") and " score " in x and " pv " in x]
    if not best or not infos:
        raise RuntimeError("SEARCH_RECEIPT_MISSING\n"+"\n".join(lines[-100:]))
    final=infos[-1]
    def grab(pat):
        m=re.search(pat,final); return m.group(1) if m else None
    prefix="info string c3x_psm_v1 " if spec["protocol"]=="env" else "info string c3x_ttread_v1 "
    tel=next((x for x in reversed(lines) if x.startswith(prefix)),None)
    if not tel: raise RuntimeError("TELEMETRY_MISSING "+spec["protocol"])
    t={}
    for z in tel.split()[3:]:
        if "=" in z:
            k,v=z.split("=",1)
            try:t[k]=int(v)
            except:t[k]=v
    if spec["protocol"]=="env":
        main=int(t.get("hits_main",0)); q=int(t.get("hits_qsearch",0))
    else:
        main=int(t.get("raw_hits_main",0)); q=int(t.get("raw_hits_qsearch",0))
    bt=best.split()
    return {
      "semantic":{
        "bestmove":bt[1] if len(bt)>1 else None,
        "score":grab(r"\bscore ((?:cp|mate) -?\d+)"),
        "wdl":grab(r"\bwdl (\d+ \d+ \d+)"),
        "depth":int(grab(r"\bdepth (\d+)") or 0),
        "seldepth":int(grab(r"\bseldepth (\d+)") or 0),
        "nodes":int(grab(r"\bnodes (\d+)") or 0),
        "pv":grab(r"\bpv (.+)$")
      },
      "engagement":{"MAIN":main,"QSEARCH":q,"floor":min(main,q),"passed":main>0 and q>0},
      "telemetry":t
    }

def world_value(c,move):
    m=next((x for x in c["world"]["moves"] if x["uci"]==move),None)
    if m is None: return None
    return {"wdl":int(m["mover_wdl"]),"precise_dtz":int(m["mover_precise_dtz"])}

def census(a):
    stage=json.loads(Path(a.stage_a).read_text()); eng=parse_engines(a.engine)
    src=[c for c in stage["candidates"] if c["material_seed_name"]==a.family]
    if len(src)!=72: raise SystemExit(f"CENSUS_FAMILY_COUNT {a.family} {len(src)}/72")
    rows=[]
    for i,c in enumerate(src,1):
        sham={}; floor=None; ok=True
        for t in TARGETS:
            r=run_search(eng[t],c["fen"],"SHAM",CENSUS_NODES)
            sham[t]=r
            ok=ok and r["engagement"]["passed"]
            f=r["engagement"]["floor"]; floor=f if floor is None else min(floor,f)
        rows.append({"candidate":c,"sham":sham,"all_targets_engaged":ok,"joint_floor":int(floor or 0)})
        print(f"P20_CENSUS {a.family} {i:02d}/72 pass={ok} floor={floor}",flush=True)
    out={
      "schema":"c3x-p20-r2-sham-census-v1","scientific_stage":"C3X 0.7.0-G9.4-P20-R2",
      "family":a.family,"stage_a_pool_sha256":stage["pool_sha256"],
      "selective_intervention_outcomes_consulted":False,
      "census_nodes":CENSUS_NODES,
      "binaries":{t:{"protocol":eng[t]["protocol"],"sha256":sha_file(eng[t]["path"])} for t in TARGETS},
      "rows":rows,
      "counts":{
        "total":len(rows),
        "eligible":sum(r["all_targets_engaged"] for r in rows),
        "eligible_by_side":{s:sum(r["all_targets_engaged"] and r["candidate"]["side_to_move"]==s for r in rows) for s in ("WHITE","BLACK")}
      }
    }
    Path(a.out).parent.mkdir(parents=True,exist_ok=True)
    Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print("P20_CENSUS_PASS",a.family,out["counts"])

def choose(rows):
    by=defaultdict(list)
    for r in rows:
        if r["all_targets_engaged"]: by[r["candidate"]["side_to_move"]].append(r)
    for s in by:
        by[s].sort(key=lambda r:(-int(r["joint_floor"]),r["candidate"]["candidate_sha256"]))
    if len(by["WHITE"])<6 or len(by["BLACK"])<6: return []
    return sorted(by["WHITE"][:6]+by["BLACK"][:6],key=lambda r:r["candidate"]["candidate_sha256"])

def seal(a):
    stage=json.loads(Path(a.stage_a).read_text())
    files=sorted(Path(a.census_dir).rglob("p20-census-*.json"))
    if len(files)!=8: raise SystemExit(f"CENSUS_FILE_COUNT {len(files)}/8")
    cs={}; binaries=None; selected=[]; counts={}
    for p in files:
        x=json.loads(p.read_text()); fam=x["family"]
        if fam in cs: raise SystemExit("CENSUS_DUP "+fam)
        if x.get("selective_intervention_outcomes_consulted") is not False: raise SystemExit("CENSUS_LEAK")
        if x["stage_a_pool_sha256"]!=stage["pool_sha256"]: raise SystemExit("CENSUS_POOL_MISMATCH")
        if binaries is None: binaries=x["binaries"]
        elif binaries!=x["binaries"]: raise SystemExit("CENSUS_BINARY_MISMATCH")
        chosen=choose(x["rows"])
        if len(chosen)!=12:
            raise SystemExit(f"P20_ENGAGEMENT_HOLD {fam} eligible={x['counts']['eligible']} chosen={len(chosen)}")
        counts[fam]={
          "eligible":x["counts"]["eligible"],
          "eligible_by_side":x["counts"]["eligible_by_side"],
          "committed":12,
          "committed_by_side":{"WHITE":6,"BLACK":6}
        }
        selected.extend(chosen); cs[fam]=x
    if set(cs)!=set(FAMILIES): raise SystemExit("CENSUS_FAMILY_SET")
    out={
      "schema":"c3x-p20-r2-sham-precommit-v1","scientific_stage":"C3X 0.7.0-G9.4-P20-R2",
      "r1_authorization":"P20-HETEROGENEOUS-ADMISSION-PASS",
      "r1_run_id":36026256576,
      "stage_a_pool_sha256":stage["pool_sha256"],
      "selective_intervention_outcomes_consulted":False,
      "targets":list(TARGETS),"binaries":binaries,
      "runtime":{"census_nodes":CENSUS_NODES,"intervention_nodes":INTERVENTION_NODES,"threads":1,"hash_mib_if_exposed":64,"fresh_process_each_arm":True},
      "selection":"minimum cross-target MAIN/QSEARCH SHAM-hit floor, then candidate hash; six per side",
      "counts":{"stage_a":len(stage["candidates"]),"committed":len(selected),"by_vertex":counts},
      "authorization":"P20-R2-INTERVENTION-AUTHORIZED",
      "committed_cells":selected
    }
    out["precommit_sha256"]=sha_obj(out)
    Path(a.out).parent.mkdir(parents=True,exist_ok=True)
    Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print("P20_R2_PRECOMMIT",out["precommit_sha256"],out["counts"])

def selected_for(pre,fam):
    return [r for r in pre["committed_cells"] if r["candidate"]["material_seed_name"]==fam]

def vertex(a):
    pre=json.loads(Path(a.precommit).read_text()); eng=parse_engines(a.engine)
    if pre.get("authorization")!="P20-R2-INTERVENTION-AUTHORIZED": raise SystemExit("P20_R2_HOLD")
    for t in TARGETS:
        if sha_file(eng[t]["path"])!=pre["binaries"][t]["sha256"]: raise SystemExit("BINARY_IDENTITY_FAIL "+t)
        if eng[t]["protocol"]!=pre["binaries"][t]["protocol"]: raise SystemExit("PROTOCOL_IDENTITY_FAIL "+t)
    src=selected_for(pre,a.family)
    if len(src)!=12: raise SystemExit("COMMIT_COUNT "+a.family)
    rows=[]
    for i,row in enumerate(src,1):
        c=row["candidate"]; rec={"candidate_sha256":c["candidate_sha256"],"family":a.family,
          "square":c["square"],"vertex":c["vertex"],"side_to_move":c["side_to_move"],"fen":c["fen"],"targets":{}}
        for t in TARGETS:
            base=run_search(eng[t],c["fen"],"SHAM",INTERVENTION_NODES)
            bv=world_value(c,base["semantic"]["bestmove"])
            if bv is None: raise SystemExit("WORLD_JOIN_FAIL SHAM "+t)
            arms={"00":{"mode":"SHAM","receipt":base,"world":bv,"action_changed":False,"fine_changed":False,"coarse_changed":False}}
            for bits in ("10","01","11","ALL"):
                rr=run_search(eng[t],c["fen"],ARMS[bits],INTERVENTION_NODES)
                wv=world_value(c,rr["semantic"]["bestmove"])
                if wv is None: raise SystemExit("WORLD_JOIN_FAIL "+bits+" "+t)
                arms[bits]={
                  "mode":ARMS[bits],"receipt":rr,"world":wv,
                  "action_changed":rr["semantic"]["bestmove"]!=base["semantic"]["bestmove"],
                  "fine_changed":(wv["wdl"],wv["precise_dtz"])!=(bv["wdl"],bv["precise_dtz"]),
                  "coarse_changed":wv["wdl"]!=bv["wdl"]
                }
            rec["targets"][t]={"arms":arms}
        rows.append(rec); print(f"P20_VERTEX {a.family} {i}/12",flush=True)
    out={
      "schema":"c3x-p20-r2-vertex-result-v1","scientific_stage":"C3X 0.7.0-G9.4-P20-R2",
      "family":a.family,"precommit_sha256":pre["precommit_sha256"],
      "binary_sha256":{t:sha_file(eng[t]["path"]) for t in TARGETS},
      "rows":rows
    }
    out["result_sha256"]=sha_obj(out)
    Path(a.out).parent.mkdir(parents=True,exist_ok=True)
    Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print("P20_VERTEX_PASS",a.family,out["result_sha256"])

def sign(x,eps=1e-12): return -1 if x < -eps else 1 if x > eps else 0
def phase(v,n):
    vals={"MAIN":abs(v[0]),"QSEARCH":abs(v[1]),"INTERACTION":abs(v[2])}
    order=sorted(vals.items(),key=lambda x:(-x[1],x[0])); floor=2/n; margin=1/n
    if order[0][1]<floor: return "NULL"
    if order[0][1]-order[1][1]<margin: return "MIXED"
    return order[0][0]+"-DOMINANT"

def vertex_summary(rows,t):
    n=len(rows)
    m=sum(r["targets"][t]["arms"]["10"]["fine_changed"] for r in rows)
    q=sum(r["targets"][t]["arms"]["01"]["fine_changed"] for r in rows)
    mq=sum(r["targets"][t]["arms"]["11"]["fine_changed"] for r in rows)
    coarse=sum(r["targets"][t]["arms"][b]["coarse_changed"] for r in rows for b in ("10","01","11","ALL"))
    action={b:sum(r["targets"][t]["arms"][b]["action_changed"] for r in rows) for b in ("10","01","11","ALL")}
    v=[m/n,q/n,mq/n-m/n-q/n]
    return {"n":n,"vector":{"MAIN":v[0],"QSEARCH":v[1],"INTERACTION":v[2]},
            "counts":{"MAIN":m,"QSEARCH":q,"MAIN_QSEARCH":mq,"coarse_total":coarse,"action":action},
            "phase":phase(v,n),"interaction_sign":sign(v[2])}

def square_analysis(vres,t):
    s={b:vertex_summary(vres[b]["rows"],t) for b in ("00","10","01","11")}
    names=("MAIN","QSEARCH","INTERACTION")
    vv={b:[s[b]["vector"][k] for k in names] for b in s}
    H=[vv["11"][i]-vv["10"][i]-vv["01"][i]+vv["00"][i] for i in range(3)]
    n=s["00"]["n"]; res=1/n; mx=max(abs(x) for x in H)
    cls="FLAT" if mx<=res+1e-12 else "CURVED" if mx>=2*res-1e-12 else "BORDERLINE"
    dom=max(range(3),key=lambda i:(abs(H[i]),-i))
    return {"vertices":s,"curvature":{"vector":dict(zip(names,H)),"linf":mx,
      "one_cell_resolution":res,"class":cls,"dominant_coordinate":names[dom],"dominant_sign":sign(H[dom])}}

def compatible(a,b):
    ca=a["curvature"]; cb=b["curvature"]
    keys=("MAIN","QSEARCH","INTERACTION")
    d=max(abs(ca["vector"][k]-cb["vector"][k]) for k in keys)
    fp=True
    if ca["class"]=="CURVED" and cb["class"]=="CURVED":
        fp=ca["dominant_coordinate"]==cb["dominant_coordinate"] and ca["dominant_sign"]==cb["dominant_sign"]
    ok=ca["class"]==cb["class"] and fp and d<=ca["one_cell_resolution"]+1e-12
    return {"compatible":ok,"class_equal":ca["class"]==cb["class"],"curved_fingerprint_equal":fp,
            "curvature_linf_delta":d,"threshold":ca["one_cell_resolution"]}

def adjudicate(a):
    files=sorted(Path(a.result_dir).rglob("p20-vertex-*.json"))
    if len(files)!=8: raise SystemExit(f"VERTEX_FILE_COUNT {len(files)}/8")
    by={}
    prehash=None
    for p in files:
        x=json.loads(p.read_text()); fam=x["family"]
        if fam in by: raise SystemExit("VERTEX_DUP "+fam)
        if prehash is None: prehash=x["precommit_sha256"]
        elif prehash!=x["precommit_sha256"]: raise SystemExit("PRECOMMIT_HASH_MISMATCH")
        by[fam]=x
    if set(by)!=set(FAMILIES): raise SystemExit("VERTEX_FAMILY_SET")
    squares={sq:{b:by[f] for b,f in mp.items()} for sq,mp in SQUARES.items()}
    targets={}; any_coarse=False
    for t in TARGETS:
        targets[t]={}
        for sq in SQUARES:
            targets[t][sq]=square_analysis(squares[sq],t)
            any_coarse=any_coarse or any(targets[t][sq]["vertices"][b]["counts"]["coarse_total"] for b in ("00","10","01","11"))
    pairwise={}
    all_compat=True
    for a0,b0 in itertools.combinations(TARGETS,2):
        key=a0+"_VS_"+b0; pairwise[key]={}
        for sq in SQUARES:
            z=compatible(targets[a0][sq],targets[b0][sq]); pairwise[key][sq]=z
            all_compat=all_compat and z["compatible"]
    replicated={}
    any_rep=False
    for sq in SQUARES:
        cur=[(t,targets[t][sq]["curvature"]) for t in TARGETS if targets[t][sq]["curvature"]["class"]=="CURVED"]
        groups=Counter((x["dominant_coordinate"],x["dominant_sign"]) for _,x in cur)
        best=max(groups.values()) if groups else 0
        replicated[sq]={"replicated_cross_family":best>=2,
          "curved_targets":[t for t,_ in cur],
          "fingerprints":{t:[targets[t][sq]["curvature"]["class"],targets[t][sq]["curvature"]["dominant_coordinate"],targets[t][sq]["curvature"]["dominant_sign"]] for t in TARGETS}}
        any_rep=any_rep or best>=2
    if all_compat:
        verdict="ENGINE-FAMILY-NATURALITY-SUPPORTED-WITHIN-SCOPE"
    elif any_rep:
        verdict="PARTIAL-CROSS-ENGINE-RELATION-LAW-TRANSPORT"
    else:
        verdict="ENGINE-FAMILY-CONDITIONED-RELATION-GEOMETRY"
    out={
      "schema":"c3x-p20-r2-cross-engine-naturality-result-v1",
      "scientific_stage":"C3X 0.7.0-G9.4-P20-R2",
      "r1_run_id":36026256576,"precommit_sha256":prehash,
      "targets":targets,"pairwise_same_world_naturality":pairwise,
      "replicated_cross_family_curvature":replicated,
      "robust_wdl_changed_any_arm":any_coarse,
      "literal_sequential_noncommutativity":"NOT_IDENTIFIED_BY_ENDPOINT_SQUARES",
      "primary_verdict":verdict,
      "authority_ceiling":"same fresh exact-world committed cells; source-locked and independently admitted heterogeneous PSM_READ targets; fixed 300k nodes; relation-level transport only"
    }
    out["result_sha256"]=sha_obj(out)
    Path(a.out).parent.mkdir(parents=True,exist_ok=True)
    Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print("P20_R2_RESULT",verdict,out["result_sha256"])
    print(json.dumps({"pairwise":pairwise,"replicated":replicated,"robust_wdl_changed_any_arm":any_coarse},sort_keys=True))

def main():
    ap=argparse.ArgumentParser(); sp=ap.add_subparsers(dest="cmd",required=True)
    c=sp.add_parser("census"); c.add_argument("--stage-a",required=True); c.add_argument("--engine",action="append",required=True); c.add_argument("--family",choices=FAMILIES,required=True); c.add_argument("--out",required=True)
    s=sp.add_parser("seal"); s.add_argument("--stage-a",required=True); s.add_argument("--census-dir",required=True); s.add_argument("--out",required=True)
    v=sp.add_parser("vertex"); v.add_argument("--precommit",required=True); v.add_argument("--engine",action="append",required=True); v.add_argument("--family",choices=FAMILIES,required=True); v.add_argument("--out",required=True)
    d=sp.add_parser("adjudicate"); d.add_argument("--result-dir",required=True); d.add_argument("--out",required=True)
    a=ap.parse_args(); {"census":census,"seal":seal,"vertex":vertex,"adjudicate":adjudicate}[a.cmd](a)

if __name__=="__main__":
    main()
