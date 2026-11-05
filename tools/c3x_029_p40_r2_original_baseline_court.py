#!/usr/bin/env python3
"""P40/R2 archived P39 exact mobility vs P37 deeper Stockfish reference.

Strictly retrospective, source-exposed eight events; zero novel engine calls.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

W_SHA = "84f037f62b86a7ee34239921f609a9015a6ea8d4cdf351f41563ef78dc6dabcf"
REF_SHA = "d92c33d05fa506b1a84c222b57729f76a53a95970dd61ba38f67ea1ce3f700fa"


def read_original(path: Path, expected: str) -> dict:
    data = path.read_bytes()
    actual = hashlib.sha256(data).hexdigest()
    if actual != expected:
        raise ValueError("HOLD_ARCHIVED_ORIGINAL_SHA_" + actual)
    return json.loads(data)


def compare_originals(mobility: dict, reference: dict) -> dict:
    if len(mobility["cases"]) != 8 or len(reference["cases"]) != 8:
        raise ValueError("HOLD_EIGHT_CASE_COUNT")
    if mobility["candidate_worlds"] != 16 or reference["candidate_response_trials"] != 16:
        raise ValueError("HOLD_SIXTEEN_ROOT_COUNT")
    if reference["target"] != "one 96k forced-root SF16 PV opponent reply, not chess ground truth":
        raise ValueError("HOLD_REFERENCE_IDENTITY")
    rows = []
    for i, (m, r) in enumerate(zip(mobility["cases"], reference["cases"])):
        if m["case_id"] != r["case_id"] or m["event_family"] != r["event_family"]:
            raise ValueError("HOLD_CASE_ALIGNMENT_" + str(i))
        a, b = m["worlds"]
        x, y = r["scored_candidate_predictions"]
        if a["root_uci"] != x["root_uci"] or b["root_uci"] != y["root_uci"]:
            raise ValueError("HOLD_MOVE_ALIGNMENT_" + str(i))
        if x["reference_96k"]["reference"]["root_uci"] != x["root_uci"]:
            raise ValueError("HOLD_REFERENCE_ROOT1")
        if y["reference_96k"]["reference"]["root_uci"] != y["root_uci"]:
            raise ValueError("HOLD_REFERENCE_ROOT2")
        if any(z["reference_96k"]["reference"].get("root_side_mate") is not None
               for z in (x, y)):
            raise ValueError("HOLD_MATE_SCORE_NOT_COMPARABLE_" + str(i))
        if any(z["reference_96k"]["reference"].get("lowerbound") or
               z["reference_96k"]["reference"].get("upperbound") for z in (x, y)):
            raise ValueError("HOLD_UNCALIBRATED_SCORE_BOUND_" + str(i))
        score1 = x["reference_96k"]["reference"]["root_side_cp"]
        score2 = y["reference_96k"]["reference"]["root_side_cp"]
        if not all(isinstance(v, int) for v in (score1, score2)):
            raise ValueError("HOLD_MISSING_CP")
        if score1 == score2:
            chosen = None
        else:
            chosen = 0 if score1 > score2 else 1
        w1, w2 = a["w"], b["w"]
        w_choice = 0 if w1 < w2 else 1 if w2 < w1 else None
        first_correct = chosen == 0 if chosen is not None else None
        w_correct = w_choice == chosen if (w_choice is not None and chosen is not None) else None
        rows.append({"case_id":m["case_id"],"event":m["event_family"],
                     "roots":[a["root_uci"],b["root_uci"]],
                     "w":[w1,w2],"deeper_96k_cp":[score1,score2],
                     "96k_preferred_index":chosen,
                     "24k_first_root_correct":first_correct,
                     "mobility_preferred_index":w_choice,
                     "mobility_correct_when_decided":w_correct})
    n_decided = sum(v["mobility_correct_when_decided"] is not None for v in rows)
    n_correct = sum(v["mobility_correct_when_decided"] is True for v in rows)
    first_comparable = sum(v["24k_first_root_correct"] is not None for v in rows)
    first_hits = sum(v["24k_first_root_correct"] is True for v in rows)
    paired_first_hits = sum(v["24k_first_root_correct"] is True
                            for v in rows if v["mobility_correct_when_decided"] is not None)
    return {
        "status":"POSTHOC_ARCHIVAL_PROXY_AUDIT_NOT_INDEPENDENT_CHESS_TRUTH",
        "original_games":len(rows),
        "mobility_chose":n_decided,"mobility_abstained":len(rows)-n_decided,
        "mobility_hits_when_chosen":n_correct,
        "24k_first_root_hits_all":first_hits,
        "24k_first_root_comparable_all":first_comparable,
        "24k_first_root_hits_on_mobility_decisions":paired_first_hits,
        "reference":"same family Stockfish16 separately searched 96k forced-root score; not calibrated perfect chess value",
        "claims_forbidden":["prospective result","explanation causation",
                            "value proxy superiority","independent event validation"],
        "cases":rows
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--mobility",required=True,type=Path)
    p.add_argument("--reference",required=True,type=Path)
    p.add_argument("--out",required=True,type=Path)
    a = p.parse_args()
    out = compare_originals(read_original(a.mobility,W_SHA),
                            read_original(a.reference,REF_SHA))
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n")
    print("P40_R2_EXPLORATORY",out["mobility_hits_when_chosen"],
          "of",out["mobility_chose"],"first_root",
          out["24k_first_root_hits_all"],"of",out["original_games"])


if __name__=="__main__":
    main()
