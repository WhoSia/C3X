#!/usr/bin/env python3
"""C3X 0.18: optional bounded physical TT probe/save telemetry for frozen SF16.
Research-only observer. Does NOT identify a causal mediator or prove key identity.
"""
import argparse
import hashlib
import json
from pathlib import Path

def exact(s,old,new,label):
    n=s.count(old)
    if n!=1: raise RuntimeError(f"C3X018_TT_ANCHOR_{label}_{n}")
    return s.replace(old,new,1)

def patch_tt(source):
    source=exact(source, '#include <thread>', '#include <thread>\n#include <atomic>\n#include <cstdlib>\n#include <cstdint>', 'INCLUDE')
    source=exact(source, 'TranspositionTable TT; // Our global transposition table',
'''TranspositionTable TT; // Our global transposition table
// Recording is optional. The counter is per process; events past cap are unobserved.
static std::atomic<uint64_t> c3x018_tt_event{0};
static bool c3x018_tt_active() { return std::getenv("C3X018_TT_TRACE") != nullptr; }
static constexpr uint64_t c3x018_tt_cap = 4096;
static void c3x018_tt_record(const char* kind, Key key, const TTEntry* slot,
                             int found, int depth, int bound, int value,
                             int old_depth, int old_bound, int old_value) {
    if (!c3x018_tt_active()) return;
    uint64_t seq = ++c3x018_tt_event;
    if (seq > c3x018_tt_cap) return;
    sync_cout << "info string c3x018_tt kind=" << kind
              << " seq=" << seq << " key64=" << uint64_t(key)
              << " slot=" << uint64_t(reinterpret_cast<uintptr_t>(slot))
              << " found=" << found
              << " depth=" << depth << " bound=" << bound << " value=" << value
              << " old_depth=" << old_depth << " old_bound=" << old_bound
              << " old_value=" << old_value << sync_endl;
}''','STATE')
    source=exact(source,
'''void TTEntry::save(Key k, Value v, bool pv, Bound b, Depth d, Move m, Value ev) {

  // Preserve any existing move''',
'''void TTEntry::save(Key k, Value v, bool pv, Bound b, Depth d, Move m, Value ev) {
  const int c3x018_old_depth = int(depth8);
  const int c3x018_old_bound = int(genBound8 & 3);
  const int c3x018_old_value = int(value16);

  // Preserve any existing move''','SAVE_START')
    source=exact(source,
'''      eval16    = (int16_t)ev;
  }
}''',
'''      eval16    = (int16_t)ev;
  }
  c3x018_tt_record("save", k, this, 1, int(depth8), int(genBound8 & 3),
                   int(value16), c3x018_old_depth, c3x018_old_bound,
                   c3x018_old_value);
}''','SAVE_END')
    source=exact(source,
'''          return found = (bool)tte[i].depth8, &tte[i];''',
'''          TTEntry* const observed = &tte[i];
          bool const hit = bool(tte[i].depth8);
          c3x018_tt_record("probe", key, observed, int(hit),
                           int(tte[i].depth8), int(tte[i].genBound8 & 3),
                           int(tte[i].value16), -1, -1, -1);
          return found = hit, observed;''','PROBE_HIT')
    source=exact(source,
'''  return found = false, replace;
}''',
'''  c3x018_tt_record("probe", key, replace, 0, int(replace->depth8),
                   int(replace->genBound8 & 3), int(replace->value16),
                   -1, -1, -1);
  return found = false, replace;
}''','PROBE_MISS')
    return source

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--source',required=True)
    p.add_argument('--out-manifest',required=True)
    a=p.parse_args()
    path=Path(a.source)/'src/tt.cpp'
    old=path.read_bytes()
    new=patch_tt(old.decode('utf-8')).encode('utf-8')
    path.write_bytes(new)
    out=Path(a.out_manifest)
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps({
      'schema':'c3x018-physical-tt-observer-v0',
      'source_before_sha256':hashlib.sha256(old).hexdigest(),
      'source_after_sha256':hashlib.sha256(new).hexdigest(),
      'activation_env':'C3X018_TT_TRACE',
      'max_recorded_events':4096,
      'warnings':['TT stores key16 only; logged key64 belongs to present caller',
                  'A probe is not a consumed value',
                  'Save may leave payload unchanged; compare old and new',
                  'Pointer slot identity is process-local',
                  'Beyond cap is censored; no natural writer attribution',
                  'Observer noninterference not validated',
                  'Full physical writer-generation ledger not implemented']
    },indent=2)+'\n')
if __name__=='__main__': main()
