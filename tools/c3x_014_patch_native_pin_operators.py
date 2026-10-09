#!/usr/bin/env python3
"""Instrument source-native Stockfish16 pin operations; purely observational."""
import argparse,hashlib,json
from pathlib import Path

def replace(s,a,b,label):
    n=s.count(a)
    if n!=1:raise RuntimeError("C3X014_PIN_SOURCE_ANCHOR_"+label+"_"+str(n))
    return s.replace(a,b,1)

def instrument(root):
    root=Path(root);files={n:root/"src"/n for n in ("position.cpp","evaluate.cpp","search.cpp")}
    raw={n:p.read_bytes() for n,p in files.items()}
    src={n:b.decode() for n,b in raw.items()}
    h=root/"src/c3x014_pin_trace.h"
    if h.exists():raise RuntimeError("PIN_TRACE_ALREADY_PATCHED")
    fields=("legal_normal_tests","legal_pinned_tests","legal_pinned_aligned","legal_pinned_rejected",
        "see_calls","see_pinners_guard","see_masked_recapture_episodes","see_masked_attackers",
        "classical_mobility_calls","classical_mobility_nonzero_pin_blockers",
        "classical_mobility_pin_blocker_piece_count","classical_WeakQueen_tests",
        "classical_WeakQueen_hits","classical_WeakQueen_own_blockers","classical_WeakQueen_enemy_blockers")
    hdr="#pragma once\n#include <cstdint>\nnamespace Stockfish {\nstruct C3X014PinTrace {\n"
    hdr+="".join("  std::uint64_t "+k+"=0;\n" for k in fields)
    hdr+="};\nextern C3X014PinTrace c3x014_pin;\n}\n"
    p=src["position.cpp"]
    p=replace(p,'#include "position.h"','#include "position.h"\n#include "c3x014_pin_trace.h"',"HEADER_POSITION")
    p=replace(p,'namespace Stockfish {\n','namespace Stockfish {\nC3X014PinTrace c3x014_pin;\n',"GLOBAL_COUNTER")
    p=replace(p,'  return !(blockers_for_king(us) & from)\n      || aligned(from, to, square<KING>(us));',
"""  ++c3x014_pin.legal_normal_tests;
  const bool isPinned=bool(blockers_for_king(us) & from);
  if (isPinned) {
    ++c3x014_pin.legal_pinned_tests;
    if (aligned(from,to,square<KING>(us))) ++c3x014_pin.legal_pinned_aligned;
    else ++c3x014_pin.legal_pinned_rejected;
  }
  return !isPinned || aligned(from, to, square<KING>(us));""","PIN_LEGAL")
    p=replace(p,'bool Position::see_ge(Move m, Bitboard& occupied, Value threshold) const {\n',
      'bool Position::see_ge(Move m, Bitboard& occupied, Value threshold) const {\n  ++c3x014_pin.see_calls;\n',"SEE_ENTRY")
    p=replace(p,'          stmAttackers &= ~blockers_for_king(stm);',
"""          ++c3x014_pin.see_pinners_guard;
          const Bitboard oldAttackers=stmAttackers;
          stmAttackers &= ~blockers_for_king(stm);
          const Bitboard masked=oldAttackers & ~stmAttackers;
          if (masked) {
            ++c3x014_pin.see_masked_recapture_episodes;
            c3x014_pin.see_masked_attackers += popcount(masked);
          }""","SEE_MASK")
    src["position.cpp"]=p
    e=src["evaluate.cpp"]
    e=replace(e,'#include "evaluate.h"','#include "evaluate.h"\n#include "c3x014_pin_trace.h"',"HEADER_EVAL")
    e=replace(e,'    mobilityArea[Us] = ~(b | pos.pieces(Us, KING, QUEEN) | pos.blockers_for_king(Us) | pe->pawn_attacks(Them));',
"""    const Bitboard pinBlockers=pos.blockers_for_king(Us);
    ++c3x014_pin.classical_mobility_calls;
    if (pinBlockers) {
      ++c3x014_pin.classical_mobility_nonzero_pin_blockers;
      c3x014_pin.classical_mobility_pin_blocker_piece_count += popcount(pinBlockers);
    }
    mobilityArea[Us] = ~(b | pos.pieces(Us, KING, QUEEN) | pinBlockers | pe->pawn_attacks(Them));""","CLASSICAL_MOBILITY")
    e=replace(e,'            if (pos.slider_blockers(pos.pieces(Them, ROOK, BISHOP), s, queenPinners))\n                score -= WeakQueen;',
"""            ++c3x014_pin.classical_WeakQueen_tests;
            const Bitboard weakBlockers=pos.slider_blockers(pos.pieces(Them, ROOK, BISHOP), s, queenPinners);
            if (weakBlockers) {
              ++c3x014_pin.classical_WeakQueen_hits;
              c3x014_pin.classical_WeakQueen_own_blockers += popcount(weakBlockers & pos.pieces(Us));
              c3x014_pin.classical_WeakQueen_enemy_blockers += popcount(weakBlockers & pos.pieces(Them));
              score -= WeakQueen;
            }""","CLASSICAL_WEAKQUEEN")
    src["evaluate.cpp"]=e
    s=src["search.cpp"]
    s=replace(s,'#include "search.h"','#include "search.h"\n#include "c3x014_pin_trace.h"',"HEADER_SEARCH")
    s=replace(s,'void Thread::search() {\n','void Thread::search() {\n  c3x014_pin = C3X014PinTrace{};\n',"RESET")
    info='  sync_cout << "info string c3x014_native_pin_trace"'
    info+=''.join('\n    << " '+k+'=" << c3x014_pin.'+k for k in fields)+'\n    << sync_endl;\n'
    s=replace(s,'  sync_cout << "bestmove " << UCI::move(bestThread->rootMoves[0].pv[0], rootPos.is_chess960());',
      info+'  sync_cout << "bestmove " << UCI::move(bestThread->rootMoves[0].pv[0], rootPos.is_chess960());',"TRACE_BEFORE_BESTMOVE")
    src["search.cpp"]=s
    for n,v in src.items():files[n].write_text(v)
    h.write_text(hdr)
    return {"schema":"c3x-014-genuine-sf16-pin-site-counters-v1",
      "source":"Stockfish sf_16 at 68e1e9b3811e16cad014b590d7443b9063b3eb52",
      "grain":"whole search tree; NOT root pinned-square contribution",
      "counter_fields":fields,"original_sha256":{n:hashlib.sha256(b).hexdigest() for n,b in raw.items()},
      "patched_sha256":{n:hashlib.sha256(v.encode()).hexdigest() for n,v in src.items()}}

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--source",required=True);ap.add_argument("--out-manifest",required=True)
    x=ap.parse_args();r=instrument(x.source)
    p=Path(x.out_manifest);p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(r,indent=2)+"\n")
    print("C3X014_SOURCE_NATIVE_PIN_BRANCHED_TRACE_PATCH_PASS",json.dumps(r["patched_sha256"]),flush=True)
