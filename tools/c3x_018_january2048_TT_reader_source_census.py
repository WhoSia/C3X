#!/usr/bin/env python3
"""2026-01 source pair court: expand passive V witnesses from 256 to 2048.

This is OBS ONLY, never modifies TT use or cache; 2048 is prespecified.
Runs after c3x_018_TT_reader_writer_age_bound_root_feature_overlay.py.
"""
import argparse,hashlib,json
from pathlib import Path

def patch(s):
    anchor="c3x018_discovery_count < 256"
    if s.count(anchor)!=1:
        raise RuntimeError(f"C3X018_JAN2048_DISCOVERY_ANCHOR_{s.count(anchor)}")
    return s.replace(anchor,"c3x018_discovery_count < 2048",1)

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source",required=True)
    p.add_argument("--out-manifest",required=True)
    a=p.parse_args()
    f=Path(a.source)/"src/tt.cpp"
    original=f.read_bytes();altered=patch(original.decode()).encode()
    f.write_bytes(altered)
    obj={"schema":"c3x018-Jan2026-independent-cross-window-first2048-TT-value-read-census-v1",
         "before_sha256":hashlib.sha256(original).hexdigest(),
         "after_sha256":hashlib.sha256(altered).hexdigest(),
         "census_cap":2048,"event_kind":"discovery","source_no_eval_mutation":True,
         "critical":"2048 records is source-order capped, not complete search census; cap reached means CENSORED"}
    o=Path(a.out_manifest);o.parent.mkdir(parents=True,exist_ok=True)
    o.write_text(json.dumps(obj,indent=2)+"\n")
    print("C3X018_JANUARY_FIRST_2048_SOURCE_DISCOVERY_OVERLAY_READY")

if __name__=="__main__":main()
