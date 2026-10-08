#!/usr/bin/env python3
"""Append one end-of-search-only native Stockfish16 completedDepth observation.

Does not alter search loop, TT probes/returns, evaluator, clock or parameters.
Applied AFTER frozen EP9 MAIN-path instrumentation on clean sf_16 source.
"""
import argparse,hashlib,json
from pathlib import Path

ANCHOR='  sync_cout << "bestmove " << UCI::move(bestThread->rootMoves[0].pv[0], rootPos.is_chess960());'
INSERT=('  sync_cout << "info string c3x014_completion_probe best_completed=" '
        '<< bestThread->completedDepth << " best_root_depth=" << bestThread->rootDepth '
        '<< " main_completed=" << completedDepth << sync_endl;\n\n')
def h(raw):return hashlib.sha256(raw).hexdigest()
def main():
    a=argparse.ArgumentParser()
    a.add_argument("--source",required=True);a.add_argument("--out-manifest",required=True)
    x=a.parse_args()
    file=Path(x.source)/"src/search.cpp"
    raw=file.read_bytes();s=raw.decode()
    if s.count(ANCHOR)!=1:raise SystemExit("NATIVE_COMPLETION_ANCHOR_NOT_UNIQUE")
    if "c3x014_completion_probe" in s:raise SystemExit("ALREADY_INSTRUMENTED")
    new=s.replace(ANCHOR,INSERT+ANCHOR)
    file.write_text(new)
    manifest={"schema":"c3x-014-p3-post-search-only-thread-completion-native-patch-v1",
        "source":"official Stockfish16 sf_16 commit 68e1e9b3811e16cad014b590d7443b9063b3eb52",
        "original_src_search_cpp_sha256":h(raw),
        "patched_src_search_cpp_sha256":h(new.encode()),
        "patch_once_only":True,
        "insertion_location":"MainThread::search after all workers finish, immediately before printing bestmove",
        "printed_native_fields":["bestThread->completedDepth","bestThread->rootDepth","MainThread completedDepth"],
        "expected_nonintervention":"all search code lines unchanged; no logger executed before terminating search",
        "do_not_claim":"UCI PV level alone proves an iteration completed"}
    out=Path(x.out_manifest);out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(manifest,indent=2)+"\n")
    print("NATIVE_SF16_COMPLETED_DEPTH_END_OF_SEARCH_PATCH_PASS",h(new.encode()),flush=True)
if __name__=="__main__":main()
