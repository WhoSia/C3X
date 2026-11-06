#!/usr/bin/env python3
"""R10 derives immutable original C3X027->R8->R9 source with two site probes."""
from pathlib import Path
import hashlib,subprocess,tempfile
from c3x_029_p42_r9_derived_original_draw_build import OLD,derive_r9,MAKE

EXTRA='python tools/c3x_029_p42_r10_source_site_specific_draw_parity_overlay.py --source "$root" --out-manifest evidence/C3X042_R10_DRAW_SITES.json'
def derive_r10(original):
    body=derive_r9(original)
    if body.count(MAKE)!=1 or body.index("c3x_029_p42_r9_original_value_draw_node_parity_intervention.py")>=body.index(MAKE):
        raise ValueError("R10_HOLD_R9_ORIGINAL_BUILD_ORDER")
    return body.replace(MAKE,EXTRA+"\n"+MAKE,1)

def main():
    original=OLD.read_text()
    body=derive_r10(original)
    Path("evidence").mkdir(exist_ok=True)
    Path("evidence/C3X042_R10_DERIVED_BUILD_SHA.txt").write_text(
        "original_027_sha256="+hashlib.sha256(original.encode()).hexdigest()+"\n"+
        "derived_R10_sha256="+hashlib.sha256(body.encode()).hexdigest()+"\n")
    with tempfile.TemporaryDirectory(prefix="c3x042-r10-") as tmp:
        path=Path(tmp)/"derived.sh"
        path.write_text(body)
        subprocess.run(["bash",str(path)],check=True)
    print("R10_SITE_SPECIFIC_NATIVE_BUILD_RETURNED_NO_CAUSAL_PASS")

if __name__=="__main__":
    main()
