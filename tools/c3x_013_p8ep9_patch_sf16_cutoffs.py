#!/usr/bin/env python3
"""C3X 0.13 P8-EP9: surgical Stockfish 16 TT cutoff observer/intervention.

Targets sf_16 ONLY. Changes no chess legality or NNUE representation.
The observational sham (OFF) must match a separately built identical source.
The interventions prevent only the early returns in main search or qsearch,
while leaving TT reads, ttMove ordering, and other TT uses intact.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import subprocess
from pathlib import Path

TAG = "sf_16"

def replace_one(s, old, new, label):
    n=s.count(old)
    if n != 1:
        raise ValueError(f"EP9_{label}_SOURCE_ANCHOR_COUNT_{n}")
    return s.replace(old,new,1)

STATS = r'''
  struct C3XEp9Stats {
    unsigned long long main_probes=0, main_hits=0, main_cutoff_eligible=0;
    unsigned long long main_cutoff_taken=0, main_cutoff_blocked=0;
    unsigned long long q_probes=0, q_hits=0, q_cutoff_eligible=0;
    unsigned long long q_cutoff_taken=0, q_cutoff_blocked=0;
  };
  C3XEp9Stats c3x_ep9_stats;
  int c3x_ep9_mode=0; // 0=OFF, 1=MAIN, 2=QSEARCH, 3=BOTH
  void c3x_ep9_begin_search() {
      c3x_ep9_stats = C3XEp9Stats{};
      const char* env=std::getenv("C3X_P8_EP9_BLOCK_CUTOFF");
      if (!env || !std::strcmp(env,"OFF")) c3x_ep9_mode=0;
      else if (!std::strcmp(env,"MAIN")) c3x_ep9_mode=1;
      else if (!std::strcmp(env,"QSEARCH")) c3x_ep9_mode=2;
      else if (!std::strcmp(env,"BOTH")) c3x_ep9_mode=3;
      else {
          std::cerr << "EP9_UNRECOGNIZED_INTERVENTION" << std::endl;
          std::exit(91);
      }
  }
  void c3x_ep9_dump() {
      const auto& s=c3x_ep9_stats;
      sync_cout << "info string c3x_p8_ep9"
        << " mode=" << c3x_ep9_mode
        << " main_probes=" << s.main_probes
        << " main_hits=" << s.main_hits
        << " main_eligible=" << s.main_cutoff_eligible
        << " main_taken=" << s.main_cutoff_taken
        << " main_blocked=" << s.main_cutoff_blocked
        << " q_probes=" << s.q_probes
        << " q_hits=" << s.q_hits
        << " q_eligible=" << s.q_cutoff_eligible
        << " q_taken=" << s.q_cutoff_taken
        << " q_blocked=" << s.q_cutoff_blocked
        << sync_endl;
  }

'''

def instrument(source):
    s=source
    s=replace_one(s,'#include <cstring>   // For std::memset\n',
       '#include <cstring>   // For std::memset\n#include <cstdlib>\n',"INCLUDE")
    s=replace_one(s,'namespace {\n\n  // Different node types',
       'namespace {\n'+STATS+'\n  // Different node types',"STATS")
    s=replace_one(s,'  TT.new_search();\n\n  Eval::NNUE::verify();',
       '  c3x_ep9_begin_search();\n  TT.new_search();\n\n  Eval::NNUE::verify();',"RESET")
    s=replace_one(s,'  sync_cout << "bestmove " << UCI::move(bestThread->rootMoves[0].pv[0], rootPos.is_chess960());',
       '  c3x_ep9_dump();\n  sync_cout << "bestmove " << UCI::move(bestThread->rootMoves[0].pv[0], rootPos.is_chess960());',"DUMP")
    # The TT lookup lines occur once each in different source contexts.
    s=replace_one(s,'    // Step 4. Transposition table lookup.\n    excludedMove = ss->excludedMove;\n    posKey = pos.key();\n    tte = TT.probe(posKey, ss->ttHit);',
       '    // Step 4. Transposition table lookup.\n    excludedMove = ss->excludedMove;\n    posKey = pos.key();\n    tte = TT.probe(posKey, ss->ttHit);\n    ++c3x_ep9_stats.main_probes;\n    c3x_ep9_stats.main_hits += ss->ttHit;',"MAIN_PROBE")
    s=replace_one(s,'    // Step 3. Transposition table lookup\n    posKey = pos.key();\n    tte = TT.probe(posKey, ss->ttHit);',
       '    // Step 3. Transposition table lookup\n    posKey = pos.key();\n    tte = TT.probe(posKey, ss->ttHit);\n    ++c3x_ep9_stats.q_probes;\n    c3x_ep9_stats.q_hits += ss->ttHit;',"Q_PROBE")
    s=replace_one(s,
       '    {\n        // If ttMove is quiet, update move sorting heuristics on TT hit (~2 Elo)',
       '    {\n        ++c3x_ep9_stats.main_cutoff_eligible;\n        // If ttMove is quiet, update move sorting heuristics on TT hit (~2 Elo)',"MAIN_ELIGIBLE")
    s=replace_one(s,'        if (pos.rule50_count() < 90)\n            return ttValue;',
       '''        if (pos.rule50_count() < 90)
        {
            if (c3x_ep9_mode & 1)
                ++c3x_ep9_stats.main_cutoff_blocked;
            else {
                ++c3x_ep9_stats.main_cutoff_taken;
                return ttValue;
            }
        }''',"MAIN_RETURN")
    s=replace_one(s,
       '''    if (  !PvNode
        && tte->depth() >= ttDepth
        && ttValue != VALUE_NONE // Only in case of TT access race or if !ttHit
        && (tte->bound() & (ttValue >= beta ? BOUND_LOWER : BOUND_UPPER)))
        return ttValue;''',
       '''    if (  !PvNode
        && tte->depth() >= ttDepth
        && ttValue != VALUE_NONE // Only in case of TT access race or if !ttHit
        && (tte->bound() & (ttValue >= beta ? BOUND_LOWER : BOUND_UPPER)))
    {
        ++c3x_ep9_stats.q_cutoff_eligible;
        if (c3x_ep9_mode & 2)
            ++c3x_ep9_stats.q_cutoff_blocked;
        else {
            ++c3x_ep9_stats.q_cutoff_taken;
            return ttValue;
        }
    }''',"Q_RETURN")
    return s

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source",required=True)
    p.add_argument("--out-manifest",required=True)
    a=p.parse_args()
    root=Path(a.source).resolve()
    sha=subprocess.check_output(["git","-C",str(root),"rev-parse","HEAD"],text=True).strip()
    tag=subprocess.check_output(["git","-C",str(root),"rev-parse",TAG+"^{}"],text=True).strip()
    if sha!=tag:raise SystemExit(f"STOCKFISH16_SOURCE_TAG_MISMATCH {sha} != {tag}")
    path=root/"src"/"search.cpp"
    before=path.read_text()
    after=instrument(before)
    path.write_text(after)
    payload={"schema":"c3x-013-p8ep9-sf16-tt-bound-return-patch-v1","source_tag":TAG,
             "source_commit":sha,
             "source_file_sha256_before":hashlib.sha256(before.encode()).hexdigest(),
             "source_file_sha256_after":hashlib.sha256(after.encode()).hexdigest(),
             "instrumented_metrics":["main_probes","main_hits","main_eligible","main_taken","main_blocked","q_probes","q_hits","q_eligible","q_taken","q_blocked"],
             "intervention_modes":{"OFF":0,"MAIN":1,"QSEARCH":2,"BOTH":3},
             "mechanism_note":"Only guards the specific early TT-return sites; TT move ordering, TT bound-based static evaluation and TT writes remain live. Not a full TT knockout.",
             "authority":"DESCRIPTIVE_UNTIL_SHAM_AND_PINNED_INTERVENTIONS_RUN"}
    out=Path(a.out_manifest);out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(payload,indent=2)+"\n")
    print("EP9_SF16_PATCH_ANCHORS_PASS",sha[:12])
if __name__=="__main__":main()
