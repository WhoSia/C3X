#!/usr/bin/env python3
"""One-source-site guard on SF16 TT V override: optional writer age/root/ply/bound.

Use after full December physical TT + source ancestry + age witness pipeline.
The original unfiltered V branch is unchanged if no extra C3X018_FILTER_* set.
"""
import argparse,hashlib,json
from pathlib import Path
def one(s,a,b,label):
 n=s.count(a)
 if n!=1:raise RuntimeError(f"C3X018_POSTHOC_AGE_{label}_ANCHOR_COUNT_{n}")
 return s.replace(a,b,1)
def patch(s):
 needle='''                   && exact_key && c3x018_target(key, slot, epoch);
    // E/V read gates only emit contact on a realized targeted source match.'''
 replacement='''                   && exact_key && c3x018_target(key, slot, epoch)
                   && (!std::getenv("C3X018_FILTER_MIN_WRITE_AGE") ||
                       (known && c3x018_write_serial >= it->second.writer_serial &&
                        c3x018_write_serial - it->second.writer_serial >=
                          c3x018_parameter("C3X018_FILTER_MIN_WRITE_AGE")))
                   && (!std::getenv("C3X018_FILTER_ROOT_CALL") ||
                       c3x018_root_context_call == c3x018_parameter("C3X018_FILTER_ROOT_CALL"))
                   && (!std::getenv("C3X018_FILTER_ROOT_MOVE") ||
                       c3x018_root_context_move == int(c3x018_parameter("C3X018_FILTER_ROOT_MOVE")))
                   && (!std::getenv("C3X018_FILTER_PLY") ||
                       ply == int(c3x018_parameter("C3X018_FILTER_PLY")))
                   && (!std::getenv("C3X018_FILTER_RAW_BOUND") ||
                       int(slot->bound()) == int(c3x018_parameter("C3X018_FILTER_RAW_BOUND")));
    // E/V read gates only emit contact on a realized targeted source match.'''
 return one(s,needle,replacement,"GUARD")
def main():
 p=argparse.ArgumentParser()
 p.add_argument("--source",required=True)
 p.add_argument("--out-manifest",required=True)
 a=p.parse_args()
 f=Path(a.source)/"src/tt.cpp"
 old=f.read_bytes();new=patch(old.decode()).encode();f.write_bytes(new)
 obj={"schema":"c3x018-adaptive-TT-consumer-event-age-rootcall-bound-ply-guard-v1",
      "source_before_sha256":hashlib.sha256(old).hexdigest(),
      "source_after_sha256":hashlib.sha256(new).hexdigest(),
      "optional_predicates":["C3X018_FILTER_MIN_WRITE_AGE","C3X018_FILTER_ROOT_CALL",
                 "C3X018_FILTER_ROOT_MOVE","C3X018_FILTER_PLY","C3X018_FILTER_RAW_BOUND"],
      "invariants":["no env predicate means original physical V unchanged",
        "source guard tests current writer serial minus last writer serial in same cold process",
        "root context must be matched before suppressing an actual V evaluation correction",
        "if source lineage changes, do not substitute another event"],
      "limits":["Adaptive exploration after seeing December role responses",
          "A matched source root call number across arms is not in itself causal equivalence",
          "No proof of unique natural TT mediation or independent data transport"]}
 out=Path(a.out_manifest);out.parent.mkdir(parents=True,exist_ok=True)
 out.write_text(json.dumps(obj,indent=2)+"\n")
 print("C3X018_ADAPTIVE_EVENT_SPECIFIC_TT_V_SOURCE_FILTER_PATCHED")
if __name__=="__main__":main()
