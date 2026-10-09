#!/usr/bin/env python3
"""Selective source-writer reinstatement (S) overlay for physical TT epoch court.

S with budget 2 inhibits eligible writer attempt #1, permits attempt #2 via
the unchanged original TTEntry::save(), and does NOT synthesize foreign TT
data. Contrast with W2 and W1. A restoration is local operator evidence, not
a unique natural TT mediation certificate.
"""
from pathlib import Path
import argparse,hashlib,json

def once(s,a,b,label):
    n=s.count(a)
    if n!=1: raise RuntimeError(f"C3X018_RESCUE_{label}_ANCHOR_{n}")
    return s.replace(a,b,1)

def patch(s):
    s=once(s,
      "uint64_t c3x018_writer_blocks = 0;",
      "uint64_t c3x018_writer_blocks = 0;\nuint64_t c3x018_target_attempts = 0;","STATE")
    s=once(s,
      'if ((std::strcmp(mode, "W") == 0 || std::strcmp(mode, "WR") == 0)',
      'if ((std::strcmp(mode, "W") == 0 || std::strcmp(mode, "WR") == 0 ||\n         std::strcmp(mode, "S") == 0)',"S_MODE")
    s=once(s,'        ++c3x018_writer_blocks;',
      '''        ++c3x018_target_attempts;
        if (std::strcmp(mode, "S") == 0 &&
            c3x018_target_attempts == c3x018_parameter("C3X018_TT_RESCUE_ATTEMPT")) {
            c3x018_event("writer_rescue", "original_save", key, slot, next,
                         uint64_t(key), 1, -1, -1, 0, 0, 0);
            return false;
        }
        ++c3x018_writer_blocks;''',"ALLOW_NTH")
    s=once(s,'      c3x018_writer_blocks = 0;',
       '      c3x018_writer_blocks = 0;\n      c3x018_target_attempts = 0;',"RESET")
    return s

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source",required=True)
    p.add_argument("--out-manifest",required=True)
    a=p.parse_args();f=Path(a.source)/"src/tt.cpp";old=f.read_bytes()
    new=patch(old.decode()).encode();f.write_bytes(new)
    out=Path(a.out_manifest);out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps({
      "schema":"c3x018-TT-matched-second-writer-native-reinstatement-overlay-v1",
      "before_sha256":hashlib.sha256(old).hexdigest(),
      "after_sha256":hashlib.sha256(new).hexdigest(),
      "mode":"S",
      "target":"fixed full64 key, physical slot, next accepted payload-write epoch",
      "rescue_event":"writer_rescue site=original_save before original native TTEntry::save proceeds",
      "scope":["Budget W2 vs S with rescue attempt #1, #2, unreachable #3",
               "S does NOT synthesize an external TT entry; it allows the original eligible save",
               "After restoration, future matching contacts may vanish due to epoch change",
               "A reversal by reinstatement is not a proof of exclusive natural mediator",
               "No other TT uses explicitly suppressed or controlled"]
    },indent=2)+"\n")
    print("C3X018_TT_SOURCE_WRITER_RESCUE_OVERLAY_APPLIED")
if __name__=="__main__":main()
