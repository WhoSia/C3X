#!/usr/bin/env python3
"""C3X 0.18 trial/call identity augmentation for frozen 0.17 SF16 root observer.

Apply only AFTER tools/c3x_017_early_depth1_root_window_trace_patch.py.
Read-only instrumentation: never mutate Stockfish search values or move ordering.
"""
import argparse
import hashlib
import json
from pathlib import Path


def replace_exact(source, anchor, replacement, label):
    count = source.count(anchor)
    if count != 1:
        raise RuntimeError(f"C3X018_ANCHOR_{label}_COUNT_{count}")
    return source.replace(anchor, replacement, 1)


def patch(source):
    if "static thread_local int c3x018_root_call_id" in source:
        raise RuntimeError("C3X018_ALREADY_APPLIED")
    source = replace_exact(
        source,
        "static constexpr int c3x017_root_event_limit = 4096;",
        """static constexpr int c3x017_root_event_limit = 4096;
// Observer-local within-arm identifiers, not cross-world causal equivalence.
static thread_local int c3x018_last_depth = -1;
static thread_local int c3x018_trial_at_depth = 0;
static thread_local int c3x018_root_call_id = 0;""",
        "STATE")
    source = replace_exact(
        source,
        "  c3x017_root_event_count = 0;",
        """  c3x017_root_event_count = 0;
  c3x018_last_depth = -1;
  c3x018_trial_at_depth = 0;
  c3x018_root_call_id = 0;""",
        "RESET")
    # Before each invocation of search<Root>, not merely when a bounded
    # observation happens. Thus IDs remain monotonic even beyond event cap.
    anchor = "              if(c3x017_root_event_count<c3x017_root_event_limit && rootDepth>=1) {"
    replacement = """              if (c3x018_last_depth != int(rootDepth)) {
                  c3x018_last_depth = int(rootDepth);
                  c3x018_trial_at_depth = 0;
              }
              ++c3x018_trial_at_depth;
              ++c3x018_root_call_id;
""" + anchor
    source = replace_exact(source, anchor, replacement, "TRIAL_ENTRY")
    # Event suffixes appended at native source logging sites; avoids dependence
    # on log sequence index and preserves the old columns.
    for label, marker in (
        ("ENTER", 'kind=window_enter seq=" << c3x017_root_event_count'),
        ("EXIT", 'kind=window_exit seq=" << c3x017_root_event_count'),
        ("SORT", 'kind=after_sort seq=" << c3x017_root_event_count'),
        ("CANDIDATE", 'kind=candidate seq=" << c3x017_root_event_count')):
        source = replace_exact(
            source, marker,
            marker + ' << " trial=" << c3x018_trial_at_depth'
                   + ' << " root_call=" << c3x018_root_call_id',
            label)
    return source


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--source", required=True)
    p.add_argument("--out-manifest", required=True)
    args = p.parse_args()
    file = Path(args.source) / "src/search.cpp"
    old = file.read_bytes()
    updated = patch(old.decode("utf-8")).encode("utf-8")
    file.write_bytes(updated)
    manifest = {
        "schema": "c3x018-sf16-aspiration-trial-and-root-call-observer-v1",
        "scope": "within-arm observational event IDs",
        "source_before_sha256": hashlib.sha256(old).hexdigest(),
        "source_after_sha256": hashlib.sha256(updated).hexdigest(),
        "source_root": "SF16 68e1e9b3811e16cad014b590d7443b9063b3eb52",
        "new_fields": ["trial", "root_call"],
        "gates": ["requires_017_observer_anchors_exactly_once",
                  "original_P4_O_F_Z_cores_must_remain_exact",
                  "repeated_cold_runs_must_match",
                  "cross_arm_counter_equality_is_not_causal_identity",
                  "TT_writer_reader_not_yet_instrumented"]
    }
    dest = Path(args.out_manifest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print("C3X018_SOURCE_TRIAL_CALL_PATCH_APPLIED")


if __name__ == "__main__":
    main()
