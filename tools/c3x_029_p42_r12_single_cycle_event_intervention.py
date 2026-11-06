#!/usr/bin/env python3
"""P42/R12 isolated single original cycle-alpha draw-return call intervention.

A single event is indexed by *actual native source-call ordinal*, not by
post-hoc bestmove. Pre-outcome targeted ordinals are derived exhaustively from
the first 33 source-matched R11 B-world calls where replacing the actual draw
score by zero changes the immediate alpha>=beta decision. No root outcomes
are consulted to choose events. Child code remains otherwise unchanged.
"""
from pathlib import Path
import argparse,hashlib,json
STATE_ANCHOR='  // search<>() is the main search function for both PV and non-PV nodes'
ANCHOR='''        const Value c3x042_r11_candidate =
            c3x042_r10_draw_site(pos.this_thread(),1,ss->ply);'''
REPLACEMENT=r'''        // R12: passive original value first; perturb at most one physical
        // cycle-alpha source call in this entire cold engine process.
        const Value c3x042_r12_native =
            c3x042_r10_draw_site(pos.this_thread(),1,ss->ply);
        ++c3x042_r12_ordinal;
        const char* c3x042_r12_target = std::getenv("C3X042_R12_TARGET_ORDINAL");
        const unsigned long long c3x042_r12_selected =
            c3x042_r12_target && *c3x042_r12_target
            ? std::strtoull(c3x042_r12_target,nullptr,10) : 0;
        const bool c3x042_r12_hit = c3x042_r12_selected != 0
            && c3x042_r12_ordinal == c3x042_r12_selected;
        const Value c3x042_r11_candidate =
            c3x042_r12_hit ? VALUE_DRAW : c3x042_r12_native;'''

def patch(source):
    if 'c3x042_r12_ordinal' in source:
        raise ValueError('R12_HOLD_ALREADY_PATCHED')
    if source.count(ANCHOR)!=1:
        raise ValueError('R12_HOLD_ORIGINAL_EVENT_ANCHOR_COUNT_'+str(source.count(ANCHOR)))
    if source.count(STATE_ANCHOR)!=1:
        raise ValueError('R12_HOLD_SHARED_THREAD_STATE_ANCHOR_COUNT_'+str(source.count(STATE_ANCHOR)))
    source=source.replace(STATE_ANCHOR,
        '  // R12 shared across Root/PV/NonPV template instantiations, thread-local.\\n'
        '  thread_local unsigned long long c3x042_r12_ordinal=0;\\n'
        +STATE_ANCHOR,1)
    return source.replace(ANCHOR,REPLACEMENT,1)

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--source',required=True)
    p.add_argument('--out-manifest',required=True)
    a=p.parse_args()
    f=Path(a.source)/'src/search.cpp'
    before=f.read_bytes()
    after=patch(before.decode()).encode()
    f.write_bytes(after)
    out=Path(a.out_manifest);out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps({
      'schema':'c3x042-r12-one-native-cycle-call-v1',
      'original_sha256':hashlib.sha256(before).hexdigest(),
      'derived_sha256':hashlib.sha256(after).hexdigest(),
      'source_selector':'C3X042_R12_TARGET_ORDINAL',
      'selection_rule':'all original B prefix 33 actual calls with zero-neutral cutoff decision different; expected 4',
      'selector_scoped':'one actual original source cycle-alpha call per new cold native process',
      'unnatural_direct_mediator_inference_prohibited':True
    },sort_keys=True,indent=2)+'\n')
    print('R12_ORIGINAL_ONE_EVENT_SOURCE_PATCH_ONLY')
if __name__=='__main__':
    main()
