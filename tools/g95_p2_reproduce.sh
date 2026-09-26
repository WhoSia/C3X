#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

sha256sum -c MANIFEST.sha256

rm -rf .reproduce
mkdir -p .reproduce

bin/c3x-field discover   --constitution schemas/constitution.json   --input examples/discovery-input.json   --out .reproduce/discovery-field.json
cmp .reproduce/discovery-field.json certificates/discovery-field.json

bin/c3x-field scope   --discovery .reproduce/discovery-field.json   --profiles examples/heldout-profiles.json   --out .reproduce/heldout-scope.json
cmp .reproduce/heldout-scope.json certificates/heldout-scope.json

bin/c3x-field verify   --scope .reproduce/heldout-scope.json   --targets examples/heldout-targets.json   --out .reproduce/heldout-verification.json
cmp .reproduce/heldout-verification.json certificates/heldout-verification.json

python3 - <<'PY'
import json, pathlib
root=pathlib.Path(".")
f=json.loads((root/".reproduce/discovery-field.json").read_text())
s=json.loads((root/".reproduce/heldout-scope.json").read_text())
v=json.loads((root/".reproduce/heldout-verification.json").read_text())
assert f["status"]=="PORTABLE_MINIMAL_BASIS_FRONTIER"
assert f["minimum_portable_cardinality"]==3
assert [b["basis_id"] for b in f["minimal_portable_bases"]]==[
    "P:parent_depth_bucket+event_occ_bucket+event_ordinal_bucket"
]
assert s["status"]=="HELDOUT_SCOPE_SEALED"
assert s["target_fields_consulted"] is False
assert s["coverage"]["gate_pass"] is True
assert v["verdict"]=="CONTEXT_FIELD_TRANSPORT_FALSIFIED"
assert v["covered_verified"]==132
assert v["abstained"]==60
assert len(v["contradictions"])==8
assert len(v["mixed_heldout_cells"])==1
print("C3X_TOOLKIT_REPRO_PASS",f["minimum_portable_cardinality"],s["coverage"]["seen"],v["covered_verified"],v["abstained"])
PY
