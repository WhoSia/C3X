#!/usr/bin/env python3
from __future__ import annotations
import argparse,glob,json,statistics,sys
from pathlib import Path
import chess

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"));sys.path.insert(0,str(ROOT/"harness"))
import p32_event_court as p32
import g10_p21_phase_e_carrier as carrier

def load(p): return json.loads(Path(p).read_text())
def jfiles(root):
    out=[]
    for p in Path(root).rglob("*.json"):
        try: out.append((p,load(p)))
        except: pass
    return out
def posmap(obj,prefix):
    out={}
    for z in obj.get("positions",[]):
        pid=f"{prefix}:{z['source_id']}:{z['trajectory_hash'][:12]}"
        out[pid]=z
    return out
def mat_imbalance(fen):
    b=chess.Board(fen);v={1:1,2:3,3:3,4:5,5:9,6:0}
    w=sum(v[p.piece_type] for p in b.piece_map().values() if p.color)
    k=sum(v[p.piece_type] for p in b.piece_map().values() if not p.color)
    return abs(w-k), bool(b.is_check())
def tactical(pair):
    cap=bool(pair["A"].get("capture") or pair["B"].get("capture"))
    chk=bool(pair["A"].get("check") or pair["B"].get("check"))
    if cap and chk:return "CAPTURE_AND_CHECK"
    if chk:return "ANY_CHECK"
    if cap:return "ANY_CAPTURE"
    return "QUIET_QUIET"
def fam_event_ok(fam,e):
    if fam=="MOVE_ORDER": return e.get("class")=="MOVE_ORDER_SEED"
    if fam=="CUTOFF": return e.get("class")=="CUTOFF"
    return False
def profile(binary,protocol,chain,pair,family,root):
    boards={"TARGET":chain["target_fen"],"SUBSET":chain["subset_fen"],"SHAM":chain["sham_fen"]}
    A=pair["A"]["uci"];B=pair["B"]["uci"];all_events=[];stable=True
    for arm,fen in boards.items():
        for slot,move in (("A",A),("B",B)):
            reps=[]
            for rep in range(2):
                cp,events=carrier.run(binary,protocol,fen,move,family,Path(root)/f"{arm}-{slot}-{rep}")
                ev=[e for e in events if int(e.get("ply",999))<=8 and fam_event_ok(family,e)]
                sig=[(e.get("scope"),e.get("class"),int(e.get("ply",0)),int(e.get("depth",0))) for e in ev]
                reps.append((cp,ev,sig))
            stable &= reps[0][0] is not None and reps[0][0]==reps[1][0] and reps[0][2]==reps[1][2]
            for e in reps[0][1]:
                q=dict(e);q["_arm"]=arm;q["_slot"]=slot;all_events.append(q)
    scopes=[e.get("scope") for e in all_events]
    main=sum(x=="MAIN" for x in scopes);qs=sum(x=="QSEARCH" for x in scopes)
    den=main+qs
    ac=sum(e["_slot"]=="A" for e in all_events);bc=sum(e["_slot"]=="B" for e in all_events);sd=ac+bc
    qshare=qs/len(all_events) if all_events else 0.0
    total=len(all_events)
    def abuck(n):return "<=63" if n<=63 else "64-255" if n<=255 else "256-1023" if n<=1023 else "1024+"
    def qb(x):return "0" if x==0 else "(0,.1]" if x<=.1 else "(.1,.3]" if x<=.3 else ">.3"
    return {
      "feature_repeatable":bool(stable),
      "family_event_count_total":total,
      "family_event_count_target":sum(e["_arm"]=="TARGET" for e in all_events),
      "family_event_count_subset":sum(e["_arm"]=="SUBSET" for e in all_events),
      "family_event_count_sham":sum(e["_arm"]=="SHAM" for e in all_events),
      "event_ply_median":statistics.median([int(e["ply"]) for e in all_events]) if all_events else -1,
      "event_depth_median":statistics.median([int(e["depth"]) for e in all_events]) if all_events else -1,
      "event_scope_balance":(main-qs)/den if den else 0.0,
      "candidate_side_event_imbalance":abs(ac-bc)/sd if sd else 0.0,
      "base_activity_bucket":abuck(total),
      "base_qshare_bucket":qb(qshare)
    }
