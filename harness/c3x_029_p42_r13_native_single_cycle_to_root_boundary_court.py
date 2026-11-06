#!/usr/bin/env python3
"""R13 same-physical-execution source event #33 -> root depth boundary court.

Pinned Game14 B only. Original and R12 #33 are independent source-native
interventions; the root-boundary trace is the historical 0.27 observer.
All exact source keys/windows and combined chronological log remain PRIVATE.
A temporal order is NOT by itself proof of complete natural mediation.
"""
import argparse,json,os,re
from pathlib import Path
from c3x_029_p42_r9_original_AB_neutralized_source_probe import verify_original_inputs
from c3x_023_P1_R2_T0_chronological_post_TT_common_SEE_dev import cold
from c3x_018_independent16_TT_value_transport_native import verified_reader_lineage
from c3x_027_game14_root_boundary_court import parse_boundary_lines
from c3x_029_p42_r11_native_cycle_alpha_window_court import RX
from c3x_029_p42_r12_native_single_cycle_event_court import (
    selected_ordinals,split_two_physical_plays,match_single_event)
from c3x_029_p42_r10_native_original_AB_draw_site_court import observed

TARGET=33

def physical_trace(raw,ordinal):
    lines=[s for s in raw.splitlines() if s.strip()]
    if not lines:
        raise ValueError('R13_HOLD_EMPTY_NATIVE_SOURCE_TRACE')
    single=split_two_physical_plays(lines)
    bp=parse_boundary_lines(lines)
    if bp['status']!='PASS_TWO_IDENTICAL_COLD_BOUNDARY_RUNS':
        raise ValueError('R13_HOLD_ORIGINAL_ROOT_BOUNDARIES_'+bp['status'])
    events=[]
    event33_line=None
    for idx,s in enumerate(single):
        if not s.startswith('c3x042_r11 '):
            continue
        m=RX.fullmatch(s)
        if not m:
            raise ValueError('R13_HOLD_MALFORMED_NATIVE_CYCLE_SOURCE_EVENT')
        key,ply,depth,mod,old,beta,cand,new,cut,root=map(int,m.groups())
        i=len(events)+1
        expected=0 if i==ordinal else -1+(mod&2)
        if cand!=expected or new!=cand or cut!=int(new>=beta):
            raise ValueError('R13_HOLD_SOURCE_RETURN_OR_CUTOFF_UNFAITHFUL')
        events.append({'key':key,'ply':ply,'depth':depth,'mod4':mod,
                       'old_alpha':old,'beta':beta,'candidate':cand,
                       'cutoff':cut,'root_move':root})
        if i==TARGET:event33_line=idx
    if event33_line is None:
        raise ValueError('R13_HOLD_TARGET33_NATIVE_EVENT_ABSENT')
    return {'events':events,'root_boundaries':bp['runs'][0],
            'first_trace':single,'target_source_line_index':event33_line}

def compare_temporal_source_root(original,changed):
    if match_single_event(original['events'],changed['events'],TARGET) != (
        'PASS_ACTUAL_ONE_SOURCE_EVENT_WITH_MATCHED_PREFIX'):
        return {'status':'HOLD_UNMATCHED_EXACT_SINGLE_EVENT_SOURCE'}
    if len(original['root_boundaries'])!=len(changed['root_boundaries']):
        return {'status':'HOLD_ROOT_BOUNDARY_DEPTH_SUPPORT_CHANGED',
                'old_depths':len(original['root_boundaries']),
                'new_depths':len(changed['root_boundaries'])}
    differences=[]
    first_leader=None
    for i,(o,n) in enumerate(zip(original['root_boundaries'],changed['root_boundaries'])):
        if o['depth']!=n['depth']:
            return {'status':'HOLD_ROOT_ITERATION_DEPTH_DRIFT'}
        changed_fields=[x for x in ('leader','score','average') if o[x]!=n[x]]
        if changed_fields:
            if 'leader' in changed_fields and first_leader is None:
                first_leader=o['depth']
            differences.append({'depth':o['depth'],'changed_fields':changed_fields,
                                'original_root_boundary':dict(o),
                                'target33_root_boundary':dict(n)})
    if not differences:
        return {'status':'HOLD_ROOT_BOUNDARY_NO_DIVERGENCE_DESPITE_MOVE_CHANGE'}
    first=differences[0]
    depth=first['depth']
    def position(trace):
        for idx,line in enumerate(trace['first_trace']):
            if 'event=ROOT_BOUNDARY' in line:
                fields=dict(re.findall(r'([A-Za-z_][A-Za-z0-9_]*)=([^\\s]+)',line))
                if fields.get('depth')==str(depth):
                    return idx
        return None
    old_pos=position(original)
    changed_pos=position(changed)
    if old_pos is None or changed_pos is None:
        return {'status':'HOLD_FIRST_DIVERGENT_ROOT_BOUNDARY_LINE_NOT_FOUND'}
    if (original['target_source_line_index']>=old_pos or
        changed['target_source_line_index']>=changed_pos):
        return {'status':'HOLD_ROOT_BOUNDARY_DIVERGED_BEFORE_SOURCE_EVENT',
                'first_difference_depth':depth}
    return {
      'status':'PASS_SINGLE_EVENT33_PRECEDES_FIRST_SOURCE_ROOT_BOUNDARY_DIVERGENCE_ONLY',
      'root_completed_depths':len(original['root_boundaries']),
      'first_changed_depth':depth,
      'first_changed_boundary':first,
      'first_changed_leader_depth':first_leader,
      'number_of_different_root_depth_boundaries':len(differences),
      'source_target_precedes_first_changed_root_boundary_in_both_worlds':True,
      'full_root_candidate_value_mediation_certified':False,
      'natural_TT_SEE_guard_mediation_certified':False,
      'strategic_chess_truth_certified':False,
      'prospective_holdout_certified':False
    }

