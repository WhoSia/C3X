"""C3X 0.31/P3-A1: exact finite counterexample to root-ledger-only state sufficiency.

Use original P2-D1 (78 native runs) P2-028 event19 after attempt16, depth15/16.
This is retrospective and restricted: the candidate state *excludes* cumulative
nodes, TT/history/stack. It does NOT falsify a state including those fields.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import zipfile
from c3x_031_p3_a0_interiteration_root import audit as original_a0, LOG_SHA, RESULT_ZIP_SHA

GAME = "P2-028-0"
ARMS = ("untouched", "both_off")
ATTEMPT = "16"
PUBLIC_DEPTH = "13"


def check(ok, why):
    if not ok:
        raise ValueError(why)


def sha(blob):
    return hashlib.sha256(blob).hexdigest()


def lines_for(raw):
    lines = raw.decode("utf8").splitlines()
    candidate = [r for r in lines if r.startswith("C3X_R23_CANDIDATE attempt=16 ")]
    start = [r for r in lines if r.startswith("C3X_R23_START attempt=16 ")]
    end = [r for r in lines if r.startswith("C3X_R23_END attempt=16 ")]
    event = [r for r in lines if r.startswith("C3X_R33_OPEN event=19 ")]
    check(len(candidate) == 45 and len(start) == len(end) == len(event) == 1,
          "root boundary incomplete")
    # Markov candidate projection includes full root search start (pre-contact),
    # every candidate identity/score/alpha/beta/update and end value/move/producer,
    # *not* end-of-search cumulative node work.
    e = [w for w in end[0].split() if not w.startswith("nodes=")]
    e_nodes = int(next(w.split("=")[1] for w in end[0].split()
                       if w.startswith("nodes=")))
    basis = start + candidate + [" ".join(e)]
    return {"projection_lines": basis, "node_count_after": e_nodes,
            "source_event": event[0], "candidate_count": len(candidate)}


def public_projection(raw):
    rows = [row for row in raw.decode("utf8").splitlines()
            if row.startswith("info depth 13 ")]
    check(len(rows) == 1, "terminal iteration13 public output incomplete")
    toks = rows[0].split()
    # Deliberately excludes nps/time/nodes. Reported PV, score *type* and cp,
    # seldepth, hashfull, multipv remain. This is not the entire UCI stream.
    out = []
    for i, v in enumerate(toks):
        if v in ("nodes", "nps", "time"):
            continue
        if i > 0 and toks[i - 1] in ("nodes", "nps", "time"):
            continue
        out.append(v)
    check("pv" in out and "score" in out, "no public score/PV")
    return " ".join(out)


def audit(log_zip, science_zip):
    a0 = original_a0(log_zip, science_zip)
    check(a0["original_D1_native_searches"] == 78
          and a0["new_native_searches"] == 0
          and a0["R26_prior_exposed_macro_family"], "source class changed")
    cells = {}
    with zipfile.ZipFile(log_zip) as z:
        for depth in (15,16):
            by_arm = {}
            for arm in ARMS:
                prefix = f"{GAME}/depth-{depth}/{arm}-0/"
                root = lines_for(z.read(prefix+"stderr.txt"))
                public = public_projection(z.read(prefix+"stdout.txt"))
                root["root_projection_sha256"] = sha(("\n".join(
                    root["projection_lines"])+"\n").encode("utf8"))
                root["public_projection_sha256"] = sha(public.encode("utf8"))
                root["public_projection"] = public
                by_arm[arm] = root
            c,t = (by_arm[name] for name in ARMS)
            check(c["projection_lines"] == t["projection_lines"],
                  "two source worlds have different root candidate projection")
            check(c["public_projection"] == t["public_projection"],
                  "two source worlds have different bounded public depth13 score/PV")
            check(c["root_projection_sha256"] == t["root_projection_sha256"],
                  "projection digest mismatch")
            check((c["node_count_after"], t["node_count_after"]) == (7699,7717),
                  "excluded cumulative nodes fail to distinguish original states")
            check(c["source_event"] == t["source_event"],
                  "physical pre-contact event signature differs")
            endpoint = a0["root_trajectories"][str(depth)]
            check(endpoint["final_fixed_depth_root_choice"] == ["d4e5","f4e5"],
                  "future original root contrast did not differ")
            check(endpoint["first_root_same_move_value_change"]["attempt"] == 17
                  and endpoint["first_root_leader_update_change"]["attempt"] == 18,
                  "future root divergence did not survive the identical projection")
            cells[str(depth)] = {
                "root_ledger_full_candidate_count": c["candidate_count"],
                "same_root_candidate_projection": True,
                "root_projection_sha256": c["root_projection_sha256"],
                "same_depth13_public_score_pv_projection": True,
                "public_projection_sha256": c["public_projection_sha256"],
                "original_source_event_prefix_same": True,
                "nodes_at_end16": [c["node_count_after"],t["node_count_after"]],
                "future_root_bestmoves": endpoint["final_fixed_depth_root_choice"],
                "first_future_candidate_value_drift_attempt": 17,
                "first_future_leader_update_drift_attempt": 18,
            }
    check(cells["15"]["root_projection_sha256"] ==
          cells["16"]["root_projection_sha256"],
          "same exact iteration13 checkpoint projection changed across stop depths")
    return {
        "id":"C3X_031_P3_A1_ROOT_ONLY_MARKOV_SUFFICIENCY_FINITE_COUNTEREXAMPLE",
        "classification":"RETROSPECTIVE_SINGLE_EXPOSED_GAME_TWO_CORRELATED_DEPTHS",
        "formal_statement":
            "Two naturally reached states with identical 45-candidate root "
            "iteration13 projection and score/PV projection have different "
            "subsequent root recommendations at fixed depth15/16.",
        "projection_includes":
            ["root START before intervention", "all 45 root candidate move/value/"
             "alpha/beta/depth/count/update lines", "root END move/value/producer",
             "public depth13 completed score/bound/PV/hashfull"],
        "projection_excludes":
            ["cumulative node/time/nps", "TT bytes", "full-key writer provenance",
             "main/continuation history", "search stack", "allocation state",
             "restoration/treatment provenance"],
        "scope_of_falsification":"ROOT_CANDIDATE_LEDGER_ONLY_NOT_SUFFICIENT",
        "full_engine_state_sufficiency_not_falsified":True,
        "source_TT_history_node_mediator_not_identified":True,
        "original_R26_macro_family_exposure":True,
        "native_searches_new_this_unit":0,
        "original_P2_D1_native_searches":78,
        "original_source_logs_SHA256":LOG_SHA,
        "original_science_ZIP_SHA256":RESULT_ZIP_SHA,
        "depth_cells":cells
    }


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("native_logs_zip",type=Path)
    p.add_argument("science_zip",type=Path)
    p.add_argument("output",type=Path)
    args = p.parse_args()
    out = audit(args.native_logs_zip,args.science_zip)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(out,sort_keys=True,indent=2)+"\n")
    print("P3_A1_FALSIFIER",out["scope_of_falsification"],
          "identical_root_sha",out["depth_cells"]["16"]["root_projection_sha256"],
          "derived_sha",sha(args.output.read_bytes()))


if __name__=="__main__":
    main()
