#!/usr/bin/env python3
"""R11 actual source window census: R10 mode0 versus mode1, native cold Game14.

Only same-compiled-source legal original A/B arms, two cold runs, exact original
Stockfish window events. Raw Zobrist keys and per-node scores PRIVATE; public
report contains counts and source-identity common-prefix lengths only.
"""
import argparse,json,os,re
from pathlib import Path
from c3x_029_p42_r9_original_AB_neutralized_source_probe import verify_original_inputs
from c3x_023_P1_R2_T0_chronological_post_TT_common_SEE_dev import cold
from c3x_018_independent16_TT_value_transport_native import verified_reader_lineage
from c3x_029_p42_r10_native_original_AB_draw_site_court import observed

RX=re.compile(
 r'^c3x042_r11 event=cycle_alpha key64=(\d+) ply=(\d+) depth=(-?\d+) '
 r'node_mod4=([0-3]) old_alpha=(-?\d+) beta=(-?\d+) candidate=(-?\d+) '
 r'new_alpha=(-?\d+) cutoff=([01]) root_move=(-?\d+)$',re.M)

def parse_events(raw,neutral):
    candidate_lines=[x for x in raw.splitlines() if x.startswith('c3x042_r11 ')]
    rows=RX.findall(raw)
    if len(candidate_lines)!=len(rows):
        raise ValueError('R11_HOLD_MALFORMED_PHYSICAL_SOURCE_EVENT')
    out=[]
    for group in rows:
        key,ply,depth,node,old,beta,cand,new,cut,root=map(int,group)
        if key<0 or ply<0 or node>3 or cand!=new or cut!=int(new>=beta):
            raise ValueError('R11_HOLD_SOURCE_CUTOFF_OR_WINDOW_INCONSISTENT')
        if cand!=(0 if neutral else -1+(node&2)):
            raise ValueError('R11_HOLD_SOURCE_ORIGINAL_DRAW_OR_PARITY_INCONSISTENT')
        out.append({'key':key,'ply':ply,'depth':depth,'mod4':node,
                    'old_alpha':old,'beta':beta,'candidate':cand,
                    'cutoff':cut,'root_move':root})
    return out

def summarize(events):
    return {
      'cycle_window_events':len(events),
      'cycle_immediate_cutoffs':sum(e['cutoff'] for e in events),
      'alpha_increased':sum(e['candidate']>e['old_alpha'] for e in events),
      'alpha_decreased':sum(e['candidate']<e['old_alpha'] for e in events),
      'alpha_unchanged':sum(e['candidate']==e['old_alpha'] for e in events),
      'original_node_bit_2_set':sum(bool(e['mod4']&2) for e in events),
      'candidate_negative':sum(e['candidate']<0 for e in events),
      'candidate_positive':sum(e['candidate']>0 for e in events)
    }

def compare_source_prefix(original,changed):
    # A matching position/parent window before the draw return is a higher
    # evidence class than merely comparing summary totals.
    prefix=0
    for x,y in zip(original,changed):
        if (x['key'],x['ply'],x['depth'],x['root_move'],x['old_alpha'],x['beta']) != (
            y['key'],y['ply'],y['depth'],y['root_move'],y['old_alpha'],y['beta']):
            break
        prefix+=1
    return {
       'same_pre_return_source_event_prefix':prefix,
       'within_prefix_cutoff_decision_disagreements':sum(
           x['cutoff']!=y['cutoff'] for x,y in zip(original[:prefix],changed[:prefix])),
       'within_prefix_draw_return_disagreements':sum(
           x['candidate']!=y['candidate'] for x,y in zip(original[:prefix],changed[:prefix])),
       'same_number_of_source_events':len(original)==len(changed),
       'full_dynamic_source_event_identity_equal':prefix==len(original)==len(changed)
    }

