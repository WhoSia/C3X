#!/usr/bin/env python3
"""Stockfish16 source V exact two root-call consumer gate, not a 9..13 mask.

Pass only new source-selected calls, age, bound, candidate and search window.
Do not add date, position or predetermined call indices to source patch.
Apply after c3x_018_adaptive_writer_age_root_call_V_gate.py.
"""
import argparse,hashlib,json
from pathlib import Path

def one(s,a,b,key):
    n=s.count(a)
    if n!=1:raise RuntimeError(f"C3X018_JAN_PAIR_{key}_ANCHOR_COUNT_{n}")
    return s.replace(a,b,1)

def patch(s):
    old='''                   && (!std::getenv("C3X018_FILTER_RAW_BOUND") ||
                       int(slot->bound()) == int(c3x018_parameter("C3X018_FILTER_RAW_BOUND")));
    // E/V read gates only emit contact on a realized targeted source match.'''
    new='''                   && (!std::getenv("C3X018_FILTER_RAW_BOUND") ||
                       int(slot->bound()) == int(c3x018_parameter("C3X018_FILTER_RAW_BOUND")))
                   && (!std::getenv("C3X018_FILTER_PAIR_CALL_A") ||
                       (c3x018_root_context_call == c3x018_parameter("C3X018_FILTER_PAIR_CALL_A")
                        || c3x018_root_context_call == c3x018_parameter("C3X018_FILTER_PAIR_CALL_B")))
                   && (!std::getenv("C3X018_FILTER_MAX_PLY") ||
                       (ply >= 1 && ply <= int(c3x018_parameter("C3X018_FILTER_MAX_PLY"))))
                   && (!std::getenv("C3X018_FILTER_WINDOW_WIDTH_MAX") ||
                       (beta > alpha &&
                        beta - alpha <= int(c3x018_parameter("C3X018_FILTER_WINDOW_WIDTH_MAX"))));
    // E/V read gates only emit contact on a realized targeted source match.'''
    return one(s,old,new,"PAIR_GATE")

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source",required=True)
    p.add_argument("--out-manifest",required=True)
    a=p.parse_args()
    f=Path(a.source)/"src/tt.cpp"
    old=f.read_bytes();new=patch(old.decode()).encode();f.write_bytes(new)
    obj={"schema":"c3x018-January-writer-reader-dual-aspiration-call-pair-gate-v1",
      "file":"src/tt.cpp",
      "source_before_sha256":hashlib.sha256(old).hexdigest(),
      "source_after_sha256":hashlib.sha256(new).hexdigest(),
      "optional_env":["C3X018_FILTER_PAIR_CALL_A","C3X018_FILTER_PAIR_CALL_B",
                      "C3X018_FILTER_MAX_PLY","C3X018_FILTER_WINDOW_WIDTH_MAX"],
      "previous_existing_env":["C3X018_FILTER_MIN_WRITE_AGE","C3X018_FILTER_ROOT_MOVE",
                              "C3X018_FILTER_PLY","C3X018_FILTER_RAW_BOUND"],
      "invariants":["All additional predicates conjunctive with physical full64 slot epoch V gate",
                    "Root-call pair only contains source dynamically preselected IDs, no hard-coded case11 calls",
                    "Empty pair A=B=0 cannot block a real rootcall","all C++ source search state otherwise unchanged"],
      "limits":["Two within-arm root-call handles do not imply path-invariant recursive search nodes",
               "Same physical carrier can be read at other source sites not conforming to pair filters",
               "No synthetic TT writer or exact independent natural mediator assumed"]}
    o=Path(a.out_manifest);o.parent.mkdir(parents=True,exist_ok=True)
    o.write_text(json.dumps(obj,indent=2)+"\n")
    print("C3X018_JANUARY_PAIR_CALL_AND_WINDOW_V_GATE_SOURCE_PATCHED")
if __name__=="__main__":main()
