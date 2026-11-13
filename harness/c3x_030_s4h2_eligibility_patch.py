#!/usr/bin/env python3
"""C3X S4-H2: compile a read-only, outcome-blind ply-one TT-hit eligibility logger.

Add to existing anchored S4G instrumented Stockfish 16 source. No TT mutation,
no root score, bestmove, PV or evaluation field is exported by this probe.
A first-hit ordinal within each engine process is used without substitution.
"""
import argparse
import hashlib
from pathlib import Path
from c3x_030_p11s4g_masked_invocation_patch import patch as s4g_patch

SITE = "    // C3X S4G: same compiled binary, literal source TT hit signal intervention."
ELIGIBILITY = """    // C3X S4H2: outcome-blind first actual TT hit, before any TT mask.
    static const bool c3x_h2_discovery_mode = []() {
        const char* v = std::getenv("C3X_S4H2_ELIGIBILITY_MODE");
        return v && v[0] == '1' && v[1] == 0;
    }();
    if (c3x_h2_discovery_mode && ss->ply == 1 && ss->ttHit)
    {
        const unsigned h2_ordinal = c3x_h2_hit_ordinal.fetch_add(1, std::memory_order_relaxed);
        if (h2_ordinal < 4096)
            std::cerr << "C3X_S4H2_ELIGIBLE ordinal=" << h2_ordinal
                      << " key=" << posKey
                      << " ply=" << ss->ply
                      << " hit_before=1" << std::endl;
    }
"""

def apply(original: str) -> str:
    s = s4g_patch(original)
    shared = "static std::atomic<unsigned> c3x_g_matching_hits{0};"
    if s.count(shared) != 1:
        raise ValueError("S4H2_SHARED_PROCESS_COUNTER_SOURCE_ANCHOR")
    s = s.replace(shared, shared + "\nstatic std::atomic<unsigned> c3x_h2_hit_ordinal{0};", 1)
    if s.count(SITE) != 1 or "C3X_S4H2_ELIGIBLE" in original:
        raise ValueError("S4H2_ELIGIBILITY_SOURCE_ANCHOR_MISMATCH")
    s = s.replace(SITE, ELIGIBILITY + SITE, 1)
    if s.count('C3X_S4H2_ELIGIBLE ordinal=') != 1:
        raise ValueError("S4H2_ELIGIBILITY_PATCH_MISSING")
    return s

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source",required=True)
    p.add_argument("--out",required=True)
    a=p.parse_args()
    raw=Path(a.source).read_bytes()
    output=apply(raw.decode("utf8")).encode()
    target=Path(a.out)
    target.parent.mkdir(parents=True,exist_ok=True)
    target.write_bytes(output)
    print("S4H2_ELIGIBLE_READ_ONLY_PATCH",
          hashlib.sha256(raw).hexdigest(),hashlib.sha256(output).hexdigest())

if __name__=="__main__":
    main()
