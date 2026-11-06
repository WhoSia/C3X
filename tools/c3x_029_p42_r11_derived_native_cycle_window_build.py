#!/usr/bin/env python3
"""R11 append exact original cycle-window read-only probe after frozen R10."""
from pathlib import Path
import hashlib,subprocess,tempfile
from c3x_029_p42_r10_original_site_draw_build import OLD,derive_r10,MAKE
PATCH='python tools/c3x_029_p42_r11_original_cycle_window_event_overlay.py --source "$root" --out-manifest evidence/C3X042_R11_SOURCE_WINDOW.json'

def derive_r11(original):
    stack=derive_r10(original)
    if stack.count(MAKE)!=1 or stack.index('c3x_029_p42_r10_source_site_specific_draw_parity_overlay.py')>=stack.index(MAKE):
        raise ValueError('R11_HOLD_IMMUTABLE_SOURCE_ORDER_CHANGED')
    return stack.replace(MAKE,PATCH+'\n'+MAKE,1)

def main():
    original=OLD.read_text()
    derived=derive_r11(original)
    Path('evidence').mkdir(exist_ok=True)
    Path('evidence/C3X042_R11_SOURCE_ORDER_SHA.txt').write_text(
        'original_027_sha256='+hashlib.sha256(original.encode()).hexdigest()+'\n'+
        'derived_r11_sha256='+hashlib.sha256(derived.encode()).hexdigest()+'\n')
    with tempfile.TemporaryDirectory(prefix='c3x042-r11-') as d:
        p=Path(d)/'derived.sh'
        p.write_text(derived)
        subprocess.run(['bash',str(p)],check=True)
    print('R11_ORIGINAL_NATIVE_BUILD_DONE_NO_CAUSAL_PASS')
if __name__=='__main__':
    main()