def main():
    p=argparse.ArgumentParser()
    for name in ('source','stagea','forecast','engine','private','public-out'):
        p.add_argument('--'+name,required=True)
    a=p.parse_args()
    world,clock,physical,watch,filters=verify_original_inputs(a.source,a.stagea,a.forecast)
    priv=Path(a.private);priv.mkdir(parents=True,exist_ok=True)
    records={0:[],TARGET:[]}
    for ordinal in (0,TARGET):
        for rep in range(2):
            log=priv/(f'B_ordinal{ordinal}_cold{rep}_joint_timeline.txt')
            aux=priv/(f'B_ordinal{ordinal}_cold{rep}_r10_source_calls.txt')
            log.write_text('');aux.write_text('')
            before=os.environ.copy()
            os.environ['C3X027_GAME14_LINEAGE_LOG']=str(log.resolve())
            os.environ['C3X042_R11_CYCLE_WINDOW_TRACE']=str(log.resolve())
            os.environ['C3X042_R10_DRAW_SITE_TRACE']=str(aux.resolve())
            os.environ['C3X042_R10_NEUTRAL_DRAW_SITE']='0'
            if ordinal>0:os.environ['C3X042_R12_TARGET_ORDINAL']=str(ordinal)
            else:os.environ.pop('C3X042_R12_TARGET_ORDINAL',None)
            os.environ.pop('C3X042_R9_DRAW_PARITY_NEUTRAL',None)
            os.environ.pop('C3X042_R8_DROP_DESCENDANT_TT_SAVE',None)
            try:
                out=cold(a.engine,world,clock,'O','V',physical,filter=filters,watch=watch)
            finally:
                os.environ.clear();os.environ.update(before)
            if not verified_reader_lineage(out)['all_valid'] or not any(
                z.get('kind')=='reader_block' for z in out['blocks']):
                raise ValueError('R13_HOLD_B_PHYSICAL_TT_READER_NOT_PROVEN')
            source=physical_trace(log.read_text(),ordinal)
            r10=observed(aux.read_text(),0)
            if len(source['events'])*2 !=r10['1']['calls']:
                raise ValueError('R13_HOLD_TWO_PHYSICAL_SOURCES_COUNT_DIFFER')
            source['root_move']=out['UCI']['bestmove']
            records[ordinal].append(source)
    result={'schema':'c3x042-r13-source-cycle-event33-to-root-boundary-v1',
            'status':'HOLD','native_game14_postselected':True,
            'source_event_id':TARGET,'use_nnue':False,
            'unique_natural_mediation_certified':False,
            'strategic_chess_future_certified':False,
            'full_ancestor_value_mediation_certified':False,
            'private_source_keys_exposed':False}
    original=records[0];target=records[TARGET]
    if [x['root_move'] for x in original]!=['f3f4']*2 or [
        x['root_move'] for x in target]!=['b3a4']*2:
        result['status']='HOLD_R12_ROOT_CHOICES_NOT_REPRODUCED'
    elif selected_ordinals(original[0]['events'])!=[30,31,32,33] or [
        selected_ordinals(x['events']) for x in original]!=[[30,31,32,33]]*2:
        result['status']='HOLD_R12_FROZEN_FOUR_SELECTION_NOT_REPRODUCED'
    else:
        records_compare=[compare_temporal_source_root(original[i],target[i])
                         for i in range(2)]
        if any(not x['status'].startswith('PASS_') for x in records_compare):
            result['status']='HOLD_SOURCE_OR_ROOT_TIMELINE_INCONCLUSIVE'
            result['per_cold_status']=[x['status'] for x in records_compare]
        elif records_compare[0]!=records_compare[1]:
            result['status']='HOLD_NATIVE_ROOT_BOUNDARY_COLD_DIVERGENCE'
        else:
            result.update(records_compare[0])
            result['physical_cold_invocations']=2
            result['physical_engine_play_processes_per_cold']=2
            result['source_event33_root_actions']={'baseline':['f3f4','f3f4'],
                                                    'target33':['b3a4','b3a4']}
    target_path=Path(a.public_out)
    target_path.parent.mkdir(parents=True,exist_ok=True)
    target_path.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print('C3X042_R13_NATIVE_SOURCE33_TO_ROOT_BOUNDARY',result['status'])
    if not result['status'].startswith('PASS_'):raise SystemExit(2)
if __name__=='__main__':
    main()
