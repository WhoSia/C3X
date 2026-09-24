#!/usr/bin/env python3
import argparse,hashlib,json,os,re,subprocess
from collections import defaultdict
from pathlib import Path

TARGETS=("frozen_20260810","stockfish_19")
DISCOVERY=("KRRvKR","KRBvKR","KQvKRB","KRvKQB")
HELDOUT=("KRNvKR","KBBvKN","KQvKRN","KRvKQN")
FAMILIES=DISCOVERY+HELDOUT
NODES=300000
ARMS={"00":"SHAM","10":"MASK_MAIN","01":"MASK_QSEARCH","11":"MASK_MAIN_QSEARCH","ALL":"MASK_ALL"}
SITES=("MAIN","SUCCESSOR","QSEARCH")
SEM_FIELDS=("bestmove","score","wdl","pv")

def canon(o): return json.dumps(o,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()
def sha_obj(o): return hashlib.sha256(canon(o)).hexdigest()
def sha_file(p):
    h=hashlib.sha256()
    with open(p,"rb") as f:
        for c in iter(lambda:f.read(1<<20),b""): h.update(c)
    return h.hexdigest()
def bins(items):
    out={}
    for x in items:
        k,p=x.split("=",1); out[k]=p
    if set(out)!=set(TARGETS): raise SystemExit("need both targets")
    return out

def run_search(binary,fen,mode,nodes=NODES):
    p=subprocess.Popen([binary],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,bufsize=1)
    cmds=["uci",f"setoption name C3X_TTReadMode value {mode}",
          "setoption name C3X_Telemetry value true","setoption name Threads value 1",
          "setoption name Hash value 64","setoption name SyzygyProbeLimit value 0",
          "setoption name UCI_ShowWDL value true","setoption name Clear Hash","isready",
          f"position fen {fen}",f"go nodes {nodes}"]
    for c in cmds: p.stdin.write(c+"\n")
    p.stdin.flush(); lines=[]
    for line in p.stdout:
        line=line.rstrip("\n"); lines.append(line)
        if line.startswith("bestmove "): break
    p.terminate()
    try: rest,_=p.communicate(timeout=5)
    except subprocess.TimeoutExpired:
        p.kill(); rest,_=p.communicate(timeout=5)
    if rest: lines.extend(rest.splitlines())
    best=next((x for x in reversed(lines) if x.startswith("bestmove ")),None)
    infos=[x for x in lines if x.startswith("info depth ") and " score " in x and " pv " in x]
    tel=next((x for x in lines if x.startswith("info string c3x_ttread_v1 ")),None)
    if not best or not infos or not tel: raise RuntimeError("incomplete UCI receipt\n"+"\n".join(lines[-80:]))
    final=infos[-1]; bt=best.split()
    def grab(pat):
        m=re.search(pat,final); return m.group(1) if m else None
    t={}
    for tok in tel.split()[3:]:
        if "=" in tok:
            k,v=tok.split("=",1)
            try:t[k]=int(v)
            except:t[k]=v
    return {"semantic":{"bestmove":bt[1],"depth":int(grab(r"\bdepth (\d+)") or 0),
                        "seldepth":int(grab(r"\bseldepth (\d+)") or 0),
                        "score":grab(r"\bscore ((?:cp|mate) -?\d+)"),
                        "wdl":grab(r"\bwdl (\d+ \d+ \d+)"),
                        "nodes":int(grab(r"\bnodes (\d+)") or 0),
                        "pv":grab(r"\bpv (.+)$")},
            "telemetry":t,"telemetry_line":tel}

def site_uses(t):
    return {"MAIN":int(t.get("use_main_eval",0))+int(t.get("use_main_value",0))+int(t.get("use_main_cutoff_gate",0)),
            "SUCCESSOR":int(t.get("use_successor_value",0)),
            "QSEARCH":int(t.get("use_qsearch_eval",0))+int(t.get("use_qsearch_value",0))+int(t.get("use_qsearch_cutoff",0))}

def engagement(r):
    t=r["telemetry"]
    hits={"MAIN":int(t.get("raw_hits_main",0)),"SUCCESSOR":int(t.get("raw_hits_successor",0)),"QSEARCH":int(t.get("raw_hits_qsearch",0))}
    uses=site_uses(t); H=sum(hits.values()); U=sum(uses.values())
    passed=H>=64 and U>=16 and all(hits[s]>0 for s in SITES) and all(uses[s]>0 for s in SITES)
    return {"H":H,"U":U,"B":sum(uses[s]>0 for s in SITES),"raw_hits_by_site":hits,
            "semantic_uses_by_site":uses,"site_use_floor":min(uses.values()),"passed":passed}

def world_value(c,move):
    m=next((x for x in c["world"]["moves"] if x["uci"]==move),None)
    return None if m is None else {"wdl":int(m["mover_wdl"]),"precise_dtz":int(m["mover_precise_dtz"])}

def choose_family(rows,n=8):
    byside=defaultdict(list)
    for r in rows: byside[r["candidate"]["side_to_move"]].append(r)
    for side in byside:
        byside[side].sort(key=lambda r:(-r["selection_floor"],-int(r["candidate"]["tau4"]["tau4"]),r["candidate"]["candidate_sha256"]))
    if len(byside["WHITE"])<4 or len(byside["BLACK"])<4: return []
    out=byside["WHITE"][:4]+byside["BLACK"][:4]
    return sorted(out,key=lambda r:r["candidate"]["candidate_sha256"])

def sham_commit(a):
    stage=json.loads(Path(a.stage_a).read_text()); b=bins(a.binary); rows=[]
    for i,c in enumerate(stage["candidates"],1):
        sham={}; eg={}; allpass=True
        for t,p in b.items():
            r=run_search(p,c["fen"],"SHAM"); sham[t]=r; eg[t]=engagement(r); allpass=allpass and eg[t]["passed"]
        floor=min(eg[t]["site_use_floor"] for t in TARGETS)
        rows.append({"candidate":c,"sham":sham,"engagement":eg,"both_targets_engaged":allpass,"selection_floor":floor})
        print(f"SHAM {i:03d}/{len(stage['candidates'])} family={c['material_seed_name']} pass={allpass}",flush=True)
    selected=[]; counts={}
    for fam in FAMILIES:
        elig=[r for r in rows if r["candidate"]["material_seed_name"]==fam and r["both_targets_engaged"]]
        chosen=choose_family(elig,8); counts[fam]={"eligible":len(elig),"committed":len(chosen)}
        if len(chosen)<8: raise SystemExit(f"P18-ENGAGEMENT-HOLD {fam} eligible={len(elig)} committed={len(chosen)}")
        selected.extend(chosen)
    payload={"schema":"c3x-p18-sham-precommit-v1","scientific_stage":"C3X 0.7.0-G9.4-P18",
             "stage_a_pool_sha256":stage["pool_sha256"],"intervention_outcomes_consulted":False,
             "resource_anchor_nodes":NODES,
             "binaries":{t:{"sha256":sha_file(p),"path_basename":os.path.basename(p)} for t,p in b.items()},
             "runtime":{"threads":1,"hash_mib":64,"clear_hash_each_arm":True,"syzygy_probe_limit":0},
             "material_split":{"discovery":list(DISCOVERY),"heldout":list(HELDOUT)},
             "counts":{"stage_a":len(rows),"committed":len(selected),"by_family":counts},
             "authorization":"P18-MATERIAL-READY","committed_cells":selected}
    payload["precommit_sha256"]=sha_obj(payload)
    Path(a.out).parent.mkdir(parents=True,exist_ok=True); Path(a.out).write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n")
    print("P18_PRECOMMIT",payload["precommit_sha256"],payload["counts"])

def family_rows(pre,family):
    return [r for r in pre["committed_cells"] if r["candidate"]["material_seed_name"]==family]

def family_run(a):
    pre=json.loads(Path(a.precommit).read_text()); b=bins(a.binary); fam=a.family
    if pre["authorization"]!="P18-MATERIAL-READY": raise SystemExit("P18-HOLD")
    expected="DISCOVERY" if fam in DISCOVERY else "HELDOUT"
    if a.split!=expected: raise SystemExit("SPLIT-MISMATCH")
    if expected=="HELDOUT":
        if not a.law: raise SystemExit("HELDOUT-REQUIRES-LAW-SEAL")
        law=json.loads(Path(a.law).read_text())
        if law.get("law_sealed") is not True or law.get("precommit_sha256")!=pre["precommit_sha256"]:
            raise SystemExit("LAW-SEAL-FAIL")
    for t,p in b.items():
        if sha_file(p)!=pre["binaries"][t]["sha256"]: raise SystemExit("BINARY-IDENTITY-FAIL "+t)
    src=family_rows(pre,fam)
    if len(src)!=8: raise SystemExit(f"FAMILY-COMMIT-COUNT {fam} {len(src)}")
    out=[]
    for i,row in enumerate(src,1):
        c=row["candidate"]; o={"candidate_sha256":c["candidate_sha256"],"material_family":fam,
                              "side_to_move":c["side_to_move"],"fen":c["fen"],"targets":{}}
        for t,p in b.items():
            baseline=run_search(p,c["fen"],"SHAM"); sealed=row["sham"][t]
            if any(baseline["semantic"][f]!=sealed["semantic"][f] for f in SEM_FIELDS):
                raise SystemExit(f"SEALED-SHAM-REPLAY-FAIL {fam} {t} {c['candidate_sha256']}")
            sv=world_value(c,baseline["semantic"]["bestmove"])
            if sv is None: raise SystemExit("WORLD-JOIN-FAIL SHAM")
            arms={"00":{"mode":"SHAM","receipt":baseline,"world":sv,"action_changed":False,"fine_changed":False,"coarse_changed":False}}
            for bits in ("10","01","11","ALL"):
                rr=run_search(p,c["fen"],ARMS[bits]); wv=world_value(c,rr["semantic"]["bestmove"])
                if wv is None: raise SystemExit("WORLD-JOIN-FAIL "+bits)
                arms[bits]={"mode":ARMS[bits],"receipt":rr,"world":wv,
                            "action_changed":rr["semantic"]["bestmove"]!=baseline["semantic"]["bestmove"],
                            "fine_changed":(wv["wdl"],wv["precise_dtz"])!=(sv["wdl"],sv["precise_dtz"]),
                            "coarse_changed":wv["wdl"]!=sv["wdl"]}
            o["targets"][t]={"arms":arms}
        out.append(o); print(f"{a.split} {fam} {i}/8",flush=True)
    payload={"schema":"c3x-p18-family-result-v1","scientific_stage":"C3X 0.7.0-G9.4-P18",
             "split":a.split,"family":fam,"precommit_sha256":pre["precommit_sha256"],
             "binary_sha256":{t:sha_file(p) for t,p in b.items()},"sealed_sham_replay":"PASS","rows":out}
    payload["result_sha256"]=sha_obj(payload)
    Path(a.out).parent.mkdir(parents=True,exist_ok=True); Path(a.out).write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n")
    print("P18_FAMILY_PASS",fam,payload["result_sha256"])

def phase_from_counts(m,q,mq,n):
    inter=mq/n-m/n-q/n; floor=2/n; margin=1/n
    vals={"MAIN":abs(m/n),"QSEARCH":abs(q/n),"INTERACTION":abs(inter)}
    ordered=sorted(vals.items(),key=lambda x:(-x[1],x[0]))
    if ordered[0][1]<floor: label="NULL"
    elif ordered[0][1]-ordered[1][1]<margin: label="MIXED"
    else: label=ordered[0][0]+"-DOMINANT"
    return label,inter,vals

def summarize_rows(rows,target):
    n=len(rows); counts={}
    for bits in ("10","01","11","ALL"):
        counts[bits]={"fine":sum(r["targets"][target]["arms"][bits]["fine_changed"] for r in rows),
                      "action":sum(r["targets"][target]["arms"][bits]["action_changed"] for r in rows),
                      "coarse":sum(r["targets"][target]["arms"][bits]["coarse_changed"] for r in rows)}
    label,inter,vals=phase_from_counts(counts["10"]["fine"],counts["01"]["fine"],counts["11"]["fine"],n)
    return {"n":n,"phase":label,"counts":counts,"fine_mobius_MAINxQSEARCH":inter,"phase_component_abs":vals}

def parse_results(items):
    out={}
    for x in items:
        fam,p=x.split("=",1); out[fam]=json.loads(Path(p).read_text())
    return out

def seal_law(a):
    pre=json.loads(Path(a.precommit).read_text()); res=parse_results(a.result)
    if set(res)!=set(DISCOVERY): raise SystemExit("need all discovery families")
    law={"schema":"c3x-p18-law-seal-v1","scientific_stage":"C3X 0.7.0-G9.4-P18",
         "precommit_sha256":pre["precommit_sha256"],"heldout_outcomes_consulted":False,
         "discovery_families":list(DISCOVERY),"heldout_families":list(HELDOUT),"targets":{}}
    for t in TARGETS:
        famsum={f:summarize_rows(res[f]["rows"],t) for f in DISCOVERY}
        pooled=[r for f in DISCOVERY for r in res[f]["rows"]]
        ps=summarize_rows(pooled,t); main_n=sum(v["phase"]=="MAIN-DOMINANT" for v in famsum.values())
        global_main=(ps["phase"]=="MAIN-DOMINANT" and main_n>=3)
        pmain=[v["counts"]["10"]["fine"]/v["n"] for v in famsum.values()]
        law["targets"][t]={"family_summary":famsum,"pooled":ps,"main_dominant_families":main_n,
                           "discovery_pMAIN_range":[min(pmain),max(pmain)],
                           "sealed_prediction":"MAIN-DOMINANT-ALL-HELDOUT" if global_main else "NO-GLOBAL-LAW"}
    law["law_sealed"]=True; law["law_sha256"]=sha_obj(law)
    Path(a.out).parent.mkdir(parents=True,exist_ok=True); Path(a.out).write_text(json.dumps(law,indent=2,sort_keys=True)+"\n")
    print("P18_LAW_SEALED",law["law_sha256"],{t:law["targets"][t]["sealed_prediction"] for t in TARGETS})

def adjudicate(a):
    pre=json.loads(Path(a.precommit).read_text()); law=json.loads(Path(a.law).read_text()); res=parse_results(a.result)
    if set(res)!=set(HELDOUT): raise SystemExit("need all heldout families")
    if law.get("law_sealed") is not True or law.get("precommit_sha256")!=pre["precommit_sha256"]: raise SystemExit("LAW-SEAL-FAIL")
    out={"schema":"c3x-p18-transport-result-v1","scientific_stage":"C3X 0.7.0-G9.4-P18",
         "precommit_sha256":pre["precommit_sha256"],"law_sha256":law["law_sha256"],
         "targets":{}}
    any_coarse=False
    for t in TARGETS:
        famsum={f:summarize_rows(res[f]["rows"],t) for f in HELDOUT}
        pooled=summarize_rows([r for f in HELDOUT for r in res[f]["rows"]],t)
        pred=law["targets"][t]["sealed_prediction"]
        matches=sum(v["phase"]=="MAIN-DOMINANT" for v in famsum.values()) if pred=="MAIN-DOMINANT-ALL-HELDOUT" else 0
        pass_transport=(pred=="MAIN-DOMINANT-ALL-HELDOUT" and matches>=3 and pooled["phase"]=="MAIN-DOMINANT")
        nonnull={v["phase"] for v in famsum.values() if v["phase"]!="NULL"}
        heterogeneity=(pred=="MAIN-DOMINANT-ALL-HELDOUT" and matches<3) or len(nonnull)>=3
        any_coarse=any_coarse or any(v["counts"][bits]["coarse"] for v in famsum.values() for bits in ("10","01","11","ALL"))
        out["targets"][t]={"sealed_prediction":pred,"heldout_family_summary":famsum,"pooled_heldout":pooled,
                           "prediction_matches":matches,"transport_pass":pass_transport,
                           "material_heterogeneity_flag":heterogeneity}
    cross=all(out["targets"][t]["transport_pass"] for t in TARGETS)
    any_hetero=any(out["targets"][t]["material_heterogeneity_flag"] for t in TARGETS)
    if cross: verdict="CROSS-MATERIAL-GLOBAL-MAIN-LAW-TRANSPORTED"
    elif any_hetero: verdict="MATERIAL-CONDITIONED-CAUSAL-TOPOLOGY"
    else: verdict="GLOBAL-MAIN-LAW-NOT-ESTABLISHED"
    out["cross_version_global_law"]=cross; out["robust_wdl_changed_any_arm"]=any_coarse
    out["primary_verdict"]=verdict
    out["authority_ceiling"]="fresh P18-only exact worlds; discovery-law sealed before held-out intervention; dual-engine 300k selective TT-read transport"
    out["result_sha256"]=sha_obj(out)
    Path(a.out).parent.mkdir(parents=True,exist_ok=True); Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print("P18_RESULT",verdict,out["result_sha256"])

def main():
    ap=argparse.ArgumentParser(); sp=ap.add_subparsers(dest="cmd",required=True)
    s=sp.add_parser("sham-commit"); s.add_argument("--stage-a",required=True); s.add_argument("--binary",action="append",required=True); s.add_argument("--out",required=True)
    f=sp.add_parser("family-run"); f.add_argument("--precommit",required=True); f.add_argument("--binary",action="append",required=True); f.add_argument("--family",choices=FAMILIES,required=True); f.add_argument("--split",choices=("DISCOVERY","HELDOUT"),required=True); f.add_argument("--law"); f.add_argument("--out",required=True)
    l=sp.add_parser("seal-law"); l.add_argument("--precommit",required=True); l.add_argument("--result",action="append",required=True); l.add_argument("--out",required=True)
    a=sp.add_parser("adjudicate"); a.add_argument("--precommit",required=True); a.add_argument("--law",required=True); a.add_argument("--result",action="append",required=True); a.add_argument("--out",required=True)
    x=ap.parse_args(); {"sham-commit":sham_commit,"family-run":family_run,"seal-law":seal_law,"adjudicate":adjudicate}[x.cmd](x)
if __name__=="__main__": main()
