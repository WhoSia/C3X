#!/usr/bin/env python3
"""C3X0.25 P3 pinned unmodified Stockfish16 TTL resource side effect source audit.
This reads SOURCE only and never executes an engine, TT treatment or untested ELO.
"""
import argparse,hashlib,json,subprocess
from pathlib import Path
PINNED="68e1e9b3811e16cad014b590d7443b9063b3eb52"
SCHEMA="c3x025-P3-original-Stockfish16-TT-probe-refresh-and-replacement-source-code-audit-v1"
PROOFS={
"3_slots_per_TT_cluster":("tt.h","static constexpr int ClusterSize = 3;"),
"tiny_entry_key_fragment":("tt.h","uint16_t key16;"),
"8bit_generation_delta":("tt.h","static constexpr int      GENERATION_DELTA = (1 << GENERATION_BITS);"),
"generation_new_search_step":("tt.h","void new_search() { generation8 += GENERATION_DELTA; }"),
"tt_save_preserves_move_when_same_key":("tt.cpp","if (m || (uint16_t)k != key16)"),
"exact_bound_write_preference":("tt.cpp","b == BOUND_EXACT"),
"depth_and_PV_write_priority":("tt.cpp","d - DEPTH_OFFSET + 2 * pv > depth8 - 4"),
"low_16bit_key_match_or_empty_probe":("tt.cpp","if (tte[i].key16 == key16 || !tte[i].depth8)"),
"probe_refreshes_generation_before_return":("tt.cpp","tte[i].genBound8 = uint8_t(generation8 | (tte[i].genBound8 & (GENERATION_DELTA - 1)));"),
"probe_occupancy_before_return":("tt.cpp","return found = (bool)tte[i].depth8, &tte[i];"),
"depth_minus_generation_age_replacement":("tt.cpp","GENERATION_CYCLE + generation8 - replace->genBound8"),
"tt_native_search_probes":("search.cpp","tte = TT.probe(posKey, ss->ttHit);"),
"tt_native_value_converted_before_use":("search.cpp","ttValue = ss->ttHit ? value_from_tt(tte->value(), ss->ply, pos.rule50_count()) : VALUE_NONE;"),
"tt_native_move_as_separate_consumer":("search.cpp","ttMove =  rootNode ?"),
"nonPV_bound_cutoff_possible":("search.cpp","tte->bound() & (ttValue >= beta ? BOUND_LOWER : BOUND_UPPER)"),
"native_SEE_ge_pruning_sites_exist":("search.cpp","pos.see_ge(")}
def audit(blobs):
    if set(blobs)!={"tt.h","tt.cpp","search.cpp"}:
        raise ValueError("P3_ONLY_THREE_ORIGINAL_STOCKFISH16_SOURCE_FILES")
    parsed={k:v.decode("utf-8",errors="strict") if isinstance(v,bytes) else v for k,v in blobs.items()}
    for name,(file,code) in PROOFS.items():
        if code not in parsed[file]:
            raise ValueError("P3_PINNED_STOCKFISH16_SEMANTIC_CHANGED_"+name)
    if any("c3x018" in parsed[k] or "c3x023" in parsed[k] for k in parsed):
        raise ValueError("P3_PINNED_SOURCE_IS_ALREADY_INSTRUMENTED_NOT_UPSTREAM")
    return {"schema":SCHEMA,"scientific_scope":"PINNED_SOURCE_STATIC_SEMANTICS_ONLY_NOT_NATIVE_EXECUTION_OR_ELO",
       "unmodified_original_upstream_git_commit":PINNED,
       "unmodified_upstream_cpp_sha256":{
          k:hashlib.sha256(v.encode() if isinstance(v,str) else v).hexdigest()
          for k,v in sorted(blobs.items())},
       "static_semantic_source_gates_all_passed":{k:True for k in PROOFS},
       "TT_probe_can_refresh_replacement_age_without_consuming_value":True,
       "original_TT_entry_contains_low16_fragment_not_full_physical_proof":True,
       "tt_move_ordering_separate_from_numeric_tt_value_return":True,
       "tt_generation_and_replacement_age_may_change_future_resource_residency":True,
       "SEE_full_computational_node_state_or_causal_mediation_identified":False,
       "source_code_presence_proves_real_2025July_case_branch_executed":False,
       "TT_engine_improvement_or_Elo_performance_validated":False,
       "next_engineering_tests":["actual native E0/E1 resource-preserving trace",
           "isolate target TT_MOVE ordering from TT_NUMERIC cutoff",
           "separate TT refresh and replacement strategy interventions",
           "exact legality/SEE parity negative controls",
           "paired equal-hardware nodes speed and chess Elo game-strength CI"],
       "rights":"Original GPLv3 upstream source referred by commit and SHA only; no modified source or binaries redistributed."}
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--root",required=True)
    p.add_argument("--out",required=True)
    a=p.parse_args()
    root=Path(a.root)
    rev=subprocess.check_output(["git","-C",str(root),"rev-parse","HEAD"],text=True).strip()
    if rev!=PINNED:raise ValueError("P3_ORIGINAL_STOCKFISH16_HEAD_NOT_PINNED")
    d=audit({x:(root/"src"/x).read_bytes() for x in ("tt.h","tt.cpp","search.cpp")})
    dest=Path(a.out);dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(json.dumps(d,sort_keys=True,indent=2)+"\n")
    print("C3X025_P3_ORIGINAL_STOCKFISH16_TT_PROBE_GENERATION_REFRESH_VERIFIED",
          {"exact_upstream_head":PINNED,"files_SHA256":d["unmodified_upstream_cpp_sha256"],
           "source_semantic_flags":list(d["static_semantic_source_gates_all_passed"])},flush=True)
    print("C3X025_P3_TT_STATIC_SOURCE_JSON_SHA256",hashlib.sha256(dest.read_bytes()).hexdigest(),flush=True)
if __name__=="__main__":main()
