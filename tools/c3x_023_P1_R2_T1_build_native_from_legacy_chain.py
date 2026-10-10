#!/usr/bin/env python3
"""Build pinned Stockfish16 plus C3X source-faithful overlays, then T1 read-only state.

All patches use original public git source. Do not change legality/SEE Boolean.
Do not release modified GPLv3 binary from this workflow without full source.
"""
import argparse,hashlib,json,subprocess
from pathlib import Path
UPSTREAM="68e1e9b3811e16cad014b590d7443b9063b3eb52"
PATCHES="""c3x_016_P4_independent_12root_source_order_patch
c3x_017_early_depth1_root_window_trace_patch
c3x_018_trial_call_identity_patch
c3x_018_physical_epoch_lineage_patch
c3x_018_tt_eval_consumption_overlay
c3x_018_physical_value_witness_overlay
c3x_018_root_TT_genealogy_overlay
c3x_018_TT_reader_writer_age_bound_root_feature_overlay
c3x_018_january2048_TT_reader_source_census
c3x_018_adaptive_writer_age_root_call_V_gate
c3x_018_january_cross_window_pair_source_gate
c3x_018_jan_original_key_TT_probe_watch_overlay
c3x_018_jan_TT_probe_physical_writer_epoch_witness
c3x_018_P0P1_TT_save_decision_writer_reinstate_overlay
c3x_018_P1_pre_second_reader_temporal_scope_overlay
c3x_019_tt_raw_bytes_shadow_writer_orthogonal_overlay
c3x_019_actual_native_tt_eval_use_source_witness
c3x_019_native_TT_cutoff_actual_return_overlay
c3x_019_root_return_one_site_rescue_overlay
c3x_020_multi_state_root_repair_overlay
c3x_022_P2_R2_native_SEE_source_witness_overlay
c3x_022_P2_R2_D1_rootcall_only_SEE_observer
c3x_023_P1_native_SEE_parent_path_key_overlay
c3x_023_P1_R2_T1_source_search_state_overlay""".split()
def call(cmd):
    subprocess.run(cmd,check=True)
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source",required=True);p.add_argument("--evidence",required=True)
    a=p.parse_args();src=Path(a.source);ev=Path(a.evidence)
    if src.exists():raise ValueError("T1_NATIVE_DIR_MUST_BE_NEW")
    ev.mkdir(parents=True,exist_ok=True)
    call(["git","clone","--quiet","--single-branch","--branch","sf_16",
          "https://github.com/official-stockfish/Stockfish.git",str(src)])
    git=subprocess.check_output(["git","-C",str(src),"rev-parse","HEAD"],text=True).strip()
    if git!=UPSTREAM:raise ValueError("T1_UPSTREAM_SOURCE_DRIFT")
    for n in PATCHES:
        call(["python",str(Path("tools")/(n+".py")),"--source",str(src),
              "--out-manifest",str(ev/(n+".json"))])
    diff=subprocess.check_output(["git","-C",str(src),"diff","--","src/"])
    diffsha=hashlib.sha256(diff).hexdigest()
    call(["make","-s","-C",str(src/"src"),"-j2","build","ARCH=x86-64"])
    engine=src/"src"/"stockfish"
    binarysha=hashlib.sha256(engine.read_bytes()).hexdigest()
    (ev/"T1_PINNED_SOURCE_HASHES_ONLY.json").write_text(json.dumps(
       {"original_git":git,"ordered_patches":PATCHES,
        "modified_source_diff_sha256":diffsha,
        "binary_sha256":binarysha,"modified_GPLv3_binary_not_publicly_uploaded":True,
        "SEE_operator_unchanged":True},indent=2)+"\n")
    print("C3X023_T1_NATIVE_SOURCE_VERIFIED",git,diffsha,binarysha)
if __name__=="__main__":main()
