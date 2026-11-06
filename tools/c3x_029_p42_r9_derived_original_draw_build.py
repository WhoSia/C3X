#!/usr/bin/env python3
"""R9 derives immutable R8 ABC+D source recipe with one extra draw probe."""
from pathlib import Path
import hashlib
import subprocess
import tempfile
from c3x_029_p42_r8_derived_native_build import OLD, derive_r8, MAKE

DRAW='python tools/c3x_029_p42_r9_original_value_draw_node_parity_intervention.py --source "$root" --out-manifest evidence/C3X042_R9_NATIVE_DRAW_SOURCE.json'

def derive_r9(source):
    original=derive_r8(source)
    if original.count(MAKE)!=1 or original.index("c3x_029_p42_r8_guard_descendant_tt_save_intervention.py")>=original.index(MAKE):
        raise ValueError("R9_HOLD_R8_PATCH_ORDER_DRIFT")
    return original.replace(MAKE,DRAW+"\n"+MAKE,1)

def main():
    orig=OLD.read_text()
    final=derive_r9(orig)
    Path("evidence").mkdir(exist_ok=True)
    Path("evidence/C3X042_R9_SOURCE_RECIPE_CUSTODY.txt").write_text(
        "original_sha256="+hashlib.sha256(orig.encode()).hexdigest()+"\n"+
        "r9_sha256="+hashlib.sha256(final.encode()).hexdigest()+"\n")
    with tempfile.TemporaryDirectory(prefix="c3x042-r9-") as tmp:
        script=Path(tmp)/"original-source-plus-draw.sh"
        script.write_text(final)
        subprocess.run(["bash",str(script)],check=True)
    print("R9_NATIVE_BUILD_RETURNED_NO_DRAW_CAUSAL_CLAIM")
if __name__=="__main__":
    main()
