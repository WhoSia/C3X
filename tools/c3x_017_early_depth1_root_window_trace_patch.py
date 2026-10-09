#!/usr/bin/env python3
"""C3X 0.17: passive SF16 root candidate/window event profiler atop frozen P4 source patch.
Never edit TT, alpha-beta values, move ordering, evaluation or root score.
"""
import argparse, hashlib, json
from pathlib import Path
def one(s,a,b,label):
 n=s.count(a)
 if n!=1: raise RuntimeError("C3X017_EARLY_TRACE_SOURCE_ANCHOR_"+label+"_"+str(n))
 return s.replace(a,b,1)
def main():
 p=argparse.ArgumentParser();p.add_argument("--source",required=True);p.add_argument("--out-manifest",required=True)
 a=p.parse_args();f=Path(a.source)/"src/search.cpp"
 before=f.read_bytes();s=before.decode()
 s=one(s,"namespace Stockfish {\n",r"""namespace Stockfish {

// Passive source-native C3X017_EARLY root search monitor. Reports only; no search mutation.
static thread_local int c3x017_root_event_count = 0;
static constexpr int c3x017_root_event_limit = 4096;
""","NAMESPACE")
 s=one(s,"  const char* c3x_p4_mode = std::getenv(\"C3X016_P4_MODE\");",
 r"""  c3x017_root_event_count = 0;
  const char* c3x_p4_mode = std::getenv("C3X016_P4_MODE");""","RESET")
 s=one(s,
 "              bestValue = Stockfish::search<Root>(rootPos, ss, alpha, beta, adjustedDepth, false);",
 r"""              if(c3x017_root_event_count<c3x017_root_event_limit && rootDepth>=1) {
                  ++c3x017_root_event_count;
                  sync_cout << "info string c3x017_root_event kind=window_enter seq=" << c3x017_root_event_count
                            << " depth=" << int(rootDepth) << " alpha=" << int(alpha)
                            << " beta=" << int(beta) << " first_move=" << int(rootMoves[0].pv[0])
                            << " root_nodes=" << this->nodes.load(std::memory_order_relaxed) << sync_endl;
              }
              bestValue = Stockfish::search<Root>(rootPos, ss, alpha, beta, adjustedDepth, false);
              if(c3x017_root_event_count<c3x017_root_event_limit && rootDepth>=1) {
                  ++c3x017_root_event_count;
                  sync_cout << "info string c3x017_root_event kind=window_exit seq=" << c3x017_root_event_count
                            << " depth=" << int(rootDepth) << " alpha=" << int(alpha)
                            << " beta=" << int(beta) << " value=" << int(bestValue)
                            << " root_nodes=" << this->nodes.load(std::memory_order_relaxed) << sync_endl;
              }""","WINDOW")
 s=one(s,"              std::stable_sort(rootMoves.begin() + pvIdx, rootMoves.begin() + pvLast);",
 r"""              std::stable_sort(rootMoves.begin() + pvIdx, rootMoves.begin() + pvLast);
              if(c3x017_root_event_count<c3x017_root_event_limit && rootDepth>=1) {
                  ++c3x017_root_event_count;
                  sync_cout << "info string c3x017_root_event kind=after_sort seq=" << c3x017_root_event_count
                            << " depth=" << int(rootDepth) << " alpha=" << int(alpha)
                            << " beta=" << int(beta) << " value=" << int(bestValue)
                            << " first_move=" << int(rootMoves[0].pv[0])
                            << " first_score=" << int(rootMoves[0].score) << sync_endl;
              }""","SORT")
 s=one(s,"          RootMove& rm = *std::find(thisThread->rootMoves.begin(),\n                                    thisThread->rootMoves.end(), move);",
 r"""          RootMove& rm = *std::find(thisThread->rootMoves.begin(),
                                    thisThread->rootMoves.end(), move);
          const int c3x017_prior_root_score = int(rm.score);""","ROOT_BEFORE")
 s=one(s,"              rm.score = -VALUE_INFINITE;\n      }\n\n      if (value > bestValue)",
 r"""              rm.score = -VALUE_INFINITE;
          if(c3x017_root_event_count<c3x017_root_event_limit && thisThread->rootDepth>=1) {
              ++c3x017_root_event_count;
              sync_cout << "info string c3x017_root_event kind=candidate seq=" << c3x017_root_event_count
                        << " depth=" << int(thisThread->rootDepth) << " move=" << int(move)
                        << " index=" << moveCount << " child_return=" << int(value)
                        << " alpha=" << int(alpha) << " beta=" << int(beta)
                        << " before=" << c3x017_prior_root_score << " after=" << int(rm.score)
                        << " root_nodes=" << thisThread->nodes.load(std::memory_order_relaxed)
                        << sync_endl;
          }
      }

      if (value > bestValue)""","ROOT_AFTER")
 f.write_text(s)
 j={"schema":"c3x017-root-order-window-candidate-passive-v1",
 "upstream":"SF16 68e1e9b3811e16cad014b590d7443b9063b3eb52 + frozen C3X016 P4 root-order source patch",
 "source_before_sha256":hashlib.sha256(before).hexdigest(),
 "source_after_sha256":hashlib.sha256(f.read_bytes()).hexdigest(),
 "source_events":["window_enter","window_exit","after_sort","candidate"],
 "min_depth":1,"max_observed_events":4096,
 "limits":["Observer records no TT writer-reader origin; no assertion of natural TT mediation",
 "No changes to chess move legality, candidate order policy or source search values",
 "Event order is NOT a causal necessity test; report censoring if cap reached",
 "Sham must exactly replay previous P4 O/F/Z native UCI cores"]}
 out=Path(a.out_manifest);out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(j,indent=2)+"\n")
 print("C3X017_EARLY_PASSIVE_SF16_ROOT_WINDOW_AND_CANDIDATE_PATCH_APPLIED")
if __name__=="__main__":main()
