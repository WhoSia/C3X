#!/usr/bin/env python3
"""R40: passive TT event log on the exact R27/R29/R30/R31/R33 source stack.
Reuse R31's native tuple writer; record every actual save, refresh and miss.
No additional probe, no state transplantation, single-thread fixed-depth only.
Run on a disposable source checkout. Strict anchors and roundtrip before writing.
"""
import argparse
import hashlib
import json
from pathlib import Path

RULES = {
    "tt.cpp": [
        ("#include <thread>\n",
         "#include <thread>\n#include <cstdlib>\n#include <cstdint>\n#include <sstream>\n", "includes"),
        ("thread_local const TTEntry* C3XR31WatchCluster = nullptr;\n",
         """thread_local const TTEntry* C3XR31WatchCluster = nullptr;

// R40 is an observer, not a source of engine decisions. Fixed-depth, one thread.
bool c3x_r40_on() {
  static const bool enabled = [] {
    const char* p = std::getenv("C3X_R40_TT_EVENTS");
    return p && std::strcmp(p, "1") == 0;
  }();
  return enabled && int(Options["Threads"]) == 1;
}
""", "gate"),
        ("""  const bool watched = C3XR31WatchCluster && TT.first_entry(k) == C3XR31WatchCluster;""",
         """  const bool r40 = c3x_r40_on();
  TTEntry r40_before{};
  bool r40_move_write = false;
  if (r40) {
      r40_before = *this;
      r40_move_write = bool(m || (uint16_t)k != key16);
  }
  const bool watched = C3XR31WatchCluster && TT.first_entry(k) == C3XR31WatchCluster;""", "save_before"),
        ("""  if (watched)
  {
      std::cerr << " replaced=" << replace << " after=";""",
         """  if (r40) {
      // Stable numeric identity, never publish process pointer addresses.
      const auto off = reinterpret_cast<std::uintptr_t>(this)
                     - reinterpret_cast<std::uintptr_t>(TT.table);
      const auto cluster = off / sizeof(TranspositionTable::Cluster);
      const auto in_cluster = off % sizeof(TranspositionTable::Cluster);
      const bool valid = cluster < TT.clusterCount
                      && in_cluster % sizeof(TTEntry) == 0
                      && in_cluster / sizeof(TTEntry) < TranspositionTable::ClusterSize
                      && cluster == mul_hi64(k, TT.clusterCount);
      std::ostringstream o;
      o << "C3X_R40_SAVE key=" << k << " cluster=" << cluster
        << " slot=" << in_cluster / sizeof(TTEntry) << " valid=" << int(valid)
        << " site=" << site << " ply=" << ply
        << " move_write=" << int(r40_move_write) << " score_write=" << int(replace)
        << " before=";
      r40_before.c3x_write_tuple(o);
      o << " after=";
      c3x_write_tuple(o);
      std::cerr << o.str() << '\\n';
  }
  if (watched)
  {
      std::cerr << " replaced=" << replace << " after=";""", "save_after"),
        ("""  for (std::thread& th : threads)
      th.join();
}""",
         """  for (std::thread& th : threads)
      th.join();
  if (c3x_r40_on())
      std::cerr << "C3X_R40_RESET clusters=" << clusterCount
                << " generation=" << int(generation8 >> 3) << '\\n';
}""", "reset"),
        ("""          const auto refreshed = uint8_t(generation8 | (tte[i].genBound8 & (GENERATION_DELTA - 1)));""",
         """          const bool r40 = c3x_r40_on();
          TTEntry r40_before{};
          if (r40)
              r40_before = tte[i];
          const auto refreshed = uint8_t(generation8 | (tte[i].genBound8 & (GENERATION_DELTA - 1)));""", "probe_before"),
        ("""          return found = (bool)tte[i].depth8, &tte[i];""",
         """          if (r40) {
              std::ostringstream o;
              o << "C3X_R40_PROBE key=" << key << " cluster=" << mul_hi64(key, clusterCount)
                << " slot=" << i << " hit=" << int(bool(tte[i].depth8))
                << " refresh=1 generation=" << int(generation8 >> 3) << " before=";
              r40_before.c3x_write_tuple(o);
              o << " after=";
              tte[i].c3x_write_tuple(o);
              std::cerr << o.str() << '\\n';
          }
          return found = (bool)tte[i].depth8, &tte[i];""", "probe_refresh"),
        ("""  return found = false, replace;""",
         """  if (c3x_r40_on()) {
      std::ostringstream o;
      o << "C3X_R40_PROBE key=" << key << " cluster=" << mul_hi64(key, clusterCount)
        << " slot=" << (replace - tte) << " hit=0 refresh=0 generation="
        << int(generation8 >> 3) << " before=";
      replace->c3x_write_tuple(o);
      o << " after=";
      replace->c3x_write_tuple(o);
      std::cerr << o.str() << '\\n';
  }
  return found = false, replace;""", "probe_replacement"),
    ],
    "search.cpp": [
        ("namespace Stockfish {\n",
         "namespace Stockfish {\n\nbool c3x_r40_on();\n", "observer_declaration"),
        ("""              bestValue = Stockfish::search<Root>(rootPos, ss, alpha, beta, adjustedDepth, false);""",
         """              if (c3x_r40_on() && c3x_trace() && c3xAttempt == 17)
                  std::cerr << "C3X_R40_CHECKPOINT attempt=" << c3xAttempt
                            << " root_depth=" << rootDepth << " completed=" << completedDepth
                            << " adjusted=" << adjustedDepth << " pv_idx=" << pvIdx
                            << " alpha=" << alpha << " beta=" << beta
                            << " stopped=" << int(Threads.stop.load(std::memory_order_relaxed))
                            << " nodes=" << Threads.nodes_searched() << '\\n';
              bestValue = Stockfish::search<Root>(rootPos, ss, alpha, beta, adjustedDepth, false);""", "checkpoint"),
    ],
}


def edit(source, reverse=False):
    result = {}
    for filename, rules in RULES.items():
        s = source[filename]
        for before, after, label in reversed(rules) if reverse else rules:
            if reverse:
                before, after = after, before
            if s.count(before) != 1:
                raise ValueError(f"R40_ANCHOR_{filename}_{label}_{s.count(before)}")
            s = s.replace(before, after, 1)
        result[filename] = s
    return result


def main():
    p = argparse.ArgumentParser()
    p.add_argument("source", type=Path)
    p.add_argument("manifest", type=Path)
    a = p.parse_args()
    root = a.source / "src"
    old = {n: (root / n).read_bytes().decode("utf-8") for n in RULES}
    changed = edit(old)
    if edit(changed, reverse=True) != old:
        raise ValueError("R40_NOT_BYTE_REVERSIBLE")
    if sum(s.count("TT.probe(") for s in old.values()) != sum(s.count("TT.probe(") for s in changed.values()):
        raise ValueError("R40_PROBE_COUNT_CHANGED")
    h = lambda s: hashlib.sha256(s.encode("utf-8")).hexdigest()
    for n, s in changed.items():
        (root / n).write_bytes(s.encode("utf-8"))
    a.manifest.parent.mkdir(parents=True, exist_ok=True)
    a.manifest.write_text(json.dumps({"source_before": {n:h(s) for n,s in old.items()},
                                     "source_after": {n:h(s) for n,s in changed.items()},
                                     "roundtrip": True, "extra_probe": False,
                                     "native_parity": "UNEXECUTED_BY_PATCHER"},indent=2)+"\n")


if __name__ == "__main__":
    main()
