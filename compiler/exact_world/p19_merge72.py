#!/usr/bin/env python3
import argparse,hashlib,json
from collections import Counter
from pathlib import Path

EXPECTED=("KQQvKQ","KQRvKQ","KQQvKR","KQRvKR","KRBvKB","KRNvKB","KRBvKN","KRNvKN")
VERSION="c3x-p19-stage-a-v2-fine-exact-split"

def canon(o):
    return json.dumps(o,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()

def sha(o):
    return hashlib.sha256(canon(o)).hexdigest()

def fam_counts(cands):
    by={m:[] for m in EXPECTED}
    for c in cands:
        m=c["material_seed_name"]
        if m not in by: raise SystemExit(f"P19-MERGE72-UNKNOWN-MATERIAL {m}")
        by[m].append(c)
    return by

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--base",required=True)
    ap.add_argument("--supp-dir",required=True)
    ap.add_argument("--out",required=True)
    a=ap.parse_args()

    base=json.loads(Path(a.base).read_text())
    if base.get("stockfish_outcomes_consulted") is not False:
        raise SystemExit("P19-MERGE72-BASE-OUTCOME-LEAK")
    b=fam_counts(base["candidates"])
    for m in EXPECTED:
        if len(b[m])!=36 or Counter(x["side_to_move"] for x in b[m])!=Counter({"WHITE":18,"BLACK":18}):
            raise SystemExit(f"P19-MERGE72-BASE-CONSTITUTION {m}")

    root=Path(a.supp_dir)
    files=sorted(root.glob("p19-supp-*.json"))
    if len(files)!=8: raise SystemExit(f"P19-MERGE72-SUPP-FILE-COUNT {len(files)}/8")
    sparts={}
    for p in files:
        x=json.loads(p.read_text())
        if x.get("compiler_version")!=VERSION or x.get("stockfish_outcomes_consulted") is not False:
            raise SystemExit(f"P19-MERGE72-SUPP-INVALID {p.name}")
        mats={c["material_seed_name"] for c in x["candidates"]}
        if len(mats)!=1: raise SystemExit(f"P19-MERGE72-SUPP-MATERIAL {p.name}")
        m=next(iter(mats))
        if m in sparts: raise SystemExit(f"P19-MERGE72-SUPP-DUP {m}")
        if len(x["candidates"])!=36 or Counter(c["side_to_move"] for c in x["candidates"])!=Counter({"WHITE":18,"BLACK":18}):
            raise SystemExit(f"P19-MERGE72-SUPP-CONSTITUTION {m}")
        if x.get("freshness",{}).get("generation_index_offset")!=70000:
            raise SystemExit(f"P19-MERGE72-SUPP-OFFSET {m} {x.get('freshness')}")
        sparts[m]=x
    if set(sparts)!=set(EXPECTED): raise SystemExit("P19-MERGE72-SUPP-MATERIAL-SET")

    outc=[]; seen=set(); audit={}; component={}
    for m in EXPECTED:
        cs=b[m]+sparts[m]["candidates"]
        sides=Counter(c["side_to_move"] for c in cs)
        if len(cs)!=72 or sides!=Counter({"WHITE":36,"BLACK":36}):
            raise SystemExit(f"P19-MERGE72-COMBINED-CONSTITUTION {m} {len(cs)} {dict(sides)}")
        for c in cs:
            h=c["candidate_sha256"]
            if h in seen: raise SystemExit(f"P19-MERGE72-CANDIDATE-DUP {h}")
            seen.add(h)
        outc.extend(cs)
        audit[m]={
            "accepted":72,
            "accepted_by_side":{"WHITE":36,"BLACK":36},
            "base_pool":"p19-stage-a-fresh-squares-canonical-repair",
            "supplement_pool_sha256":sparts[m]["pool_sha256"]
        }
        component[m]={"base":"inherited-from-base-pool","supplement":sparts[m]["pool_sha256"]}

    payload={
      "schema":"c3x-p19-stage-a-pool-v3-symmetric-expanded",
      "scientific_stage":"C3X 0.7.0-G9.4-P19",
      "compiler_version":VERSION,
      "stockfish_outcomes_consulted":False,
      "freshness":{
        "base_generation_index_offset":60000,
        "supplement_generation_index_offset":70000,
        "historical_confirmatory_cells_reused":False
      },
      "constitution":dict(base["constitution"],symmetric_post_sham_reserve_expansion=True,
                          worlds_per_vertex=72,worlds_per_side_per_vertex=36),
      "squares":base["squares"],
      "world_authority":base["world_authority"],
      "base_pool_sha256":base["pool_sha256"],
      "component_pool_sha256":component,
      "audit_by_vertex":audit,
      "candidates":outc
    }
    payload["pool_sha256"]=sha(payload)
    if len(outc)!=576: raise SystemExit(f"P19-MERGE72-TOTAL {len(outc)}/576")
    Path(a.out).parent.mkdir(parents=True,exist_ok=True)
    Path(a.out).write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n")
    print("P19_STAGE_A_EXPANDED_PASS",len(outc),payload["pool_sha256"])

if __name__=="__main__":
    main()
