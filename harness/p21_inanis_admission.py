#!/usr/bin/env python3
import argparse,json,os,re,subprocess
from pathlib import Path

FENS=[
"r1bq1rk1/pp2bppp/2n1pn2/2pp4/3P4/2PBPN2/PPQN1PPP/R1B2RK1 w - - 4 9",
"2r2rk1/pp1b1ppp/2n1pn2/q2p4/3P4/2P1PN2/PPQN1PPP/2R2RK1 w - - 2 12",
"4rrk1/1pp2ppp/p1np1n2/4p3/2P1P3/1PN2P2/PB1N2PP/2RR2K1 w - - 1 18",
"r2q1rk1/pp1nbppp/2p1pn2/3p4/3P1B2/2NBPN2/PPQ2PPP/2R1K2R w K - 4 10"
]
CMP=("bestmove","score","pv","nodes")
CHANNELS={
 "TT_MAIN":("MASK_TT_MAIN","removal_tt_main","tt_main"),
 "PAWN_MAIN":("MASK_PAWN_MAIN","removal_pawn_main","pawn_main"),
 "PAWN_Q":("MASK_PAWN_Q","removal_pawn_q","pawn_q"),
}

def until(p,pred,limit=80000):
    out=[]
    for _ in range(limit):
        x=p.stdout.readline()
        if x=="": break
        x=x.rstrip("\n");out.append(x)
        if pred(x): break
    return out

def run(bin_path,fen,nodes,mode=None):
    env=os.environ.copy()
    if mode is None: env.pop("C3X_P21_MODE",None)
    else: env["C3X_P21_MODE"]=mode
    p=subprocess.Popen([bin_path],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,bufsize=1,env=env)
    p.stdin.write("uci\n");p.stdin.flush()
    pre=until(p,lambda x:x.strip()=="uciok")
    if not any(x.strip()=="uciok" for x in pre):
        raise RuntimeError("uciok missing\n"+"\n".join(pre[-80:]))
    opts="\n".join(pre)
    if re.search(r"^option name Threads\b",opts,re.M): p.stdin.write("setoption name Threads value 1\n")
    if re.search(r"^option name Hash\b",opts,re.M): p.stdin.write("setoption name Hash value 64\n")
    if re.search(r"^option name Search Noise\b",opts,re.M): p.stdin.write("setoption name Search Noise value false\n")
    if re.search(r"^option name Clear Hash\b",opts,re.M): p.stdin.write("setoption name Clear Hash\n")
    p.stdin.write("isready\n");p.stdin.flush()
    ready=until(p,lambda x:x.strip()=="readyok")
    if not any(x.strip()=="readyok" for x in ready):
        raise RuntimeError("readyok missing")
    p.stdin.write(f"position fen {fen}\ngo nodes {nodes}\n");p.stdin.flush()
    lines=pre+ready+until(p,lambda x:x.startswith("bestmove "))
    p.terminate()
    try: rest,_=p.communicate(timeout=3)
    except subprocess.TimeoutExpired:
        p.kill();rest,_=p.communicate(timeout=3)
    if rest: lines+=rest.splitlines()
    best=next((x for x in reversed(lines) if x.startswith("bestmove ")),None)
    infos=[x for x in lines if x.startswith("info ") and " score " in x and " pv " in x]
    tel=next((x for x in reversed(lines) if x.startswith("info string c3x_p21_inanis_v1 ")),None)
    if not best or not infos:
        raise RuntimeError("search receipt missing\n"+"\n".join(lines[-120:]))
    final=infos[-1]
    def g(pat):
        m=re.search(pat,final)
        return m.group(1) if m else None
    t={}
    if tel:
        for z in tel.split()[3:]:
            if "=" not in z: continue
            k,v=z.split("=",1)
            try:t[k]=int(v)
            except:t[k]=v
    return {
      "semantic":{
        "bestmove":best.split()[1],
        "score":g(r"\bscore ((?:cp|mate) -?\d+)"),
        "nodes":int(g(r"\bnodes (\d+)") or 0),
        "depth":int(g(r"\bdepth (\d+)") or 0),
        "pv":g(r"\bpv (.+)$")
      },
      "telemetry":t,
      "telemetry_line":tel
    }

def same(a,b):
    return all(a["semantic"].get(k)==b["semantic"].get(k) for k in CMP)

