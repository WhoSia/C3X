#!/usr/bin/env python3
"""C3X 0.18 physical TT payload writer/consumer lineage, native SF16 only.

Independent shadow state preserves the exact 10-byte TTEntry and 32-byte
cluster. Single-thread, independent cold process is required for causal use.
OBS, W, R, WR are source-level treatment arms; rescue is NOT implemented.
"""
import argparse
import hashlib
import json
from pathlib import Path


def once(s, old, new, label):
    n = s.count(old)
    if n != 1:
        raise RuntimeError(f"C3X018_LINEAGE_ANCHOR_{label}_{n}")
    return s.replace(old, new, 1)


HEADER_DECL = r"""
// C3X018 optional, source-exact TT shadow witness; NOT part of TTEntry.
bool c3x018_writer_block(Key key, const TTEntry* slot, bool would_write);
void c3x018_note_payload_write(Key key, const TTEntry* slot, int depth,
                               int bound, int value);
bool c3x018_consumer_gate(const char* site, Key key, const TTEntry* slot,
                         int ply, int depth, int alpha, int beta, int value);
"""

TT_IMPL = r"""
// C3X018 physical shadow ledger. No modification of SF16 TTEntry layout.
namespace {
struct C3X018Writer {
    uint64_t epoch = 0;  // slot-local successful payload write ordinal
    uint64_t key64 = 0;
};
std::mutex c3x018_shadow_mutex;
std::unordered_map<const TTEntry*, C3X018Writer> c3x018_shadow;
uint64_t c3x018_event_seq = 0;
bool c3x018_overflow_reported = false;
uint64_t c3x018_writer_blocks = 0;
constexpr uint64_t C3X018_LOG_LIMIT = 30000;
const char* c3x018_mode() {
    const char* value = std::getenv("C3X018_TT_MODE");
    return value ? value : "";
}
bool c3x018_active() { return *c3x018_mode() != '\0'; }
uint64_t c3x018_parameter(const char* name) {
    const char* x = std::getenv(name);
    return x ? std::strtoull(x, nullptr, 10) : 0;
}
int c3x018_slot(const Key key, const TTEntry* ptr) {
    auto offset = ptr - TT.first_entry(key);
    return offset >= 0 && offset < 3 ? int(offset) : -1;
}
bool c3x018_target(const Key key, const TTEntry* ptr, uint64_t epoch) {
    if (!std::getenv("C3X018_TT_TARGET_KEY64") ||
        !std::getenv("C3X018_TT_TARGET_SLOT") ||
        !std::getenv("C3X018_TT_TARGET_EPOCH")) return false;
    return uint64_t(key) == c3x018_parameter("C3X018_TT_TARGET_KEY64")
        && c3x018_slot(key, ptr) == int(c3x018_parameter("C3X018_TT_TARGET_SLOT"))
        && epoch == c3x018_parameter("C3X018_TT_TARGET_EPOCH");
}
void c3x018_event(const char* kind, const char* site, Key key,
                   const TTEntry* ptr, uint64_t epoch, uint64_t writer_key,
                   int matched, int ply, int depth, int alpha, int beta, int value) {
    uint64_t seq = ++c3x018_event_seq;
    if (seq > C3X018_LOG_LIMIT) {
        if (!c3x018_overflow_reported) {
            c3x018_overflow_reported = true;
            sync_cout << "info string c3x018_lineage kind=trace_censored"
                      << " seq=" << seq << sync_endl;
        }
        return;
    }
    sync_cout << "info string c3x018_lineage kind=" << kind
              << " site=" << site << " seq=" << seq
              << " key64=" << uint64_t(key)
              << " writer_key64=" << writer_key
              << " slot=" << c3x018_slot(key, ptr)
              << " epoch=" << epoch << " key_match=" << matched
              << " ply=" << ply << " depth=" << depth
              << " alpha=" << alpha << " beta=" << beta
              << " value=" << value << sync_endl;
}
} // anonymous namespace

bool c3x018_writer_block(Key key, const TTEntry* slot, bool would_write) {
    if (!c3x018_active() || !would_write) return false;
    std::lock_guard<std::mutex> lock(c3x018_shadow_mutex);
    auto it = c3x018_shadow.find(slot);
    const uint64_t next = it == c3x018_shadow.end() ? 1 : it->second.epoch + 1;
    const char* mode = c3x018_mode();
    const uint64_t budget = std::getenv("C3X018_TT_WRITER_BLOCK_BUDGET")
        ? c3x018_parameter("C3X018_TT_WRITER_BLOCK_BUDGET") : 1;
    if ((std::strcmp(mode, "W") == 0 || std::strcmp(mode, "WR") == 0)
        && c3x018_writer_blocks < budget
        && c3x018_target(key, slot, next)) {
        ++c3x018_writer_blocks;
        c3x018_event("writer_block", "save", key, slot, next, uint64_t(key),
                     1, -1, -1, 0, 0, 0);
        return true;
    }
    return false;
}

void c3x018_note_payload_write(Key key, const TTEntry* slot,
                               int depth, int bound, int value) {
    if (!c3x018_active()) return;
    std::lock_guard<std::mutex> lock(c3x018_shadow_mutex);
    auto& record = c3x018_shadow[slot];
    ++record.epoch;
    record.key64 = uint64_t(key);
    // Full write logging is deliberately opt-in: otherwise early-depth writes
    // would censor the much rarer actual consumer contacts at later depths.
    if (std::getenv("C3X018_TT_LOG_WRITES"))
        c3x018_event("payload_write", "save", key, slot, record.epoch,
                     record.key64, 1, -1, depth, 0, bound, value);
}

bool c3x018_consumer_gate(const char* site, Key key, const TTEntry* slot,
                         int ply, int depth, int alpha, int beta, int value) {
    if (!c3x018_active()) return false;
    std::lock_guard<std::mutex> lock(c3x018_shadow_mutex);
    auto it = c3x018_shadow.find(slot);
    const bool known = it != c3x018_shadow.end();
    const uint64_t epoch = known ? it->second.epoch : 0;
    const uint64_t writer_key = known ? it->second.key64 : 0;
    const bool exact_key = known && writer_key == uint64_t(key);
    const char* mode = c3x018_mode();
    const bool block = (std::strcmp(mode, "R") == 0 ||
                        std::strcmp(mode, "WR") == 0)
                   && exact_key && c3x018_target(key, slot, epoch);
    c3x018_event(block ? "reader_block" : "consumer_reached", site,
                 key, slot, epoch, writer_key, exact_key,
                 ply, depth, alpha, beta, value);
    return block;
}
"""

