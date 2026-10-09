#!/usr/bin/env python3
"""C3X 0.14: instrument SF16 actual TTEntry save provenance to first TT consumer.

Surgical wrapper of all six known search.cpp TTEntry::save sites, a sidecar
indexed by physical TTEntry address, and a read-only provenance lookup at
the first dynamically blocked main TT early return. Does not change TTEntry
layout, native replacement ordering or stored 16-bit key semantics.
"""
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path

def once(s,old,new,label):
    n=s.count(old)
    if n!=1:raise RuntimeError("C3X014_LINEAGE_ANCHOR_"+label+"_"+str(n))
    return s.replace(old,new,1)
def h(b):return hashlib.sha256(b).hexdigest()

HEADER=r'''
// C3X 0.14 source-native physical-slot lineage, instrumentation only.
struct C3X014TTLineage {
    unsigned long long full_key=0, write_sequence=0, replacement_count=0;
    unsigned long long slot_write_count=0;
    int writer_site=0, last_was_full_overwrite=0, known=0, full_key_match=0;
};
struct C3X014TTLineageSummary {
    unsigned long long saves=0, full_overwrites=0, move_only_or_preserve=0;
    unsigned long long different_full_key_slot_reuses=0, mapped_slots=0;
};
void c3x014_tt_lineage_reset();
void c3x014_tt_lineage_set_next_site(int site);
void c3x014_tt_lineage_note_save(const TTEntry* slot, Key key, bool full_overwrite);
C3X014TTLineage c3x014_tt_lineage_inspect(Key requested, const TTEntry* slot);
C3X014TTLineageSummary c3x014_tt_lineage_summary();

inline void c3x014_tt_tagged_save(TTEntry* tte, int site, Key k, Value v,
                                bool pv, Bound b, Depth d, Move m, Value ev) {
    c3x014_tt_lineage_set_next_site(site);
    tte->save(k, v, pv, b, d, m, ev);
}
'''

IMPL=r'''
// The native TT stores only 16 key bits; sidecar preserves full writer key.
namespace {
  struct C3X014TTSlotRecord {
      Key fullKey=0;
      unsigned long long lastWriterSequence=0;
      unsigned long long differentKeyReuses=0;
      unsigned long long writes=0;
      int writerSite=0;
      bool lastFullWrite=false;
      bool hasFullWriter=false;
  };
  std::unordered_map<const TTEntry*, C3X014TTSlotRecord> c3x014_slot_log;
  C3X014TTLineageSummary c3x014_slot_counts;
  unsigned long long c3x014_write_seq=0;
  int c3x014_next_writer_site=0;
}
void c3x014_tt_lineage_reset() {
    c3x014_slot_log.clear();
    c3x014_slot_counts = C3X014TTLineageSummary{};
    c3x014_write_seq=0;
    c3x014_next_writer_site=0;
}
void c3x014_tt_lineage_set_next_site(int site) {c3x014_next_writer_site=site;}
void c3x014_tt_lineage_note_save(const TTEntry* slot, Key key, bool full_overwrite) {
    int site = c3x014_next_writer_site;
    c3x014_next_writer_site=0;
    ++c3x014_slot_counts.saves;
    auto& r=c3x014_slot_log[slot];
    ++r.writes;
    if (full_overwrite) {
        ++c3x014_slot_counts.full_overwrites;
        if (r.hasFullWriter && r.fullKey != key) {
            ++r.differentKeyReuses;
            ++c3x014_slot_counts.different_full_key_slot_reuses;
        }
        r.fullKey=key;
        r.writerSite=site;
        r.lastWriterSequence=++c3x014_write_seq;
        r.lastFullWrite=true;
        r.hasFullWriter=true;
    } else {
        ++c3x014_slot_counts.move_only_or_preserve;
        r.lastFullWrite=false;
    }
}
C3X014TTLineage c3x014_tt_lineage_inspect(Key requested, const TTEntry* slot) {
    C3X014TTLineage out;
    auto iter=c3x014_slot_log.find(slot);
    if (iter==c3x014_slot_log.end()) return out;
    const auto& r=iter->second;
    out.known=int(r.hasFullWriter);
    out.full_key=r.hasFullWriter ? r.fullKey : 0;
    out.full_key_match=int(r.hasFullWriter && r.fullKey==requested);
    out.writer_site=r.hasFullWriter ? r.writerSite : 0;
    out.write_sequence=r.lastWriterSequence;
    out.replacement_count=r.differentKeyReuses;
    out.slot_write_count=r.writes;
    out.last_was_full_overwrite=int(r.lastFullWrite);
    return out;
}
C3X014TTLineageSummary c3x014_tt_lineage_summary() {
    auto out=c3x014_slot_counts;
    out.mapped_slots=c3x014_slot_log.size();
    return out;
}
'''

