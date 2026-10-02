#!/usr/bin/env python3
from __future__ import annotations
import argparse,json
from collections import Counter,defaultdict
from pathlib import Path

BOUNDS=("UPPER","LOWER")

def load(p): return json.loads(Path(p).read_text())

def collect(root,schema):
    out=[]
    for p in Path(root).rglob("*.json"):
        try:x=load(p)
        except Exception:continue
        if x.get("schema")==schema: out.append(x)
    return out

def root_uci(board):
    return (board.get("native") or {}).get("bestmove")

def rec(board,bound):
    return ((board.get("bounds") or {}).get(bound) or {}).get("record")

def troot_uci(record):
    if not record:return None
    return ((record.get("t_only_root") or {}).get("uci"))

def bridge_levels(b0,bx,bs,bsub,bound,A,B):
    pair={A,B}
    r0=rec(b0,bound); rx=rec(bx,bound)
    l0=True
    l1=bool(r0 and rx)
    n0=root_uci(b0); nx=root_uci(bx)
    l2=bool(l1 and n0 in pair and nx in pair and n0!=nx)
    t0=troot_uci(r0); tx=troot_uci(rx)
    l3=bool(l2 and t0 in pair and tx in pair and t0==tx)
    sham_rep=False
    rs=rec(bs,bound); ns=root_uci(bs)
    if l3 and rs and n0 in pair and ns in pair and n0!=ns:
        ts=troot_uci(rs)
        sham_rep=bool(ts in pair and ts==t0)
    l4=bool(l3 and not sham_rep)

    # subset bridge reproduction under the same frozen bridge grammar
    rsub=rec(bsub,bound); nsub=root_uci(bsub); tsub=troot_uci(rsub)
    subset_l1=bool(r0 and rsub)
    subset_l2=bool(subset_l1 and n0 in pair and nsub in pair and n0!=nsub)
    subset_l3=bool(subset_l2 and t0 in pair and tsub in pair and t0==tsub)
    subset_sham=False
    if subset_l3 and rs and n0 in pair and ns in pair and n0!=ns:
        ts=troot_uci(rs)
        subset_sham=bool(ts in pair and ts==t0)
    subset_bridge=bool(subset_l3 and not subset_sham)
    l5=bool(l4 and not subset_bridge)
    return [l0,l1,l2,l3,l4,l5]

def bound_vec(chain,board):
    return tuple(int(q in set(chain["board_topology"][board]["available_bounds"])) for q in BOUNDS)

