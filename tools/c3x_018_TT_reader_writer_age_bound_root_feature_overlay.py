#!/usr/bin/env python3
"""Passive SF16 TT reader features: global-writer age, bound, ply, root ancestry.

Apply AFTER P4, C3X017 early events, 0.18 trial IDs, physical epoch,
value V gate, value payload witness, and root->TT context overlay.
Extends only discovery census to 256 source-positive readings.
"""
import argparse,hashlib,json
from pathlib import Path
def once(s,a,b,name):
    n=s.count(a)
    if n!=1:raise RuntimeError(f"C3X018_FEATURE_{name}_ANCHOR_{n}")
    return s.replace(a,b,1)
def patch(s):
    s=once(s,"c3x018_discovery_count < 32",
              "c3x018_discovery_count < 256","CENSUS_CAP")
    s=once(s,
         '              << " raw_value=" << int(slot->value())',
         '              << " writer_age_writes=" << (c3x018_write_serial >= w.writer_serial ? c3x018_write_serial - w.writer_serial : 0)\n'
         '              << " current_write_serial=" << c3x018_write_serial\n'
         '              << " reader_root_call=" << c3x018_root_context_call\n'
         '              << " reader_root_move=" << c3x018_root_context_move\n'
         '              << " raw_value=" << int(slot->value())',
         "READER_FEATURES")
    return s
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source",required=True)
    p.add_argument("--out-manifest",required=True)
    a=p.parse_args()
    f=Path(a.source)/"src/tt.cpp"
    before=f.read_bytes();after=patch(before.decode()).encode();f.write_bytes(after)
    obj={"schema":"c3x018-sf16-TT-source-writer-age-bound-ply-root-features-v1",
         "before_sha256":hashlib.sha256(before).hexdigest(),
         "after_sha256":hashlib.sha256(after).hexdigest(),
         "passive_census_limit":256,
         "reader_fields":["full64 writer_key64","key64","physical slot","slot epoch","writer_serial",
             "current_write_serial","writer_age_writes","raw_bound","raw_depth","ply","depth",
             "reader_root_call","reader_root_move","effective_value","raw_value","site"],
         "invariants":["writer_age_writes=current_write_serial-writer_serial >=0",
             "writer shadow raw value and root ancestry remain source-native, no synthetic event identity",
             "full64 key and raw value matched during actual source reader",
             "source visitor limited to one single-threaded cold process"],
         "limits":["age counts accepted TT writes, not elapsed time",
                   "reader_root_move is root candidate ancestry, not unique TT writer ownership",
                   "selected target uses full64 key + physical slot + epoch, which might contact several readers",
                   "a capped 256 witness list cannot establish that later source sites do not exist"]}
    o=Path(a.out_manifest);o.parent.mkdir(parents=True,exist_ok=True)
    o.write_text(json.dumps(obj,indent=2)+"\n")
    print("C3X018_PASSIVE_SOURCE_READER_FEATURES_256_PATCH_APPLIED")
if __name__=="__main__":main()
