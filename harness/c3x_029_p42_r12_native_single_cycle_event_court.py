#!/usr/bin/env python3
"""R12 native exhaustive cutoff-changing single-event intervention on Game14 B.

Selection rule is FROZEN by R11's 33-event matched source-state prefix and
exact original candidate/beta relation, NOT by root outcome. All four selected
events are challenged independently, each twice in a clean native engine.
This is development Game14, not a random or prospective holdout.
"""
import argparse,json,os
from pathlib import Path
from c3x_029_p42_r9_original_AB_neutralized_source_probe import verify_original_inputs
from c3x_023_P1_R2_T0_chronological_post_TT_common_SEE_dev import cold
from c3x_018_independent16_TT_value_transport_native import verified_reader_lineage
from c3x_029_p42_r10_native_original_AB_draw_site_court import observed
from c3x_029_p42_r11_native_cycle_alpha_window_court import parse_events,compare_source_prefix

PREFIX_LIMIT=33
EXPECTED_CUTOFF_FLIPS=4
def selected_ordinals(baseline):
    if len(baseline)<PREFIX_LIMIT:
        raise ValueError('R12_HOLD_R11_PREFIX_NOT_PRESENT')
    eligible=[i for i,x in enumerate(baseline[:PREFIX_LIMIT],1)
              if (x['candidate']>=x['beta'])!=(0>=x['beta'])]
    if len(eligible)!=EXPECTED_CUTOFF_FLIPS:
        raise ValueError('R12_HOLD_R11_FROZEN_FOUR_LOCAL_CUTOFF_FLIPS_NOT_REPRODUCED')
    return eligible

def match_single_event(baseline,modified,ordinal):
    if ordinal<1 or len(modified)<ordinal or len(baseline)<ordinal:
        return 'HOLD_SINGLE_NATIVE_SOURCE_EVENT_MISSING'
    fields=('key','ply','depth','mod4','old_alpha','beta','root_move')
    for i in range(ordinal):
        x,y=baseline[i],modified[i]
        if any(x[k]!=y[k] for k in fields):
            return 'HOLD_PREINTERVENTION_NATIVE_SOURCE_IDENTITY_DRIFT'
        expected=0 if i+1==ordinal else x['candidate']
        if y['candidate']!=expected:
            return 'HOLD_INCORRECT_SOURCE_EVENT_MUTATION_SCOPE'
        if y['cutoff']!=int(expected>=y['beta']):
            return 'HOLD_INCORRECT_SINGLE_EVENT_CUTOFF'
    target=baseline[ordinal-1]
    if int(target['candidate']>=target['beta'])==int(0>=target['beta']):
        return 'HOLD_SOURCE_EVENT_NOT_A_FROZEN_CUTOFF_DISAGREEMENT'
    return 'PASS_ACTUAL_ONE_SOURCE_EVENT_WITH_MATCHED_PREFIX'

def summarize_court(baseline,probe,selected,reader_valid,baseline_reader_valid):
    report={
      'schema':'c3x042-r12-four-single-cycle-native-source-events-v1',
      'game14_postselected':True,'nnue_enabled':False,
      'natural_causal_mediation_certified':False,
      'true_chess_strategic_reason_certified':False,
      'single_event_source_to_root_path_certified':False,
      'prospective_generalization_certified':False,
      'source_keys_and_private_windows_disclosed':False
    }
    if not all(reader_valid) or not all(baseline_reader_valid):
        return dict(report,status='HOLD_NATIVE_TT_FIRST_READER_PROOF')
    if len(baseline)!=2 or any(x['move']!='f3f4' for x in baseline):
        return dict(report,status='HOLD_ORIGINAL_GAME14_B_COLD_BASELINE_DRIFT')
    try:
        original_eligible=[selected_ordinals(x['events']) for x in baseline]
    except ValueError as e:
        return dict(report,status=str(e))
    if original_eligible[0]!=original_eligible[1] or original_eligible[0]!=selected:
        return dict(report,status='HOLD_SOURCE_EVENT_SELECTION_COLD_DRIFT')
    detail=[]
    for ordnum in selected:
        if len(probe.get(ordnum,[]))!=2:
            return dict(report,status='HOLD_SINGLE_EVENT_COLD_REPLAY_MISSING')
        runs=[]
        for i,x in enumerate(probe[ordnum]):
            status=match_single_event(baseline[i]['events'],x['events'],ordnum)
            if not status.startswith('PASS_'):
                return dict(report,status=status,target_ordinal=ordnum)
            if not x['reader_valid']:
                return dict(report,status='HOLD_TARGETED_TT_READER_PROVENANCE')
            runs.append(x['move'])
        detail.append({'target_ordinal':ordnum,'native_bestmoves':runs,
                       'root_choice_changes':[m!='f3f4' for m in runs],
                       'cold_replay_root_choice_stable':runs[0]==runs[1],
                       'single_event_verified':[True,True]})
    return dict(report,status='PASS_FOUR_ORIGINAL_SINGLE_EVENT_SOURCE_INTERVENTIONS_ONLY',
                baseline_B_bestmove=['f3f4','f3f4'],
                selection_rule='all frozen first33 B original actual cycle windows where neutral draw changes immediate cutoff',
                selection_ordinals=selected,targets=detail,
                successful_single_event_root_restorations=sum(
                    d['native_bestmoves']==['b3a4','b3a4'] for d in detail),
                caveat='Source ordinal is unique within native cold process; a single-site intervention may alter downstream states; root action change alone is not a unique natural mediator.')

