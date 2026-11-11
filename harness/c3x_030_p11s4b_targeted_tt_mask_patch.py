#!/usr/bin/env python3
"""C3X P11/S4-B: controlled exact TT hit invalidation, NOT general TT erase.

Instrument only one predeclared main-search position key at ply=1.
The non-matching sham mask executes precisely the same instrumented C++ code.
First-hit target keys are extracted from S4-A ORIGINAL read-only native trace,
and sealed by S4-A raw JSON SHA before any S4-B outcomes.
"""
import argparse
import hashlib
from pathlib import Path

ANCHOR='    excludedMove = ss->excludedMove;\n    posKey = pos.key();\n    tte = TT.probe(posKey, ss->ttHit);'
PATCH='''    excludedMove = ss->excludedMove;
    posKey = pos.key();
    tte = TT.probe(posKey, ss->ttHit);
    // C3X S4-B only: skip use of exactly one previously declared TT hit.
    // The TT storage itself is intentionally NOT altered by this condition.
    static const unsigned long long c3x_target_key = []() -> unsigned long long {
        const char* v = std::getenv("C3X_S4B_TARGET_TT_KEY");
        return v ? std::strtoull(v, nullptr, 10) : 0ULL;
    }();
    if (c3x_target_key && ss->ply == 1
        && static_cast<unsigned long long>(posKey) == c3x_target_key && ss->ttHit)
    {
        // A real source-level physical intervention on the TT hit signal.
        ss->ttHit = false;
        static unsigned c3x_masked_count = 0;
        if (c3x_masked_count++ < 8)
            std::cerr << "C3X_S4B_MASKED key=" << posKey
                      << " ply=" << ss->ply << " hit_became=0" << std::endl;
    }'''
def sha(s):return hashlib.sha256(s).hexdigest()
def apply(src):
    if 'C3X_S4B_MASKED' in src:raise ValueError('S4B_HOLD_DOUBLE_INSTRUMENTATION')
    if src.count(ANCHOR)!=1 or src.count('#include <iostream>')!=1:
        raise ValueError('S4B_HOLD_SOURCE_ANCHOR')
    new=src.replace('#include <iostream>','#include <iostream>\n#include <cstdlib>',1)
    new=new.replace(ANCHOR,PATCH,1)
    if new.count('tte = TT.probe(posKey, ss->ttHit);') != src.count('tte = TT.probe(posKey, ss->ttHit);'):
        raise ValueError('S4B_HOLD_ORIGINAL_TT_PROBE_REMOVED')
    if new.count('tte->save(')!=src.count('tte->save('):
        raise ValueError('S4B_HOLD_ORIGINAL_TT_SAVE_REMOVED')
    return new

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--source',required=True)
    p.add_argument('--out',required=True)
    a=p.parse_args()
    raw=Path(a.source).read_bytes()
    out=apply(raw.decode('utf8')).encode('utf8')
    path=Path(a.out);path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(out)
    print('C3X_S4B_ORIGINAL_SEARCH_CPP_SHA',sha(raw),'MASKED_SEARCH_CPP_SHA',sha(out))
if __name__=='__main__':main()
