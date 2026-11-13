#!/usr/bin/env python3
"""C3X 0.30 S4-L: read-only source-tagged root candidate update receipts.

Restricts per-go logging to the first 512 ROOT evaluations. Logs value,
pre-update bestValue and alpha/beta, whether the root-move score branch
would update, moveCount, and the branch's raw Move identity.

Does NOT prove an invoked TT hit caused that score: such attribution would
require per-call return provenance. The root-log cap and its actual total
are distinct. Never align ordinal across separate engine processes.
"""
from pathlib import Path
import argparse, hashlib
from c3x_030_s4k_go_epoch_patch import patch as previous

GLOBAL='static std::atomic<unsigned> c3x_k_go_epoch{0};'
GO_RESET='''  c3x_i_logged_cutoffs.store(0, std::memory_order_relaxed);'''
GO_END='''  std::cerr << "C3X_S4K_GO_END epoch=" << c3x_k_current_epoch
            << " source_cutoff_total="'''
SITE='''      if (rootNode)
      {
          RootMove& rm = *std::find(thisThread->rootMoves.begin(),
                                    thisThread->rootMoves.end(), move);'''
TRACE='''      if (rootNode)
      {
          // C3X S4L: completed root-child score, BEFORE the existing
          // RootMove update. This is not a proven TT/parent mediation edge.
          const unsigned c3x_l_rank = c3x_l_root_score_total.fetch_add(1, std::memory_order_relaxed);
          if (c3x_l_rank < 512)
              std::cerr << "C3X_S4L_ROOT_SCORE ordinal=" << c3x_l_rank
                        << " epoch=" << c3x_k_go_epoch.load(std::memory_order_relaxed)
                        << " root_move_raw=" << static_cast<int>(move)
                        << " value=" << value
                        << " old_best=" << bestValue
                        << " alpha=" << alpha
                        << " beta=" << beta
                        << " move_count=" << moveCount
                        << " will_update_best=" << int(value > bestValue)
                        << " will_update_root_pv=" << int(moveCount == 1 || value > alpha)
                        << " depth=" << depth << std::endl;
          RootMove& rm = *std::find(thisThread->rootMoves.begin(),
                                    thisThread->rootMoves.end(), move);'''

def patch(original):
    s=previous(original)
    for anchor in (GLOBAL, GO_RESET, GO_END, SITE):
        if s.count(anchor)!=1:
            raise ValueError("S4L_PINNED_SEARCH_SOURCE_ANCHOR_"+anchor[:38])
    s=s.replace(GLOBAL,GLOBAL+"\nstatic std::atomic<unsigned> c3x_l_root_score_total{0};",1)
    s=s.replace(GO_RESET,GO_RESET+"\n  c3x_l_root_score_total.store(0, std::memory_order_relaxed);",1)
    s=s.replace(SITE,TRACE,1)
    s=s.replace('''            << " source_cutoff_total="
            << c3x_i_logged_cutoffs.load(std::memory_order_relaxed)
            << std::endl;''','''            << " source_cutoff_total="
            << c3x_i_logged_cutoffs.load(std::memory_order_relaxed)
            << " root_score_total="
            << c3x_l_root_score_total.load(std::memory_order_relaxed)
            << std::endl;''',1)
    if s.count('C3X_S4L_ROOT_SCORE ordinal=')!=1 or s.count('" root_score_total="')!=1:
        raise ValueError("S4L_ROOT_LOGGER_MISSING")
    return s

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source",required=True)
    p.add_argument("--out",required=True)
    a=p.parse_args()
    raw=Path(a.source).read_bytes()
    out=patch(raw.decode()).encode()
    dest=Path(a.out);dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_bytes(out)
    print("C3X_S4L_SOURCE_PATCH",hashlib.sha256(raw).hexdigest(),hashlib.sha256(out).hexdigest())
if __name__=="__main__":main()
