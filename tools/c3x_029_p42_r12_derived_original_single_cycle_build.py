#!/usr/bin/env python3
"""R12 immutable original 0.27->R8/R9/R10/R11 plus single-event source patch."""
from pathlib import Path
import hashlib,subprocess,tempfile
from c3x_029_p42_r11_derived_native_cycle_window_build import OLD,derive_r11,MAKE
EXTRA='python tools/c3x_029_p42_r12_single_cycle_event_intervention.py --source "$root" --out-manifest evidence/C3X042_R12_SINGLE_EVENT_SOURCE.json'
def derive_r12(source):
    base=derive_r11(source)
    if base.count(MAKE)!=1 or base.index('c3x_029_p42_r11_original_cycle_window_event_overlay.py')>=base.index(MAKE):
        raise ValueError('R12_HOLD_R11_SOURCE_PATCH_ORDER_DRIFT')
    return base.replace(MAKE,EXTRA+'\n'+MAKE,1)
def main():
    source=OLD.read_text()
    product=derive_r12(source)
    Path('evidence').mkdir(exist_ok=True)
    Path('evidence/C3X042_R12_ORIGINAL_AND_DERIVED_RECIPE_SHA.txt').write_text(
       'original_027_sha256='+hashlib.sha256(source.encode()).hexdigest()+'\n'+
       'derived_r12_sha256='+hashlib.sha256(product.encode()).hexdigest()+'\n')
    with tempfile.TemporaryDirectory(prefix='c3x042-r12-') as d:
        script=Path(d)/'source.sh';script.write_text(product)
        subprocess.run(['bash',str(script)],check=True)
    print('R12_NATIVE_BUILD_COMPLETE_NO_SINGLE_EVENT_CAUSAL_PASS')
if __name__=='__main__':
    main()
