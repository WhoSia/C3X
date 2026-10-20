#!/usr/bin/env python3
"""Fail-closed evidence gate for pinned Stockfish16 SEE differential; no silent mismatches."""
import json
from pathlib import Path
random=json.loads(Path("C3X_027_SEE_DIFFERENTIAL.json").read_text())
boundary=json.loads(Path("C3X_027_SEE_BOUNDARY_DIFFERENTIAL.json").read_text())
manifest=json.loads(Path("C3X027_NATIVE_SEE_BRANCH_MANIFEST.json").read_text())
assert len(manifest["names"])==21, "INSTRUMENTATION_INCOMPLETE"
assert random["samples"]==960 and random["mismatches"]==0,"RANDOM_SEE_DIFFERENTIAL_FAIL"
assert boundary["comparisons"]>=495 and boundary["mismatch_count"]==0,"BOUNDARY_SEE_DIFFERENTIAL_FAIL"
assert boundary["castle_compared"]==18 and not boundary["exclusions"],"CASTLING_SCOPE_FAIL"
assert boundary["targeted_pin_tested"]>=9,"PIN_REGRESSION_NOT_EXERCISED"
assert int(boundary["native_branch_counts"]["6"])>=1,"NO_ACTUAL_PIN_FILTER_BRANCH"
out={"schema":"c3x027-see-adversarial-source-differential-gate-v1","random_compared":random["samples"],"boundary_compared":boundary["comparisons"],"compared_total":random["samples"]+boundary["comparisons"],"mismatches":0,"castles_compared":boundary["castle_compared"],"pin_filter_native_events":boundary["native_branch_counts"]["6"],"branch_mask":{manifest["names"][i]:int(random["native_branch_counts"][str(i)])+int(boundary["native_branch_counts"][str(i)]) for i in range(21)},"status":"SOURCE_DIFFERENTIAL_OBSERVED_PASS_NOT_FORMAL_EQUIVALENCE"}
Path("C3X_027_SEE_COVERAGE_GATE.json").write_text(json.dumps(out,indent=2)+"\n")
print("C3X027_COVERAGE_GATE_PASS",out["compared_total"],"pin_filters",out["pin_filter_native_events"],"actual_xray_reveals",[out["branch_mask"].get(k) for k in ("bishop_xray_new_attacker","rook_xray_new_attacker","queen_xray_new_attacker")])
