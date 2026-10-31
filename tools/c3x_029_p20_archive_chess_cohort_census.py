"""P20 actual archive cohort census: source identity and missing history.

Requires repository checkout; only archive read, no Stockfish simulation.
"""
import json
from pathlib import Path

def census(manifest):
    cases=manifest["cases"]
    if len(cases)!=12 or len({x["id"] for x in cases})!=12:
        return {"status":"FAIL_COHORT_CARDINALITY"}
    known={"SKEWER_RAY","INTERFERENCE_RAY","DEFENDER_REMOVAL_RAY","NO_MOTIF_RAY_OPPORTUNITY"}
    distribution={k:sum(x["motif"]==k for x in cases) for k in sorted(known)}
    if any(v!=3 for v in distribution.values()):
        return {"status":"FAIL_MOTIF_STRATA","strata":distribution}
    if any(not isinstance(x.get("fen"),str) or len(x["fen"].split())!=4 for x in cases):
        return {"status":"FAIL_EXPECTED_FOUR_FIELD_FEN"}
    if any(not isinstance(x.get("source_short_hash"),str) or not x["source_short_hash"] for x in cases):
        return {"status":"HOLD_SOURCE_IDENTITY"}
    return {"status":"ARCHIVE_CENSUS_PASS_BENCHMARK_ADMISSION_HOLD",
            "cases":len(cases),"strata":distribution,
            "origin":"Lichess 2026-06 source-selected; game-disjoint per archived declaration",
            "limitations":["standalone FEN only; complete history unavailable in this artifact",
                           "source geometry labels are not independent semantic truth",
                           "no candidate-pair best/alternative and no nearby-negative continuations",
                           "archived cases are exposed development rather than new heldout"]}

def main():
    root=Path(__file__).resolve().parents[1]
    path=root/"c3x/cohorts/c3x-016-P4-Lichess-12-standalone-FEN-source-geometry-3x4-preoutcome.json"
    print(json.dumps(census(json.loads(path.read_text())),indent=2))

if __name__=="__main__":main()
