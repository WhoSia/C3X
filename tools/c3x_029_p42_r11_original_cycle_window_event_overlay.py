#!/usr/bin/env python3
"""R11 strict original-source cycle-alpha cutoffs and search-window chronology.

Derived ONLY after R10 overlay. R11 instruments the concrete original
conditional branch, not a proxy for a move's quality or a natural mediator.
Every source event is written to private file, no raw key in public JSON.
"""
from pathlib import Path
import argparse, hashlib, json
OLD='''        alpha = c3x042_r10_draw_site(pos.this_thread(),1,ss->ply);
        if (alpha >= beta)
            return alpha;'''
NEW=r'''        const Value c3x042_r11_old_alpha = alpha;
        const Value c3x042_r11_candidate =
            c3x042_r10_draw_site(pos.this_thread(),1,ss->ply);
        alpha = c3x042_r11_candidate;
        const bool c3x042_r11_cut = alpha >= beta;
        if (const char* c3x042_r11_path = std::getenv("C3X042_R11_CYCLE_WINDOW_TRACE")) {
            if (*c3x042_r11_path) {
                if (auto* f = std::fopen(c3x042_r11_path,"a")) {
                    std::fprintf(f,
                      "c3x042_r11 event=cycle_alpha key64=%llu ply=%d depth=%d "
                      "node_mod4=%d old_alpha=%d beta=%d candidate=%d "
                      "new_alpha=%d cutoff=%d root_move=%d\n",
                      (unsigned long long)pos.key(),ss->ply,int(depth),
                      int(pos.this_thread()->nodes & 3),int(c3x042_r11_old_alpha),
                      int(beta),int(c3x042_r11_candidate),int(alpha),
                      int(c3x042_r11_cut),int(c3x018_root_context_move));
                    std::fclose(f);
                }
            }
        }
        if (c3x042_r11_cut)
            return alpha;'''

def patch(source):
    if 'c3x042_r11_old_alpha' in source:
        raise ValueError('R11_HOLD_ALREADY_INSTRUMENTED')
    if source.count(OLD)!=1:
        raise ValueError('R11_HOLD_SOURCE_CYCLE_WINDOW_ANCHOR_COUNT_'+str(source.count(OLD)))
    return source.replace(OLD,NEW,1)

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--source',required=True)
    p.add_argument('--out-manifest',required=True)
    a=p.parse_args()
    f=Path(a.source)/'src/search.cpp'
    before=f.read_bytes()
    after=patch(before.decode()).encode()
    f.write_bytes(after)
    out=Path(a.out_manifest)
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps({
        'schema':'c3x042-r11-native-cycle-window-surgery-v1',
        'input_sha256':hashlib.sha256(before).hexdigest(),
        'output_sha256':hashlib.sha256(after).hexdigest(),
        'source_site':'original Stockfish16 non-root game-cycle alpha assignment',
        'privacy':'native keys, window scores, full event chronology private',
        'original_control_modes':'R10 mode 0 unmodified; R10 mode 1 global cycle-alpha neutralization',
        'source_cutoff_is_not_full_ancestor_root_mediation':True
    },indent=2,sort_keys=True)+'\n')
    print('C3X042_R11_CYCLE_WINDOW_PATCH_ONLY_NO_NATIVE_VERDICT')

if __name__=='__main__':
    main()
