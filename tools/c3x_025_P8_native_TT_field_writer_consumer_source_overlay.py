#!/usr/bin/env python3
"""Strict SHA pinned SF16 original TT field-sensitive shadow + source reader observer.
No actual Stockfish branch, value, TT slot or native SEE result is changed.
Single-thread diagnostics only; 256 total emitted events + CENSORED marker.
"""
import argparse,hashlib,json
from pathlib import Path

SHA={"tt.cpp":"d132fb235050916682ea258de2dc8825712d370216342f46f64d7977ee1557ba",
     "search.cpp":"21b79baa7ce9dabec5b3b9e3854bed9869a1935277247832e550cf395bccd644"}
REPLACEMENTS={
"tt.cpp":[
 ("#include <thread>\n","#include <thread>\n#include <cstdlib>\n#include <unordered_map>\n","includes"),
 ("TranspositionTable TT; // Our global transposition table\n",
"""TranspositionTable TT; // Our global transposition table

// C3X025-P8 metadata-only per-TTEntry* two independent original writer origins.
// This log is single-thread-only, bounded and never part of actual TT decisions.
struct C3X025_P8_FieldWriters {
    uint64_t move_serial=0, score_serial=0;
    Key move_key=0, score_key=0;
};
static thread_local std::unordered_map<const TTEntry*,C3X025_P8_FieldWriters> c3x025_p8_meta;
static thread_local uint64_t c3x025_p8_clock=0;
static thread_local unsigned c3x025_p8_public_count=0;
static thread_local bool c3x025_p8_censored=false;
bool c3x025_p8_on() {
    const char* v=std::getenv("C3X025_P8_TT_FIELDS");
    return v && std::strcmp(v,"1")==0;
}
static void c3x025_p8_log(const char* kind, uint64_t serial,
       uint64_t move_writer, uint64_t score_writer,
       bool move_exact, bool score_exact, bool found, int depth, int ply) {
    if (!c3x025_p8_on()) return;
    if (c3x025_p8_public_count++ >= 256) {
        if (!c3x025_p8_censored) {
            c3x025_p8_censored=true;
            sync_cout << "info string c3x025_p8 kind=CENSORED"
                      << " after_public_events=256" << sync_endl;
        }
        return;
    }
    sync_cout << "info string c3x025_p8 kind=" << kind
              << " serial=" << serial
              << " move_writer=" << move_writer
              << " score_writer=" << score_writer
              << " move_key_exact=" << int(move_exact)
              << " score_key_exact=" << int(score_exact)
              << " tt_hit=" << int(found)
              << " depth=" << depth << " ply=" << ply
              << sync_endl;
}
// Source-native *actual assignment* or actual numeric cutoff, never guessed
// from an outer probe hit. Stored keys remain in the private process only.
void c3x025_p8_consume(const TTEntry* slot, Key native_key, const char* kind,
                      bool found, int depth, int ply) {
    if (!c3x025_p8_on()) return;
    const uint64_t now=++c3x025_p8_clock;
    auto i=c3x025_p8_meta.find(slot);
    if (i==c3x025_p8_meta.end()) {
        c3x025_p8_log(kind,now,0,0,false,false,found,depth,ply);
        return;
    }
    const auto& a=i->second;
    c3x025_p8_log(kind,now,a.move_serial,a.score_serial,
                  a.move_serial && a.move_key==native_key,
                  a.score_serial && a.score_key==native_key,
                  found,depth,ply);
}
""","shadow-state"),
 ("void TTEntry::save(Key k, Value v, bool pv, Bound b, Depth d, Move m, Value ev) {",
"""void TTEntry::save(Key k, Value v, bool pv, Bound b, Depth d, Move m, Value ev) {
  const bool c3x025_p8_movewrite=bool(m || (uint16_t)k!=key16);
  const bool c3x025_p8_scorewrite=(b==BOUND_EXACT || (uint16_t)k!=key16 ||
                                  d-DEPTH_OFFSET+2*pv>depth8-4);
""","before-save-branch"),
 ("      eval16    = (int16_t)ev;\n  }\n}\n\n\n/// TranspositionTable::resize()",
"""      eval16    = (int16_t)ev;
  }
  if (c3x025_p8_on() && (c3x025_p8_movewrite || c3x025_p8_scorewrite)) {
      auto &origin=c3x025_p8_meta[this];
      if (c3x025_p8_movewrite) {
          origin.move_serial=++c3x025_p8_clock;
          origin.move_key=k;
          c3x025_p8_log("WRITE_MOVE",origin.move_serial,origin.move_serial,
                   origin.score_serial,true,
                   origin.score_serial && origin.score_key==k,
                   true,int(depth8),-1);
      }
      if (c3x025_p8_scorewrite) {
          origin.score_serial=++c3x025_p8_clock;
          origin.score_key=k;
          c3x025_p8_log("WRITE_SCORE",origin.score_serial,origin.move_serial,
                   origin.score_serial,origin.move_serial && origin.move_key==k,
                   true,true,int(depth8),-1);
      }
  }
}


/// TranspositionTable::resize()""","after-save-original"),
 ],
"search.cpp":[
 ("namespace Stockfish {\n",
"""namespace Stockfish {
// C3X025-P8 forward declaration; implementation in source-only tt.cpp.
void c3x025_p8_consume(const TTEntry*, Key,const char*,bool,int,int);
""","forward-consumer"),
 ("    ttCapture = ttMove && pos.capture_stage(ttMove);",
"""    if (ss->ttHit && !rootNode && ttMove)
        c3x025_p8_consume(tte,posKey,"MAIN_MOVE_HINT_READ",true,depth,ss->ply);
    if (ss->ttHit && ttValue!=VALUE_NONE)
        c3x025_p8_consume(tte,posKey,"MAIN_SCORE_CONVERTED",true,depth,ss->ply);
    ttCapture = ttMove && pos.capture_stage(ttMove);""","main-assignment"),
 ("    {\n        // If ttMove is quiet, update move sorting heuristics on TT hit (~2 Elo)",
"""    {
        c3x025_p8_consume(tte,posKey,"MAIN_TT_BOUNDED_CUTOFF_EXECUTED",ss->ttHit,depth,ss->ply);
        // If ttMove is quiet, update move sorting heuristics on TT hit (~2 Elo)""","main-actual-cutoff"),
 ("    ttMove = ss->ttHit ? tte->move() : MOVE_NONE;\n    pvHit = ss->ttHit && tte->is_pv();",
"""    ttMove = ss->ttHit ? tte->move() : MOVE_NONE;
    if (ss->ttHit && ttMove)
        c3x025_p8_consume(tte,posKey,"Q_MOVE_HINT_READ",true,ttDepth,ss->ply);
    if (ss->ttHit && ttValue!=VALUE_NONE)
        c3x025_p8_consume(tte,posKey,"Q_SCORE_CONVERTED",true,ttDepth,ss->ply);
    pvHit = ss->ttHit && tte->is_pv();""","q-assignment"),
 ("""        && (tte->bound() & (ttValue >= beta ? BOUND_LOWER : BOUND_UPPER)))
        return ttValue;

    // Step 4. Static evaluation of the position""",
"""        && (tte->bound() & (ttValue >= beta ? BOUND_LOWER : BOUND_UPPER)))
    {
        c3x025_p8_consume(tte,posKey,"Q_TT_BOUNDED_CUTOFF_EXECUTED",ss->ttHit,ttDepth,ss->ply);
        return ttValue;
    }

    // Step 4. Static evaluation of the position""","q-actual-cutoff"),
 ]}