def boundary(boards):
    gs={k:int(v["gap_cp_abs"]) for k,v in boards.items()}
    return {
      "base_target_gap_cp":gs["TARGET"],"base_subset_gap_cp":gs["SUBSET"],"base_sham_gap_cp":gs["SHAM"],
      "base_max_gap_cp":max(gs.values()),"base_min_slack_to_50cp":min(abs(50-x) for x in gs.values()),
      "base_support_pattern":"".join("1" if boards[k]["supported"] else "0" for k in ("TARGET","SUBSET","SHAM"))
    }
def relation_family(chain):
    xs=chain.get("target_atoms") or []
    return xs[0] if len(xs)==1 else "MULTI" if xs else "NONE"
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--p20-base",required=True);ap.add_argument("--p19-projection",required=True)
    ap.add_argument("--p21-chain",required=True);ap.add_argument("--p21-projection",required=True);ap.add_argument("--p21-carrier",required=True)
    ap.add_argument("--build-dir",required=True);ap.add_argument("--shard",type=int,required=True);ap.add_argument("--shards",type=int,required=True);ap.add_argument("--out-dir",required=True)
    a=ap.parse_args();out=Path(a.out_dir);out.mkdir(parents=True,exist_ok=True)
    p19=posmap(load(a.p19_projection),"p19");p21=posmap(load(a.p21_projection),"p21")
    tasks=[]
    for p,o in jfiles(a.p20_base):
        if o.get("schema")!="c3x-g10-p20-class-screen-row-v1":continue
        for fam in ("MOVE_ORDER","CUTOFF"):
            tasks.append(("P20",o["case_id"]+"||"+fam,o,fam))
    chain={o["position_id"]:o for _,o in jfiles(a.p21_chain) if o.get("schema")=="c3x-g10-p21-phase-e-chain-world-v1"}
    gate=load(a.p21_carrier)
    for c in gate["carriers"]:
        z=chain[c["position_id"]]
        tasks.append(("P21",c["position_id"]+"||"+c["engine"]+"||"+c["family"],(z,c),c["family"]))
    tasks.sort(key=lambda x:x[1])
    done=0
    for idx,(origin,uid,obj,fam) in enumerate(tasks):
        if idx%a.shards!=a.shard:continue
        if origin=="P20":
            o=obj;engine=o["engine"];pid=o["position_id"];chain0=o["chain"];pair=o["pair"];src=o["source_id"]
            boards=o["arms"]["BASE"]["boards"];ctx=o["raw"];world=p19.get(pid)
            if world is None: raise SystemExit(f"P22_P19_WORLD {pid}")
            phase=ctx["phase"];branch=ctx["branching"];tact=ctx["tactical_surface"];rtype=ctx.get("relation_atom_family",relation_family(chain0));ctype=ctx.get("chain_type",chain0.get("type","NA"))
        else:
            z,c=obj;engine=c["engine"];pid=z["position_id"];chain0=z["chain"];pair=z["pair"];src=z["source_id"]
            boards=z["engines"][engine]["boards"];ctx=z["context"];world=p21.get(pid)
            if world is None: raise SystemExit(f"P22_P21_WORLD {pid}")
            phase=ctx["phase"];branch=ctx["branching"];tact=ctx["tactical_surface"];rtype=relation_family(chain0);ctype=chain0.get("type","NA")
        b=carrier.find_binary(a.build_dir,engine);protocol=p32.protocol_for(engine)
        dynamic=profile(b,protocol,chain0,pair,fam,out/f".private-{idx}")
        mi,inch=mat_imbalance(world["fen"])
        row={
          "schema":"c3x-g10-p22-preintervention-profile-v1","stage":"C3X 0.10.0-G10-P22","origin":origin,
          "uid":uid,"source_id":src,"position_id":pid,"engine":engine,"family":fam,
          **boundary(boards),**dynamic,
          "phase":phase,"legal_branching":branch,"tactical_surface":tact,"material_imbalance":mi,"in_check":inch,
          "candidate_tactical_mode":tactical(pair),"relation_atom_family":rtype,"chain_type":ctype,
          "family_x_engine":fam+"|"+engine,
          "activation_label_present":False
        }
        (out/f"{idx:03d}.json").write_text(json.dumps(row,indent=2,sort_keys=True)+"\n");done+=1
    print("P22_PROFILE_SHARD",a.shard,"ROWS",done,"TOTAL_TASKS",len(tasks))
if __name__=="__main__":main()
