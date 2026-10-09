#!/usr/bin/env python3
"""Augment C3X 018 physical TT writer blocks with source-site proposal fingerprints.

Layer after physical_epoch_lineage_patch, optionally after payload_only overlay.
Do not change event eligibility, TTEntry byte layout, or chess computation.
"""
from pathlib import Path
import argparse,hashlib,json

def once(s,a,b,n):
    k=s.count(a)
    if k!=1:raise RuntimeError(f"C3X018_FINGERPRINT_{n}_ANCHOR_{k}")
    return s.replace(a,b,1)

def patch_header(s):
    return once(s,
      "bool c3x018_writer_block(Key key, const TTEntry* slot, bool would_write);",
      "bool c3x018_writer_block(Key key, const TTEntry* slot, bool would_write,\n"
      "                         int proposed_move, int proposed_depth, int proposed_bound,\n"
      "                         int proposed_value, int prior_move, int prior_depth,\n"
      "                         int prior_bound, int prior_value);","HDR")

def patch_tt(s):
    s=once(s,
       "bool c3x018_writer_block(Key key, const TTEntry* slot, bool would_write) {",
       "bool c3x018_writer_block(Key key, const TTEntry* slot, bool would_write,\n"
       "                         int proposed_move, int proposed_depth, int proposed_bound,\n"
       "                         int proposed_value, int prior_move, int prior_depth,\n"
       "                         int prior_bound, int prior_value) {","IMPL")
    s=once(s,
       '        ++c3x018_writer_blocks;',
       '''        ++c3x018_writer_blocks;
        sync_cout << "info string c3x018_write_fingerprint"
                  << " contact=" << c3x018_writer_blocks
                  << " key64=" << uint64_t(key)
                  << " slot=" << c3x018_slot(key, slot)
                  << " epoch=" << next
                  << " proposed_move=" << proposed_move
                  << " proposed_depth=" << proposed_depth
                  << " proposed_bound=" << proposed_bound
                  << " proposed_value=" << proposed_value
                  << " prior_move=" << prior_move
                  << " prior_depth=" << prior_depth
                  << " prior_bound=" << prior_bound
                  << " prior_value=" << prior_value << sync_endl;''',"SITE")
    bare="c3x018_writer_block(k, this, c3x018_would_payload_write)"
    payload="c3x018_writer_block(\n      k, this, c3x018_would_payload_write)"
    options=[form for form in (bare,payload) if s.count(form)==1]
    if len(options)!=1:
        raise RuntimeError(f"C3X018_FINGERPRINT_CALL_ANCHOR_COUNT_{len(options)}")
    s=once(s,options[0],
       "c3x018_writer_block(\n      k, this, c3x018_would_payload_write,\n"
       "      int(m), int(d), int(b), int(v), int(move16),\n"
       "      int(depth8) + int(DEPTH_OFFSET), int(genBound8 & 3), int(value16))",
       "CALL")
    return s

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source",required=True)
    p.add_argument("--out-manifest",required=True)
    a=p.parse_args()
    result={}
    root=Path(a.source)/"src"
    for filename,fn in (("tt.h",patch_header),("tt.cpp",patch_tt)):
        path=root/filename
        old=path.read_bytes()
        new=fn(old.decode()).encode()
        path.write_bytes(new)
        result[filename]={"before_sha256":hashlib.sha256(old).hexdigest(),
                          "after_sha256":hashlib.sha256(new).hexdigest()}
    dest=Path(a.out_manifest)
    dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(json.dumps({
      "schema":"c3x018-writer-block-source-proposal-fingerprint-v1",
      "modified":result,"event":"c3x018_write_fingerprint",
      "fields":["key64","slot","epoch","contact","proposed_move",
                "proposed_depth","proposed_bound","proposed_value",
                "prior_move","prior_depth","prior_bound","prior_value"],
      "scope":"fingerprints describe blocked call inputs, not cross-arm identical natural event",
      "guard":"source anchors must occur exactly once; require prior epoch patch"
    },indent=2)+"\n")
    print("C3X018_WRITER_FINGERPRINT_OVERLAY_PASS")
if __name__=="__main__":main()
