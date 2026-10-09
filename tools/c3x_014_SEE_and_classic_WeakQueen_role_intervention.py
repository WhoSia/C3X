#!/usr/bin/env python3
"""C3X 0.14 program-causal site-only intervention, preserves chess move legality.

Exact Stockfish16 after passive native PIN legal/SEE/mobility/WeakQueen site patch:
  OFF: original behavior.
  SEE_UNMASK: remove only pinned attacker exclusion from *static exchange* SEE.
  WQ_OWN: remove only classical WeakQueen evaluation penalty for own blocker.
  WQ_ENEMY: remove only WeakQueen evaluation penalty for attacker-side blocker.
  WQ_BOTH: union of the two score-term interventions.
All actual chess legal move generation remains untouched.
"""
import argparse,hashlib,json
from pathlib import Path
def once(s,a,b,label):
    n=s.count(a)
    if n!=1:raise RuntimeError("INTERVENTION_EXACT_SOURCE_ANCHOR_"+label+"_"+str(n))
    return s.replace(a,b,1)

def patch(root):
    root=Path(root)
    paths={n:root/"src"/n for n in
          ("c3x014_pin_trace.h","position.cpp","evaluate.cpp","search.cpp")}
    old={n:p.read_bytes() for n,p in paths.items()}
    s={n:b.decode() for n,b in old.items()}
    h=s["c3x014_pin_trace.h"]
    h=once(h,"extern C3X014PinTrace c3x014_pin;",
        """extern C3X014PinTrace c3x014_pin;
struct C3X014PinIntervention {
  std::uint64_t see_unmask_effective=0;
  std::uint64_t weak_own_skip_fired=0;
  std::uint64_t weak_enemy_skip_fired=0;
};
extern C3X014PinIntervention c3x014_intervention;
int c3x014_pin_intervention_mode();""","SOURCE_HEADER")
    s["c3x014_pin_trace.h"]=h
    p=s["position.cpp"]
    p=once(p,'#include "position.h"','#include "position.h"\n#include <cstdlib>\n#include <cstring>',"CSTD_HEADERS")
    p=once(p,'C3X014PinTrace c3x014_pin;',
        """C3X014PinTrace c3x014_pin;
C3X014PinIntervention c3x014_intervention;
int c3x014_pin_intervention_mode() {
  static int mode=[]() {
    const char* s=std::getenv("C3X014_PIN_INTERVENTION");
    if (!s || !std::strcmp(s,"OFF")) return 0;
    if (!std::strcmp(s,"SEE_UNMASK")) return 1;
    if (!std::strcmp(s,"WQ_OWN")) return 2;
    if (!std::strcmp(s,"WQ_ENEMY")) return 4;
    if (!std::strcmp(s,"WQ_BOTH")) return 6;
    return -1;
  }();
  return mode;
}""","INTERVENTION_SELECT")
    p=once(p,"          stmAttackers &= ~blockers_for_king(stm);",
        """          if (c3x014_pin_intervention_mode()==1) {
            if (stmAttackers & blockers_for_king(stm))
                ++c3x014_intervention.see_unmask_effective;
          } else {
            stmAttackers &= ~blockers_for_king(stm);
          }""","SEE_STATIC_EXCHANGE_ONLY_FILTER")
    s["position.cpp"]=p
    e=s["evaluate.cpp"]
    e=once(e,'              score -= WeakQueen;',
        """              const int mask=c3x014_pin_intervention_mode();
              const bool own=bool(weakBlockers & pos.pieces(Us));
              const bool enemy=bool(weakBlockers & pos.pieces(Them));
              const bool ownSkip=bool(mask&2) && own;
              const bool enemySkip=bool(mask&4) && enemy;
              if (ownSkip) ++c3x014_intervention.weak_own_skip_fired;
              if (enemySkip) ++c3x014_intervention.weak_enemy_skip_fired;
              if (!(ownSkip || enemySkip)) score -= WeakQueen;""","WEAKQUEEN_NATIVE_EVAL_SCORING_ONLY")
    s["evaluate.cpp"]=e
    q=s["search.cpp"]
    q=once(q,"  c3x014_pin = C3X014PinTrace{};",
        "  c3x014_pin = C3X014PinTrace{};\n  c3x014_intervention = C3X014PinIntervention{};",
        "CLEAR_INTERVENTION_COUNTERS_PER_SEARCH")
    oldline='  sync_cout << "bestmove " << UCI::move(bestThread->rootMoves[0].pv[0], rootPos.is_chess960());'
    add="""  sync_cout << "info string c3x014_pin_causal_mask"
            << " mode=" << c3x014_pin_intervention_mode()
            << " SEE_unmask_fired=" << c3x014_intervention.see_unmask_effective
            << " WQ_own_skip_fired=" << c3x014_intervention.weak_own_skip_fired
            << " WQ_enemy_skip_fired=" << c3x014_intervention.weak_enemy_skip_fired
            << sync_endl;

"""
    q=once(q,oldline,add+oldline,"POST_SEARCH_SOURCE_EVENT_GATE")
    s["search.cpp"]=q
    for n,z in s.items():paths[n].write_text(z)
    return {"schema":"c3x-014-source-SF16-SEE-unmask-and-classic-WeakQueen-role-specific-causal-intervention-v1",
       "source_tag":"Stockfish sf_16 68e1e9b3811e16cad014b590d7443b9063b3eb52",
       "mode_map":{"OFF":0,"SEE_UNMASK":1,"WQ_OWN":2,"WQ_ENEMY":4,"WQ_BOTH":6},
       "actual_chess_move_legality_modified":False,
       "native_change_sites":["Position::see_ge pinned SEE recapture attacker filter only",
                              "classical Evaluation::pieces<QUEEN> WeakQueen score subtract only"],
       "original_sha256":{n:hashlib.sha256(v).hexdigest() for n,v in old.items()},
       "patched_sha256":{n:hashlib.sha256(v.encode()).hexdigest() for n,v in s.items()}}
if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--source",required=True);p.add_argument("--out-manifest",required=True)
    a=p.parse_args();r=patch(a.source)
    f=Path(a.out_manifest);f.parent.mkdir(parents=True,exist_ok=True)
    f.write_text(json.dumps(r,indent=2)+"\n")
    print("C3X014_SOURCE_NATIVE_PIN_COURT_SEE_WEAKQUEEN_ROLE_INTERVENTION_PASS",r["mode_map"],flush=True)
