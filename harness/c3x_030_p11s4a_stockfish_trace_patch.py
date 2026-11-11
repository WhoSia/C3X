#!/usr/bin/env python3
"""P11/S4-A strict upstream Stockfish16 source patch, trace only.

Observes a bounded number of MAIN search TT probe and final-save events at
ply<=3 in the exact pinned search.cpp. No causal bypass intervention.
Original source untouched; patch output is a distinct build and SHA-sealed.
"""
import argparse
import hashlib
from pathlib import Path

UPSTREAM_SHA="68e1e9b3811e16cad014b590d7443b9063b3eb52"
INCLUDE='#include <atomic>\n#include <algorithm>'
PROBE='    excludedMove = ss->excludedMove;\\n    posKey = pos.key();\\n    tte = TT.probe(posKey, ss->ttHit);'
SAVE='''    // Write gathered information in transposition table
    if (!excludedMove && !(rootNode && thisThread->pvIdx))
        tte->save(posKey, value_to_tt(bestValue, ss->ply), ss->ttPv,
                  bestValue >= beta ? BOUND_LOWER :
                  PvNode && bestMove ? BOUND_EXACT : BOUND_UPPER,
                  depth, bestMove, ss->staticEval);'''
PROBE_PATCH='''    excludedMove = ss->excludedMove;\n    posKey = pos.key();\n    tte = TT.probe(posKey, ss->ttHit);
    // C3X S4-A observation only: no condition, TT value, or move ordering changed.
    if (ss->ply <= 3)
    {
        const auto c3x_index = c3x_tt_probes.fetch_add(1, std::memory_order_relaxed);
        if (c3x_index < 64)
            std::cerr << "C3X_TT_EVENT kind=probe index=" << c3x_index
                      << " ply=" << ss->ply << " key=" << posKey
                      << " hit=" << int(ss->ttHit) << " depth=" << depth
                      << " root=" << int(rootNode) << std::endl;
    }'''
SAVE_PATCH='''    // Write gathered information in transposition table
    if (!excludedMove && !(rootNode && thisThread->pvIdx))
    {
        // C3X S4-A: log *before* calling the original, unchanged TTEntry::save.
        if (ss->ply <= 3)
        {
            const auto c3x_index = c3x_tt_saves.fetch_add(1, std::memory_order_relaxed);
            if (c3x_index < 64)
                std::cerr << "C3X_TT_EVENT kind=save index=" << c3x_index
                          << " ply=" << ss->ply << " key=" << posKey
                          << " value=" << bestValue << " depth=" << depth
                          << " root=" << int(rootNode) << std::endl;
        }
        tte->save(posKey, value_to_tt(bestValue, ss->ply), ss->ttPv,
                  bestValue >= beta ? BOUND_LOWER :
                  PvNode && bestMove ? BOUND_EXACT : BOUND_UPPER,
                  depth, bestMove, ss->staticEval);
    }'''
COUNTER='''namespace Stockfish {

namespace Search {'''
COUNTER_PATCH='''namespace Stockfish {

// Bounded diagnostic bookkeeping; NEVER read by engine search decisions.
static std::atomic<unsigned> c3x_tt_probes{0};\nstatic std::atomic<unsigned> c3x_tt_saves{0};

namespace Search {'''

def sha(data):return hashlib.sha256(data).hexdigest()
def apply(raw):
    if "C3X_TT_EVENT" in raw:raise ValueError("S4A_HOLD_ALREADY_PATCHED")
    rules=(( "#include <algorithm>", INCLUDE),
           (COUNTER,COUNTER_PATCH),(PROBE,PROBE_PATCH),(SAVE,SAVE_PATCH))
    for old,new in rules:
        if raw.count(old)!=1:
            raise ValueError("S4A_HOLD_UPSTREAM_SOURCE_ANCHOR:"+str(raw.count(old)))
        raw=raw.replace(old,new,1)
    if raw.count("C3X_TT_EVENT kind=")!=2:
        raise ValueError("S4A_HOLD_TRACE_MARKER")
    if raw.count("tte->save(posKey, value_to_tt(bestValue")!=1:
        raise ValueError("S4A_HOLD_ORIGINAL_TT_SAVE_LOST")
    return raw

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--source",required=True)
    ap.add_argument("--out",required=True)
    a=ap.parse_args()
    before=Path(a.source).read_bytes()
    try: raw=before.decode("utf8")
    except UnicodeError as exc:raise ValueError("S4A_HOLD_ENCODING") from exc
    patched=apply(raw).encode("utf8")
    p=Path(a.out);p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(patched)
    print("C3X_S4A_PATCH_SOURCE_SHA256",sha(before),
          "PATCHED_SEARCH_CPP_SHA256",sha(patched),
          "ADDED_BYTES",len(patched)-len(before))
if __name__=="__main__":main()
