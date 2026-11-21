"""C3X 0.30 R33: retrospective, fail-closed public-vs-native causal trace audit.

Takes the R29 and R30 original *ZIP* archives, never mutates prior receipts.
The unit of the experiment is a matched intervention, not a distinct game.
This audit must not be described as prospective or as a mediation proof.
"""
from __future__ import annotations
import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import re
from zipfile import ZipFile


READ_DYNAMIC = {"mask", "mask_move", "mask_value", "effective", "effective_value"}


def require(test, reason):
    if not test:
        raise ValueError(reason)


def stable_read(r):
    return {k: v for k, v in r.items() if k not in READ_DYNAMIC}


def public_signature(raw):
    """What an engine GUI can infer from depth, score/bound and PV only.

    Must ignore time, nodes, speed, seldepth, hashfull, probe flags.
    """
    result = []
    for line in raw.decode('utf-8').splitlines():
        fields = line.split()
        if len(fields) < 2 or fields[:2] != ['info', 'depth']:
            continue
        require('score' in fields and 'pv' in fields, 'incomplete info line')
        def after(token):
            require(token in fields and len(fields)>fields.index(token)+1, 'missing '+token)
            return fields[fields.index(token)+1]
        k = fields.index('score')
        pv = fields.index('pv')
        # Score type/value and full PV are part of GUI evidence; not exact cp if bound.
        result.append({'depth': int(after('depth')),
                       'multipv':int(after('multipv')) if 'multipv' in fields else 1,
                       'score_type': fields[k+1], 'score_value': int(fields[k+2]),
                       'bound': 'lower' if 'lowerbound' in fields else 'upper' if 'upperbound' in fields else 'exact',
                       'pv': fields[pv+1:]})
    require(result, 'no public search lines')
    return result


def unpack(archive, file):
    return archive.read(file)


def baseline_path(cohort, case):
    if cohort=='R29':
        return f'unseen-logs/{case}/sham/stdout.txt'
    return f'discover/{case}/baseline/stdout.txt'


def mask_path(cohort, case, policy):
    prefix = 'unseen-logs' if cohort=='R29' else 'masks'
    channel = ('move' if policy=='move' else 'value' if policy=='value' else 'fallback')
    return f'{prefix}/{case}/{channel}-mask/stdout.txt'


