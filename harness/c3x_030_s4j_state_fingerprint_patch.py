#!/usr/bin/env python3
"""C3X S4-J: source anchored, read-only TT cutoff state fingerprint.

Fingerprint is a candidate cross-run state key, NOT invocation identity.
No alpha/beta, position, TT, search decisions or return values are modified.
"""
import argparse,hashlib
from pathlib import Path
from c3x_030_s4i_tt_early_cutoff_patch import patch as s4i_patch

BEFORE='''                              << " return_value=" << ttValue << std::endl;'''
AFTER='''                              << " search_depth=" << depth
                              << " alpha=" << alpha
                              << " beta=" << beta
                              << " pv=" << int(PvNode)
                              << " cutnode=" << int(cutNode)
                              << " return_value=" << ttValue << std::endl;'''

def patch(original: str) -> str:
    s=s4i_patch(original)
    if s.count(BEFORE)!=1:
        raise ValueError("S4J_HOLD_CUTOFF_ANCHOR_NOT_UNIQUE")
    s=s.replace(BEFORE,AFTER,1)
    if s.count('" search_depth=" << depth')!=1 or s.count("return ttValue;")!=1:
        raise ValueError("S4J_HOLD_SOURCE_PATCH_DRIFT")
    return s

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source",required=True)
    p.add_argument("--out",required=True)
    a=p.parse_args()
    original=Path(a.source).read_bytes()
    modified=patch(original.decode("utf-8")).encode("utf-8")
    dest=Path(a.out);dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_bytes(modified)
    print("S4J_TT_CUTOFF_STATE_SOURCE",hashlib.sha256(original).hexdigest(),hashlib.sha256(modified).hexdigest())
if __name__=="__main__": main()
