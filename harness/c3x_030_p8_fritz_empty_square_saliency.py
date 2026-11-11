"""C3X 0.30/P8: Fritz & Fuer nkranz (2021) section VI-A scoring adapter.
Does NOT place pawns, validate chess legality or query engines. Requires
independently legal source/perturbed positions and aligned real Q supports.
Only complete two-color results are ranked; absent evidence is UNKNOWN.
"""
import argparse
import json
import re
from pathlib import Path
from c3x_030_r1_sarfa_logdomain import sarfa_logdomain

SCHEMA = "c3x030-p8-fritz-empty-square-evidence-adapter-v1"
PAWN_COLORS = ("white", "black")

def summarize(record):
    if not isinstance(record, dict) or record.get("schema") != "c3x030-p8-fritz-raw-probe-v1":
        raise ValueError("P8_HOLD_SCHEMA")
    base, action, t, positions = (record.get(k) for k in
                                  ("original_q", "selected_action", "temperature", "square_probes"))
    if (not isinstance(positions, list) or not positions or
            not isinstance(base, dict) or action not in base):
        raise ValueError("P8_HOLD_SOURCE_INPUT")
    seen, out = set(), []
    for p in positions:
        sq = p.get("square")
        if not isinstance(sq, str) or not re.fullmatch(r"[a-h][2-7]", sq) or sq in seen:
            raise ValueError("P8_HOLD_SQUARE_IDENTITY")
        seen.add(sq)
        if p.get("was_empty_at_source") is not True:
            raise ValueError("P8_HOLD_SQUARE_NOT_PROVEN_EMPTY")
        probes = p.get("pawn_probes")
        if not isinstance(probes, dict) or set(probes) != set(PAWN_COLORS):
            raise ValueError("P8_HOLD_BOTH_PAWN_COLORS_REQUIRED")
        sub = {}
        for color in PAWN_COLORS:
            entry = probes[color]
            if entry.get("status") not in ("legal_measured", "illegal_check", "not_measured"):
                raise ValueError("P8_HOLD_PROBE_STATUS")
            status = entry["status"]
            if status == "legal_measured":
                if entry.get("position_legality_verified_externally") is not True:
                    raise ValueError("P8_HOLD_LEGALITY_PROVENANCE")
                if entry.get("same_action_legal_in_perturbation") is not True:
                    raise ValueError("P8_HOLD_SELECTED_ACTION_NOT_LEGAL")
                if entry.get("same_engine_and_search_budget") is not True:
                    raise ValueError("P8_HOLD_ENGINE_OR_BUDGET_MISMATCH")
                outcome = sarfa_logdomain(base, entry.get("perturbed_q"), action, t)
                sub[color] = {"status": "legal_measured",
                              "score": outcome["sarfa_harmonic_saliency"],
                              "specificity_delta": outcome["specificity_delta_raw_signed"]}
            else:
                if "perturbed_q" in entry:
                    raise ValueError("P8_HOLD_UNMEASURED_SCORES_PRESENT")
                sub[color] = {"status": status, "score": None}
        complete = all(sub[c]["status"] == "legal_measured" for c in PAWN_COLORS)
        out.append({"square": sq, "color_probe_evidence": sub,
                    "complete_two_color_evidence": complete,
                    "max_two_color_saliency_or_null":
                        max(sub[c]["score"] for c in PAWN_COLORS) if complete else None})
    complete_rows = sorted((p for p in out if p["complete_two_color_evidence"]),
                           key=lambda x: (-x["max_two_color_saliency_or_null"], x["square"]))
    return {"schema": SCHEMA,
            "literature_primary_original": "https://drive.google.com/file/d/13orvM8vIILK80Uq9GlPC9QjHC0FD4BIe/view",
            "source_record_type": "REQUIRES_REAL_PAIRED_Q_PROBES",
            "ranked_complete_top3": [{"square": p["square"],
                                      "score": p["max_two_color_saliency_or_null"]}
                                     for p in complete_rows[:3]],
            "all_candidates": out,
            "complete_two_color_count": len(complete_rows),
            "incomplete_unknown_count": len(out)-len(complete_rows),
            "number_of_new_native_searches_in_this_adapter": 0,
            "hardcoded_move_square_floor_used_as_numeric_evidence": False,
            "unmeasured_legal_squares_are_not_zero": True,
            "this_does_not_prove_original_engine_causality": True,
            "source_insertion_legality_and_q_values_not_verified_here": True}

def main():
    a = argparse.ArgumentParser()
    a.add_argument("--input", required=True)
    a.add_argument("--out", required=True)
    v = a.parse_args()
    out = summarize(json.loads(Path(v.input).read_text(encoding="utf-8")))
    Path(v.out).write_text(json.dumps(out, ensure_ascii=False, indent=2, sort_keys=True,
                                         allow_nan=False)+"\n", encoding="utf-8")
    print("C3X_P8_ADAPTER_OK", out["complete_two_color_count"], out["incomplete_unknown_count"])

if __name__ == "__main__":
    main()
