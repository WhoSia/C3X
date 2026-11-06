#!/usr/bin/env python3
"""R8 derives the exact R6 (original C3b + real child) recipe without mutation."""
from pathlib import Path
import hashlib,subprocess,tempfile
from c3x_029_p42_r6_joint_original_c3b_and_real_child_build import OLD,derive

MAKE='make -s -C "$root/src" -j2 build ARCH=x86-64'
R8='python tools/c3x_029_p42_r8_guard_descendant_tt_save_intervention.py --source "$root" --out-manifest evidence/C3X042_R8_TT_WRITE_SOURCE.json'

def derive_r8(source):
    r6=derive(source)
    if r6.count(MAKE)!=1 or r6.index("c3x_029_p42_r5_game14_capture_local_lineage_overlay.py")>=r6.index(MAKE):
        raise ValueError("R8_HOLD_R6_SOURCE_ORDER_DRIFT")
    return r6.replace(MAKE,R8+"\n"+MAKE,1)

def main():
    source=OLD.read_text()
    merged=derive_r8(source)
    Path("evidence").mkdir(exist_ok=True)
    Path("evidence/C3X042_R8_FROZEN_RECIPE_SHA256.txt").write_text(
        "original_027="+hashlib.sha256(source.encode()).hexdigest()+"\n"
        "R8_derived="+hashlib.sha256(merged.encode()).hexdigest()+"\n")
    with tempfile.TemporaryDirectory(prefix="c3x042-r8-") as tmp:
        p=Path(tmp)/"derived-immutable-original-with-r8.sh"
        p.write_text(merged)
        subprocess.run(["bash",str(p)],check=True)
    print("C3X042_R8_NATIVE_BUILD_FINISHED_NO_WORLD_CAUSATION_CLAIM")

if __name__=="__main__":
    main()
