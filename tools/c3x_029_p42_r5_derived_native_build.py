#!/usr/bin/env python3
"""C3X P42/R5 native build: derive from immutable historical recipe.

Never edit historical build or source overlay. Fail if exact insertion site drifts.
Creates local GPL Stockfish executable only in CI; never uploads binary.
"""
from pathlib import Path
import hashlib
import subprocess
import tempfile

BASE = Path("tools/c3x_027_sept_capture_counterfactual_build.sh")
INSERT = 'make -s -C "$root/src" -j2 build ARCH=x86-64'
NEW = 'python tools/c3x_029_p42_r5_game14_capture_local_lineage_overlay.py --source "$root" --out-manifest evidence/C3X042_R5_LOCAL_SOURCE_OVERLAY.json'
def build():
    original=BASE.read_text()
    if original.count(INSERT)!=1 or original.count("c3x_027_sept_capture_counterfactual_patch.py")!=1:
        raise ValueError("P42_R5_HOLD_OLD_BUILD_RECIPE_DRIFT")
    if original.index("c3x_027_sept_capture_counterfactual_patch.py") > original.index(INSERT):
        raise ValueError("P42_R5_HOLD_INVALID_PATCH_ORDER")
    derived=original.replace(INSERT,NEW+"\n"+INSERT,1)
    Path("evidence").mkdir(exist_ok=True)
    Path("evidence/C3X042_R5_BUILD_RECIPE_SHA256.txt").write_text(
        "historical_recipe_sha256="+hashlib.sha256(original.encode()).hexdigest()+"\n"+
        "derived_recipe_sha256="+hashlib.sha256(derived.encode()).hexdigest()+"\n"
    )
    with tempfile.TemporaryDirectory(prefix="c3x-r5-") as tmp:
        path=Path(tmp)/"derived-native-build.sh"
        path.write_text(derived)
        subprocess.run(["bash",str(path)],check=True)
    print("C3X042_R5_NATIVE_BUILD_ATTEMPT_FINISHED_CHECK_SEPARATE_CI_RESULTS")

if __name__=="__main__":
    build()
