#!/usr/bin/env python3
"""C3X 0.30/S4-K: tag TRUE UCI 'go' epochs in TT-cutoff logs.

Extension of S4-J. Separate go epoch counters and per-go censoring accounting
without changing TT probes, values, search windows, or move selection.
Stockfish16 only; requires exact source anchors. Threads=1 mandatory.
"""
import argparse, hashlib
from pathlib import Path
from c3x_030_s4j_state_fingerprint_patch import patch as s4j_patch

GLOBAL='static std::atomic<unsigned> c3x_i_logged_cutoffs{0};'
ENTRY='void MainThread::search() {\n'
END='''      Thread::search();          // main thread start searching
  }

  // When we reach the maximum depth'''
CUTOFF='''                    std::cerr << "C3X_S4I_TT_CUTOFF ordinal=" << c3x_i_index'''
NEW_CUTOFF='''                    std::cerr << "C3X_S4I_TT_CUTOFF ordinal=" << c3x_i_index
                              << " epoch=" << c3x_k_go_epoch.load(std::memory_order_relaxed)'''

def patch(original: str) -> str:
    s=s4j_patch(original)
    for anchor in (GLOBAL, ENTRY, END, CUTOFF):
        if s.count(anchor)!=1:
            raise ValueError("S4K_UNIQUE_PINNED_SOURCE_SITE_"+anchor[:32])
    s=s.replace(GLOBAL,GLOBAL+"\nstatic std::atomic<unsigned> c3x_k_go_epoch{0};",1)
    s=s.replace(ENTRY,ENTRY+'''
  // UCI 'go' boundary: accounting only, no search behavior mutation.
  const unsigned c3x_k_current_epoch =
      c3x_k_go_epoch.fetch_add(1, std::memory_order_relaxed) + 1;
  c3x_i_logged_cutoffs.store(0, std::memory_order_relaxed);
  std::cerr << "C3X_S4K_GO_BEGIN epoch=" << c3x_k_current_epoch
            << " cap_per_go=8" << std::endl;
''',1)
    s=s.replace(END,'''      Thread::search();          // main thread start searching
  }
  std::cerr << "C3X_S4K_GO_END epoch=" << c3x_k_current_epoch
            << " source_cutoff_total="
            << c3x_i_logged_cutoffs.load(std::memory_order_relaxed)
            << std::endl;

  // When we reach the maximum depth''',1)
    s=s.replace(CUTOFF,NEW_CUTOFF,1)
    if (s.count('C3X_S4K_GO_BEGIN epoch=')!=1 or
        s.count('C3X_S4K_GO_END epoch=')!=1 or
        s.count('" epoch=" << c3x_k_go_epoch.load')!=1):
        raise ValueError("S4K_EPOCH_TAG_MISSING")
    return s

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source",required=True)
    p.add_argument("--out",required=True)
    args=p.parse_args()
    raw=Path(args.source).read_bytes()
    output=patch(raw.decode("utf-8")).encode("utf-8")
    dest=Path(args.out);dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_bytes(output)
    print("S4K_SOURCE_PATCH",hashlib.sha256(raw).hexdigest(),
          hashlib.sha256(output).hexdigest())
if __name__=="__main__":
    main()
