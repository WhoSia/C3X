#!/usr/bin/env python3
"""Source-exact, single-contact SF16 root child-return counterfactual.

Apply after P4 root order, C3X017 root trace and C3X018 trial-call ancestry.
The only mutation is value AFTER child search and undo, BEFORE RootMove
score/average/PV and alpha-beta root bestValue updates.
"""
import argparse
import hashlib
import json
from pathlib import Path

STATE = r"""
// C3X019 return-repair is opt-in; source-conditional event coordinates only.
// A root call ID is NOT invariant after branching search histories.
static thread_local int c3x019_return_repair_contacts = 0;
"""

EVENT = r"""
      // C3X019 one-site synthetic edge intervention, after child subtree search.
      // No changes to native TT, child recursion, chess legality or root order.
      const char* c3x019_repair_mode = std::getenv("C3X019_RETURN_REPAIR_MODE");
      if (rootNode && c3x019_repair_mode
          && c3x019_return_repair_contacts == 0
          && int(thisThread->rootDepth) ==
               int(std::strtol(std::getenv("C3X019_RETURN_DEPTH"), nullptr, 10))
          && c3x018_root_call_id ==
               int(std::strtol(std::getenv("C3X019_RETURN_ROOT_CALL"), nullptr, 10))
          && c3x018_trial_at_depth ==
               int(std::strtol(std::getenv("C3X019_RETURN_TRIAL"), nullptr, 10))
          && int(move) ==
               int(std::strtol(std::getenv("C3X019_RETURN_MOVE"), nullptr, 10))
          && moveCount ==
               int(std::strtol(std::getenv("C3X019_RETURN_INDEX"), nullptr, 10))
          && int(alpha) ==
               int(std::strtol(std::getenv("C3X019_RETURN_ALPHA"), nullptr, 10))
          && int(beta) ==
               int(std::strtol(std::getenv("C3X019_RETURN_BETA"), nullptr, 10)))
      {
          const int c3x019_before = int(value);
          const int c3x019_expected =
              int(std::strtol(std::getenv("C3X019_RETURN_EXPECTED"), nullptr, 10));
          const int c3x019_target =
              int(std::strtol(std::getenv("C3X019_RETURN_REPLACEMENT"), nullptr, 10));
          const bool c3x019_matched = (c3x019_before == c3x019_expected);
          const bool c3x019_edit = c3x019_matched
                               && c3x019_repair_mode[0] == 'R';
          if (c3x019_edit)
              value = Value(c3x019_target);
          ++c3x019_return_repair_contacts;
          sync_cout << "info string c3x019_return_repair kind="
                    << (c3x019_matched ?
                          (c3x019_edit ? "repaired" : "observed")
                          : "source_mismatch")
                    << " depth=" << int(thisThread->rootDepth)
                    << " root_call=" << c3x018_root_call_id
                    << " trial=" << c3x018_trial_at_depth
                    << " move=" << int(move)
                    << " index=" << moveCount
                    << " alpha=" << int(alpha)
                    << " beta=" << int(beta)
                    << " child_before=" << c3x019_before
                    << " child_after=" << int(value)
                    << " expected=" << c3x019_expected
                    << " replacement=" << c3x019_target
                    << sync_endl;
      }

"""

def one(s,old,new,label):
    count=s.count(old)
    if count != 1:
        raise RuntimeError(f"C3X019_RETURN_SOURCE_{label}_ANCHOR_{count}")
    return s.replace(old,new,1)

def patch(s):
    s=one(s,"namespace Stockfish {\n",
          "namespace Stockfish {\n"+STATE,"NAMESPACE")
    s=one(s,"  c3x017_root_event_count = 0;",
          "  c3x017_root_event_count = 0;\n  c3x019_return_repair_contacts = 0;",
          "RESET")
    anchor=("      if (rootNode)\n"
            "      {\n"
            "          RootMove& rm = *std::find(thisThread->rootMoves.begin(),\n"
            "                                    thisThread->rootMoves.end(), move);")
    s=one(s,anchor,EVENT+anchor,"AFTER_CHILD_BEFORE_ROOT_SCORE")
    return s

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source",required=True)
    p.add_argument("--out-manifest",required=True)
    a=p.parse_args()
    f=Path(a.source)/"src/search.cpp"
    before=f.read_bytes()
    after=patch(before.decode()).encode()
    f.write_bytes(after)
    report={"schema":"c3x019-root-return-synthetic-edge-restoration-source-overlay-v1",
            "upstream":"official-stockfish/Stockfish 68e1e9b3811e16cad014b590d7443b9063b3eb52",
            "source_before_sha256":hashlib.sha256(before).hexdigest(),
            "source_after_sha256":hashlib.sha256(after).hexdigest(),
            "mutation_site":"after child return and undo, before root RootMove score and alpha-beta bestValue",
            "only_mutation":"value = Value(frozen_F_child_return)",
            "selectors":["depth","root_call","trial","move","moveCount","alpha","beta","expected_value"],
            "source_events":["observed","repaired","source_mismatch"],
            "max_contacts_per_cold_process":1,
            "no_env_means_exact_original_engine":True,
            "limits":["One root-call ID from an observational prefix, not invariant node identity",
                      "Already-completed descendant search and TT writes cannot be rolled back",
                      "Source value repair does not prove the native original TT mechanism or natural mediation"]}
    dest=Path(a.out_manifest);dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(json.dumps(report,indent=2)+"\n")
    print("C3X019_ONE_SITE_POST_CHILD_RETURN_ROOT_SCORE_REPAIR_OVERLAY_READY")

if __name__=="__main__":
    main()