def edit(root):
    tt_h=root/"src"/"tt.h";tt_cpp=root/"src"/"tt.cpp";search=root/"src"/"search.cpp"
    files={p:p.read_bytes() for p in (tt_h,tt_cpp,search)}
    h_s=files[tt_h].decode()
    h_s=once(h_s,"extern TranspositionTable TT;",HEADER+"\nextern TranspositionTable TT;","TT_H_INTERFACE")
    cpp=files[tt_cpp].decode()
    cpp=once(cpp,"#include <iostream>\n","#include <iostream>\n#include <unordered_map>\n","TT_CPP_INCLUDE")
    cpp=once(cpp,"TranspositionTable TT; // Our global transposition table",
        "TranspositionTable TT; // Our global transposition table\n"+IMPL,"TT_CPP_SIDECAR")
    cpp=once(cpp,
        "void TTEntry::save(Key k, Value v, bool pv, Bound b, Depth d, Move m, Value ev) {\n",
        """void TTEntry::save(Key k, Value v, bool pv, Bound b, Depth d, Move m, Value ev) {
  const bool c3x014_full_overwrite = (   b == BOUND_EXACT
      || (uint16_t)k != key16
      || d - DEPTH_OFFSET + 2 * pv > depth8 - 4);
""","TT_SAVE_PRECONDITION")
    cpp=once(cpp,
        '''      eval16    = (int16_t)ev;
  }
}


/// TranspositionTable::resize()''',
        '''      eval16    = (int16_t)ev;
  }
  c3x014_tt_lineage_note_save(this, k, c3x014_full_overwrite);
}


/// TranspositionTable::resize()''',"TT_SAVE_WRITER_CAPTURE")
    ss=files[search].decode()
    tags=[("TABLEBASE",1),("STATIC_EVAL",2),("PROBCUT",3),("MAIN_TERMINAL",4),("Q_STAND_PAT",5),("Q_TERMINAL",6)]
    if ss.count("tte->save(")!=6:raise RuntimeError("SIX_TT_WRITER_CALL_SITES_NOT_EXACT_"+str(ss.count("tte->save(")))
    for label,site in tags:
        ss=ss.replace("tte->save(",f"c3x014_tt_tagged_save(tte, {site}, ",1)
    if ss.count("tte->save(")!=0:raise RuntimeError("UNLABELED_TT_WRITER")
    ss=once(ss,"  c3x_ep9_begin_search();\n  TT.new_search();",
        "  c3x_ep9_begin_search();\n  c3x014_tt_lineage_reset();\n  TT.new_search();","TT_RESET_AT_GO")
    # ONE_MAIN patch saves the exact event being suppressed at source-native code site.
    ss=once(ss,
        "                    c3x014_trace.first_blocked_beta = int(beta);",
        """                    c3x014_trace.first_blocked_beta = int(beta);
                    auto c3x014_writer = c3x014_tt_lineage_inspect(posKey, tte);
                    c3x014_trace.first_writer_known = c3x014_writer.known;
                    c3x014_trace.first_writer_key_match = c3x014_writer.full_key_match;
                    c3x014_trace.first_writer_full_key = c3x014_writer.full_key;
                    c3x014_trace.first_writer_site = c3x014_writer.writer_site;
                    c3x014_trace.first_writer_sequence = c3x014_writer.write_sequence;
                    c3x014_trace.first_writer_slot_replacements = c3x014_writer.replacement_count;
                    c3x014_trace.first_writer_slot_saves = c3x014_writer.slot_write_count;
                    c3x014_trace.first_writer_full_overwrite = c3x014_writer.last_was_full_overwrite;""","FIRST_TT_CONSUMER_PROVENANCE")
    ss=once(ss,
        "      unsigned long long first_blocked_key=0;",
        """      unsigned long long first_blocked_key=0;
      int first_writer_known=0, first_writer_key_match=0, first_writer_site=0;
      int first_writer_full_overwrite=0;
      unsigned long long first_writer_full_key=0, first_writer_sequence=0;
      unsigned long long first_writer_slot_replacements=0, first_writer_slot_saves=0;""",
        "FIRST_TT_LINEAGE_COUNTERS")
    ss=once(ss,'''      << " first_blocked_beta=" << a.first_blocked_beta''',
        '''      << " first_blocked_beta=" << a.first_blocked_beta
      << " first_writer_known=" << a.first_writer_known
      << " first_writer_key_match=" << a.first_writer_key_match
      << " first_writer_site=" << a.first_writer_site
      << " first_writer_full_key=" << a.first_writer_full_key
      << " first_writer_sequence=" << a.first_writer_sequence
      << " first_writer_slot_replacements=" << a.first_writer_slot_replacements
      << " first_writer_slot_saves=" << a.first_writer_slot_saves
      << " first_writer_full_overwrite=" << a.first_writer_full_overwrite''',
        "PROVENANCE_TO_EXISTING_UCI_INFO")
    ss=once(ss,'  c3x014_dump_mechanism();',
        '''  c3x014_dump_mechanism();
  {
    const auto c3x014_totals=c3x014_tt_lineage_summary();
    sync_cout << "info string c3x014_slot_provenance"
      << " saves=" << c3x014_totals.saves
      << " full_overwrites=" << c3x014_totals.full_overwrites
      << " move_only_preserves=" << c3x014_totals.move_only_or_preserve
      << " other_fullkey_slot_reuses=" << c3x014_totals.different_full_key_slot_reuses
      << " mapped_slots=" << c3x014_totals.mapped_slots
      << sync_endl;
  }''',"LINEAGE_GLOBAL_SAVE_SUMMARY")
    modified={tt_h:h_s.encode(),tt_cpp:cpp.encode(),search:ss.encode()}
    # Write only after all three exact-source gates have passed.
    for f in modified:f.write_bytes(modified[f])
    return {"schema":"c3x-014-stockfish16-source-native-tt-physical-slot-writer-consumer-v1",
        "upstream":"sf_16 68e1e9b3811e16cad014b590d7443b9063b3eb52",
        "prerequisite":"EP9 + native completedDepth + ONE_MAIN patch already source-anchor-passed",
        "writer_sites":{k:v for k,v in tags},
        "modified_file_sha256":{str(k.relative_to(root)):{"before":h(files[k]),"after":h(modified[k])} for k in modified},
        "slot_registry_key":"TTEntry* physical slot address; no modification to TTEntry 10 bytes",
        "source_key_limitation":"Original TT stores only 16 low bits + cluster index; source-native sidecar stores full Key from last full TTEntry::save",
        "full_writer_certification":"sidecar last physical slot full overwrite match at ONE_MAIN actual first blocked TT lookup; this is NOT earlier writer ancestry",
        "producer_class_labels":"All six search.cpp TTEntry::save sites labeled; other TTEntry writers outside search.cpp if later discovered will be 0 and cannot be assigned a known causal producer",
        "intervention":"Only first actual would-be main nonPV TT early return blocked by pre-existing ONE_MAIN; lineage is passive",
        "control":"CLEAN-vs-OFF exact root bestmove, all rank values and nodes, cold replication; no outcome data from P1 heldout."}

def main():
    a=argparse.ArgumentParser();a.add_argument("--source",required=True);a.add_argument("--out-manifest",required=True)
    z=a.parse_args();r=Path(z.source).resolve();manifest=edit(r)
    out=Path(z.out_manifest);out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(manifest,indent=2)+"\n")
    print("C3X014_NATIVE_TT_SLOT_PRODUCER_CONSUMER_PATCH_PASS",
          manifest["modified_file_sha256"]["src/tt.cpp"]["after"],flush=True)
if __name__=="__main__":main()