def patch_header(s):
    return once(s, "extern TranspositionTable TT;", HEADER_DECL + "\nextern TranspositionTable TT;", "HEADER")

def patch_tt(s):
    s = once(s, "#include <thread>", "#include <thread>\n#include <mutex>\n#include <unordered_map>\n#include <cstdint>\n#include <cstdlib>", "TT_INCLUDES")
    s = once(s, "TranspositionTable TT; // Our global transposition table",
             "TranspositionTable TT; // Our global transposition table\n" + TT_IMPL, "TT_SHADOW")
    before = """void TTEntry::save(Key k, Value v, bool pv, Bound b, Depth d, Move m, Value ev) {

  // Preserve any existing move"""
    after = """void TTEntry::save(Key k, Value v, bool pv, Bound b, Depth d, Move m, Value ev) {
  const bool c3x018_would_payload_write =
      b == BOUND_EXACT || (uint16_t)k != key16
      || d - DEPTH_OFFSET + 2 * pv > depth8 - 4;
  if (c3x018_writer_block(k, this, c3x018_would_payload_write))
      return;
  // Preserve any existing move"""
    s = once(s, before, after, "SAVE_GUARD")
    s = once(s, """      eval16    = (int16_t)ev;
  }
}""", """      eval16    = (int16_t)ev;
      c3x018_note_payload_write(k, this, int(depth8),
                                int(genBound8 & 3), int(value16));
  }
}""", "SAVE_WRITE")
    # TT.clear() is called on resize and ucinewgame; stale records must be purged.
    s = once(s, """  for (std::thread& th : threads)
      th.join();
}""", """  for (std::thread& th : threads)
      th.join();

  if (c3x018_active()) {
      std::lock_guard<std::mutex> lock(c3x018_shadow_mutex);
      c3x018_shadow.clear();
      c3x018_event_seq = 0;
      c3x018_overflow_reported = false;
      c3x018_writer_blocks = 0;
  }
}""", "CLEAR")
    return s

