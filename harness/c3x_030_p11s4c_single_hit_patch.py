#!/usr/bin/env python3
"""P11/S4C1: EXACTLY ONE actual TT-hit-flag intervention per Stockfish process.

The TT key is frozen from S4B's immutable original, not selected by S4C
outcomes. A namespace-scope atomic flag is shared by every template instance
of search<NodeType>; unlike S4B's per-template counter, it prevents repeated
hits to the same selected key from being modified more than once.
"""
import argparse
import hashlib
from pathlib import Path

ORIGINAL_COMMIT="68e1e9b3811e16cad014b590d7443b9063b3eb52"
ANCHOR='    excludedMove = ss->excludedMove;\n    posKey = pos.key();\n    tte = TT.probe(posKey, ss->ttHit);'
NS='namespace Stockfish {\n\nnamespace Search {'
NS_PATCH='''namespace Stockfish {

// One process-wide gate, shared across Root/PV/NonPV template instances.
static std::atomic<bool> c3x_s4c_one_hit_claimed{false};

namespace Search {'''
PATCH='''    excludedMove = ss->excludedMove;
    posKey = pos.key();
    tte = TT.probe(posKey, ss->ttHit);
    // One explicitly selected source-site TT-hit signal, once per process.
    static const unsigned long long c3x_s4c_key = []() -> unsigned long long {
        const char* p = std::getenv("C3X_S4C_FIRST_HIT_KEY");
        return p ? std::strtoull(p, nullptr, 10) : 0ULL;
    }();
    if (c3x_s4c_key && ss->ply == 1 && ss->ttHit
        && static_cast<unsigned long long>(posKey) == c3x_s4c_key
        && !c3x_s4c_one_hit_claimed.exchange(true, std::memory_order_seq_cst))
    {
        // Logged before modification; parent_move is a stack value, not an
        // independently reconstructed parent/ancestor causal chain.
        std::cerr << "C3X_S4C_SINGLE_HIT key=" << posKey
                  << " ply=" << ss->ply << " depth=" << depth
                  << " parent_move_raw=" << static_cast<int>((ss-1)->currentMove)
                  << " tt_depth=" << tte->depth()
                  << " alpha=" << alpha << " beta=" << beta
                  << " old_hit=1 new_hit=0" << std::endl;
        ss->ttHit = false;
    }'''

def sha(x):return hashlib.sha256(x).hexdigest()

def apply(source):
    if "C3X_S4C_SINGLE_HIT" in source:
        raise ValueError("S4C_HOLD_DOUBLE_PATCH")
    keys=(
        ("#include <algorithm>","#include <atomic>\n#include <cstdlib>\n#include <algorithm>"),
        (NS,NS_PATCH),(ANCHOR,PATCH))
    for old,new in keys:
        if source.count(old)!=1:raise ValueError("S4C_HOLD_NONUNIQUE_ORIGINAL_ANCHOR")
        source=source.replace(old,new,1)
    if source.count("c3x_s4c_one_hit_claimed.exchange(")!=1:
        raise ValueError("S4C_HOLD_ONE_PROCESS_WIDE_GATE")
    if source.count("C3X_S4C_SINGLE_HIT key=")!=1:
        raise ValueError("S4C_HOLD_EVENT_TRACE")
    return source

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source",required=True);p.add_argument("--out",required=True)
    a=p.parse_args()
    original=Path(a.source).read_bytes()
    patched=apply(original.decode("utf8")).encode("utf8")
    path=Path(a.out);path.parent.mkdir(parents=True,exist_ok=True)
    path.write_bytes(patched)
    print("S4C_ORIGINAL_SRC_SHA",sha(original),
          "S4C_SINGLE_HIT_PATCH_SHA",sha(patched))
if __name__=="__main__":main()
