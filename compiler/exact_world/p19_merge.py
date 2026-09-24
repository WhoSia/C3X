#!/usr/bin/env python3
import argparse,hashlib,json
from pathlib import Path

EXPECTED=("KQQvKQ","KQRvKQ","KQQvKR","KQRvKR","KRBvKB","KRNvKB","KRBvKN","KRNvKN")
VERSION="c3x-p19-stage-a-v2-fine-exact-split"

def canon(o):
    return json.dumps(o,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()

def sha(o):
    return hashlib.sha256(canon(o)).hexdigest()

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--dir",required=True)
    ap.add_argument("--out",required=True)
    a=ap.parse_args()
    root=Path(a.dir)
    files=sorted(root.glob("p19-stage-a-*.json"))
    if len(files)!=len(EXPECTED):
        raise SystemExit(f"P19-MERGE-FILE-COUNT {len(files)}/{len(EXPECTED)}")
    parts={}
    for p in files:
        x=json.loads(p.read_text())
        if x.get("compiler_version")!=VERSION:
            raise SystemExit(f"P19-MERGE-VERSION {p.name} {x.get('compiler_version')}")
        if x.get("stockfish_outcomes_consulted") is not False:
            raise SystemExit(f"P19-MERGE-OUTCOME-LEAK {p.name}")
        mats={c["material_seed_name"] for c in x.get("candidates",[])}
        if len(mats)!=1:
            raise SystemExit(f"P19-MERGE-MATERIAL-CARDINALITY {p.name} {sorted(mats)}")
        mat=next(iter(mats))
        if mat in parts:
            raise SystemExit(f"P19-MERGE-DUPLICATE {mat}")
        parts[mat]=x
    if set(parts)!=set(EXPECTED):
        raise SystemExit(f"P19-MERGE-MATERIAL-SET {sorted(parts)}")
    candidates=[]
    audit={}
    component_sha={}
    seen=set()
    for mat in EXPECTED:
        x=parts[mat]
        cs=x["candidates"]
        if len(cs)!=18:
            raise SystemExit(f"P19-MERGE-CANDIDATE-COUNT {mat} {len(cs)}")
        sides={}
        for c in cs:
            sides[c["side_to_move"]]=sides.get(c["side_to_move"],0)+1
            h=c["candidate_sha256"]
            if h in seen:
                raise SystemExit(f"P19-MERGE-CANDIDATE-DUP {h}")
            seen.add(h)
        if sides!={"WHITE":9,"BLACK":9}:
            raise SystemExit(f"P19-MERGE-SIDE-BALANCE {mat} {sides}")
        candidates.extend(cs)
        audit.update(x["audit_by_vertex"])
        component_sha[mat]=x["pool_sha256"]
    template=parts[EXPECTED[0]]
    payload={
        "schema":"c3x-p19-stage-a-pool-v2-merged",
        "scientific_stage":"C3X 0.7.0-G9.4-P19",
        "compiler_version":VERSION,
        "stockfish_outcomes_consulted":False,
        "freshness":template["freshness"],
        "constitution":dict(template["constitution"],parallel_vertex_merge=True),
        "squares":template["squares"],
        "world_authority":template["world_authority"],
        "component_pool_sha256":component_sha,
        "audit_by_vertex":audit,
        "candidates":candidates
    }
    payload["pool_sha256"]=sha(payload)
    if len(candidates)!=144:
        raise SystemExit(f"P19-MERGE-TOTAL {len(candidates)}/144")
    Path(a.out).parent.mkdir(parents=True,exist_ok=True)
    Path(a.out).write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n")
    print("P19_STAGE_A_MERGE_PASS",len(candidates),payload["pool_sha256"])

if __name__=="__main__":
    main()
