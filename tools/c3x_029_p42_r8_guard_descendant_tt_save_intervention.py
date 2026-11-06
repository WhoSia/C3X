#!/usr/bin/env python3
"""C3X P42/R8: target-branch TTEntry::save intervention, NOT causal proof.

Apply after original 0.27 C3b + P42/R5 actual-key overlay. Source pin must
be checked by the build chain. Existing off-mode is observational-only.
"""
import argparse,hashlib,json
from pathlib import Path

SEARCH_ANCHOR="thread_local C3X042_R5_Local c3x042_r5;"
AFTER_DO="  c3x042_r5.did_move=true;"
BEFORE_UNDO="  c3x042_r5.child_returned=true;"
TT_ANCHOR="void TTEntry::save(Key k, Value v, bool pv, Bound b, Depth d, Move m, Value ev) {"
TT_INCLUDE='#include "tt.h"'

EXPORTED='''\nthread_local bool c3x042_r8_target_descendant=false;
thread_local unsigned long long c3x042_r8_tt_attempts=0;
thread_local unsigned long long c3x042_r8_tt_suppressed=0;
'''\n\nGLOBALS="""
// P42/R8: single-thread source intervention restricted to the actually
// executed descendant of the *already* source-selected Game14 guard.
void c3x042_r8_end_trace() {
  const char* dest=std::getenv("C3X042_R5_LOCAL_TRACE");
  if (!dest || !*dest) return;
  if (auto* f=std::fopen(dest,"a")) {
    std::fprintf(f,"c3x042_r8 attempts=%llu suppressed=%llu\\n",
      c3x042_r8_tt_attempts,c3x042_r8_tt_suppressed);
    std::fclose(f);
  }
}
"""

TT_PROBE="""
  if (c3x042_r8_target_descendant) {
      ++c3x042_r8_tt_attempts;
      const char* drop=std::getenv("C3X042_R8_DROP_DESCENDANT_TT_SAVE");
      if (drop && drop[0]=='1' && drop[1]=='\\0') {
          ++c3x042_r8_tt_suppressed;
          return;
      }
  }
"""

def once(s,needle,replacement,tag):
    n=s.count(needle)
    if n!=1:raise ValueError(f"P42_R8_HOLD_{tag}_ANCHOR_COUNT_{n}")
    return s.replace(needle,replacement,1)

def patch_search(s):
    if "c3x042_r8_target_descendant" in s:
        raise ValueError("P42_R8_HOLD_ALREADY_PATCHED_SEARCH")
    # The search helper lives in Stockfish's anonymous namespace, while
    # tt.cpp requires externally linked Stockfish::thread_local symbols.
    s=once(s,"namespace Stockfish {\n",
           "namespace Stockfish {\n"+EXPORTED+"\n","EXPORTED_GLOBALS")
    s=once(s,SEARCH_ANCHOR,GLOBALS+"\n"+SEARCH_ANCHOR,"LOCAL_HELPER")
    s=once(s,AFTER_DO,AFTER_DO+"\n  c3x042_r8_target_descendant=true;\n  c3x042_r8_tt_attempts=0;\n  c3x042_r8_tt_suppressed=0;","AFTER_DO")
    s=once(s,BEFORE_UNDO,BEFORE_UNDO+"\n  c3x042_r8_target_descendant=false;\n  c3x042_r8_end_trace();","BEFORE_UNDO")
    return s

def patch_tt(s):
    if "c3x042_r8_tt_attempts" in s:raise ValueError("P42_R8_HOLD_ALREADY_PATCHED_TT")
    s=once(s,TT_INCLUDE,TT_INCLUDE+'\n#include <cstdlib>',"HEADER")
    extern="""
extern thread_local bool c3x042_r8_target_descendant;
extern thread_local unsigned long long c3x042_r8_tt_attempts;
extern thread_local unsigned long long c3x042_r8_tt_suppressed;
"""
    return once(s,TT_ANCHOR,extern+"\n"+TT_ANCHOR+TT_PROBE,"TTENTRY_SAVE")

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source",required=True)
    p.add_argument("--out-manifest",required=True)
    a=p.parse_args()
    root=Path(a.source)/"src"
    paths=[root/"search.cpp",root/"tt.cpp"]
    old=[p.read_bytes() for p in paths]
    new=[patch_search(old[0].decode()).encode(),patch_tt(old[1].decode()).encode()]
    # Compute both completely before any byte mutation to avoid half-patches.
    for p,b in zip(paths,new):p.write_bytes(b)
    out=Path(a.out_manifest);out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps({
      "schema":"c3x042-r8-guard-descendant-TTEntry-save-intervention-v1",
      "source_sha256_before":{p.name:hashlib.sha256(b).hexdigest() for p,b in zip(paths,old)},
      "source_sha256_after":{p.name:hashlib.sha256(b).hexdigest() for p,b in zip(paths,new)},
      "control_variable":"C3X042_R8_DROP_DESCENDANT_TT_SAVE",
      "unit":"only entered exact source-targeted Game14 guard descendant",
      "not_total_TT_side_effect_isolation":True,
      "not_natural_mediation":True,
      "no_native_success_claim":True
    },sort_keys=True,indent=2)+"\n")
    print("C3X042_R8_SOURCE_PATCHED_NATIVE_UNVERIFIED")
if __name__=="__main__":main()
