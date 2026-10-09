#!/usr/bin/env python3
"""Add five-bit inclusion mask for case11 TT age64 root calls 9..13.

Apply only after c3x_018_adaptive_writer_age_root_call_V_gate.py.
Absent mask env retains original guards; present mask0 permits no TT V blocks.
"""
import argparse,hashlib,json
from pathlib import Path
def one(s,a,b,label):
 n=s.count(a)
 if n!=1:raise RuntimeError(f"C3X018_COALITION_{label}_ANCHOR_{n}")
 return s.replace(a,b,1)
def patch(s):
 old='''                   && (!std::getenv("C3X018_FILTER_RAW_BOUND") ||
                       int(slot->bound()) == int(c3x018_parameter("C3X018_FILTER_RAW_BOUND")));
    // E/V read gates only emit contact on a realized targeted source match.'''
 new='''                   && (!std::getenv("C3X018_FILTER_RAW_BOUND") ||
                       int(slot->bound()) == int(c3x018_parameter("C3X018_FILTER_RAW_BOUND")))
                   && (!std::getenv("C3X018_FILTER_CALL_MASK_9_13") ||
                       (c3x018_root_context_call >= 9 &&
                        c3x018_root_context_call <= 13 &&
                        ((c3x018_parameter("C3X018_FILTER_CALL_MASK_9_13") >>
                          (c3x018_root_context_call - 9)) & 1ULL)));
    // E/V read gates only emit contact on a realized targeted source match.'''
 return one(s,old,new,"ROOT_9_TO_13_MASK")
def main():
 p=argparse.ArgumentParser()
 p.add_argument("--source",required=True)
 p.add_argument("--out-manifest",required=True)
 a=p.parse_args()
 f=Path(a.source)/"src/tt.cpp"
 b=f.read_bytes();c=patch(b.decode()).encode();f.write_bytes(c)
 obj={"schema":"c3x018-case11-TT-five-reader-coalition-mask-9to13-source-v1",
 "before_sha256":hashlib.sha256(b).hexdigest(),
 "after_sha256":hashlib.sha256(c).hexdigest(),
 "one_optional_flag":"C3X018_FILTER_CALL_MASK_9_13",
 "bit_number_to_root_call":{"0":9,"1":10,"2":11,"3":12,"4":13},
 "bounds":{"minimum_accepted_global_write_age":64,"allowed_masks":list(range(32))},
 "limits":["Each bit is a source root-call guard, not immutable interventional node identity after a search trajectory changes",
           "Masks may produce different count of source contacts; record and do not force or retarget events"]}
 o=Path(a.out_manifest);o.parent.mkdir(parents=True,exist_ok=True)
 o.write_text(json.dumps(obj,indent=2)+"\n")
 print("C3X018_CASE11_SOURCE_FIVE_READER_COMBINATION_MASK_READY")
if __name__=="__main__":main()
