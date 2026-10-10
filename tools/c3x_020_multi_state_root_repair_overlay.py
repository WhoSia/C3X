#!/usr/bin/env python3
"""C3X020 two independent native source interventions, opt-in and fail-closed.

Apply AFTER the C3X019 one-site overlay to frozen Stockfish16 search.cpp.
The second-return gate is AFTER native child search/undo and BEFORE root score
updates. The persistent-state gate is AFTER a completed depth's root sorting
and BEFORE iterative-deepening's next depth. Neither edits legal moves or TT.
"""
import argparse
import hashlib
import json
from pathlib import Path

STATE = r"""
// C3X020 bounded second candidate return and depth-boundary rootMove graft.
static thread_local int c3x020_second_contacts = 0;
static thread_local int c3x020_boundary_contacts = 0;
"""

SECOND = r"""
      // C3X020 independently selected second root candidate return; opt-in.
      const char* c3x020_second_mode = std::getenv("C3X020_SECOND_MODE");
      if (rootNode && c3x020_second_mode && c3x020_second_contacts == 0
          && int(thisThread->rootDepth) == int(std::strtol(std::getenv("C3X020_SECOND_DEPTH"), nullptr, 10))
          && c3x018_root_call_id == int(std::strtol(std::getenv("C3X020_SECOND_ROOT_CALL"), nullptr, 10))
          && c3x018_trial_at_depth == int(std::strtol(std::getenv("C3X020_SECOND_TRIAL"), nullptr, 10))
          && int(move) == int(std::strtol(std::getenv("C3X020_SECOND_MOVE"), nullptr, 10))
          && moveCount == int(std::strtol(std::getenv("C3X020_SECOND_INDEX"), nullptr, 10))
          && int(alpha) == int(std::strtol(std::getenv("C3X020_SECOND_ALPHA"), nullptr, 10))
          && int(beta) == int(std::strtol(std::getenv("C3X020_SECOND_BETA"), nullptr, 10)))
      {
          const int before = int(value);
          const int expected = int(std::strtol(std::getenv("C3X020_SECOND_EXPECTED"), nullptr, 10));
          const int target = int(std::strtol(std::getenv("C3X020_SECOND_TARGET"), nullptr, 10));
          const bool matched = before == expected;
          const bool edit = matched && c3x020_second_mode[0] == 'R';
          if (edit)
              value = Value(target);
          ++c3x020_second_contacts;
          sync_cout << "info string c3x020_second kind="
                    << (matched ? (edit ? "repaired" : "observed") : "source_mismatch")
                    << " depth=" << int(thisThread->rootDepth)
                    << " root_call=" << c3x018_root_call_id
                    << " trial=" << c3x018_trial_at_depth
                    << " move=" << int(move)
                    << " index=" << moveCount
                    << " alpha=" << int(alpha)
                    << " beta=" << int(beta)
                    << " before=" << before
                    << " after=" << int(value)
                    << " expected=" << expected
                    << " target=" << target << sync_endl;
      }

"""

