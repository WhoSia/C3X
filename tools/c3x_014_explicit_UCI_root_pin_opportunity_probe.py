#!/usr/bin/env python3
"""C3X 0.14 post-hoc UCI root-opportunity probe: no GO search."""
import argparse,hashlib,json
from pathlib import Path

def change(s,a,b,label):
    n=s.count(a)
    if n!=1:raise RuntimeError("ROOT_PROBE_SOURCE_ANCHOR_"+label+"_"+str(n))
    return s.replace(a,b,1)
def patch(root):
    root=Path(root)
    path=root/"src/uci.cpp";raw=path.read_bytes();s=raw.decode()
    if "c3x014_pin_trace.h" not in (root/"src/search.cpp").read_text():raise RuntimeError("ROOT_SITE_PARENT_PATCH_REQUIRED")
    s=change(s,'#include "uci.h"','#include "uci.h"\n#include "c3x014_pin_trace.h"',"INCLUDE_PIN_NATIVE")
    old='      else if (token == "eval")     trace_eval(pos);'
    new=r'''      else if (token == "c3x014_root_probe")
      {
          // NEVER use in same process as a measured go search. The caller uses
          // a fresh no-go engine process; these are explicit source OPPORTUNITY
          // probes, NOT organically selected search nodes.
          c3x014_pin = C3X014PinTrace{};
          c3x014_pin.root_key=pos.key();
          int pseudo=0, legal=0, captures=0, seeSamples=0, seePass=0;
          auto record=[&](Move m) {
              ++pseudo;
              const bool allowed=pos.legal(m);
              if (!allowed) return;
              ++legal;
              if (pos.capture(m)) {
                  ++captures;
                  for (Value t : {Value(-100), Value(0), Value(100)}) {
                      ++seeSamples;
                      if (pos.see_ge(m,t)) ++seePass;
                  }
              }
          };
          if (pos.checkers()) {
              for (const auto& ex : MoveList<EVASIONS>(pos)) record(ex.move);
          } else {
              for (const auto& ex : MoveList<NON_EVASIONS>(pos)) record(ex.move);
          }
          const bool inCheck=bool(pos.checkers());
          if (!inCheck) {
              // The original Eval::trace performs classical static evaluation
              // even with NNUE enabled; read-only measurement runs *without go*.
              const std::string unused=Eval::trace(pos);
              (void)unused;
          }
          sync_cout << "info string c3x014_explicit_root_probe"
                    << " key=" << pos.key()
                    << " in_check=" << int(inCheck)
                    << " pseudo=" << pseudo << " legal=" << legal
                    << " captures=" << captures
                    << " see_samples=" << seeSamples << " see_pass=" << seePass
                    << " root_legal_pinned_checks=" << c3x014_pin.root_legal_pinned_checks
                    << " root_legal_pin_rejects=" << c3x014_pin.root_legal_pin_rejects
                    << " root_see_pinned_masks=" << c3x014_pin.root_see_pinned_masks
                    << " root_mobility_pin_blockers=" << c3x014_pin.root_mobility_pin_blockers
                    << " root_WeakQueen_hits=" << c3x014_pin.root_WeakQueen_hits
                    << " classical_mobility_nonzero_pin_blockers=" << c3x014_pin.classical_mobility_nonzero_pin_blockers
                    << " classical_WeakQueen_hits=" << c3x014_pin.classical_WeakQueen_hits
                    << " classical_WeakQueen_own_blockers=" << c3x014_pin.classical_WeakQueen_own_blockers
                    << " classical_WeakQueen_enemy_blockers=" << c3x014_pin.classical_WeakQueen_enemy_blockers
                    << sync_endl;
      }
      else if (token == "eval")     trace_eval(pos);'''
    s=change(s,old,new,"EXPLICIT_UCI_NO_GO_COMMAND")
    path.write_text(s)
    return {"schema":"c3x-014-source-native-post-hoc-root-opportunity-probe-v1",
       "game_search":False,
       "root_method_sources":["Position::legal on pseudo root moves","Position::see_ge on legal root captures at -100,0,+100",
          "Eval::trace classical static root evaluation if not in check"],
       "probe_site":"UCI command c3x014_root_probe on original fully replayed position in a fresh standalone engine process",
       "guard":"No go command is issued; probe is never conflated with naturally selected search calls",
       "original_source_sha256":hashlib.sha256(raw).hexdigest(),
       "patched_source_sha256":hashlib.sha256(s.encode()).hexdigest()}
if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--source",required=True);ap.add_argument("--out-manifest",required=True)
    a=ap.parse_args();r=patch(a.source)
    dest=Path(a.out_manifest);dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(json.dumps(r,indent=2)+"\n")
    print("C3X014_FRESH_POSTHOC_ROOT_OPERATOR_PROBE_SOURCE_PATCH_PASS",r["patched_source_sha256"],flush=True)
