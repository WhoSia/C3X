#!/usr/bin/env python3
"""C3X 0.14 TT-entry last-writer physical-slot sidecar; fails closed on sf_16 drift.

Apply AFTER frozen C3X EP9, completedDepth and ONE_MAIN patch. No TTEntry
layout or search decision changes. Single-thread source-audited experiment.
"""
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path

def put_once(s,old,new,name):
    n=s.count(old)
    if n!=1:raise RuntimeError(f"TT_LINEAGE_ANCHOR_{name}_{n}")
    return s.replace(old,new,1)

HEADER=r"""
// C3X 0.14 Pn internal observability only; does not alter native TTEntry storage.
struct C3X014Lineage {
  std::uint64_t slot_cluster=0, last_full_key=0, last_write_sequence=0, previous_full_key=0;
  int slot_offset=-1, producer_kind=0, last_touch_kind=0;
  int full_key_exact=0, previous_full_key_exists=0, ever_written=0;
  int full_overwrites=0, slot_reuse_events=0, last_write_was_move_only=0;
};
struct C3X014TTTotals {
  std::uint64_t save_calls=0, full_field_writes=0, move_only_writes=0;
  std::uint64_t physical_slot_reuse=0, matched_exact_consumptions=0;
  std::uint64_t unknown_slot_consumptions=0, unequal_key_consumptions=0;
  std::uint64_t probe_calls=0, probe_nonempty_hits=0;
};
C3X014Lineage c3x014_tt_lookup_lineage(const TTEntry*, Key);
C3X014TTTotals c3x014_tt_total_snapshot();
void c3x014_tt_reset_sidecar();
void c3x014_tt_save_labeled(TTEntry*, int producer_kind, Key, Value, bool, Bound, Depth, Move, Value);
"""

CPP=r"""
// C3X 0.14 sidecar: pointer identifies the concrete TTEntry slot, distinct from
// the weak low16 original key. No change to native 10-byte TTEntry layout.
// All experiments pinned Threads=1; NOT thread safe for parallel engines.
struct C3X014PhysicalWrite {
  Key full_key=0, predecessor_key=0, last_touch_key=0;
  std::uint64_t write_sequence=0;
  int tag=0, touch_tag=0, full_overwrites=0, reuse_events=0;
  bool initialized=false, had_predecessor=false, last_move_only=false;
};
static std::unordered_map<const TTEntry*, C3X014PhysicalWrite> c3x014_slots;
static C3X014TTTotals c3x014_tt_totals;
static int c3x014_active_writer_label=0;

void c3x014_tt_reset_sidecar() {
  c3x014_slots.clear();
  c3x014_tt_totals=C3X014TTTotals{};
  c3x014_active_writer_label=0;
}
void c3x014_record_saved_slot(const TTEntry* p, Key k, bool full) {
  ++c3x014_tt_totals.save_calls;
  auto& r=c3x014_slots[p];
  r.last_touch_key=k;
  r.touch_tag=c3x014_active_writer_label;
  r.last_move_only=!full;
  if (full) {
    ++c3x014_tt_totals.full_field_writes;
    if (r.initialized && r.full_key != k) {
      ++c3x014_tt_totals.physical_slot_reuse;
      ++r.reuse_events;
      r.predecessor_key=r.full_key;
      r.had_predecessor=true;
    }
    r.initialized=true;
    r.full_key=k;
    r.tag=c3x014_active_writer_label;
    r.write_sequence=c3x014_tt_totals.save_calls;
    ++r.full_overwrites;
  } else {
    ++c3x014_tt_totals.move_only_writes;
  }
}
void c3x014_tt_save_labeled(TTEntry* e, int tag, Key k, Value v, bool pv, Bound b,
                            Depth d, Move m, Value ev) {
  const int old=c3x014_active_writer_label;
  c3x014_active_writer_label=tag;
  e->save(k,v,pv,b,d,m,ev);
  c3x014_active_writer_label=old;
}
C3X014Lineage c3x014_tt_lookup_lineage(const TTEntry* p, Key key) {
  C3X014Lineage x;
  x.slot_cluster=TT.c3x014_cluster_index(key);
  x.slot_offset=int(p - TT.first_entry(key));
  auto it=c3x014_slots.find(p);
  if (it==c3x014_slots.end() || !it->second.initialized) {
    ++c3x014_tt_totals.unknown_slot_consumptions;
    return x;
  }
  const auto& r=it->second;
  x.ever_written=1;
  x.last_full_key=r.full_key;
  x.full_key_exact=int(r.full_key==key);
  x.last_write_sequence=r.write_sequence;
  x.producer_kind=r.tag;
  x.last_touch_kind=r.touch_tag;
  x.previous_full_key=r.predecessor_key;
  x.previous_full_key_exists=int(r.had_predecessor);
  x.full_overwrites=r.full_overwrites;
  x.slot_reuse_events=r.reuse_events;
  x.last_write_was_move_only=int(r.last_move_only);
  if (x.full_key_exact)++c3x014_tt_totals.matched_exact_consumptions;
  else ++c3x014_tt_totals.unequal_key_consumptions;
  return x;
}
C3X014TTTotals c3x014_tt_total_snapshot() { return c3x014_tt_totals; }
"""

