#!/usr/bin/env python3
"""Outcome-blind side-parallel accelerator for the frozen P21 pawnless core.

It preserves candidate generation, world predicate, tau4 semantics, namespace,
offset and candidate hashes. It only evaluates one side-to-move per process.
"""
import argparse,json,time
from pathlib import Path
import chess
import p19_compile as base
from p20_tau4_fast import tau4_fast

VERSION="c3x-p21-core-v1"
OFFSET=140000
base.VERSION=VERSION
base.OFFSET=OFFSET
base.tau4=tau4_fast

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--material",choices=tuple(base.VERTICES),required=True)
    ap.add_argument("--side",choices=("WHITE","BLACK"),required=True)
    ap.add_argument("--target",type=int,default=24)
    ap.add_argument("--max-generated",type=int,default=1200)
    ap.add_argument("--out",required=True)
    a=ap.parse_args()
    square,vertex,pieces=base.VERTICES[a.material]
    side=chess.WHITE if a.side=="WHITE" else chess.BLACK
    accepted=[];audited=0;world_pass=0
    for i in range(a.max_generated):
        b=base.candidate(a.material,pieces,side,i)
        if b is None:continue
        audited+=1
        try:w=base.world(b)
        except RuntimeError as e:
            print("WORLD_QUERY_RETRY_EXHAUSTED",a.material,a.side,e,flush=True);continue
        time.sleep(.04)
        if w is None:continue
        world_pass+=1;t=tau4_fast(b)
        if t["overflow"] or not t["tau4"]:continue
        x={"compiler_version":VERSION,"generation_index":OFFSET+i,"square":square,"vertex":vertex,
           "material_seed_name":a.material,"material_signature":base.sig(b),"side_to_move":a.side,
           "fen":b.fen(),"legal_move_count":b.legal_moves.count(),"world":w,"tau4":t}
        x["candidate_sha256"]=base.h(base.canon(x));accepted.append(x)
        print("P21_CORE_SIDE_ACCEPT",a.material,a.side,len(accepted),x["candidate_sha256"][:12],flush=True)
        if len(accepted)>=a.target:break
    if len(accepted)!=a.target:raise SystemExit(f"P21_CORE_SIDE_SHORTFALL {a.material} {a.side} {len(accepted)}/{a.target}")
    out={"schema":"c3x-p21-core-side-part-v1","scientific_stage":"C3X 0.7.0-G9.4-P21",
         "compiler_version":VERSION,"material":a.material,"square":square,"vertex":vertex,
         "side":a.side,"target":a.target,"engine_outcomes_consulted":False,
         "freshness":{"generation_index_offset":OFFSET,"p20_cells_reused":False},
         "audit":{"audited":audited,"world_split_pass":world_pass,"accepted":len(accepted)},
         "candidates":accepted}
    out["part_sha256"]=base.h(base.canon(out))
    Path(a.out).parent.mkdir(parents=True,exist_ok=True);Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print("P21_CORE_SIDE_PASS",a.material,a.side,out["part_sha256"])

if __name__=="__main__":main()
