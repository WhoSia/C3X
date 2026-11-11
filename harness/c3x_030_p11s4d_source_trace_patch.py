#!/usr/bin/env python3
"""C3X S4-D/A strictly read-only source TT-hit -> search-return -> root-candidate tracing.

No TT entry or source behavior is altered. This does NOT instrument early
returns / qsearch and is not a complete causality chain. Source-anchored,
losslessly retains original calls; bounded stderr diagnostics.
"""
import argparse
import hashlib
from pathlib import Path

ORIG_PROBE='    excludedMove = ss->excludedMove;\n    posKey = pos.key();\n    tte = TT.probe(posKey, ss->ttHit);'
ORIG_RETURN='    assert(bestValue > -VALUE_INFINITE && bestValue < VALUE_INFINITE);\n\n    return bestValue;\n  }\n\n\n  // qsearch()'
ORIG_ROOT='''          RootMove& rm = *std::find(thisThread->rootMoves.begin(),
                                    thisThread->rootMoves.end(), move);'''
ORIG_NS='namespace Stockfish {\n\nnamespace Search {'
COUNTERS='''namespace Stockfish {

// Bounded observation ONLY; these counters are never consulted by search logic.
static std::atomic<unsigned> c3x_d_probe_count{0};
static std::atomic<unsigned> c3x_d_return_count{0};
static std::atomic<unsigned> c3x_d_root_count{0};

namespace Search {'''
PROBE='''    excludedMove = ss->excludedMove;
    posKey = pos.key();
    tte = TT.probe(posKey, ss->ttHit);
    static const unsigned long long c3x_d_target_key = []() -> unsigned long long {
        const char* s = std::getenv("C3X_S4D_TARGET_KEY");
        return s ? std::strtoull(s, nullptr, 10) : 0ULL;
    }();
    if (c3x_d_target_key && ss->ply == 1
        && static_cast<unsigned long long>(posKey) == c3x_d_target_key)
    {
        const auto n = c3x_d_probe_count.fetch_add(1, std::memory_order_relaxed);
        if (n < 120)
            std::cerr << "C3X_S4D kind=probe seq=" << n
                      << " key=" << posKey << " ply=" << ss->ply
                      << " parent_move_raw=" << static_cast<int>((ss-1)->currentMove)
                      << " hit=" << int(ss->ttHit) << " depth=" << depth
                      << " alpha=" << alpha << " beta=" << beta << std::endl;
    }'''
RETURN='''    assert(bestValue > -VALUE_INFINITE && bestValue < VALUE_INFINITE);
    if (c3x_d_target_key && ss->ply == 1
        && static_cast<unsigned long long>(posKey) == c3x_d_target_key)
    {
        const auto n = c3x_d_return_count.fetch_add(1, std::memory_order_relaxed);
        if (n < 120)
            std::cerr << "C3X_S4D kind=normal_return seq=" << n
                      << " key=" << posKey << " ply=" << ss->ply
                      << " parent_move_raw=" << static_cast<int>((ss-1)->currentMove)
                      << " best_value=" << bestValue
                      << " alpha_final=" << alpha << " beta=" << beta << std::endl;
    }
    return bestValue;\n  }\n\n\n  // qsearch()'''
ROOT='''          RootMove& rm = *std::find(thisThread->rootMoves.begin(),
                                    thisThread->rootMoves.end(), move);
          // Root candidate value is measured BEFORE stockfish's original update.
          if (c3x_d_target_key)
          {
              const auto n = c3x_d_root_count.fetch_add(1, std::memory_order_relaxed);
              if (n < 180)
                  std::cerr << "C3X_S4D kind=root_candidate seq=" << n
                            << " root_move_raw=" << static_cast<int>(move)
                            << " root_value=" << value << " old_best=" << bestValue
                            << " root_alpha=" << alpha << " root_beta=" << beta
                            << " root_depth=" << depth << std::endl;
          }'''

def sha(data):return hashlib.sha256(data).hexdigest()
def apply(src):
    if 'C3X_S4D kind=' in src:raise ValueError('S4D_HOLD_ALREADY_INSTRUMENTED')
    baseline_probes=src.count('tte = TT.probe(posKey, ss->ttHit);')
    baseline_saves=src.count('tte->save(')
    edits=[
      ('#include <algorithm>','#include <atomic>\n#include <cstdlib>\n#include <algorithm>'),
      (ORIG_NS,COUNTERS),(ORIG_PROBE,PROBE),(ORIG_RETURN,RETURN),(ORIG_ROOT,ROOT)]
    for old,new in edits:
        if src.count(old)!=1:raise ValueError('S4D_HOLD_SOURCE_ANCHOR_NOT_UNIQUE:'+str(src.count(old)))
        src=src.replace(old,new,1)
    if src.count('tte = TT.probe(posKey, ss->ttHit);')!=baseline_probes or src.count('tte->save(')!=baseline_saves:
        raise ValueError('S4D_HOLD_UPSTREAM_TT_CALL_MUTATION')
    if src.count('C3X_S4D kind=')!=3:raise ValueError('S4D_HOLD_OBSERVATION_SITE_COUNT')
    return src

def main():
    a=argparse.ArgumentParser()
    a.add_argument('--source',required=True)
    a.add_argument('--out',required=True)
    z=a.parse_args()
    data=Path(z.source).read_bytes()
    fixed=apply(data.decode('utf8')).encode('utf8')
    dest=Path(z.out);dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_bytes(fixed)
    print('S4D_UPSTREAM_SOURCE_SHA',sha(data),'OBSERVATION_ONLY_SOURCE_SHA',sha(fixed))
if __name__=='__main__':main()