def main():
    ap=argparse.ArgumentParser()
    for x in ("baseline","instrument","removal_tt_main","removal_pawn_main","removal_pawn_q","instrument_manifest","out"):
        ap.add_argument("--"+x.replace("_","-"),dest=x,required=True)
    ap.add_argument("--nodes",type=int,default=100000)
    a=ap.parse_args()
    manifest=json.loads(Path(a.instrument_manifest).read_text())
    if manifest.get("source_commit")!="7ef903e8f86f7dcaf4fd04aeecb22711190d2a6d":
        raise SystemExit("SOURCE_LOCK_MANIFEST_FAIL")
    if not manifest.get("complete_scoped_mediation") or not manifest.get("native_rust"):
        raise SystemExit("STATIC_MEDIATION_FAIL")
    removals={
      "removal_tt_main":a.removal_tt_main,
      "removal_pawn_main":a.removal_pawn_main,
      "removal_pawn_q":a.removal_pawn_q
    }
    rows=[]
    agg={k:0 for k in (
      "tt_main_probes","tt_main_hits","tt_main_masks",
      "pawn_main_probes","pawn_main_hits","pawn_main_masks",
      "pawn_q_probes","pawn_q_hits","pawn_q_masks","pawn_other_probes"
    )}
    channel_eq={k:True for k in CHANNELS}
    channel_mask_engaged={k:True for k in CHANNELS}
    identity=True
    for i,fen in enumerate(FENS):
        b=run(a.baseline,fen,a.nodes)
        n=run(a.instrument,fen,a.nodes,"NATIVE")
        s=run(a.instrument,fen,a.nodes,"SHAM")
        ip=same(b,n) and same(n,s)
        identity=identity and ip
        if not s["telemetry_line"]:
            raise SystemExit("TELEMETRY_MISSING")
        for k in agg:
            agg[k]+=int(s["telemetry"].get(k,0))
        channel_rows={}
        for ch,(mode,rkey,prefix) in CHANNELS.items():
            m=run(a.instrument,fen,a.nodes,mode)
            r=run(removals[rkey],fen,a.nodes)
            eq=same(m,r)
            masks=int(m["telemetry"].get(prefix+"_masks",0))
            hits=int(m["telemetry"].get(prefix+"_hits",0))
            channel_eq[ch]=channel_eq[ch] and eq
            channel_mask_engaged[ch]=channel_mask_engaged[ch] and masks>0 and hits>0
            channel_rows[ch]={
              "mode":mode,
              "semantic_removal_equivalence_pass":eq,
              "mask_hit_count":masks,
              "raw_hit_count":hits,
              "mask_semantic":m["semantic"],
              "removal_semantic":r["semantic"]
            }
        rows.append({
          "fen_index":i,"fen":fen,
          "native_sham_identity_pass":ip,
          "baseline":b["semantic"],"native":n["semantic"],"sham":s["semantic"],
          "sham_telemetry":s["telemetry"],
          "channels":channel_rows
        })
        print("P21_INANIS_ADMISSION",i,ip,{k:v["semantic_removal_equivalence_pass"] for k,v in channel_rows.items()},flush=True)

    dynamic={
      "TT_MAIN":agg["tt_main_probes"]>0 and agg["tt_main_hits"]>0,
      "PAWN_MAIN":agg["pawn_main_probes"]>0 and agg["pawn_main_hits"]>0,
      "PAWN_Q":agg["pawn_q_probes"]>0 and agg["pawn_q_hits"]>0,
    }
    phase_leak_free=agg["pawn_other_probes"]==0
    verdict=identity and all(channel_eq.values()) and all(channel_mask_engaged.values()) and all(dynamic.values()) and phase_leak_free
    out={
      "schema":"c3x-p21-inanis-channel-admission-v1",
      "scientific_stage":"C3X 0.7.0-G9.4-P21",
      "engine":"inanis",
      "source_commit":"7ef903e8f86f7dcaf4fd04aeecb22711190d2a6d",
      "language":"Rust",
      "nodes_per_fen":a.nodes,
      "fens":len(FENS),
      "native_sham_noninterference":identity,
      "semantic_removal_equivalence_by_channel":channel_eq,
      "masked_hit_engagement_by_channel":channel_mask_engaged,
      "dynamic_engagement_pass_by_channel":dynamic,
      "dynamic_engagement":agg,
      "phase_tag_leak_free":phase_leak_free,
      "structural_zero":{"QSEARCH×SEARCH_TT":True},
      "admitted_channels":["MAIN×SEARCH_TT","MAIN×PAWN_EVAL_CACHE","QSEARCH×PAWN_EVAL_CACHE"] if verdict else [],
      "authority":"CHANNEL_FACTORIZED_CAUSAL_ADMISSION" if verdict else "HOLD",
      "rows":rows,
      "instrument_manifest":manifest,
      "verdict":"PASS" if verdict else "HOLD"
    }
    Path(a.out).parent.mkdir(parents=True,exist_ok=True)
    Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"verdict":out["verdict"],"dynamic":dynamic,"equivalence":channel_eq,"mask_engaged":channel_mask_engaged,"aggregate":agg},sort_keys=True))
    if not verdict:
        raise SystemExit("P21-INANIS-CHANNEL-ADMISSION-HOLD")

if __name__=="__main__":
    main()