def main():
    p=argparse.ArgumentParser()
    for k in ('source','stagea','forecast','engine','private','public-out'):
        p.add_argument('--'+k,required=True)
    a=p.parse_args()
    world,clock,physical,watch,filters=verify_original_inputs(a.source,a.stagea,a.forecast)
    priv=Path(a.private);priv.mkdir(parents=True,exist_ok=True)
    def run(ordinal,trial,arm='B'):
        tag=f"{arm}_ordinal{ordinal}_cold{trial}"
        window=priv/(tag+'_windows.txt'); site=priv/(tag+'_sites.txt')
        window.write_text('');site.write_text('')
        before=os.environ.copy()
        os.environ['C3X042_R11_CYCLE_WINDOW_TRACE']=str(window.resolve())
        os.environ['C3X042_R10_DRAW_SITE_TRACE']=str(site.resolve())
        os.environ['C3X042_R10_NEUTRAL_DRAW_SITE']='0'
        if ordinal>0:os.environ['C3X042_R12_TARGET_ORDINAL']=str(ordinal)
        else:os.environ.pop('C3X042_R12_TARGET_ORDINAL',None)
        os.environ.pop('C3X042_R9_DRAW_PARITY_NEUTRAL',None)
        os.environ.pop('C3X042_R8_DROP_DESCENDANT_TT_SAVE',None)
        try:
            out=(cold(a.engine,world,clock,'O','OBS',watch=watch) if arm=='A'
                 else cold(a.engine,world,clock,'O','V',physical,filter=filters,watch=watch))
        finally:
            os.environ.clear();os.environ.update(before)
        # The original R11 parser requires globally unmodified parity values.
        # For targeted trial parse source events under the R11 strict grammar,
        # requiring exactly one deliberate deviation at the target ordinal.
        from c3x_029_p42_r11_native_cycle_alpha_window_court import RX
        lines=[line for line in window.read_text().splitlines()
               if line.startswith('c3x042_r11 ')]
        matches=RX.findall(window.read_text())
        if len(lines)!=len(matches):
            raise ValueError('R12_HOLD_INVALID_PRIVATE_NATIVE_WINDOW_LINE')
        events=[]
        for i,x in enumerate(matches,1):
            key,ply,depth,mod,old,beta,candidate,after,cut,root=map(int,x)
            expected=(0 if ordinal==i and ordinal>0 else -1+(mod&2))
            if candidate!=expected or after!=candidate or cut!=int(after>=beta):
                raise ValueError('R12_HOLD_NATIVE_SELECTED_SOURCE_RETURN_INCONSISTENT')
            events.append({'key':key,'ply':ply,'depth':depth,'mod4':mod,
                'old_alpha':old,'beta':beta,'candidate':candidate,
                'cutoff':cut,'root_move':root})
        calls=observed(site.read_text(),0)
        if len(events)!=calls['1']['calls']:
            raise ValueError('R12_HOLD_ORIGINAL_R10_R11_SOURCE_CALL_COUNT_DRIFT')
        rv=(bool(verified_reader_lineage(out)['all_valid'])
            and any(x.get('kind')=='reader_block' for x in out['blocks'])) if arm=='B' else True
        return {'move':out['UCI']['bestmove'],'events':events,'reader_valid':rv}
    baseline=[run(0,i) for i in range(2)]
    selected=selected_ordinals(baseline[0]['events'])
    probe={k:[run(k,i) for i in range(2)] for k in selected}
    report=summarize_court(baseline,probe,selected,
        [x['reader_valid'] for k in selected for x in probe[k]],
        [x['reader_valid'] for x in baseline])
    out=Path(a.public_out);out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
    print('C3X042_R12_SINGLE_NATIVE_ORIGINAL_CYCLE_EVENT_COURT',report['status'],
          [(x['target_ordinal'],x['native_bestmoves']) for x in report.get('targets',[])])
    if not report['status'].startswith('PASS_'):raise SystemExit(2)
if __name__=='__main__':
    main()