MAIN = """        && (tte->bound() & (ttValue >= beta ? BOUND_LOWER : BOUND_UPPER)))
    {
        // If ttMove is quiet, update move sorting heuristics on TT hit (~2 Elo)"""
MAIN_NEW = """        && (tte->bound() & (ttValue >= beta ? BOUND_LOWER : BOUND_UPPER))
        && !c3x018_consumer_gate("main", posKey, tte, ss->ply,
                                 depth, int(alpha), int(beta), int(ttValue)))
    {
        // If ttMove is quiet, update move sorting heuristics on TT hit (~2 Elo)"""
QS = """        && (tte->bound() & (ttValue >= beta ? BOUND_LOWER : BOUND_UPPER)))
        return ttValue;"""
QS_NEW = """        && (tte->bound() & (ttValue >= beta ? BOUND_LOWER : BOUND_UPPER))
        && !c3x018_consumer_gate("qsearch", posKey, tte, ss->ply,
                                 ttDepth, int(alpha), int(beta), int(ttValue)))
        return ttValue;"""

def patch_search(s):
    s = once(s, MAIN, MAIN_NEW, "MAIN_CONSUMER")
    s = once(s, QS, QS_NEW, "QS_CONSUMER")
    return s

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--source", required=True)
    p.add_argument("--out-manifest", required=True)
    args = p.parse_args()
    root = Path(args.source) / "src"
    result = {}
    for filename, transform in (("tt.h", patch_header),
                                ("tt.cpp", patch_tt),
                                ("search.cpp", patch_search)):
        file = root / filename
        original = file.read_bytes()
        altered = transform(original.decode("utf-8")).encode("utf-8")
        file.write_bytes(altered)
        result[filename] = {
            "before": hashlib.sha256(original).hexdigest(),
            "after": hashlib.sha256(altered).hexdigest()
        }
    receipt = {
       "schema": "c3x018-physical-payload-writer-consumer-lineage-native-v1",
       "frozen_sf16_commit": "68e1e9b3811e16cad014b590d7443b9063b3eb52",
       "files": result,
       "modes": ["OBS", "W", "R", "WR"],
       "env": ["C3X018_TT_MODE", "C3X018_TT_TARGET_KEY64",
               "C3X018_TT_TARGET_SLOT", "C3X018_TT_TARGET_EPOCH",
               "C3X018_TT_LOG_WRITES",
               "C3X018_TT_WRITER_BLOCK_BUDGET"],
       "limits": [
           "Single-thread cold-process native only for provenance interpretation",
           "TTEntry and Cluster layouts unchanged; shadow sidecar owns epochs",
           "Slot ordinal counts accepted payload writes, not save() calls",
           "W/WR suppress the first N matching write attempts; default budget N=1",
           "Writer budget N>1 is a cumulative intervention, not one causal writer",
           "Key16 collision is possible; only full64 writer witness is exact-key",
           "Thread concurrency may invalidate linearized writer/reader snapshot",
           "Main TT cutoff branch condition is reached; final return may be adjusted",
           "Only main/qsearch early-cutoff consumption sites covered",
           "Logging is capped at 30000 events with explicit censor marker",
           "No rescue, no proof of necessary natural mediation"
       ]
    }
    out = Path(args.out_manifest)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(receipt, indent=2) + "\n")
    print("C3X018_PHYSICAL_LINEAGE_PATCH_APPLIED")

if __name__ == "__main__":
    main()
