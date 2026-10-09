#!/usr/bin/env python3
"""P10 passive Stockfish16 ROOT candidate/aspiration event observer.
Apply after P9-A1 source patch, on EXACT frozen SF16 commit stack.
Fail closed on all changed original source anchors.
"""
import argparse,hashlib,json
from pathlib import Path
def only(s,old,new,label):
 count=s.count(old)
 if count!=1:raise RuntimeError("P10_SOURCE_ANCHOR_"+label+"_COUNT_"+str(count))
 return s.replace(old,new,1)
def patch(root):
 root=Path(root)/"src"
 names=["c3x014_pin_trace.h","position.cpp","search.cpp"]
 files={n:root/n for n in names}
 before={n:p.read_bytes() for n,p in files.items()}
 h,p,s=(before[n].decode() for n in names)
 h=only(h,"std::string c3x015_p9_treatment_summary();",
    """std::string c3x015_p9_treatment_summary();
void c3x015_p10_root_candidate(Key,int,int,int,int,int,int,int,int,int);
void c3x015_p10_root_sorted(Key,int,int,int,int,int,int,int);
std::string c3x015_p10_root_trace_summary();""","HEADER")
 p=only(p,"static thread_local C3X015P9A1 c3x015_p9;",
 r"""static thread_local C3X015P9A1 c3x015_p9;
struct C3X015P10 {
 unsigned long long seen=0,retained=0,truncated=0;
 std::vector<std::string> rows;
};
static thread_local C3X015P10 c3x015_p10;
static void c3x015_p10_add(Key key,int iteration,int kind,int move,int moveCount,
                           int value,int alpha,int beta,int priorScore,int nextScore,int flag) {
 ++c3x015_p10.seen;
 if(c3x015_p10.rows.size()>=1024){++c3x015_p10.truncated;return;}
 std::ostringstream o;
 o<<c3x015_p10.seen<<":"<<std::uint64_t(key)<<":"<<iteration<<":"<<kind
  <<":"<<move<<":"<<moveCount<<":"<<value<<":"<<alpha<<":"<<beta
  <<":"<<priorScore<<":"<<nextScore<<":"<<flag;
 c3x015_p10.rows.push_back(o.str());
 ++c3x015_p10.retained;
}
void c3x015_p10_root_candidate(Key k,int iteration,int move,int moveCount,int value,
                               int alpha,int beta,int previous,int after,int pvFlag) {
 c3x015_p10_add(k,iteration,10,move,moveCount,value,alpha,beta,previous,after,pvFlag);
}
void c3x015_p10_root_sorted(Key k,int iteration,int frontMove,int score,int alpha,
                            int beta,int value,int pvIndex) {
 c3x015_p10_add(k,iteration,20,frontMove,pvIndex,value,alpha,beta,score,score,0);
}
std::string c3x015_p10_root_trace_summary(){
 std::ostringstream o;
 o<<"seen="<<c3x015_p10.seen<<" retained="<<c3x015_p10.retained
  <<" truncated="<<c3x015_p10.truncated<<" stream=";
 for(const auto&line:c3x015_p10.rows)o<<line<<"|";
 return o.str();
}""","ROOT_EVENT_OBSERVER")
 p=only(p," c3x015_p9=C3X015P9A1{};",
    " c3x015_p9=C3X015P9A1{};\n c3x015_p10=C3X015P10{};","ROOT_EVENT_RESET")
 s=only(s,"          RootMove& rm = *std::find(thisThread->rootMoves.begin(),\n                                    thisThread->rootMoves.end(), move);",
    """          RootMove& rm = *std::find(thisThread->rootMoves.begin(),
                                    thisThread->rootMoves.end(), move);
          const int c3x015_p10_prev_root_candidate_score = int(rm.score);""","ROOT_SCORE_BEFORE")
 s=only(s,"          else\n              rm.score = -VALUE_INFINITE;\n      }\n\n      if (value > bestValue)",
    """          else
              rm.score = -VALUE_INFINITE;
          c3x015_p10_root_candidate(pos.key(),int(thisThread->rootDepth),int(move),
                                    int(moveCount),int(value),int(alpha),int(beta),
                                    c3x015_p10_prev_root_candidate_score,int(rm.score),
                                    int(moveCount==1 || value>alpha));
      }

      if (value > bestValue)""","ROOT_CANDIDATE_AFTER")
 s=only(s,"              std::stable_sort(rootMoves.begin() + pvIdx, rootMoves.begin() + pvLast);",
    """              std::stable_sort(rootMoves.begin() + pvIdx, rootMoves.begin() + pvLast);
              c3x015_p10_root_sorted(rootPos.key(),int(rootDepth),
                                      int(rootMoves[pvIdx].pv[0]),int(rootMoves[pvIdx].score),
                                      int(alpha),int(beta),int(bestValue),int(pvIdx));""","ROOT_SORT")
 s=only(s,'  sync_cout << "info string c3x015_p9_a1_intervention " << c3x015_p9_treatment_summary() << sync_endl;',
    '  sync_cout << "info string c3x015_p9_a1_intervention " << c3x015_p9_treatment_summary() << sync_endl;\n  sync_cout << "info string c3x015_p10_root_lineage " << c3x015_p10_root_trace_summary() << sync_endl;',
    "ROOT_UCI_REPORT")
 for n,t in zip(names,(h,p,s)):files[n].write_text(t)
 return {"schema":"c3x015-P10-SF16-passive-root-candidate-aspiration-trace-v1",
  "source_before_sha256":{n:hashlib.sha256(b).hexdigest() for n,b in before.items()},
  "source_after_sha256":{n:hashlib.sha256(files[n].read_bytes()).hexdigest() for n in names},
  "events":{"10":"ROOT_CANDIDATE_SCORE_BEFORE_AFTER","20":"ROOT_STABLE_SORT_ASPIRATION_LOOP"},
  "retained_max":1024,
  "limits":["Read-only root source observation; event order not causal necessity.",
            "Candidate score before/after preserved with actual full64 root key, depth, root move ordinal, alpha/beta.",
            "Identical native prior bestmove/score/nodes/PV across P9-A1 mandatory.",
            "Possible first-event truncation does not license whole-history first-divergence claims."]}
if __name__=="__main__":
 ap=argparse.ArgumentParser();ap.add_argument("--source",required=True);ap.add_argument("--out-manifest",required=True)
 a=ap.parse_args()
 x=patch(a.source);out=Path(a.out_manifest);out.parent.mkdir(parents=True,exist_ok=True)
 out.write_text(json.dumps(x,indent=2)+"\n")
 print("C3X015_P10_SF16_ROOT_CANDIDATE_ASPIRATION_READONLY_SOURCE_PATCH_PASS")
