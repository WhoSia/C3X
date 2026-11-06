#!/usr/bin/env python3
"""R14: compare original guarded C vs independent cycle event33 B33 IN ONE binary.

Legacy source-exact C is produced by the unmodified official C3X027 runner.
The newer R12 single-event counterfactual B33 uses exactly the same build.
The original capture-prune target's raw keys and ancestry stay private.
Root boundary equality is not equivalence of source-state causal mechanisms.
"""
import argparse,json,os,re,subprocess
from pathlib import Path
from c3x_029_p42_r9_original_AB_neutralized_source_probe import verify_original_inputs
from c3x_023_P1_R2_T0_chronological_post_TT_common_SEE_dev import cold
from c3x_018_independent16_TT_value_transport_native import verified_reader_lineage
from c3x_018_jan16_TT_cross_window_pair_native import RULES,mask_filters
from c3x_027_game14_root_boundary_court import parse_boundary_lines
from c3x_029_p42_r11_native_cycle_alpha_window_court import RX
from c3x_029_p42_r12_native_single_cycle_event_court import (
   split_two_physical_plays,selected_ordinals,match_single_event)

SOURCE_FIELDS=('key64','root_call','move','threshold')

def parsed_actions(raw):
    out=[]
    for line in raw.splitlines():
        if 'action=' not in line:
            continue
        row=dict(re.findall(r'([A-Za-z_][A-Za-z0-9_]*)=([^\s]+)',line))
        if any(x not in row for x in SOURCE_FIELDS+('action',)):
            raise ValueError('R14_HOLD_MALFORMED_NATIVE_CAPTURE_GUARD')
        out.append(row)
    return out

def parse_three_cold_root_worlds(raw):
    lines=[x for x in raw.splitlines() if 'event=ROOT_BOUNDARY' in x]
    groups=[]
    for line in lines:
        row=dict(re.findall(r'([A-Za-z_][A-Za-z0-9_]*)=([^\s]+)',line))
        if 'depth' not in row:
            raise ValueError('R14_HOLD_ROOT_DEPTH_MISSING')
        if row['depth']=='1':groups.append([])
        if not groups:
            raise ValueError('R14_HOLD_ORPHAN_ROOT_BOUNDARY')
        groups[-1].append(line)
    if len(groups)!=6:
        raise ValueError('R14_HOLD_NOT_SIX_NATIVE_ABC_ENGINE_PROCESSES')
    out={}
    for i,name in enumerate(('A','B','C')):
        pair='\n'.join(groups[i*2]+groups[i*2+1])
        court=parse_boundary_lines(pair.splitlines())
        if court['status']!='PASS_TWO_IDENTICAL_COLD_BOUNDARY_RUNS':
            raise ValueError('R14_HOLD_'+name+'_'+court['status'])
        out[name]=court['runs'][0]
    return out

def cycle_rows(raw):
    matched=RX.findall(raw)
    lines=[x for x in raw.splitlines() if x.startswith('c3x042_r11 ')]
    if len(matched)!=len(lines):
        raise ValueError('R14_HOLD_R11_NATIVE_CYCLE_STREAM_MALFORMED')
    out=[]
    for row in matched:
        key,ply,depth,mod,old,beta,candidate,new,cut,root=map(int,row)
        if cut!=int(candidate>=beta) or candidate!=new:
            raise ValueError('R14_HOLD_ACTUAL_SOURCE_WINDOW_INCONSISTENT')
        out.append({'key':key,'ply':ply,'depth':depth,'mod4':mod,
            'old_alpha':old,'beta':beta,'candidate':candidate,
            'cutoff':cut,'root_move':root})
    return out

