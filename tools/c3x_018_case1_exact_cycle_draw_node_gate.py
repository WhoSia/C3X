#!/usr/bin/env python3
"""C3X018 exact case1 single-node chess cycle/draw suppression experiment.

After native observer root ancestry patch. G=cycle-only, D=immediate-draw
only, GD=both. Contact matches exact same key64/rootcall/root candidate/ply.
No synthetic chess history or TT write; this is adaptive after observing
source-positive repetition evidence.
"""
import argparse,hashlib,json
from pathlib import Path
def one(s,a,b,k):
 n=s.count(a)
 if n!=1:raise RuntimeError(f"C3X018_EXACT_CYCLE_{k}_SOURCE_COUNT_{n}")
 return s.replace(a,b,1)

SOURCE_KEY=1393645049232160636
ROOT_MOVE=2313

def patch(s):
 s=one(s,"namespace Stockfish {", "#include <cstdlib>\n#include <cstring>\nnamespace Stockfish {","INCLUDE")
 helper=r"""
// Exact selective counterfactual at the one observed source node.
namespace {
unsigned long long c3x018_exact_draw_gate_hits = 0;
bool c3x018_exact_draw_target(Position& pos, int ply, const char* which) {
    const char* mode=std::getenv("C3X018_EXACT_DRAW_SUPPRESS");
    if (!mode || !*mode) return false;
    const bool selected=std::strcmp(mode,"GD")==0 ||
        (std::strcmp(mode,"G")==0 && std::strcmp(which,"cycle")==0) ||
        (std::strcmp(mode,"D")==0 && std::strcmp(which,"immediate")==0);
    if (!selected || c3x018_root_context_call!=1 ||
        c3x018_root_context_move!=2313 || ply!=1 ||
        uint64_t(pos.key())!=1393645049232160636ULL)
        return false;
    ++c3x018_exact_draw_gate_hits;
    sync_cout << "info string c3x018_exact_draw_intervention"
              << " site=" << which << " key64=" << uint64_t(pos.key())
              << " root_call=" << c3x018_root_context_call
              << " root_move=" << c3x018_root_context_move
              << " ply=" << ply
              << " contact=" << c3x018_exact_draw_gate_hits << sync_endl;
    return true;
}
} // C3X018_EXACT_DRAW_TARGET
"""
 s=one(s,"// C3X018 draw predicate observer, one search worker.",
       helper+"\n// C3X018 draw predicate observer, one search worker.",
       "FUNCTION_PRELUDE")
 s=one(s,
'''    return yes;
}
bool c3x018_cycle_check(Position& pos, int ply) {''',
'''    if (yes && c3x018_exact_draw_target(pos,ply,"immediate"))
        return false;
    return yes;
}
bool c3x018_cycle_check(Position& pos, int ply) {''',"DRAW_SUPPRESS")
 s=one(s,
'''    return yes;
}
} // C3X018_DRAW_OBSERVER''',
'''    if (yes && c3x018_exact_draw_target(pos,ply,"cycle"))
        return false;
    return yes;
}
} // C3X018_DRAW_OBSERVER''',"CYCLE_SUPPRESS")
 return s

def main():
 p=argparse.ArgumentParser()
 p.add_argument("--source",required=True);p.add_argument("--out-manifest",required=True)
 a=p.parse_args();f=Path(a.source)/"src/search.cpp"
 before=f.read_bytes();after=patch(before.decode()).encode();f.write_bytes(after)
 result={"schema":"c3x018-case1-exact-source-game-cycle-draw-double-gate-v1",
 "before_sha256":hashlib.sha256(before).hexdigest(),
 "after_sha256":hashlib.sha256(after).hexdigest(),
 "fixed_target":{"full64":SOURCE_KEY,"root_call":1,"root_move":ROOT_MOVE,"ply":1},
 "modes":{"G":"block upcoming game cycle only at this key","D":"block immediate draw only at this key","GD":"both"},
 "claims":["Actual true predicate contact logged and only same exact source node suppressed",
           "Site G and D distinct; if upstream cycle cutoff happens D may not fire",
           "Original history and FEN6 controls remain unchanged"],
 "limits":["Case1 chosen adaptively after observed first divergence, not a preregistered effect on independent games",
           "Suppressing draw detection at one call is an artificial diagnostic counterfactual, not a recommendation for chess engine play",
           "No unique TT writer-reader mediation"]}
 o=Path(a.out_manifest);o.parent.mkdir(parents=True,exist_ok=True)
 o.write_text(json.dumps(result,indent=2)+"\n")
 print("C3X018_EXACT_SINGLE_DRAW_NODE_SOURCE_OVERLAY_APPLIED")
if __name__=="__main__":main()
