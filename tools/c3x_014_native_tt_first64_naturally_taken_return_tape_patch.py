#!/usr/bin/env python3
"""C3X 0.14 bounded census of naturally TAKEN main TT early returns (first 64).

One exactly source-pinned SF16, in known prior source legal histories.
Apply AFTER EP9, completedDepth, ONE_MAIN, writer-sidecar, first-eligible patch.
Records only OFF returns; writes event tape AFTER engine search, not inside it.
"""
import argparse,hashlib,json
from pathlib import Path
CAP=64
def once(s,a,b,name):
    n=s.count(a)
    if n!=1:raise RuntimeError("C3X014_NATIVE_TT_TAPE_ANCHOR_"+name+"_"+str(n))
    return s.replace(a,b,1)
DECL=r"""
  struct C3X014ActualTTReturn {
    std::uint64_t key=0, writer_key=0, writer_ordinal=0, cluster=0;
    int sequence=0, ply=0, depth=0, alpha=0, beta=0, tt_value=0;
    int bound=0, saved_depth=0, saved_bound=0, saved_value=0, writer_ply=0;
    int writer_class=0, slot=-1, last_full64_match=0, writer_known=0;
    int slot_replacements=0, slot_full_writes=0, pinned_king_attacked=0;
  };
  std::vector<C3X014ActualTTReturn> c3x014_real_tt_tape;
  std::uint64_t c3x014_real_tt_taken_total=0;
  void c3x014_dump_real_tt_tape() {
    sync_cout << "info string c3x014_return_census_summary"
      << " taken_total=" << c3x014_real_tt_taken_total
      << " prefix_cap=64"
      << " recorded=" << c3x014_real_tt_tape.size() << sync_endl;
    for (const auto& e : c3x014_real_tt_tape)
      sync_cout << "info string c3x014_return_event"
        << " sequence=" << e.sequence
        << " key=" << e.key << " cluster=" << e.cluster
        << " slot=" << e.slot
        << " ply=" << e.ply << " depth=" << e.depth
        << " alpha=" << e.alpha << " beta=" << e.beta
        << " tt_value=" << e.tt_value << " tt_bound=" << e.bound
        << " writer_key=" << e.writer_key
        << " writer_ordinal=" << e.writer_ordinal
        << " writer_class=" << e.writer_class
        << " writer_ply=" << e.writer_ply
        << " writer_depth=" << e.saved_depth
        << " writer_bound=" << e.saved_bound
        << " writer_value=" << e.saved_value
        << " writer_known=" << e.writer_known
        << " full64_match=" << e.last_full64_match
        << " slot_replacements=" << e.slot_replacements
        << " slot_full_writes=" << e.slot_full_writes
        << " in_check=" << e.pinned_king_attacked
        << sync_endl;
  }
"""
TRACE=r"""
                ++c3x014_real_tt_taken_total;
                if (c3x014_real_tt_tape.size() < 64) {
                    // Passive last full-field TT writer, after native lookup was
                    // already performed; no extra Stockfish TT.probe() or save.
                    const auto nativeWriter=c3x014_tt_lookup_lineage(tte,posKey);
                    C3X014ActualTTReturn e;
                    e.sequence=int(c3x014_real_tt_taken_total);
                    e.key=posKey; e.cluster=nativeWriter.slot_cluster;
                    e.slot=nativeWriter.slot_offset;
                    e.ply=ss->ply; e.depth=depth; e.alpha=int(alpha);
                    e.beta=int(beta); e.tt_value=int(ttValue);
                    e.bound=int(tte->bound());
                    e.writer_key=nativeWriter.last_full_key;
                    e.writer_ordinal=nativeWriter.last_write_sequence;
                    e.writer_class=nativeWriter.producer_kind;
                    e.writer_ply=nativeWriter.writer_ply;
                    e.saved_depth=nativeWriter.writer_saved_depth;
                    e.saved_bound=nativeWriter.writer_saved_bound;
                    e.saved_value=nativeWriter.writer_saved_tt_value;
                    e.last_full64_match=nativeWriter.full_key_exact;
                    e.writer_known=nativeWriter.ever_written;
                    e.slot_replacements=nativeWriter.slot_reuse_events;
                    e.slot_full_writes=nativeWriter.full_overwrites;
                    e.pinned_king_attacked=int(ss->inCheck);
                    c3x014_real_tt_tape.push_back(e);
                }
"""
def main():
    p=argparse.ArgumentParser();p.add_argument("--source",required=True);p.add_argument("--out-manifest",required=True)
    a=p.parse_args()
    fn=Path(a.source)/"src/search.cpp";original=fn.read_bytes();s=original.decode()
    for token in ("c3x014_tt_lookup_lineage","c3x014_trace.first_eligible_ply","c3x014_dump_mechanism"):
        if token not in s:raise SystemExit("PREREQUISITE_NOT_LOADED_"+token)
    s=once(s,'#include "search.h"','#include "search.h"\n#include <vector>',"VECTOR_INCLUDE")
    s=once(s,'  C3X014TraceCounters c3x014_trace;',
       '  C3X014TraceCounters c3x014_trace;\n'+DECL,'RETURN_TAPE_STRUCT')
    s=once(s,'      c3x014_trace = C3X014TraceCounters{};',
       '      c3x014_trace = C3X014TraceCounters{};\n      c3x014_real_tt_tape.clear();\n      c3x014_real_tt_taken_total=0;','RETURN_TAPE_RESET')
    # This site is reached ONLY if native SF16 actually TAKES the main TT
    # early return, not a would-return event in MAIN or ONE_MAIN.
    s=once(s,'''                ++c3x_ep9_stats.main_cutoff_taken;
                return ttValue;''',
       '''                ++c3x_ep9_stats.main_cutoff_taken;
'''+TRACE+'''                return ttValue;''','NATURALLY_TAKEN_RETURN')
    s=once(s,'  c3x014_dump_mechanism();',
       '  c3x014_dump_mechanism();\n  c3x014_dump_real_tt_tape();','TAPE_OUT_AFTER_SEARCH')
    fn.write_text(s)
    result={"schema":"c3x-014-first64-actually-taken-native-main-TT-return-event-census-patch-v1",
        "native_original_sf16_commit":"68e1e9b3811e16cad014b590d7443b9063b3eb52",
        "first_K_events":64,
        "population":"All naturally TAKEN nonPV MAIN TT early returns, original Rule50/bound/depth satisfied, C3X EP9 OFF only.",
        "instrumentation_location":"original source main TT return directly before return ttValue, observational vector dumped only after run",
        "native_TT_storage_modified":False,
        "original_sha256":hashlib.sha256(original).hexdigest(),
        "patched_sha256":hashlib.sha256(s.encode()).hexdigest(),
        "limit":"Prefix first64, not random. Counts all returns but stores bounded initial events. Writer is last successful full-field TT slot save, not full value derivation."}
    f=Path(a.out_manifest);f.parent.mkdir(parents=True,exist_ok=True)
    f.write_text(json.dumps(result,indent=2)+"\n")
    print("C3X014_TT_NATURALLY_TAKEN_RETURN_TAPE_PATCH_PASS",result["patched_sha256"])
if __name__=="__main__":main()
