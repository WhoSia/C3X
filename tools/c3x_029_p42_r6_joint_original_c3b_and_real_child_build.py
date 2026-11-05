#!/usr/bin/env python3
"""P42/R6: jointly run *existing* C3X027 G4-G9 source overlays with R5.

Do not modify historical 0.27 instruments. Appends only the new passive,
post-do_move-key source probe after the original C3b chain and before make.
A successful build is NOT a successful causal explanation.
"""
from pathlib import Path
import hashlib
import subprocess
import tempfile

OLD=Path("tools/c3x_027_game14_lineage_build.sh")
LEGACY='python tools/c3x_027_game14_C3b_passive_ancestor_overlay.py --source "$root" --out-manifest evidence/C3X027_GAME14_C3B_PASSIVE.json'
MAKE='make -s -C "$root/src" -j2 build ARCH=x86-64'
ADDED='python tools/c3x_029_p42_r5_game14_capture_local_lineage_overlay.py --source "$root" --out-manifest evidence/C3X042_R6_JOINT_LOCAL_SOURCE.json'

def derive(original: str) -> str:
    if original.count(LEGACY)!=1 or original.count(MAKE)!=1:
        raise ValueError("R6_HOLD_HISTORICAL_SOURCE_BUILD_CHANGED")
    if original.index(LEGACY)>=original.index(MAKE):
        raise ValueError("R6_HOLD_C3B_COMES_AFTER_BUILD")
    if original.count("c3x_027_game14_passive_lineage_overlay.py")!=1:
        raise ValueError("R6_HOLD_HISTORICAL_CHILD_LINEAGE_MISSING")
    if original.index("c3x_027_game14_passive_lineage_overlay.py")>=original.index(LEGACY):
        raise ValueError("R6_HOLD_PARENT_PRECEDES_CHILD_OVERLAY")
    return original.replace(MAKE,ADDED+"\n"+MAKE,1)

def main():
    before=OLD.read_text()
    compiled_recipe=derive(before)
    Path("evidence").mkdir(exist_ok=True)
    Path("evidence/C3X042_R6_JOINT_BUILD_CUSTODY.txt").write_text(
        "original_recipe_sha256="+hashlib.sha256(before.encode()).hexdigest()+"\n"+
        "derived_recipe_sha256="+hashlib.sha256(compiled_recipe.encode()).hexdigest()+"\n")
    with tempfile.TemporaryDirectory(prefix="c3x042-r6-") as temp:
        script=Path(temp)/"derived-original-plus-r5.sh"
        script.write_text(compiled_recipe)
        subprocess.run(["bash",str(script)],check=True)
    print("C3X042_R6_JOINT_NATIVE_BUILD_RETURNED_ONLY_NO_CAUSAL_COURT")

if __name__=="__main__":
    main()