def inspect_case(cohort, case, policy, arms, zipreader):
    require(set(arms)=={'sham','mask','restore'},'missing sham-mask-restore: '+case['id'])
    s,m,r= (arms[key] for key in ('sham','mask','restore'))
    require({k:v for k,v in r.items() if k!='uci_changed'}==s,'restore mismatch: '+case['id'])
    require(stable_read(s['read']) == stable_read(m['read']), 'pre-treatment read mismatch: '+case['id'])
    require(s['read']['mask']=='0' and m['read']['mask']=='1','mask flag mismatch: '+case['id'])
    require(len(s['masked'])==0 and len(m['masked'])==1,'not exactly one read masked: '+case['id'])
    read=m['read']
    require(int(read['attempt']) <= int(case['source_attempt']),'event after producer: '+case['id'])
    for f in ('id','source','stratum','source_attempt'):
        require(f in case,'position missing '+f)
    child_s,child_m=s['direct_child'],m['direct_child']
    child_comparable=False
    if isinstance(child_s,dict) and isinstance(child_m,dict):
        keys=('attempt','candidate_next','root','stage')
        child_comparable=all(child_s.get(k)==child_m.get(k) for k in keys) and child_s.get('stopped')==child_m.get('stopped')=='0'
    child_changed=(child_s.get('child_value')!=child_m.get('child_value')) if child_comparable else None
    c_s,c_m=s['target_candidate'],m['target_candidate']
    candidate_comparable=isinstance(c_s,dict) and isinstance(c_m,dict) and all(c_s.get(k)==c_m.get(k) for k in ('attempt','move','alpha','beta','depth'))
    local_update_changed = (c_s['update'] != c_m['update']) if candidate_comparable else None
    candidate_value_changed = (c_s['value'] != c_m['value']) if candidate_comparable else None
    producer_changed = (s['producer']['attempt'],s['producer']['id'])!=(m['producer']['attempt'],m['producer']['id'])
    producer_attempt_changed = s['producer']['attempt']!=m['producer']['attempt']
    final_changed = s['best']['move'] != m['best']['move']
    baseline_raw=unpack(zipreader,baseline_path(cohort,case['id']))
    mask_raw=unpack(zipreader,mask_path(cohort,case['id'],policy))
    public_s=public_signature(baseline_raw)
    public_m=public_signature(mask_raw)
    restore_raw=unpack(zipreader,mask_path(cohort,case['id'],policy).replace('-mask/', '-restore/'))
    require(public_signature(restore_raw)==public_s, 'public restoration mismatch')
    def recorded_best(raw):
        moves=[line.split()[1] for line in raw.decode('utf-8').splitlines() if line.startswith('bestmove ')]
        require(len(moves)==1, 'missing or duplicate bestmove')
        return moves[0]
    require(recorded_best(baseline_raw)==s['best']['move'],'baseline bestmove mismatch')
    require(recorded_best(mask_raw)==m['best']['move'],'masked bestmove mismatch')
    require(recorded_best(restore_raw)==s['best']['move'],'restored bestmove mismatch')
    # Check the baseline's final move and score against the original receipt.
    src_last=public_s[-1]
    receipt_last=s['last_report']['public']
    require(src_last['score_type']==receipt_last['kind'] and src_last['score_value']==int(receipt_last['score']), 'inconsistent public score: '+case['id']+':'+policy)
    require(src_last['bound']==({'none':'exact','lower':'lower','upper':'upper'}.get(receipt_last['bound'])), 'inconsistent public bound: '+case['id']+':'+policy)
    changed_last_card = public_s[-1]!=public_m[-1] or final_changed
    mask_last=m['last_report']['public']
    require(public_m[-1]['score_type']==mask_last['kind'] and public_m[-1]['score_value']==int(mask_last['score']), 'inconsistent masked score')
    require(public_m[-1]['bound']=={'none':'exact','lower':'lower','upper':'upper'}.get(mask_last['bound']), 'inconsistent masked bound')
    candidate_set={case['source']['recommendation'],case['source']['alternative']}
    new_move=m['best']['move']
    judge=case['source']['judge']
    judge_coverage=all(new_move in row.get('measurements',{}) for row in judge.get('rows',[]))
    # Independent judge may be inconclusive, and has no licensed claim on unscored third moves.
    # Re-evaluate source reports, the original comparison may miss PV changes.
    return {
      'id':case['id'],'cohort':cohort,'stratum':case['stratum'],'policy':policy,
      'event_attempt':int(s['read']['attempt']),'producer_attempt':int(case['source_attempt']),
      'event_in_original_producer':int(s['read']['attempt'])==int(case['source_attempt']),
      'first_reply_changed':s['replies'][:1]!=m['replies'][:1],
      'direct_child_return_changed':child_changed,
      'root_candidate_same_window':candidate_comparable,
      'root_candidate_return_changed':candidate_value_changed,
      'root_candidate_leader_update_changed':local_update_changed,
      'producer_changed':producer_changed,'producer_attempt_changed':producer_attempt_changed,
      'final_recommendation_changed':final_changed,
      'final_bestmove':{'before':s['best']['move'],'after':m['best']['move']},
      'position_fen':case['source']['fen'],
      'reference_pair':{'recommendation':case['source']['recommendation'],'alternative':case['source']['alternative']},
      'post_intervention_third_move':final_changed and new_move not in candidate_set,
      'post_intervention_independent_judge_coverage':judge_coverage,
      'independent_reference_judge_label':judge['label'],
      'reference_pair_independent_margins_cp':[row['margin_cp'] for row in judge.get('rows',[])],
      'public_pv_score_trajectory_changed': public_s!=public_m,
      'public_last_card_changed':changed_last_card,
      'public_score_pv_same':public_s==public_m and not final_changed,
      'changed_child_invisible_in_score_pv':child_changed is True and public_s==public_m and not final_changed,
      'child_changed_but_final_move_stable':child_changed is True and not final_changed,
      'local_leader_changed_but_final_move_stable':local_update_changed is True and not final_changed,
      'public_depths': [len(public_s),len(public_m)],
      'terminal_native_score': [receipt_last['score'], m['last_report']['public']['score']],
      'terminal_native_bound': [receipt_last['bound'],m['last_report']['public']['bound']],
      'explanation_permission':('causal_final_choice_effect; mediation not established' if final_changed else
                                  'local_search_effect_only' if child_changed is True else
                                  'no_observed_child_effect' if child_changed is False else 'child_effect_unobserved'),
    }