def compare_native_worlds(root,C_guard_actions,B33_guard_actions):
    a,b,c,d=(root[x] for x in ('A','B','C','B33'))
    if len(a)!=len(b) or len(a)!=len(c) or len(a)!=len(d):
        return {'status':'HOLD_ROOT_DEPTH_SUPPORT_DIFFERENT'}
    if any(tuple(rows[i]['depth'] for rows in (a,b,c,d)) != (i+1,)*4
           for i in range(len(a))):
        return {'status':'HOLD_ROOT_DEPTH_IDENTITY_CHANGED'}
    firstdiff=lambda x,y:next((i+1 for i,(p,q) in enumerate(zip(x,y))
                               if any(p[k]!=q[k] for k in ('leader','score','average'))),None)
    at9=8
    c9=c[at9]; d9=d[at9]
    result={
      'status':'PASS_ACTUAL_NATIVE_C_AND_B33_SOURCE_ROOT_COMPARISON_ONLY',
      'root_depths':len(a),
      'first_B_C_divergent_depth':firstdiff(b,c),
      'first_B_B33_divergent_depth':firstdiff(b,d),
      'first_C_B33_divergent_depth':firstdiff(c,d),
      'C_vs_B33_matching_leader_and_score_depths':[
         row['depth'] for row,other in zip(c,d)
         if row['leader']==other['leader'] and row['score']==other['score']],
      'C_vs_B33_all_depth_summary_equal':c==d,
      'depth9_source_boundary':{
         'B_TT_FIRST':dict(b[at9]),
         'C_capture_guard_bypass':dict(c9),
         'B33_one_cycle_call':dict(d9)},
      'C_guard_exact_reenable_native_source_attempts':len(C_guard_actions),
      'B33_same_original_guard_source_actions':dict(B33_guard_actions),
      'identical_full_source_search_state_certified':False,
      'natural_guard_cycle_mediation_certified':False,
      'independent_strategic_chess_future_certified':False,
      'prospective_transport_certified':False,
      'private_chess_key_exposed':False
    }
    return result

