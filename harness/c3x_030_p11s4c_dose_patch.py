#!/usr/bin/env python3
"""C3X S4C2: same native binary and predeclared target, dose 0/1/2/unbounded.

One process-global atomic matching-hit counter across PV/NonPV/Root search
template instantiations. No change to original Stockfish TT store operations.
Limits are read once from run-start environment for each process. The only
thing varied within the same compiled patched binary is the budget of
physical TT hit-flag suppressions.
"""
import argparse
import hashlib
from pathlib import Path
from c3x_030_p11s4c_single_hit_patch import ANCHOR,NS

def sha(data):return hashlib.sha256(data).hexdigest()

PATCH='''    excludedMove = ss->excludedMove;
    posKey = pos.key();
    tte = TT.probe(posKey, ss->ttHit);
    static const unsigned long long c3x_s4c2_key = []() -> unsigned long long {
        const char* s = std::getenv("C3X_S4C2_KEY");
        return s ? std::strtoull(s, nullptr, 10) : 0ULL;
    }();
    static const unsigned c3x_s4c2_limit = []() -> unsigned {
        const char* s = std::getenv("C3X_S4C2_LIMIT");
        return s ? static_cast<unsigned>(std::strtoul(s, nullptr, 10)) : 0U;
    }();
    if (c3x_s4c2_key && ss->ply == 1 && ss->ttHit
        && static_cast<unsigned long long>(posKey) == c3x_s4c2_key)
    {
        const auto c3x_ordinal = c3x_s4c2_matching_hits.fetch_add(1, std::memory_order_seq_cst);
        if (c3x_ordinal < c3x_s4c2_limit)
        {
            ss->ttHit = false;
            if (c3x_ordinal < 8)
                std::cerr << "C3X_S4C2_MASK ordinal=" << c3x_ordinal
                          << " key=" << posKey << " ply=" << ss->ply
                          << " parent_move_raw=" << static_cast<int>((ss-1)->currentMove)
                          << " depth=" << depth << " new_hit=0" << std::endl;
        }
    }'''

NAMESPACE_PATCH='''namespace Stockfish {

// Exactly one native counter across all templated search<NodeType> instances.
static std::atomic<unsigned> c3x_s4c2_matching_hits{0};

namespace Search {'''

def apply(original):
    if "C3X_S4C2_MASK" in original:
        raise ValueError("S4C2_HOLD_DOUBLE_PATCH")
    changes=(
        ("#include <algorithm>","#include <atomic>\n#include <cstdlib>\n#include <algorithm>"),
        (NS,NAMESPACE_PATCH),
        (ANCHOR,PATCH))
    before_probe=original.count("tte = TT.probe(posKey, ss->ttHit);")
    before_save=original.count("tte->save(")
    for old,new in changes:
        if original.count(old)!=1:
            raise ValueError("S4C2_HOLD_NONUNIQUE_SOURCE_ANCHOR")
        original=original.replace(old,new,1)
    if (original.count("tte = TT.probe(posKey, ss->ttHit);")!=before_probe
        or original.count("tte->save(")!=before_save):
        raise ValueError("S4C2_HOLD_ORIGINAL_SOURCE_CALL_MUTATION")
    if original.count("c3x_s4c2_matching_hits.fetch_add")!=1:
        raise ValueError("S4C2_HOLD_PROCESS_GLOBAL_GATE")
    return original

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source",required=True)
    p.add_argument("--out",required=True)
    a=p.parse_args()
    raw=Path(a.source).read_bytes()
    new=apply(raw.decode("utf8")).encode("utf8")
    dest=Path(a.out);dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_bytes(new)
    print("C3X_S4C2_SOURCE_SHA",sha(raw),"DOSE_PATCH_SHA",sha(new))
if __name__=="__main__":main()
