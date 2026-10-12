#!/usr/bin/env python3
"""P14-P4 minimal original SF16 source-only C++ root attempt/score observer.
No cascaded historical TT/writer overlays, no unnecessary large machine traces.
The human-reviewed source spans are byte-reversible.
"""
import argparse
from pathlib import Path
Q="""    // At non-PV nodes we check for an early TT cutoff
    if (  !PvNode
        && tte->depth() >= ttDepth
        && ttValue != VALUE_NONE // Only in case of TT access race or if !ttHit
        && (tte->bound() & (ttValue >= beta ? BOUND_LOWER : BOUND_UPPER)))
        return ttValue;"""
NEWQ=Q.replace("        return ttValue;","""    {
        if (!c3x025_p14p4_skip_one(int(ss->ply),int(ttValue),int(beta),int(pos.rule50_count())))
            return ttValue;
    }""")
INCLUDE='#include <cstdlib>\n'
SCOPE='namespace Stockfish {\n'
CPP=r"""
// The ONLY mutation is skipping precisely the first original eligible
// qsearch bounded numeric TT early return in the physical SCORE arm.
// All root audit output is read-only and deliberately small.
static thread_local bool c3x025_p14p4_first=false;
bool c3x025_p14p4_trace() {
    return std::getenv("C3X025_P14P4_TRACE") != nullptr;
}
bool c3x025_p14p4_skip_one(int ply,int value,int beta,int rule50) {
    if (!c3x025_p14p4_first) {
        c3x025_p14p4_first=true;
        const char* arm=std::getenv("C3X025_P14P4_ARM");
        const bool change=arm && std::strcmp(arm,"SCORE")==0;
        if (c3x025_p14p4_trace())
            sync_cout << "info string c3x025_p14p4 event=FIRST_QSCORE"
                      << " changed=" << int(change) << " ply=" << ply
                      << " value=" << value << " beta=" << beta
                      << " rule50=" << rule50 << sync_endl;
        return change;
    }
    return false;
}
"""
ROOT_ASSIGN="              bestValue = Stockfish::search<Root>(rootPos, ss, alpha, beta, adjustedDepth, false);"
ROOT_NEW=ROOT_ASSIGN+"""
              // Source event AFTER the original root search returned but BEFORE
              // stable sort / alpha-beta aspiration window adjustment.
              if (c3x025_p14p4_trace())
              {
                  static thread_local unsigned attempt=0;
                  ++attempt;
                  sync_cout << "info string c3x025_p14p4 event=ROOT_ATTEMPT"
                    << " seq=" << attempt << " root_depth=" << int(rootDepth)
                    << " effective_depth=" << int(adjustedDepth)
                    << " pv_idx=" << pvIdx << " alpha=" << int(alpha)
                    << " beta=" << int(beta) << " returned=" << int(bestValue)
                    << " window_class=" << (bestValue<=alpha ? "FAIL_LOW" : bestValue>=beta ? "FAIL_HIGH" : "INSIDE")
                    << " count=" << rootMoves.size() << sync_endl;
                  for (const auto& rm:rootMoves) {
                      sync_cout << "info string c3x025_p14p4 event=ROOT_STORED_CANDIDATE"
                        << " seq=" << attempt
                        << " move=" << (rm.pv.empty()?0u:unsigned(rm.pv[0]))
                        << " score=" << int(rm.score)
                        << " uci=" << int(rm.uciScore)
                        << " avg=" << int(rm.averageScore)
                        << " prior=" << int(rm.previousScore)
                        << " lo=" << int(rm.scoreLowerbound)
                        << " hi=" << int(rm.scoreUpperbound)
                        << " pvlen=" << rm.pv.size() << sync_endl;
                  }
              }"""
ROOT_MOVE="              rm.score = -VALUE_INFINITE;\n      }\n\n      if (value > bestValue)"
ROOT_MOVE_NEW="""              rm.score = -VALUE_INFINITE;
          // Original C++ actually evaluated this move, even if the sort-visible
          // score is then erased. A numeric result is not always an exact value.
          if (c3x025_p14p4_trace())
              sync_cout << "info string c3x025_p14p4 event=ROOT_MOVE_RESULT"
                << " root_depth=" << int(thisThread->rootDepth)
                << " move=" << unsigned(move)
                << " move_order=" << int(moveCount)
                << " returned=" << int(value)
                << " alpha=" << int(alpha) << " beta=" << int(beta)
                << " stored=" << int(rm.score)
                << " lo=" << int(rm.scoreLowerbound)
                << " hi=" << int(rm.scoreUpperbound)
                << sync_endl;
      }

      if (value > bestValue)"""
def change(s,old,new,label):
 if s.count(old)!=1:raise ValueError("P14P4_MISSING_OR_AMBIGUOUS_ORIGINAL_"+label+str(s.count(old)))
 return s.replace(old,new,1)
def patch(raw):
 s=raw.decode()
 s=change(s,SCOPE,SCOPE+CPP+"\n","scope")
 s=change(s,'#include <cassert>\n','#include <cassert>\n'+INCLUDE,"include")
 s=change(s,Q,NEWQ,"native_qcutoff")
 s=change(s,ROOT_ASSIGN,ROOT_NEW,"root_attempt")
 s=change(s,ROOT_MOVE,ROOT_MOVE_NEW,"root_move")
 result=s.encode()
 if undo(result)!=raw:raise ValueError("P14P4_EXACT_BYTE_INVERSE_FAIL")
 return result
def undo(post):
 s=post.decode()
 s=change(s,ROOT_MOVE_NEW,ROOT_MOVE,"undo_move")
 s=change(s,ROOT_NEW,ROOT_ASSIGN,"undo_attempt")
 s=change(s,NEWQ,Q,"undo_q")
 s=change(s,'#include <cassert>\n'+INCLUDE,'#include <cassert>\n',"undo_include")
 s=change(s,SCOPE+CPP+"\n",SCOPE,"undo_scope")
 return s.encode()
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--root',required=True);ap.add_argument('--out',required=True)
 a=ap.parse_args()
 p=Path(a.root)/'src/search.cpp'
 original=p.read_bytes()
 # Git HEAD for official SF16 is the strong upstream identity; check one source gate only.
 import hashlib,json
 original_digest=hashlib.sha256(original).hexdigest()
 if original_digest!="21b79baa7ce9dabec5b3b9e3854bed9869a1935277247832e550cf395bccd644":
  raise ValueError('P14P4_NOT_THE_OFFICIAL_ORIGINAL_SOURCE')
 updated=patch(original);p.write_bytes(updated)
 out=Path(a.out);out.parent.mkdir(parents=True,exist_ok=True)
 out.write_text(json.dumps({"schema":"c3x025-P14-P4-minimal-original-native-root-attempt-candidate-source-v1",
  "pinned_official_git":"68e1e9b3811e16cad014b590d7443b9063b3eb52",
  "byte_exact_reversible":True,
  "only_mutation":"original first qsearch numeric bounded TT score return suppressed exactly once in SCORE",
  "source_observed":["actual_original_root_move_value_and_stored_sentinel","each_root_aspiration_attempt_input_window_output_fail_class","each_original_stored_candidate_score_bound_flags"],
  "real_root_score_intervals_certified":False,"natural_TT_to_SEE_root_mediation_certified":False,
  "extra_full64_key_or_PGN_logged":False},indent=2)+"\n")
 print("P14P4_MINIMAL_ORIGINAL_SOURCE_PATCH_AND_BYTE_REVERSAL_PASS")
if __name__=='__main__':main()
