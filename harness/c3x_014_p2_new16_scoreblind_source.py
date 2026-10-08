#!/usr/bin/env python3
"""P2: Select sixteen NEW outcome-blind game groups without opening P1 sealed data.

Selection wholly independent of all engine output and TT intervention outcomes.
P1 public JSON contains development group IDs and OPAQUE heldout group hashes.
"""
from __future__ import annotations
import argparse,hashlib,json,sys
from pathlib import Path
import c3x_014_p1_tcec_s29_source_intake as p1

SALT="C3X_014_P2_TCEC_S29_NEW16_SCOREBLIND_V1"
COUNT=16
P1_PUBLIC_SHA="bbaef73beda60d9e03c9f83324651db3b130606be4c84cb9f8a170a958a96274"

def main():
    a=argparse.ArgumentParser()
    a.add_argument("--pgn",required=True)
    a.add_argument("--p1-public",required=True)
    a.add_argument("--out",required=True)
    args=a.parse_args()
    pg=Path(args.pgn).read_bytes()
    assert p1.git_blob_sha1(pg)==p1.EXPECTED_BLOB,"OFFICIAL_SOURCE_BYTES_MISMATCH"
    prior=Path(args.p1_public).read_bytes()
    assert hashlib.sha256(prior).hexdigest()==P1_PUBLIC_SHA,"P1_PUBLIC_COHORT_SHA_MISMATCH"
    p=json.loads(prior)
    assert len(p["development_games"])==4 and len(p["procedurally_sealed_holdout_group_hashes"])==4
    old_dev={g["opening_group_hash"] for g in p["development_games"]}
    old_hold=set(p["procedurally_sealed_holdout_group_hashes"])
    assert not old_dev.intersection(old_hold)
    forbidden=old_dev|old_hold
    cohort,audit=p1.eligible(pg)
    unseen=[k for k in cohort if k not in forbidden]
    unseen.sort(key=lambda k:p1.digest(SALT+":"+k))
    selected=[cohort[k] for k in unseen[:COUNT]]
    if len(selected)!=COUNT:raise SystemExit("P2_INSUFFICIENT_UNUSED_GROUPS")
    assert len({x["opening_group_hash"] for x in selected})==COUNT
    assert not ({x["opening_group_hash"] for x in selected}&forbidden)
    o={"schema":"c3x-014-p2-official-s29-score-blind-independent-16-source-groups-v1",
       "status":"COHORT_FREEZE_BEFORE_ENGINE_SCORE__NO_HOLDOUT_OPENED",
       "official_source":{"git_commit":p1.SOURCE_COMMIT,"git_blob_sha1":p1.EXPECTED_BLOB,
                          "source_sha256":hashlib.sha256(pg).hexdigest()},
       "parent_public_cohort_sha256":P1_PUBLIC_SHA,
       "source_game_count":audit["total_games_read"],
       "eligible_opening_group_count":len(cohort),
       "excluded_p1_dev_and_opaque_holdout_group_count":len(forbidden),
       "unused_groups_available":len(unseen),
       "cohort_selection_salt":SALT,
       "selected_16_game_groups":selected,
       "hidden_p1_holdout_game_details_read":False,
       "engine_scores_read":False,
       "score_adjusted_selection":False,
       "source_group_samples":COUNT,
       "scientific_ceiling":"SOURCE_GAMES_NOT_INDEPENDENT_ECOLOGIES__NO_CHESS_CAUSAL_MEDIATION"}
    f=Path(args.out);f.parent.mkdir(parents=True,exist_ok=True)
    f.write_text(json.dumps(o,indent=2)+"\n")
    print("P2_SOURCE_COHORT_FROZEN",json.dumps({
        "all":audit["total_games_read"],"distinct_prefix_groups":len(cohort),
        "p1_reserved":len(forbidden),"unused":len(unseen),"new":COUNT}),flush=True)
if __name__=="__main__":main()
