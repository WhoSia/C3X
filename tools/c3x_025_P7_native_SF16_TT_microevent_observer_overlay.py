#!/usr/bin/env python3
"""Opt-in original Stockfish16 tt.cpp scalar-only native observer, reversible patch.
Source checksum pin, no TT/SEE move/value, search policy or legality changes.
No modified binary distributed. Original Stockfish is GPLv3.
"""
import argparse,hashlib,json
from pathlib import Path

CPP_SHA="d132fb235050916682ea258de2dc8825712d370216342f46f64d7977ee1557ba"
INCLUDE='#include <thread>\n'
INCLUDE_NEW='#include <thread>\n#include <cstdlib>  // C3X025 opt-in TT scalar-only observer\n'
STATE='TranspositionTable TT; // Our global transposition table\n'
STATE_NEW=STATE+"""
// C3X025-P7 observer: bounded source scalar tags, original TT clauses unchanged.
thread_local int c3x025_p7_probe_count=0;
thread_local int c3x025_p7_moveonly_count=0;
bool c3x025_p7_enabled() {
    const char* e=std::getenv("C3X025_P7_TT_MICRO_OBS");
    return e && std::strcmp(e,"1")==0;
}
"""
SAVE='void TTEntry::save(Key k, Value v, bool pv, Bound b, Depth d, Move m, Value ev) {\n'
SAVE_NEW=SAVE+"""
  // Observe EXACT original field write guards, not one unified TT writer.
  const bool c3x025_p7_move_write=bool(m || (uint16_t)k != key16);
  const bool c3x025_p7_score_write=(b == BOUND_EXACT || (uint16_t)k != key16
                                      || d - DEPTH_OFFSET + 2 * pv > depth8 - 4);
"""
END_SAVE='      eval16    = (int16_t)ev;\n  }\n}\n\n\n/// TranspositionTable::resize()'
END_SAVE_NEW="""      eval16    = (int16_t)ev;
  }
  if (c3x025_p7_move_write && !c3x025_p7_score_write &&
      c3x025_p7_enabled() && c3x025_p7_moveonly_count<8) {
      ++c3x025_p7_moveonly_count;
      sync_cout << "info string c3x025_tt_micro kind=move_only_save"
                << " move_changed=1 score_fields_changed=0"
                << " seq=" << c3x025_p7_moveonly_count << sync_endl;
  }
}


/// TranspositionTable::resize()"""
REFRESH='          tte[i].genBound8 = uint8_t(generation8 | (tte[i].genBound8 & (GENERATION_DELTA - 1))); // Refresh'
REFRESH_NEW="""          const bool c3x025_p7_log=c3x025_p7_enabled() && c3x025_p7_probe_count<8;
          const unsigned c3x025_p7_oldgen=unsigned(tte[i].genBound8);
          tte[i].genBound8 = uint8_t(generation8 | (tte[i].genBound8 & (GENERATION_DELTA - 1))); // Refresh
          if (c3x025_p7_log) {
              ++c3x025_p7_probe_count;
              sync_cout << "info string c3x025_tt_micro kind=probe_refresh"
                        << " found=" << int(bool(tte[i].depth8))
                        << " prev_gen=" << c3x025_p7_oldgen
                        << " new_gen=" << unsigned(tte[i].genBound8)
                        << " current_gen=" << unsigned(generation8)
                        << " seq=" << c3x025_p7_probe_count << sync_endl;
          }"""

REPL=(("include",INCLUDE,INCLUDE_NEW),("state",STATE,STATE_NEW),
      ("save-head",SAVE,SAVE_NEW),("save-tail",END_SAVE,END_SAVE_NEW),
      ("probe-generation-refresh",REFRESH,REFRESH_NEW))
def patch(src:str)->str:
    for name,old,new in REPL:
        if src.count(old)!=1:
            raise ValueError("P7_OFFICIAL_PINNED_SOURCE_ANCHOR_"+name+"_COUNT_"+str(src.count(old)))
        src=src.replace(old,new,1)
    return src
def restore(modified:str)->str:
    for name,old,new in reversed(REPL):
        if modified.count(new)!=1:
            raise ValueError("P7_REVERSAL_SOURCE_PATCH_SCOPE_"+name)
        modified=modified.replace(new,old,1)
    return modified
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source",required=True)
    p.add_argument("--out-manifest",required=True)
    a=p.parse_args()
    source=Path(a.source)/"src"/"tt.cpp"
    original=source.read_bytes()
    digest=hashlib.sha256(original).hexdigest()
    if digest!=CPP_SHA:raise ValueError("P7_ORIGINAL_UPSTREAM_TT_CPP_SHA_DRIFT")
    mod=patch(original.decode("utf-8"))
    if restore(mod).encode("utf-8")!=original:
        raise AssertionError("P7_OBSERVER_ONLY_EXACT_SOURCE_REVERSAL_NOT_BYTE_EQUAL")
    source.write_bytes(mod.encode("utf-8"))
    result={
      "schema":"c3x025-P7-read-only-optin-native-TT-source-probe-and-move-provenance-overlay-v1",
      "official_Stockfish16_tt_cpp_original_SHA256":digest,
      "modified_compilation_source_SHA256":hashlib.sha256(source.read_bytes()).hexdigest(),
      "source_patch_reversible_original_byte_equal":True,
      "opt_in_environment":"C3X025_P7_TT_MICRO_OBS",
      "TT_native_bounded_probe_refresh_cap":8,
      "TT_native_bounded_move_only_save_cap":8,
      "original_native_TT_probe_write_guards_unchanged":True,
      "no_original_Stockfish_cpp_or_modified_binary_redistributed":True,
      "no_original_chess_keys_FEN_PGN_ancestors_printed":True,
      "scientific_limit":"OBSERVATIONAL_NATIVE_SOURCE_MICROEVENTS_NOT_TT_FIRST_DOSE_NOT_ELO_OR_NATURAL_SEE_MEDIATION"}
    dest=Path(a.out_manifest)
    dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(json.dumps(result,sort_keys=True,indent=2)+"\n")
    print("C3X025_P7_NATIVE_TT_OBSERVER_PATCH_REVERSIBLE_SOURCE_SHA",result["modified_compilation_source_SHA256"],flush=True)
if __name__=="__main__":main()