def xor_vec(a,b):
    return tuple(int(x!=y) for x,y in zip(a,b))

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--opportunity",required=True)
    ap.add_argument("--factorial",required=True)
    ap.add_argument("--out",required=True)
    a=ap.parse_args()

    opp=collect(a.opportunity,"c3x-g10-p10-opportunity-world-v1")
    fac=collect(a.factorial,"c3x-g95-p16-factorial-world-v1")
    opp_by={x["case_id"]:x for x in opp}
    fac_by={x["case_id"]:x for x in fac}

    ladder=Counter()
    strict={f"L{i}_NOT_L{i+1}":[] for i in range(5)}
    l6_not_l7=[]
    consistency=[]
    units=0

    for cid,w in fac_by.items():
        if not w.get("active"):continue
        pair=w["pair"];A=pair["A"]["uci"];B=pair["B"]["uci"]
        for ch in w.get("chains",[]):
            boards=ch["boards"]
            for bound in BOUNDS:
                lv=bridge_levels(boards["B0"],boards["TARGET"],boards["SHAM"],boards["SUBSET"],bound,A,B)
                units+=1
                for i,v in enumerate(lv):
                    ladder[f"L{i}"]+=int(v)
                for i in range(5):
                    if lv[i] and not lv[i+1] and len(strict[f"L{i}_NOT_L{i+1}"])<8:
                        strict[f"L{i}_NOT_L{i+1}"].append({
                          "case_id":cid,"engine":w["engine"],"position_id":w["position_id"],
                          "chain_id":ch["chain_id"],"bound":bound
                        })
                l6=any(r.get("kind")=="MINIMAL_FULL_BRIDGE" and r.get("bound")==bound for r in ch.get("bridge_records",[]))
                ladder["L6"]+=int(l6)
                if l6!=lv[5] and len(consistency)<20:
                    consistency.append({"case_id":cid,"chain_id":ch["chain_id"],"bound":bound,"L5":lv[5],"L6":l6})
                # P9 had no replicated family-member authority; every L6 is a witness against L6=>L7 converse.
                if l6 and len(l6_not_l7)<8:
                    l6_not_l7.append({"case_id":cid,"engine":w["engine"],"position_id":w["position_id"],"chain_id":ch["chain_id"],"bound":bound})
    ladder["L7"]=0

    # Engine x board-edit opportunity square.
    rows=[]
    for w in opp:
        if not w.get("active"):continue
        for ch in w.get("chains",[]):
            rows.append((w["position_id"],w["source_id"],w["engine"],ch["chain_id"],ch))
    bypc=defaultdict(list)
    for pos,src,e,cid,ch in rows:bypc[(pos,src,cid)].append((e,ch))
    squares=0; noncomm=0; pair_stats=defaultdict(lambda:[0,0]); witnesses=[]
    for (pos,src,cid),ers in bypc.items():
        ers=sorted(ers)
        for i in range(len(ers)):
            for j in range(i+1,len(ers)):
                e1,c1=ers[i];e2,c2=ers[j]
                d0=xor_vec(bound_vec(c1,"B0"),bound_vec(c2,"B0"))
                dt=xor_vec(bound_vec(c1,"TARGET"),bound_vec(c2,"TARGET"))
                squares+=1
                nc=d0!=dt
                noncomm+=int(nc)
                k="|".join(sorted((e1,e2)))
                pair_stats[k][1]+=1;pair_stats[k][0]+=int(nc)
                if nc and len(witnesses)<20:
                    witnesses.append({
                      "position_id":pos,"source_id":src,"chain_id":cid,
                      "engine_pair":[e1,e2],"engine_difference_B0":list(d0),"engine_difference_TARGET":list(dt),
                      "B0_vectors":{e1:list(bound_vec(c1,"B0")),e2:list(bound_vec(c2,"B0"))},
                      "TARGET_vectors":{e1:list(bound_vec(c1,"TARGET")),e2:list(bound_vec(c2,"TARGET"))}
                    })

    out={
      "schema":"c3x-g10-p10-ladder-transport-v1",
      "status":"DEVELOPMENT_ONLY_NO_CONFIRMATORY_AUTHORITY",
      "ladder":{
        "unit_count":units,
        "counts":dict(ladder),
        "strict_converse_failure_witnesses":strict,
        "L6_NOT_L7_witnesses":l6_not_l7,
        "implementation_consistency_mismatches_L5_vs_L6":consistency,
        "all_forward_implications_respected":len(consistency)==0
      },
      "engine_board_opportunity_interaction":{
        "engine_board_squares":squares,
        "noncommuting_squares":noncomm,
        "noncommuting_fraction":noncomm/squares if squares else None,
        "engine_pair_noncommuting_fraction":{k:(v[0]/v[1] if v[1] else None) for k,v in sorted(pair_stats.items())},
        "witnesses":witnesses,
        "interpretation":"A noncommuting square means the engine-to-engine opportunity difference changes after the same board edit; this is an engine-conditioned board-opportunity interaction, not a causal operator algebra claim."
      },
      "firewall":{
        "factorial_outcomes_used":"DEVELOPMENT_ONLY",
        "opportunity_definition_refit":False,
        "p9_geometry_refit":False,
        "confirmatory_authority":False
      }
    }
    Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print("G10_P10_LADDER_TRANSPORT_PASS")
    print("LADDER",dict(ladder))
    print("STRICT", {k:len(v) for k,v in strict.items()}, "L6_NOT_L7",len(l6_not_l7),"CONSISTENCY",len(consistency))
    print("ENGINE_BOARD",squares,noncomm,out["engine_board_opportunity_interaction"]["noncommuting_fraction"])
    print("PAIR_INTERACTION",out["engine_board_opportunity_interaction"]["engine_pair_noncommuting_fraction"])

if __name__=="__main__":main()
