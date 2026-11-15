"""Interchange the observed London Nd2 null-window result before the PV gate."""
import argparse
import hashlib
from pathlib import Path

BASE = "b9376e4fc13c4c483e94292781e217c7aa061cb700e3b920962e17628a45024f"
SITE = "      // For PV nodes only, do a full PV search on the first move or after a fail"
PROBE = """      if (rootNode && c3x_k_go_epoch.load(std::memory_order_relaxed) == 2
          && thisThread->rootDepth == 8 && depth == 6 && moveCount == 2
          && static_cast<int>(move) == 75 && alpha == 0 && beta == 10
          && !Threads.stop.load(std::memory_order_relaxed))
      {
          std::ifstream settings("c3x_s4l_r8_probe.txt");
          int expected, replacement;
          if (settings >> expected >> replacement
              && (expected == 0 || expected == 6)
              && (replacement == 0 || replacement == 6)
              && value == expected)
          {
              std::cerr << "C3X_R8_PROBE before=" << value << " after=" << replacement
                        << " parent=" << c3x_e_scope.id
                        << " child=" << c3x_e_last_child[1] << std::endl;
              value = Value(replacement);
          }
      }

"""


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("search_source", type=Path)
    args = parser.parse_args()
    source = args.search_source.read_bytes()
    if hashlib.sha256(source).hexdigest() != BASE or source.count(SITE.encode()) != 1:
        raise ValueError("Expected exact R4 search overlay")
    args.search_source.write_bytes(source.replace(SITE.encode(), (PROBE + SITE).encode(), 1))


if __name__ == "__main__":
    main()
