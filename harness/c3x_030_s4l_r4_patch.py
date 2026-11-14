"""Add process-local experiment commands for exchanging TT and move histories."""
import argparse
import hashlib
from pathlib import Path

ANCHORS = {
    "uci.cpp": "7f72ea362a5e14da30c6c69ff42f3d31e4c02f558bb5fac3fe14597612289941",
}

def unique_replace(source, old, new):
    if source.count(old) != 1:
        raise ValueError(f"Expected unique anchor: {old}")
    return source.replace(old, new, 1)

def patch(src):
    tt_path = src / "tt.h"
    uci_path = src / "uci.cpp"
    tt = tt_path.read_text()
    uci = uci_path.read_text()
    if hashlib.sha256(uci.encode()).hexdigest() != ANCHORS["uci.cpp"]:
        raise ValueError("Expected R3 uci.cpp")
    tt = '#include <fstream>\n#include <vector>\n#include <cstring>\n' + tt
    tt = unique_replace(tt, "  void clear();", """  void clear();
  bool c3x_exchange(std::fstream& file, bool save) {
    const auto bytes = clusterCount * sizeof(Cluster);
    if (save)
      return bool(file.write(reinterpret_cast<const char*>(&clusterCount), sizeof(clusterCount))
                      .write(reinterpret_cast<const char*>(&generation8), sizeof(generation8))
                      .write(reinterpret_cast<const char*>(table), bytes));
    size_t count = 0;
    uint8_t generation = 0;
    file.read(reinterpret_cast<char*>(&count), sizeof(count));
    file.read(reinterpret_cast<char*>(&generation), sizeof(generation));
    if (!file || count != clusterCount) return false;
    std::vector<char> data(bytes);
    if (!file.read(data.data(), bytes) || file.peek() != std::char_traits<char>::eof()) return false;
    std::memcpy(table, data.data(), bytes);
    generation8 = generation;
    return true;
  }""")
    uci = '#include <fstream>\n#include <type_traits>\n#include <tuple>\n' + uci
    old = '      else if (token == "c3xreset")'
    uci = unique_replace(uci, old, """      else if (token == "c3xexchange")
      {
          std::string operation, block, path;
          is >> operation >> block >> path;
          Threads.main()->wait_for_search_finished();
          const bool save = operation == "save";
          std::fstream file(path, std::ios::binary | (save ? std::ios::out : std::ios::in));
          auto* th = Threads.main();
          bool ok = false;
          if (file && (save || operation == "load") && Threads.size() == 1)
          {
              if (block == "tt")
                  ok = TT.c3x_exchange(file, save);
              else if (block == "history")
              {
                  auto history = std::tie(th->counterMoves, th->mainHistory,
                                          th->captureHistory, th->continuationHistory);
                  auto exchange = [&](auto&... fields) {
                      static_assert((std::is_trivially_copyable_v<std::remove_reference_t<decltype(fields)>> && ...));
                      if (save)
                          (file.write(reinterpret_cast<const char*>(&fields), sizeof(fields)), ...);
                      else
                          (file.read(reinterpret_cast<char*>(&fields), sizeof(fields)), ...);
                  };
                  std::apply(exchange, history);
                  ok = bool(file) && (save || file.peek() == std::char_traits<char>::eof());
              }
              if (save) { file.flush(); ok = ok && bool(file); }
          }
          sync_cout << "c3xexchange " << (ok ? "ok" : "error") << sync_endl;
      }
""" + old)
    tt_path.write_text(tt)
    uci_path.write_text(uci)

if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("src", type=Path)
    patch(p.parse_args().src)
