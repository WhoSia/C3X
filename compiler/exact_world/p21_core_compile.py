#!/usr/bin/env python3
"""P21 pawnless-core exact-world constitution.

Disjoint from P20 by compiler namespace and generation offset.  It preserves
the validated P19/P20 pawnless tau4 semantics via the exact-semantic fast
implementation, but has no access to P20/P21 engine outcomes.
"""
import json,sys
from pathlib import Path
import p19_compile as base
from p20_tau4_fast import tau4_fast

VERSION="c3x-p21-core-v1"
OFFSET=140000
base.VERSION=VERSION
base.OFFSET=OFFSET
base.tau4=tau4_fast

def out_path(argv):
    for i,x in enumerate(argv):
        if x=="--out" and i+1<len(argv): return Path(argv[i+1])
    raise SystemExit("P21_CORE_OUT_MISSING")

if __name__=="__main__":
    p=out_path(sys.argv)
    base.main()
    x=json.loads(p.read_text())
    x["schema"]="c3x-p21-core-part-v1"
    x["scientific_stage"]="C3X 0.7.0-G9.4-P21"
    x["compiler_version"]=VERSION
    x["stockfish_outcomes_consulted"]=False
    x["cross_engine_outcomes_consulted"]=False
    x["freshness"]={
      "generation_index_offset":OFFSET,
      "p20_cells_reused":False,
      "p20_generation_offsets_reused":False
    }
    x["constitution"]["lane"]="PAWNLESS_CORE"
    x["constitution"]["tau4_semantics"]="P19_FROZEN_EXACT"
    x["constitution"]["tau4_implementation"]="P20_FAST_EXACT_SEMANTIC_V1"
    x["pool_sha256"]=base.h(base.canon({k:v for k,v in x.items() if k!="pool_sha256"}))
    p.write_text(json.dumps(x,indent=2,sort_keys=True)+"\n")
    print("P21_CORE_PART_PASS",len(x["candidates"]),x["pool_sha256"])