SOURCE_SAVE_LABELS=[
    ("MAIN_TABLEBASE_WRITE",1),
    ("MAIN_STATIC_EVALUATION",2),
    ("MAIN_PROBCUT",3),
    ("MAIN_TERMINAL",4),
    ("QSEARCH_EARLY",5),
    ("QSEARCH_TERMINAL",6)
]

def patch_sf(root):
    root=Path(root);header=root/"src/tt.h";ttcpp=root/"src/tt.cpp";search=root/"src/search.cpp"
    raw={k:f.read_bytes() for k,f in (("tt.h",header),("tt.cpp",ttcpp),("search.cpp",search))}
    h,cpp,s=(raw[k].decode() for k in ("tt.h","tt.cpp","search.cpp"))
    if "c3x014_tt_lookup_lineage" in h or "c3x014_tt_lookup_lineage" in cpp:
        raise RuntimeError("TT_LINEAGE_DUPLICATE_PATCH")
    for marker in ("c3x014_completion_probe","C3X014TraceCounters","c3x014_path","ONE_MAIN"):
        if marker not in s:raise RuntimeError("TT_LINEAGE_REQUIRES_EXISTING_PATCH_"+marker)
    h=put_once(h,'#include "misc.h"','#include "misc.h"\n#include <cstdint>','HEADER_INCLUDE')
    h=put_once(h,'  TTEntry* first_entry(const Key key) const {',
      '  std::uint64_t c3x014_cluster_index(const Key key) const { return mul_hi64(key, clusterCount); }\n\n  TTEntry* first_entry(const Key key) const {','HEADER_CLUSTER')
    h=put_once(h,"extern TranspositionTable TT;",HEADER+"\nextern TranspositionTable TT;","HEADER_DECL")
    cpp=put_once(cpp,'#include <thread>','#include <thread>\n#include <unordered_map>\n#include <cstdint>','CPP_INCLUDES')
    cpp=put_once(cpp,'TranspositionTable TT; // Our global transposition table',
       'TranspositionTable TT; // Our global transposition table\n'+CPP,'CPP_SIDECAR')
    # Determine precisely whether save overwrites key/depth/value/bound/eval or
    # only move16. New bool is identical to original if expression.
    orig="""  if (   b == BOUND_EXACT
      || (uint16_t)k != key16
      || d - DEPTH_OFFSET + 2 * pv > depth8 - 4)
  {"""
    new="""  const bool c3x014_full_field_write=(   b == BOUND_EXACT
      || (uint16_t)k != key16
      || d - DEPTH_OFFSET + 2 * pv > depth8 - 4);
  if (c3x014_full_field_write)
  {"""
    cpp=put_once(cpp,orig,new,"TT_SAVE_CONDITION")
    cpp=put_once(cpp,"      eval16    = (int16_t)ev;\n  }\n}",
       "      eval16    = (int16_t)ev;\n  }\n  c3x014_record_saved_slot(this,k,c3x014_full_field_write);\n}","TT_SAVE_RECORD")
    cpp=put_once(cpp,"TTEntry* TranspositionTable::probe(const Key key, bool& found) const {\n",
      "TTEntry* TranspositionTable::probe(const Key key, bool& found) const {\n  ++c3x014_tt_totals.probe_calls;\n","TT_PROBE_CALL")
    cpp=put_once(cpp,"          return found = (bool)tte[i].depth8, &tte[i];",
      "          c3x014_tt_totals.probe_nonempty_hits += bool(tte[i].depth8);\n          return found = (bool)tte[i].depth8, &tte[i];","TT_PROBE_HIT")
    # Source audit found EXACTLY six dynamic TT writes in original SF16 search.cpp.
    if s.count("tte->save(")!=6:raise RuntimeError("TT_SAVE_CALLER_CENSUS_CHANGED_"+str(s.count("tte->save(")))
    for name,tag in SOURCE_SAVE_LABELS:
        s=s.replace("tte->save(",f"c3x014_tt_save_labeled(tte, {tag}, ",1)
    # Reset registry in the original EP9 native run initialization, before root search.
    s=put_once(s,'      c3x014_trace = C3X014TraceCounters{};',
      '      c3x014_trace = C3X014TraceCounters{};\n      c3x014_tt_reset_sidecar();','RESET')
    # Attach producer sidecar to exact event BEFORE the suppressed return falls through.
    old="                    c3x014_trace.first_blocked_beta = int(beta);"
    new=old+"""
                    const auto producer=c3x014_tt_lookup_lineage(tte,posKey);
                    c3x014_trace.first_slot_cluster=producer.slot_cluster;
                    c3x014_trace.first_slot_offset=producer.slot_offset;
                    c3x014_trace.first_last_saved_full_key=producer.last_full_key;
                    c3x014_trace.first_last_write_seq=producer.last_write_sequence;
                    c3x014_trace.first_writer_kind=producer.producer_kind;
                    c3x014_trace.first_last_touch_kind=producer.last_touch_kind;
                    c3x014_trace.first_fullkey_exact=producer.full_key_exact;
                    c3x014_trace.first_writer_exists=producer.ever_written;
                    c3x014_trace.first_slot_reuse=producer.slot_reuse_events;
                    c3x014_trace.first_full_overwrites=producer.full_overwrites;
                    c3x014_trace.first_last_move_only=producer.last_write_was_move_only;
                    c3x014_trace.first_previous_writer_key=producer.previous_full_key;
"""
    s=put_once(s,old,new,"FIRST_RETURN_LINEAGE")
    old="      unsigned long long first_blocked_key=0;"
    new=old+"""
      std::uint64_t first_slot_cluster=0, first_last_saved_full_key=0,first_last_write_seq=0,first_previous_writer_key=0;
      int first_slot_offset=-1,first_writer_kind=0,first_last_touch_kind=0;
      int first_fullkey_exact=0,first_writer_exists=0,first_slot_reuse=0,first_full_overwrites=0,first_last_move_only=0;
"""
    s=put_once(s,old,new,"LINEAGE_STRUCT")
    old='      << " first_blocked_beta=" << a.first_blocked_beta'
    new=old+"""
      << " producer_cluster=" << a.first_slot_cluster
      << " producer_slot_offset=" << a.first_slot_offset
      << " producer_full_key=" << a.first_last_saved_full_key
      << " producer_write_sequence=" << a.first_last_write_seq
      << " producer_class=" << a.first_writer_kind
      << " producer_last_touch_class=" << a.first_last_touch_kind
      << " producer_full_key_matches=" << a.first_fullkey_exact
      << " producer_known=" << a.first_writer_exists
      << " producer_slot_replacements=" << a.first_slot_reuse
      << " producer_full_field_writes=" << a.first_full_overwrites
      << " producer_last_move_only=" << a.first_last_move_only
      << " producer_previous_full_key=" << a.first_previous_writer_key
"""
    s=put_once(s,old,new,"LINEAGE_DUMP")
    old='  c3x014_dump_mechanism();'
    new=old+"""
  {
    const auto t=c3x014_tt_total_snapshot();
    sync_cout << "info string c3x014_tt_writes"
       << " saves=" << t.save_calls
       << " full=" << t.full_field_writes
       << " move_only=" << t.move_only_writes
       << " recycled=" << t.physical_slot_reuse
       << " first_key_match=" << t.matched_exact_consumptions
       << " first_unknown=" << t.unknown_slot_consumptions
       << " first_key_mismatch=" << t.unequal_key_consumptions
       << " probes=" << t.probe_calls
       << " probe_hits=" << t.probe_nonempty_hits
       << sync_endl;
  }
"""
    s=put_once(s,old,new,"SIDECARE_TOTAL_DUMP")
    # Source labels order is a fixed audit of the six saved-entry call sites.
    after={"tt.h":h.encode(),"tt.cpp":cpp.encode(),"search.cpp":s.encode()}
    for name in after:
        (root/"src"/name).write_bytes(after[name])
    return {"schema":"c3x-014-tt-producer-consumer-physical-slot-sidecar-patch-v1",
      "source":"official Stockfish16 sf_16 68e1e9b3811e16cad014b590d7443b9063b3eb52 plus exact C3X EP9/completedDepth/ONE_MAIN",
      "tt_entry_layout_changed":False,"source_writers_tagged":dict(SOURCE_SAVE_LABELS),
      "tags_meaning":"1 main tablebase, 2 main static eval, 3 main probcut, 4 main terminal, 5 qsearch early, 6 qsearch terminal",
      "data_justification":"TTEntry contains only 16-bit key but pointer sidecar preserves last 64-bit full-field writer key and same physical slot reuse",
      "truth_limit":"Sidecar records last full-field successful TT save and move-only touches, not all NNUE/history or full TT ancestry; one-thread only",
      "original_sha256":{k:hashlib.sha256(v).hexdigest() for k,v in raw.items()},
      "patched_sha256":{k:hashlib.sha256(v).hexdigest() for k,v in after.items()}}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source",required=True);p.add_argument("--out-manifest",required=True)
    a=p.parse_args()
    obj=patch_sf(a.source)
    out=Path(a.out_manifest);out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(obj,indent=2)+"\n")
    print("C3X014_NATIVE_TT_FULL64_PRODUCER_LINEAGE_PATCH_PASS",
      json.dumps(obj["patched_sha256"]),flush=True)
if __name__=="__main__":main()