def verify_manifest(archive, manifest):
    rows=archive.read(manifest).decode('utf-8').splitlines()
    checked=0
    for row in rows:
        match=re.fullmatch(r'([0-9a-f]{64})  (.+)',row)
        require(match is not None,'malformed SHA-256 manifest')
        require(hashlib.sha256(archive.read(match.group(2))).hexdigest()==match.group(1),
                'broken source archive SHA-256: '+match.group(2))
        checked+=1
    return checked


def audit(cohort, archive):
    main_path=('unseen-logs/result.json' if cohort=='R29' else 'masks/result.json')
    manifest='SHA256SUMS' if cohort=='R29' else 'COHORT-SHA256SUMS'
    checked=verify_manifest(archive,manifest)
    raw=archive.read(main_path)
    j=json.loads(raw)
    positions=j['positions']
    require(len(positions)==32, 'unexpected cohort size')
    require(len({c['id'] for c in positions})==32,'duplicate position IDs')
    rows=[]
    for c in positions:
        for policy,arms in c['arms'].items():
            require(policy in {'move','value','fallback'},'unrecognized policy')
            rows.append(inspect_case(cohort,c,policy,arms,archive))
    return rows,{'manifest':manifest,'manifest_files_verified':checked,'file':main_path,'sha256':hashlib.sha256(raw).hexdigest(),'positions':len(positions),
                 'tested_positions':sum(bool(c['arms']) for c in positions),
                 'no_selected_event':sum(not bool(c['arms']) for c in positions)}


def summarize(rows):
    out={}
    keys=['first_reply_changed','direct_child_return_changed','root_candidate_return_changed',
          'root_candidate_leader_update_changed','producer_changed','producer_attempt_changed','final_recommendation_changed',
          'post_intervention_third_move',
          'public_pv_score_trajectory_changed','public_last_card_changed','public_score_pv_same',
          'changed_child_invisible_in_score_pv','child_changed_but_final_move_stable',
          'local_leader_changed_but_final_move_stable']
    def summary(rr):
        d={'interventions':len(rr),'positions':len({x['id'] for x in rr})}
        for key in keys:
            d[key]=sum(row[key] is True for row in rr)
            d[key+'_unobserved']=sum(row[key] is None for row in rr)
        d['event_in_producer']=sum(row['event_in_original_producer'] for row in rr)
        d['same_alpha_candidate_pairs']=sum(row['root_candidate_same_window'] for row in rr)
        return d
    out['all']=summary(rows)
    for cohort in sorted({r['cohort'] for r in rows}):
        rr=[r for r in rows if r['cohort']==cohort]
        out[cohort]=summary(rr)
        out[cohort+'_policies']={p:summary([r for r in rr if r['policy']==p]) for p in sorted({r['policy'] for r in rr})}
    return out


def run(p29,p30):
    with ZipFile(p29) as a,ZipFile(p30) as b:
        require(a.testzip() is None and b.testzip() is None, 'archive CRC mismatch')
        r29,meta29=audit('R29',a)
        r30,meta30=audit('R30',b)
    rows=r29+r30
    return {'protocol':'C3X 0.30 R33 retrospective paired engine-event audit v1',
            'claims':['No prospective/generalizable effect probability','No proof of event-to-root mediation',
                      'Alpha-beta bounds are not calibrated point estimates',
                      'Visibility means ONLY depth, score/bound, PV and bestmove; node counts, time and NPS excluded',
                      'A logged root update is an active-leader event, not necessarily a final rank'],
            'source':{'R29':dict(meta29,zip_sha256=hashlib.sha256(Path(p29).read_bytes()).hexdigest()),
                      'R30':dict(meta30,zip_sha256=hashlib.sha256(Path(p30).read_bytes()).hexdigest())},
            'counts':summarize(rows),'rows':rows}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('r29',type=Path)
    parser.add_argument('r30',type=Path)
    parser.add_argument('out',type=Path)
    args=parser.parse_args()
    output=run(args.r29,args.r30)
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(output,ensure_ascii=False,indent=2,sort_keys=True)+'\n')
    print(json.dumps(output['counts'],indent=2))

if __name__=='__main__':main()
