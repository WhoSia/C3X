#!/usr/bin/env python3
"""C3X0.14 surgical SEE unmask ONLY the original root royal-pin object.

Apply after original passive C3X014 PIN site telemetry, not global causal patch.
No move-gen legality, NNUE, WeakQueen or other SEE pinned pieces modified.
"""
import argparse,hashlib,json
from pathlib import Path
def one(s,a,b,k):
    n=s.count(a)
    if n!=1:raise RuntimeError("C3X014_ROOT_OBJECT_PIN_SOURCE_ANCHOR_"+k+"_"+str(n))
    return s.replace(a,b,1)
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--source",required=True)
    ap.add_argument("--out-manifest",required=True)
    x=ap.parse_args()
    root=Path(x.source);files={p:root/"src"/p for p in
        ("position.cpp","search.cpp","c3x014_pin_trace.h")}
    raw={p:f.read_bytes() for p,f in files.items()}
    s={p:b.decode() for p,b in raw.items()}
    h=s["c3x014_pin_trace.h"]
    h=one(h,"extern C3X014PinTrace c3x014_pin;",
    """extern C3X014PinTrace c3x014_pin;
struct C3X014RootObjectSEE {
  int arm=0;
  int pinned_square=-1, pinner_square=-1, king_square=-1;
  Piece root_pinned_piece=NO_PIECE, root_pinner_piece=NO_PIECE;
  Color root_pinned_side=WHITE;
  std::uint64_t considered_guard=0, fired=0;
};
extern C3X014RootObjectSEE c3x014_root_obj;
void c3x014_root_object_prepare(const Position& root);""","OBJECT_HEADER_TYPE")
    # Position referenced in header only via forward-declaration include
    h=one(h,"namespace Stockfish {\n","namespace Stockfish {\nclass Position;\n","POSITION_FORWARD_DECL")
    s["c3x014_pin_trace.h"]=h
    p=s["position.cpp"]
    p=one(p,'#include "position.h"','#include "position.h"\n#include <cstdlib>\n#include <cstring>',"CSTDLIB")
    p=one(p,'C3X014PinTrace c3x014_pin;',
    r'''C3X014PinTrace c3x014_pin;
C3X014RootObjectSEE c3x014_root_obj;
void c3x014_root_object_prepare(const Position& root) {
  c3x014_root_obj=C3X014RootObjectSEE{};
  const char* arm=std::getenv("C3X014_PIN_ROOT_OBJECT_ARM");
  const char* source=std::getenv("C3X014_PIN_ROOT_SQUARE_ID");
  const char* sniper=std::getenv("C3X014_PIN_ROOT_PINNER_ID");
  if (!arm || !source || !sniper) { c3x014_root_obj.arm=-1; return; }
  if (std::strcmp(arm,"OFF") == 0) c3x014_root_obj.arm=0;
  else if (std::strcmp(arm,"ROOT_OBJECT_SEE_UNMASK")==0) c3x014_root_obj.arm=1;
  else { c3x014_root_obj.arm=-1; return; }
  int sq=std::atoi(source), pn=std::atoi(sniper);
  if (sq<0 || sq>=64 || pn<0 || pn>=64 || sq==pn) {
    c3x014_root_obj.arm=-1; return;
  }
  c3x014_root_obj.pinned_square=sq;
  c3x014_root_obj.pinner_square=pn;
  c3x014_root_obj.root_pinned_piece=root.piece_on(Square(sq));
  c3x014_root_obj.root_pinner_piece=root.piece_on(Square(pn));
  if (c3x014_root_obj.root_pinned_piece==NO_PIECE ||
      c3x014_root_obj.root_pinner_piece==NO_PIECE) {
    c3x014_root_obj.arm=-1; return;
  }
  const Color us=color_of(c3x014_root_obj.root_pinned_piece);
  c3x014_root_obj.root_pinned_side=us;
  c3x014_root_obj.king_square=int(root.square<KING>(us));
  if (color_of(c3x014_root_obj.root_pinner_piece)==us ||
      !(root.blockers_for_king(us)&square_bb(Square(sq))) ||
      !(root.pinners(~us)&square_bb(Square(pn)))) {
    c3x014_root_obj.arm=-1;
  }
}''',"OBJECT_PREPARE")
    p=one(p,"          stmAttackers &= ~blockers_for_king(stm);",
    r'''          Bitboard c3x014_SEE_exclusions=blockers_for_king(stm);
          if (c3x014_root_obj.arm==1
              && stm==c3x014_root_obj.root_pinned_side
              && c3x014_root_obj.pinned_square>=0
              && c3x014_root_obj.pinner_square>=0) {
              const Square p=Square(c3x014_root_obj.pinned_square);
              const Square a=Square(c3x014_root_obj.pinner_square);
              const Bitboard pinnedBit=square_bb(p);
              const Bitboard pinnerBit=square_bb(a);
              if ((stmAttackers & pinnedBit)
                  && (c3x014_SEE_exclusions & pinnedBit)) {
                  ++c3x014_root_obj.considered_guard;
                  if (piece_on(p)==c3x014_root_obj.root_pinned_piece
                      && piece_on(a)==c3x014_root_obj.root_pinner_piece
                      && int(square<KING>(stm))==c3x014_root_obj.king_square
                      && (pinners(~stm)&pinnerBit)
                      && (occupied&pinnerBit)) {
                      c3x014_SEE_exclusions &= ~pinnedBit;
                      ++c3x014_root_obj.fired;
                  }
              }
          }
          stmAttackers &= ~c3x014_SEE_exclusions;''',"TARGETED_SEE_MASK_ONE_PINNED_OBJECT")
    s["position.cpp"]=p
    q=s["search.cpp"]
    q=one(q,"  c3x014_pin = C3X014PinTrace{};",
        "  c3x014_pin = C3X014PinTrace{};\n  c3x014_root_object_prepare(rootPos);","OBJECT_INIT_AT_THREAD_SEARCH")
    old='  sync_cout << "bestmove " << UCI::move(bestThread->rootMoves[0].pv[0], rootPos.is_chess960());'
    new=r'''  sync_cout << "info string c3x014_root_object_see"
            << " arm=" << c3x014_root_obj.arm
            << " pinned_square=" << c3x014_root_obj.pinned_square
            << " pinner_square=" << c3x014_root_obj.pinner_square
            << " king_square=" << c3x014_root_obj.king_square
            << " considered=" << c3x014_root_obj.considered_guard
            << " target_fired=" << c3x014_root_obj.fired
            << sync_endl;
'''+old
    q=one(q,old,new,"OBJECT_EVENT_AFTER_SEARCH")
    s["search.cpp"]=q
    for n,v in s.items():files[n].write_text(v)
    info={"schema":"c3x-014-native-SEE-root-pinned-object-identity-source-conditional-unmask-v1",
       "SF16_original_commit":"68e1e9b3811e16cad014b590d7443b9063b3eb52",
       "modes":["OFF","ROOT_OBJECT_SEE_UNMASK"],
       "legal_move_generation_untouched":True,
       "source_guard":"Actual original pinned-piece and pinner Piece identities, original king square and side, blockers_for_king, pinners, SEE occupied pinner, stmAttackers includes exact root pinned piece. Only original root pinned object bit is unmasked, while other pinned attackers remain masked.",
       "source_is_source_native":True,
       "source_type_scope":"SEE only, NOT NNUE or WeakQueen, not altering actual legal chess moves",
       "orig_SHA256":{n:hashlib.sha256(b).hexdigest() for n,b in raw.items()},
       "new_SHA256":{n:hashlib.sha256(v.encode()).hexdigest() for n,v in s.items()}}
    f=Path(x.out_manifest);f.parent.mkdir(parents=True,exist_ok=True);f.write_text(json.dumps(info,indent=2)+"\n")
    print("C3X014_TRUE_OBJECT_GUARDED_NATIVE_PIN_SEE_SOURCE_PATCH_PASS",info["new_SHA256"],flush=True)
if __name__=="__main__":main()
