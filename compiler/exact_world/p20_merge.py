#!/usr/bin/env python3
import argparse,hashlib,json
from collections import Counter
from pathlib import Path

EXPECTED=("KQQvKQ","KQRvKQ","KQQvKR","KQRvKR","KRBvKB","KRNvKB","KRBvKN","KRNvKN")
VERSION="c3x-p20-r2-stage-a-v1"

def canon(o):
    return json.dumps(o,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--parts",required=True)
    ap.add_argument("--out",required=True)
    a=ap.parse_args()
    root=Path(a.parts)
    files=sorted(root.rglob("p20-stage-a-*.json"))
    if len(files)!=8: raise SystemExit(f"P20_PART_COUNT {len(files)}/8")
    by={}; seen=set(); allc=[]; audits={}
    template=None
    for p in files:
        x=json.loads(p.read_text())
        if x.get("scientific_stage")!="C3X 0.7.0-G9.4-P20-R2": raise SystemExit("P20_STAGE_MISMATCH")
        if x.get("compiler_version")!=VERSION: raise SystemExit("P20_VERSION_MISMATCH")
        if x.get("stockfish_outcomes_consulted") is not False: raise SystemExit("P20_OUTCOME_LEAK")
        cs=x["candidates"]
        mats={c["material_seed_name"] for c in cs}
        if len(mats)!=1: raise SystemExit("P20_PART_MATERIAL_SET")
        m=next(iter(mats))
        if m in by: raise SystemExit("P20_PART_DUP "+m)
        sides=Counter(c["side_to_move"] for c in cs)
        if len(cs)!=72 or sides!=Counter({"WHITE":36,"BLACK":36}):
            raise SystemExit(f"P20_PART_CONSTITUTION {m} {len(cs)} {dict(sides)}")
        if any(int(c["generation_index"])<80000 for c in cs):
            raise SystemExit("P20_OFFSET_FAIL "+m)
        for c in cs:
            h=c["candidate_sha256"]
            if h in seen: raise SystemExit("P20_CANDIDATE_DUP "+h)
            seen.add(h)
        by[m]=x; allc.extend(cs); audits[m]=x["audit_by_vertex"][m]
        if template is None: template=x
    if set(by)!=set(EXPECTED): raise SystemExit("P20_MATERIAL_SET")
    out={
      "schema":"c3x-p20-r2-stage-a-pool-v1",
      "scientific_stage":"C3X 0.7.0-G9.4-P20-R2",
      "compiler_version":VERSION,
      "stockfish_outcomes_consulted":False,
      "cross_engine_transport_outcomes_consulted":False,
      "freshness":{
        "generation_index_offset":80000,
        "p19_selected_cells_reused":False,
        "p19_generation_offsets_reused":False
      },
      "constitution":dict(template["constitution"],worlds_per_vertex=72,worlds_per_side_per_vertex=36),
      "squares":template["squares"],
      "world_authority":template["world_authority"],
      "component_pool_sha256":{m:by[m]["pool_sha256"] for m in EXPECTED},
      "audit_by_vertex":audits,
      "candidates":allc
    }
    out["pool_sha256"]=hashlib.sha256(canon(out)).hexdigest()
    if len(allc)!=576: raise SystemExit(f"P20_TOTAL {len(allc)}/576")
    Path(a.out).parent.mkdir(parents=True,exist_ok=True)
    Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print("P20_R2_STAGE_A_PASS",len(allc),out["pool_sha256"])

if __name__=="__main__":
    main()
