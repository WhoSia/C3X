#!/usr/bin/env python3
"""S4-I source-anchored TT early-cutoff trace for known development TT keys.

The source patch only records bounded true TT cutoff return values; it does not
modify TT hit, the return value, alpha/beta, or search state.
"""
import argparse,hashlib
from pathlib import Path
from c3x_030_s4h2_eligibility_patch import apply as s4h2_patch

TT_CUTOFF="""        if (pos.rule50_count() < 90)
            return ttValue;"""
TT_CUTOFF_TRACE="""        if (pos.rule50_count() < 90)
        {
            // S4-I: observe only actual TT short-circuit returns at target ply1.
            if (c3x_e_scope.interested)
            {
                const unsigned c3x_i_index = c3x_i_logged_cutoffs.fetch_add(1, std::memory_order_relaxed);
                if (c3x_i_index < 8)
                    std::cerr << "C3X_S4I_TT_CUTOFF ordinal=" << c3x_i_index
                              << " id=" << c3x_e_scope.id
                              << " parent=" << c3x_e_scope.parent_id
                              << " key=" << posKey
                              << " ply=" << ss->ply
                              << " return_value=" << ttValue << std::endl;
            }
            return ttValue;
        }"""

def patch(original):
    s=s4h2_patch(original)
    shared="static std::atomic<unsigned> c3x_h2_hit_ordinal{0};"
    if s.count(shared)!=1 or s.count(TT_CUTOFF)!=1:
        raise ValueError("S4I_HOLD_UPSTREAM_SOURCE_ANCHORS")
    s=s.replace(shared,shared+"\nstatic std::atomic<unsigned> c3x_i_logged_cutoffs{0};",1)
    s=s.replace(TT_CUTOFF,TT_CUTOFF_TRACE,1)
    if s.count('C3X_S4I_TT_CUTOFF ordinal=')!=1:
        raise ValueError("S4I_HOLD_MISSING_CUTOFF_EVENT")
    return s

def main():
    a=argparse.ArgumentParser()
    a.add_argument("--source",required=True)
    a.add_argument("--out",required=True)
    x=a.parse_args()
    src=Path(x.source).read_bytes()
    new=patch(src.decode()).encode()
    dest=Path(x.out);dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_bytes(new)
    print("C3X_S4I_TT_CUTOFF_SOURCE",hashlib.sha256(src).hexdigest(),hashlib.sha256(new).hexdigest())

if __name__=="__main__":main()
