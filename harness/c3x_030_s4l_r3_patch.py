"""Patch the SHA-pinned S4-L/R2 source for Italian restoration and reset trials."""
import argparse
import hashlib
from pathlib import Path

R2_SHA = "7e458b4f74f01ee519ee4e641b1176ac252576dda0cb57a3ec62fe13a113d398"

def replace_one(source, old, new):
    if source.count(old) != 1:
        raise ValueError(f"Nonunique anchor: {old!r}")
    return source.replace(old, new, 1)

def patch(search, uci):
    if hashlib.sha256(search.encode()).hexdigest() != R2_SHA:
        raise ValueError("Expected archived R2 search.cpp")
    old = "      // Step 19. Undo move"
    hook = """      // R3 changes the root-consumed value after all child work finishes.
      if (rootNode && c3x_k_go_epoch.load(std::memory_order_relaxed) == 1
          && thisThread->rootDepth == 2 && depth == 2 && moveCount == 1
          && static_cast<int>(move) == 1243 && alpha == 138 && beta == 160
          && !Threads.stop.load(std::memory_order_relaxed))
      {
          static const int replacement = []() {
              std::ifstream config("c3x_s4l_r3_value.txt");
              int configured_value = 0;
              config >> configured_value;
              return configured_value;
          }();
          if (replacement == 134 || replacement == 149)
          {
              std::cerr << "C3X_R3_VALUE parent=" << c3x_e_scope.id
                        << " child=" << c3x_e_last_child[1]
                        << " before=" << value << " after=" << replacement << std::endl;
              value = Value(replacement);
          }
      }

"""
    search = replace_one(search, old, hook + old)
    old = '      else if (token == "ucinewgame") Search::clear();'
    uci = replace_one(uci, old, old + """
      else if (token == "c3xreset")
      {
          std::string mode;
          is >> mode;
          Threads.main()->wait_for_search_finished();
          if (mode == "tt" || mode == "both" || mode == "tt_history" || mode == "tt_prior")
              TT.clear();
          if (mode == "threads" || mode == "both")
              Threads.clear();
          if (mode == "history" || mode == "tt_history")
              Threads.main()->clear(); // Single-thread trial.
          if (mode == "prior" || mode == "tt_prior")
          {
              Threads.main()->callsCnt = 0;
              Threads.main()->bestPreviousScore = VALUE_INFINITE;
              Threads.main()->bestPreviousAverageScore = VALUE_INFINITE;
              Threads.main()->previousTimeReduction = 1.0;
          }
          sync_cout << "c3xresetok " << mode << sync_endl;
      }""")
    if '#include "tt.h"' not in uci:
        uci = '#include "tt.h"\n' + uci
    return search, uci

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("r2_search", type=Path)
    parser.add_argument("src", type=Path)
    args = parser.parse_args()
    uci_path = args.src / "uci.cpp"
    search, uci = patch(args.r2_search.read_text(), uci_path.read_text())
    (args.src / "search.cpp").write_text(search)
    uci_path.write_text(uci)
