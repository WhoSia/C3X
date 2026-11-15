"""Substitute the root-consumed value after the London PV child has run."""
import argparse
import hashlib
from pathlib import Path

BASE = "49ee5de65590b35e2c9cbe2d2f8ff69e804f077b6287399bffc8b587d9d30783"
SITE = "      // R3 changes the root-consumed value after all child work finishes."
EDIT = """      if (c3x_r9_target && c3x_r9_pv_ran && !Threads.stop.load(std::memory_order_relaxed))
      {
          std::ifstream settings("c3x_s4l_r9_pv.txt");
          int expected, replacement;
          if (settings >> expected >> replacement
              && (expected == 0 || expected == 14)
              && (replacement == 0 || replacement == 14)
              && value == expected)
          {
              std::cerr << "C3X_R9_PV before=" << value << " after=" << replacement
                        << " parent=" << c3x_e_scope.id
                        << " child=" << c3x_e_last_child[1] << std::endl;
              value = Value(replacement);
          }
      }

"""
GATE = """      if (PvNode && (moveCount == 1 || (value > alpha && (rootNode || value < beta))))
      {"""
TARGET = """      const bool c3x_r9_target = rootNode
          && c3x_k_go_epoch.load(std::memory_order_relaxed) == 2
          && thisThread->rootDepth == 8 && depth == 6 && moveCount == 2
          && static_cast<int>(move) == 75 && alpha == 0 && beta == 10;
      const bool c3x_r9_pv_ran = PvNode && (moveCount == 1 || (value > alpha && (rootNode || value < beta)));
      if (c3x_r9_pv_ran)
      {"""


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("search_source", type=Path)
    args = parser.parse_args()
    source = args.search_source.read_bytes()
    if hashlib.sha256(source).hexdigest() != BASE:
        raise ValueError("Expected exact R8 search overlay")
    if source.count(SITE.encode()) != 1 or source.count(GATE.encode()) != 1:
        raise ValueError("Expected one PV gate and one post-child site")
    args.search_source.write_bytes(source.replace(GATE.encode(), TARGET.encode())
                                        .replace(SITE.encode(), (EDIT + SITE).encode()))


if __name__ == "__main__":
    main()