BOUNDARY = r"""
      // C3X020 boundary snapshot/graft. The completed-depth values will be
      // carried into the next iteration's root sorting and aspiration logic.
      const char* c3x020_boundary_mode = std::getenv("C3X020_BOUNDARY_MODE");
      if (c3x020_boundary_mode && c3x020_boundary_contacts == 0
          && int(rootDepth) == int(std::strtol(std::getenv("C3X020_BOUNDARY_DEPTH"), nullptr, 10)))
      {
          const int selected = int(std::strtol(std::getenv("C3X020_BOUNDARY_MOVE"), nullptr, 10));
          auto it = std::find_if(rootMoves.begin(), rootMoves.end(),
                          [selected](const RootMove& r) { return int(r.pv[0]) == selected; });
          if (it != rootMoves.end())
          {
              int before_score = int(it->score);
              int before_average = int(it->averageScore);
              const int expected_score = int(std::strtol(std::getenv("C3X020_BOUNDARY_EXPECT_SCORE"), nullptr, 10));
              const int expected_average = int(std::strtol(std::getenv("C3X020_BOUNDARY_EXPECT_AVERAGE"), nullptr, 10));
              const int target_score = int(std::strtol(std::getenv("C3X020_BOUNDARY_TARGET_SCORE"), nullptr, 10));
              const int target_average = int(std::strtol(std::getenv("C3X020_BOUNDARY_TARGET_AVERAGE"), nullptr, 10));
              const char kind = c3x020_boundary_mode[0]; // O observe, A average, S score, B both
              const bool matched = kind == 'O' || (before_score == expected_score && before_average == expected_average);
              const bool editing = matched && (kind == 'A' || kind == 'S' || kind == 'B');
              if (editing && (kind == 'S' || kind == 'B'))
                  it->score = Value(target_score);
              if (editing && (kind == 'A' || kind == 'B'))
                  it->averageScore = Value(target_average);
              ++c3x020_boundary_contacts;
              sync_cout << "info string c3x020_boundary kind="
                        << (matched ? (editing ? "repaired" : "observed") : "source_mismatch")
                        << " depth=" << int(rootDepth)
                        << " move=" << selected
                        << " before_score=" << before_score
                        << " after_score=" << int(it->score)
                        << " before_average=" << before_average
                        << " after_average=" << int(it->averageScore)
                        << " expected_score=" << expected_score
                        << " expected_average=" << expected_average
                        << " target_score=" << target_score
                        << " target_average=" << target_average
                        << " mode=" << kind << sync_endl;
          }
      }

"""

def replace_once(source, anchor, replacement, label):
    count = source.count(anchor)
    if count != 1:
        raise RuntimeError(f"C3X020_SOURCE_{label}_ANCHOR_COUNT_{count}")
    return source.replace(anchor, replacement, 1)

def patch(source):
    if "static thread_local int c3x020_second_contacts = 0;" in source:
        raise RuntimeError("C3X020_SOURCE_ALREADY_PATCHED")
    source = replace_once(source, "namespace Stockfish {\n",
                          "namespace Stockfish {\n" + STATE, "NAMESPACE")
    source = replace_once(source, "  c3x019_return_repair_contacts = 0;",
                          "  c3x019_return_repair_contacts = 0;\n"
                          "  c3x020_second_contacts = 0;\n"
                          "  c3x020_boundary_contacts = 0;", "RESET")
    source = replace_once(source,
        "      // C3X019 one-site synthetic edge intervention, after child subtree search.",
        SECOND + "      // C3X019 one-site synthetic edge intervention, after child subtree search.",
        "SECOND_AFTER_CHILD")
    anchor = "      if (!Threads.stop)\n          completedDepth = rootDepth;\n"
    source = replace_once(source, anchor, anchor + BOUNDARY, "DEPTH_BOUNDARY")
    return source

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--source", required=True)
    p.add_argument("--out-manifest", required=True)
    args = p.parse_args()
    f = Path(args.source) / "src/search.cpp"
    old = f.read_bytes()
    new = patch(old.decode("utf-8")).encode("utf-8")
    f.write_bytes(new)
    receipt = {
        "schema": "c3x020-second-return-and-depth-boundary-rootmove-native-overlay-v1",
        "parent": "C3X019 post-child single-return overlay on pinned Stockfish16",
        "source_before_sha256": hashlib.sha256(old).hexdigest(),
        "source_after_sha256": hashlib.sha256(new).hexdigest(),
        "second_return_stage": "post-native-child/undo; before original C3X019 gate and root score",
        "boundary_stage": "after completed-depth sort, before subsequent iterative depth",
        "allowed_second_modes": ["OBS", "REPAIR"],
        "allowed_boundary_modes": ["O", "A", "S", "B"],
        "max_second_contacts": 1,
        "max_boundary_contacts": 1,
        "no_env_exact_native": True,
        "claim": "Implementation only; no native 0.20-B effect measured yet",
    }
    dest = Path(args.out_manifest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print("C3X020_NATIVE_MULTI_STATE_OVERLAY_READY")

if __name__ == "__main__":
    main()
