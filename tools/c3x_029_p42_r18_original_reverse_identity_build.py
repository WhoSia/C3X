#!/usr/bin/env python3
"""R18 derived original source + R12 exact ordinal code + source-ID reverse."""
import hashlib,subprocess,tempfile
from pathlib import Path
from c3x_029_p42_r12_derived_original_single_cycle_build import OLD,derive_r12,MAKE

EXTRA='python tools/c3x_029_p42_r18_source_identity_reverse_B33_in_C_overlay.py --source "$root" --out-manifest evidence/C3X042_R18_REVERSE_NATIVE_SOURCE.json'
def derive_r18(source):
    body=derive_r12(source)
    if body.count(MAKE)!=1 or body.index("c3x_029_p42_r12_single_cycle_event_intervention.py")>=body.index(MAKE):
        raise ValueError("R18_HOLD_FROZEN_R12_BUILD_ORDER")
    return body.replace(MAKE,EXTRA+"\n"+MAKE,1)
def main():
    original=OLD.read_text();derived=derive_r18(original)
    Path("evidence").mkdir(exist_ok=True)
    Path("evidence/C3X042_R18_ORIGINAL_DERIVED_BUILD_SHA.txt").write_text(
        "original_027_sha256="+hashlib.sha256(original.encode()).hexdigest()+"\n"+
        "R18_derived_sha256="+hashlib.sha256(derived.encode()).hexdigest()+"\n")
    with tempfile.TemporaryDirectory(prefix="c3x042-r18-") as d:
        script=Path(d)/"source.sh";script.write_text(derived)
        subprocess.run(["bash",str(script)],check=True)
    print("R18_ORIGINAL_BUILD_COMPLETED_NO_NATIVE_CAUSAL_VERDICT")
if __name__=="__main__":
    main()
