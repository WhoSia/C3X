#!/usr/bin/env python3
"""Join TT shadow events to within-arm aspiration/root-call/root-candidate context.

Apply after: P4, C3X017 early trace, C3X018 trial-call, C3X018 shadow epoch,
optional payload-only overlay, and optional writer fingerprint overlay.
This is observer-only; call numbers never imply O/F causal identity.
"""
import argparse,hashlib,json
from pathlib import Path

def once(s,a,b,label):
    n=s.count(a)
    if n!=1: raise RuntimeError(f"C3X018_ROOT_TT_CONTEXT_{label}_ANCHOR_{n}")
    return s.replace(a,b,1)

def patch_header(s):
    return once(s, "extern TranspositionTable TT;",
       """// Observer-local root ancestry of TT events; single-thread court only.
extern thread_local unsigned long long c3x018_root_context_call;
extern thread_local int c3x018_root_context_move;
extern TranspositionTable TT;""","HDR")

def patch_tt(s):
    s=once(s, "TranspositionTable TT; // Our global transposition table",
       """TranspositionTable TT; // Our global transposition table
thread_local unsigned long long c3x018_root_context_call = 0;
thread_local int c3x018_root_context_move = 0;""","DEFINITION")
    s=once(s,
       '              << " value=" << value << sync_endl;',
       '              << " value=" << value\n'
       '              << " root_call=" << c3x018_root_context_call\n'
       '              << " root_move=" << c3x018_root_context_move << sync_endl;',
       "EVENT")
    # Optional writer proposal fingerprint must carry the same within-arm ancestry.
    if '<< " prior_value=" << prior_value << sync_endl;' in s:
        s=once(s, '<< " prior_value=" << prior_value << sync_endl;',
          '<< " prior_value=" << prior_value\n'
          '                  << " root_call=" << c3x018_root_context_call\n'
          '                  << " root_move=" << c3x018_root_context_move << sync_endl;',
          "WRITER_FINGERPRINT")
    return s

def patch_search(s):
    s=once(s, "              ++c3x018_root_call_id;",
       """              ++c3x018_root_call_id;
              c3x018_root_context_call = c3x018_root_call_id;
              c3x018_root_context_move = 0;""","CALL_ENTRY")
    s=once(s, "      ss->moveCount = ++moveCount;",
       """      if (rootNode)
          c3x018_root_context_move = int(move);
      ss->moveCount = ++moveCount;""","CANDIDATE_ENTRY")
    return s

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source",required=True)
    p.add_argument("--out-manifest",required=True)
    a=p.parse_args()
    root=Path(a.source)/"src"
    changed={}
    for name,fun in (("tt.h",patch_header),("tt.cpp",patch_tt),("search.cpp",patch_search)):
        f=root/name;old=f.read_bytes();new=fun(old.decode()).encode()
        f.write_bytes(new)
        changed[name]={"before_sha256":hashlib.sha256(old).hexdigest(),
                       "after_sha256":hashlib.sha256(new).hexdigest()}
    dest=Path(a.out_manifest);dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(json.dumps({
      "schema":"c3x018-root-aspiration-to-TT-provenance-observer-v1",
      "source_changes":changed,
      "event_fields":["root_call","root_move"],
      "cautions":["Thread-local only; run Threads=1",
                  "Root move remains last candidate until next root call; do not treat events after root search as child events",
                  "root_call is within-arm identifier; O/F equal numbers do not imply equal causal identity",
                  "TT cutoff branch is not full TT use coverage",
                  "Verify exact original P4 UCI core and no trace truncation"]
    },indent=2)+"\n")
    print("C3X018_ROOT_TT_CONTEXT_SOURCE_PATCH_APPLIED")
if __name__=="__main__":main()