def patch(source:dict[str,bytes])->tuple[dict[str,bytes],dict]:
    if set(source)!=set(SHA):raise ValueError("P8_EXACT_TWO_ORIGINAL_SOURCE_FILES_REQUIRED")
    for path,raw in source.items():
        if hashlib.sha256(raw).hexdigest()!=SHA[path]:
            raise ValueError("P8_ORIGINAL_UPSTREAM_SOURCE_SHA_NOT_VERIFIED_"+path)
    result={}
    for path,rules in REPLACEMENTS.items():
        s=source[path].decode("utf-8")
        for old,new,label in rules:
            n=s.count(old)
            if n!=1:raise ValueError(f"P8_SOURCE_ANCHOR_{path}_{label}_{n}")
            s=s.replace(old,new,1)
        result[path]=s.encode()
    if restore(result)!=source:raise AssertionError("P8_EXACT_SOURCE_REVERSE_NOT_BYTE_EQUAL")
    return result,{"schema":"c3x025-P8-source-native-field-sensitive-writer-and-search-consumer-overlay-v1",
        "original_upstream_source_sha256":SHA,
        "patched_source_sha256":{n:hashlib.sha256(v).hexdigest() for n,v in result.items()},
        "full_original_source_restored_exact_bytes":True,
        "native_TT_score_vs_move_field_writers_separately_timestamped":True,
        "consumer_evidence_labels":["MAIN_MOVE_HINT_READ","MAIN_SCORE_CONVERTED",
           "MAIN_TT_BOUNDED_CUTOFF_EXECUTED","Q_MOVE_HINT_READ","Q_SCORE_CONVERTED",
           "Q_TT_BOUNDED_CUTOFF_EXECUTED"],
        "source_identity_privately_tracks_full64_writer_key":True,
        "public_native_full64_keys_or_TT_pointer_values_disclosed":False,
        "native_public_log_cap":256,"after_cap":"CENSORED",
        "causal_root_ancestry_observed":False,
        "chess_strength_performance_benefit_measured":False}
def restore(patched:dict[str,bytes])->dict[str,bytes]:
    out={}
    for path,rules in REPLACEMENTS.items():
        s=patched[path].decode()
        for old,new,label in reversed(rules):
            if s.count(new)!=1:
                raise ValueError(f"P8_REVERSE_PATCH_FAILED_{path}_{label}")
            s=s.replace(new,old,1)
        out[path]=s.encode()
    return out
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source",required=True)
    p.add_argument("--out-manifest",required=True)
    args=p.parse_args()
    root=Path(args.source)/"src"
    old={n:(root/n).read_bytes() for n in SHA}
    changed,metadata=patch(old)
    for n,b in changed.items():(root/n).write_bytes(b)
    dest=Path(args.out_manifest);dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(json.dumps(metadata,sort_keys=True,indent=2)+"\n")
    print("C3X025_P8_PINNED_ORIGINAL_AND_REVERSIBLE_SOURCE",metadata,flush=True)
if __name__=="__main__":main()
