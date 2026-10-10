#!/usr/bin/env bash
set -euo pipefail
root=/tmp/C3X020_MULTI_STATE
mkdir -p evidence
git clone -q --single-branch --branch sf_16 https://github.com/official-stockfish/Stockfish.git "$root"
test "$(git -C "$root" rev-parse HEAD)" = 68e1e9b3811e16cad014b590d7443b9063b3eb52
python tools/c3x_016_P4_independent_12root_source_order_patch.py --source "$root" --out-manifest evidence/P4.json
python tools/c3x_017_early_depth1_root_window_trace_patch.py --source "$root" --out-manifest evidence/ROOT_TRACE.json
python tools/c3x_018_trial_call_identity_patch.py --source "$root" --out-manifest evidence/TRIAL_ID.json
python tools/c3x_018_physical_epoch_lineage_patch.py --source "$root" --out-manifest evidence/EPOCH.json
python tools/c3x_018_tt_eval_consumption_overlay.py --source "$root" --out-manifest evidence/V.json
python tools/c3x_018_physical_value_witness_overlay.py --source "$root" --out-manifest evidence/WRITER_TICKET.json
python tools/c3x_018_root_TT_genealogy_overlay.py --source "$root" --out-manifest evidence/ROOT_TT_LINEAGE.json
python tools/c3x_018_TT_reader_writer_age_bound_root_feature_overlay.py --source "$root" --out-manifest evidence/AGE_BOUND.json
python tools/c3x_018_january2048_TT_reader_source_census.py --source "$root" --out-manifest evidence/CENSUS.json
python tools/c3x_018_adaptive_writer_age_root_call_V_gate.py --source "$root" --out-manifest evidence/AGE_GATE.json
python tools/c3x_018_january_cross_window_pair_source_gate.py --source "$root" --out-manifest evidence/WINDOW_GATE.json
python tools/c3x_018_jan_original_key_TT_probe_watch_overlay.py --source "$root" --out-manifest evidence/PROBE.json
python tools/c3x_018_jan_TT_probe_physical_writer_epoch_witness.py --source "$root" --out-manifest evidence/PROBE_WRITER.json
python tools/c3x_018_P0P1_TT_save_decision_writer_reinstate_overlay.py --source "$root" --out-manifest evidence/P0_P1_SOURCE_MUTATION.json
python tools/c3x_018_P1_pre_second_reader_temporal_scope_overlay.py --source "$root" --out-manifest evidence/P1_PRE_SECOND_TEMPORAL_GATE.json
python tools/c3x_019_tt_raw_bytes_shadow_writer_orthogonal_overlay.py --source "$root" --out-manifest evidence/C3X019_ORTHOGONAL_WRITER_STATE.json
python tools/c3x_019_actual_native_tt_eval_use_source_witness.py --source "$root" --out-manifest evidence/C3X019_NATIVE_EVAL_USE.json
python tools/c3x_019_native_TT_cutoff_actual_return_overlay.py --source "$root" --out-manifest evidence/C3X019_NATIVE_TT_CUTOFF_RETURN.json
python tools/c3x_019_root_return_one_site_rescue_overlay.py --source "$root" --out-manifest evidence/ONE_SITE_RETURN_MUTATION.json
python tools/c3x_020_multi_state_root_repair_overlay.py --source "$root" --out-manifest evidence/C3X020_MULTI_STATE_MUTATION.json
python tools/c3x_022_P2_R2_native_SEE_source_witness_overlay.py --source "$root" --out-manifest evidence/C3X022_R2_NATIVE_SEE_FOUR_SOURCE_SITES.json
python tools/c3x_022_P2_R2_D1_rootcall_only_SEE_observer.py --source "$root" --out-manifest evidence/C3X022_R2_D1_DESCENDANT_READONLY.json
python tools/c3x_023_P1_native_SEE_parent_path_key_overlay.py --source "$root" --out-manifest evidence/C3X023_P1_MAIN_QSEARCH_ANCESTRY_KEYPATH.json
python tools/c3x_023_P1_R2_T1_native_full_search_state_overlay.py --source "$root" --out-manifest evidence/C3X023_P1_R2_T1_SEARCH_CONTEXT_REAL_CALLER.json
python tools/c3x_023_P1_R2_T3_precise_native_SEE_boolean_source_actuator.py --source "$root" --out-manifest evidence/C3X023_P1_R2_T3_EXACT_BOOL_SITE_ACTUATOR.json
make -s -C "$root/src" -j2 build ARCH=x86-64

sha256sum "$root/src/stockfish" | awk '{print $1 "  LOCAL_UNDISTRIBUTED_GPLV3_ENGINE"}' > evidence/T3_BINARY_HASH.txt
