#!/usr/bin/env python3
import argparse,json,subprocess
from pathlib import Path

LOCKS={
 "berserk":"32628515050b83805bab4afa1026dd2bcaa93f55",
 "ethereal":"0e47e9b67f345c75eb965d9fb3e2493b6a11d09a",
 "inanis":"7ef903e8f86f7dcaf4fd04aeecb22711190d2a6d",
 "lc0":"1227b4c8c23375f4011831f4d7496d1551f85145",
}

def read(root,rel):
    return (Path(root)/rel).read_text(errors="replace")

def git_head(root):
    return subprocess.check_output(["git","-C",root,"rev-parse","HEAD"],text=True).strip()

def split_count(text,marker,needle):
    if marker not in text:
        return {"before":text.count(needle),"after":0}
    a,b=text.split(marker,1)
    return {"before":a.count(needle),"after":b.count(needle)}

def audit_berserk(root):
    s=read(root,"src/search.c")
    c=split_count(s,"int Quiesce(","TTProbe(")
    return {
      "language":"C",
      "search_family":"negamax/PVS + quiescence + TT + NNUE",
      "direct_probe_token":"TTProbe(",
      "main_region_probe_calls":c["before"],
      "qsearch_region_probe_calls":c["after"],
      "main_semantic_evidence":all(x in s for x in ["ttScore","ttDepth","ttBound","hashMove"]),
      "qsearch_semantic_evidence":"TT score pruning" in s and c["after"]>0,
      "readiness_class":"STRUCTURALLY_CLOSE_MAIN_AND_QSEARCH",
      "admission_status":"NOT_ADMITTED_STATIC_READINESS_ONLY"
    }

def audit_ethereal(root):
    s=read(root,"src/search.c")
    c=split_count(s,"int qsearch(","tt_probe(")
    return {
      "language":"C",
      "search_family":"alpha-beta/PVS + quiescence + TT",
      "direct_probe_token":"tt_probe(",
      "main_region_probe_calls":c["before"],
      "qsearch_region_probe_calls":c["after"],
      "main_semantic_evidence":all(x in s for x in ["ttValue","ttDepth","ttBound","ttMove"]),
      "qsearch_semantic_evidence":"Probe the Transposition Table" in s and c["after"]>0,
      "readiness_class":"STRUCTURALLY_CLOSE_MAIN_AND_QSEARCH",
      "admission_status":"NOT_ADMITTED_STATIC_READINESS_ONLY"
    }

def audit_inanis(root):
    s=read(root,"src/engine/search/runner.rs")
    q=read(root,"src/engine/qsearch/runner.rs")
    return {
      "language":"Rust",
      "search_family":"negamax/alpha-beta + quiescence + TT",
      "direct_probe_token":"context.ttable.get(",
      "main_region_probe_calls":s.count("context.ttable.get("),
      "qsearch_region_probe_calls":q.count("context.ttable.get("),
      "main_semantic_evidence":all(x in s for x in ["hash_move","TTableScoreType","tt_entry_found"]),
      "qsearch_semantic_evidence":"context.ttable.get(" in q,
      "readiness_class":"PARTIAL_TOPOLOGY_MAIN_TT_QSEARCH_NOT_HOMOLOGOUS" if "context.ttable.get(" not in q else "STRUCTURALLY_CLOSE_MAIN_AND_QSEARCH",
      "admission_status":"NOT_ADMITTED_STATIC_READINESS_ONLY"
    }

def audit_lc0(root):
    dag=Path(root)/"src/search/dag_classic/search.cc"
    classic=Path(root)/"src/search/classic/search.cc"
    mem=Path(root)/"src/neural/memcache.cc"
    return {
      "language":"C++",
      "search_family":"neural-network guided tree/DAG search",
      "dag_search_present":dag.exists(),
      "classic_search_present":classic.exists(),
      "neural_memcache_present":mem.exists(),
      "readiness_class":"ARCHITECTURE_ABSTRACTION_REQUIRED",
      "admission_status":"NOT_ADMITTED_NO_STOCKFISH_TT_HOMOLOGY",
      "reason":"Tree/DAG state and neural-evaluation cache cannot be equated prospectively with alpha-beta TT semantic reads."
    }

def main():
    ap=argparse.ArgumentParser()
    for k in LOCKS: ap.add_argument("--"+k,required=True)
    ap.add_argument("--build-receipt")
    ap.add_argument("--out",required=True)
    a=ap.parse_args()
    roots={k:getattr(a,k) for k in LOCKS}
    out={"schema":"c3x-p19-heterogeneous-readiness-v1",
         "scientific_stage":"C3X 0.7.0-G9.4-P19",
         "primary_authority":"NONE_RESERVE_ONLY",
         "engines":{}}
    funcs={"berserk":audit_berserk,"ethereal":audit_ethereal,"inanis":audit_inanis,"lc0":audit_lc0}
    for k,root in roots.items():
        head=git_head(root)
        if head!=LOCKS[k]: raise SystemExit(f"SOURCE_LOCK_FAIL {k} {head}")
        x=funcs[k](root)
        x["source_commit"]=head
        out["engines"][k]=x
    if a.build_receipt:
        out["build_receipt"]=json.loads(Path(a.build_receipt).read_text())
    out["admission_boundary"]=[
      "Static source proximity is not intervention equivalence.",
      "No engine becomes a P19 primary target from this audit.",
      "Berserk/Ethereal still require complete read-site mediation plus NATIVE/SHAM and FULL_MASK proofs.",
      "Inanis requires a topology-specific abstraction because qsearch lacks the same direct TT-read pattern at the locked source.",
      "Lc0 requires a new architecture-neutral persistent-search-memory causal variable."
    ]
    Path(a.out).parent.mkdir(parents=True,exist_ok=True)
    Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps(out,sort_keys=True))
if __name__=="__main__": main()