def audit(cases,reads):
    result={'schema':'c3x042-r11-actual-cycle-window-native-court-v1',
       'source_mode':'original pinned Stockfish16 Game14 NNUE OFF',
       'native_chess_strategic_truth_certified':False,
       'unique_natural_guard_to_root_mediation_certified':False,
       'single_source_event_root_causation_certified':False,
       'source_key_or_raw_event_disclosed':False}
    if len(reads)!=4 or not all(reads):
        return dict(result,status='HOLD_TT_FIRST_PHYSICAL_READER_CUSTODY')
    if any(len(cases[m][a])!=2 for m in ('0','1') for a in ('A','B')):
        return dict(result,status='HOLD_COLD_REPLAY_MISSING')
    moves={m:{a:[x['move'] for x in cases[m][a]] for a in ('A','B')} for m in ('0','1')}
    if (moves['0']['A']!=['b3a4']*2 or moves['0']['B']!=['f3f4']*2
        or moves['1']['A']!=['b3a4']*2 or moves['1']['B']!=['b3a4']*2):
        return dict(result,status='HOLD_PREDECLARED_R10_CHOICE_REPLAY_DRIFT',observed_root_choices=moves)
    for m in ('0','1'):
        for a in ('A','B'):
            for c in cases[m][a]:
                if c['r10_cycle_calls']!=len(c['events']):
                    return dict(result,status='HOLD_R10_R11_ACTUAL_SOURCE_COUNT_MISMATCH')
    out={m:{a:[summarize(x['events']) for x in cases[m][a]]
               for a in ('A','B')} for m in ('0','1')}
    comparison={a:[compare_source_prefix(cases['0'][a][i]['events'],
                                         cases['1'][a][i]['events'])
                    for i in range(2)] for a in ('A','B')}
    return dict(result,status='PASS_NATIVE_CYCLE_ALPHA_EVENT_AND_CUTOFF_OBSERVATION_ONLY',
                root_choices=moves,cycle_window_counts=out,source_event_identity_comparisons=comparison)

def main():
    p=argparse.ArgumentParser()
    for name in ('source','stagea','forecast','engine','private','public-out'):
        p.add_argument('--'+name,required=True)
    a=p.parse_args()
    world,clock,physical,watch,filters=verify_original_inputs(a.source,a.stagea,a.forecast)
    private=Path(a.private);private.mkdir(parents=True,exist_ok=True)
    cases={m:{'A':[],'B':[]} for m in ('0','1')}
    reader_valid=[]
    for mode in ('0','1'):
        for run in range(2):
            for arm in ('A','B'):
                window=private/(f'm{mode}_{arm}_cold{run}_source_windows.txt')
                site=private/(f'm{mode}_{arm}_cold{run}_source_sites.txt')
                window.write_text('');site.write_text('')
                original=os.environ.copy()
                os.environ['C3X042_R11_CYCLE_WINDOW_TRACE']=str(window.resolve())
                os.environ['C3X042_R10_DRAW_SITE_TRACE']=str(site.resolve())
                os.environ['C3X042_R10_NEUTRAL_DRAW_SITE']=mode
                os.environ.pop('C3X042_R9_DRAW_PARITY_NEUTRAL',None)
                os.environ.pop('C3X042_R8_DROP_DESCENDANT_TT_SAVE',None)
                try:
                    out=(cold(a.engine,world,clock,'O','OBS',watch=watch)
                         if arm=='A' else
                         cold(a.engine,world,clock,'O','V',physical,filter=filters,watch=watch))
                finally:
                    os.environ.clear();os.environ.update(original)
                ev=parse_events(window.read_text(),mode=='1')
                counters=observed(site.read_text(),int(mode))
                cases[mode][arm].append({
                    'move':out['UCI']['bestmove'],'events':ev,
                    'r10_cycle_calls':counters['1']['calls']})
                if arm=='B':
                    reader_valid.append(bool(verified_reader_lineage(out)['all_valid'])
                                        and any(x.get('kind')=='reader_block' for x in out['blocks']))
    result=audit(cases,reader_valid)
    dest=Path(a.public_out);dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print('C3X042_R11_NATIVE_CYCLE_WINDOW_COURT',result['status'])
    if not result['status'].startswith('PASS_'):raise SystemExit(2)

if __name__=='__main__':
    main()
