#!/usr/bin/env python3
"""Temporal scope fix for P1: only writer saves BEFORE second selected reader.

Apply after c3x_018_P0P1_TT_save_decision_writer_reinstate_overlay.py.
Preserves previously failed broad negative R5 audit separately.
"""
import argparse,hashlib,json
from pathlib import Path

def patch(s):
    a='''        !would || !known || old.key64!=uint64_t(key) ||
        old.epoch!=c3x018_parameter("C3X018_P1_WRITER_EPOCH"))'''
    b='''        !would || !known || old.key64!=uint64_t(key) ||
        old.epoch!=c3x018_parameter("C3X018_P1_WRITER_EPOCH") ||
        (std::getenv("C3X018_P1_LAST_CALL") &&
         c3x018_root_context_call > c3x018_parameter("C3X018_P1_LAST_CALL")))'''
    n=s.count(a)
    if n!=1:raise RuntimeError("C3X018_P1_TEMPORAL_SCOPE_ANCHOR_"+str(n))
    return s.replace(a,b,1)

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source",required=True)
    p.add_argument("--out-manifest",required=True)
    a=p.parse_args()
    f=Path(a.source)/"src/tt.cpp"
    original=f.read_bytes();altered=patch(original.decode()).encode()
    f.write_bytes(altered)
    obj={"schema":"c3x018-P1-temporally-qualified-rescue-before-second-source-rootcall-v1",
      "source_before_sha256":hashlib.sha256(original).hexdigest(),
      "source_after_sha256":hashlib.sha256(altered).hexdigest(),
      "policy":"C3X018_P1_LAST_CALL bound on writer suppression/repair, not passive source TT writes",
      "prior_unbounded_negative_R5":"FAIL as previously recorded in run 37995253598",
      "limits":["the upper source root-call handle is within-arm not a stable recursive node ID",
                "same TT physical key and actual previous write epoch required",
                "only the eligible first overwrite after actual targeted reader block may be affected"]}
    o=Path(a.out_manifest);o.parent.mkdir(parents=True,exist_ok=True)
    o.write_text(json.dumps(obj,indent=2)+"\n")
    print("C3X018_P1_WRITER_RESCUE_BOUND_TO_SELECTED_SECOND_ROOT_CALL")
if __name__=="__main__":main()