def main():
    p=argparse.ArgumentParser()
    for name in ('source','stagea','forecast','engine','private','public-out'):
        p.add_argument('--'+name,required=True)
    a=p.parse_args()
    world,clock,physical,watch,filters=verify_original_inputs(a.source,a.stagea,a.forecast)
    private=Path(a.private);private.mkdir(parents=True,exist_ok=True)
    olddir=private/'original_027_native';olddir.mkdir(exist_ok=True)
    legacy_roots=private/'ABC_legacy_root_depths.txt'
    legacy_cycles=private/'ABC_legacy_cycle_windows.txt'
    legacy_roots.write_text('');legacy_cycles.write_text('')
    before=os.environ.copy()
    os.environ['C3X027_GAME14_LINEAGE_LOG']=str(legacy_roots.resolve())
    os.environ['C3X042_R11_CYCLE_WINDOW_TRACE']=str(legacy_cycles.resolve())
    os.environ.pop('C3X042_R12_TARGET_ORDINAL',None)
    os.environ.pop('C3X042_R9_DRAW_PARITY_NEUTRAL',None)
    os.environ.pop('C3X042_R10_NEUTRAL_DRAW_SITE',None)
    try:
        output=private/'legacy_ABC_private_summary.json'
        subprocess.run(['python','-u','harness/c3x_027_sept_game14_direct_capture_guard.py',
            '--source',a.source,'--stagea',a.stagea,'--forecast',a.forecast,
            '--engine',a.engine,'--out',str(output),'--private',str(olddir)],
            check=True)
    finally:
        os.environ.clear();os.environ.update(before)
    original=json.loads(output.read_text())
    if not (original['baseline_bestmove']=='b3a4'
            and original['TT_FIRST_bestmove']=='f3f4'
            and original['counterfactual_bestmove']=='b3a4'
            and original['counterfactual_branch_action_counts'].get('EXACT_ONE_EVENT_REENABLED')==2):
        raise ValueError('R14_HOLD_ORIGINAL_SOURCE_ABC_CONTROL_CHANGED')
    roots=parse_three_cold_root_worlds(legacy_roots.read_text())
    original_cycles=cycle_rows(legacy_cycles.read_text())
    # The original source's ABC runner executes A, B, C in this immutable order.
    # A and B counts are independently revalidated from native R11, not inferred.
    if len(original_cycles)<380+562:
        raise ValueError('R14_HOLD_ORIGINAL_B_SOURCE_TRACE_TOO_SHORT')
    base_B=split_two_physical_plays(original_cycles[380:380+562])
    if selected_ordinals(base_B)!=[30,31,32,33]:
        raise ValueError('R14_HOLD_R12_ORIGINAL_B_EVENT_PRESELECTION_DRIFT')
    rootfile=private/'B33_source_root_depths.txt'
    cyclefile=private/'B33_single_event_window_log.txt'
    capturefile=private/'B33_capture_prune_source.txt'
    for f in (rootfile,cyclefile,capturefile):f.write_text('')
    before=os.environ.copy()
    os.environ['C3X027_GAME14_LINEAGE_LOG']=str(rootfile.resolve())
    os.environ['C3X042_R11_CYCLE_WINDOW_TRACE']=str(cyclefile.resolve())
    os.environ['C3X027_CAPTURE_BRANCH_LOG']=str(capturefile.resolve())
    os.environ['C3X042_R12_TARGET_ORDINAL']='33'
    os.environ['C3X042_R10_NEUTRAL_DRAW_SITE']='0'
    os.environ.pop('C3X042_R9_DRAW_PARITY_NEUTRAL',None)
    os.environ.pop('C3X042_R8_DROP_DESCENDANT_TT_SAVE',None)
    try:
        b33=cold(a.engine,world,clock,'O','V',physical,filter=filters,watch=watch)
    finally:
        os.environ.clear();os.environ.update(before)
    if (b33['UCI']['bestmove']!='b3a4'
        or not verified_reader_lineage(b33)['all_valid']
        or not any(x.get('kind')=='reader_block' for x in b33['blocks'])):
        raise ValueError('R14_HOLD_B33_NATIVE_MOVE_OR_TT_READER')
    B33_cold=parse_boundary_lines(rootfile.read_text().splitlines())
    if B33_cold['status']!='PASS_TWO_IDENTICAL_COLD_BOUNDARY_RUNS':
        raise ValueError('R14_HOLD_B33_NATIVE_ROOT_BOUNDARY_DRIFT')
    roots['B33']=B33_cold['runs'][0]
    changed_B=split_two_physical_plays(cycle_rows(cyclefile.read_text()))
    if match_single_event(base_B,changed_B,33) != 'PASS_ACTUAL_ONE_SOURCE_EVENT_WITH_MATCHED_PREFIX':
        raise ValueError('R14_HOLD_B33_NOT_EXACT_MATCHED_SOURCE_EVENT33')
    oldcf=parsed_actions((olddir/'TT_FIRST_REENABLE_ONE.txt').read_text())
    forced=[x for x in oldcf if x['action']=='EXACT_ONE_EVENT_REENABLED']
    if len(forced)!=2:
        raise ValueError('R14_HOLD_ORIGINAL_C_EXACT_CAPTURE_GUARD_NOT_PHYSICAL')
    signatures={tuple(x[k] for k in SOURCE_FIELDS) for x in forced}
    if len(signatures)!=1:
        raise ValueError('R14_HOLD_C_FORCED_GUARD_SOURCE_SIGNATURE_DRIFT')
    target=next(iter(signatures))
    newactions=parsed_actions(capturefile.read_text())
    from collections import Counter
    matching=Counter(x['action'] for x in newactions
                     if tuple(x[k] for k in SOURCE_FIELDS)==target)
    report=compare_native_worlds(roots,forced,matching)
    report.update({
        'schema':'c3x042-r14-original-guard-vs-single-draw-event-convergence-v1',
        'game14_postselected':True,'nnue_enabled':False,
        'historical_source_ABC_reproduced':True,
        'original_B33_exact_source_event33_verified':True,
        'C_and_B33_reproduce_b3a4':True,
        'two_actual_native_engine_plays_per_cold':2})
    path=Path(a.public_out);path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
    print('C3X042_R14_C_VS_B33_SAME_ORIGINAL_ENGINE',report['status'],
          'first_B_C',report.get('first_B_C_divergent_depth'),
          'first_B_B33',report.get('first_B_B33_divergent_depth'),
          'first_C_B33',report.get('first_C_B33_divergent_depth'))
    if not report['status'].startswith('PASS_'):raise SystemExit(2)

if __name__=='__main__':
    main()
