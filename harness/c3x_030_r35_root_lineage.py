"""Retrospective root competition lineage of frozen R34 R33-040 at depth 12.

Identifies the same-window first h3 leader loss in two different upstream
TT-gate treatments. This is *not* full node-level mediation identification.
"""
import argparse
import hashlib
import json
from pathlib import Path
from zipfile import ZipFile


def require(p, message):
    if not p:
        raise ValueError(message)


def records(raw, tag):
    result=[]
    for line in raw.decode('utf8').splitlines():
        if line.startswith(tag+' '):
            pairs=[chunk.split('=',1) for chunk in line.split()[1:]]
            require(all(len(pair)==2 for pair in pairs),'malformed '+tag)
            require(len({k for k,v in pairs})==len(pairs),'duplicate key in '+tag)
            result.append(dict(pairs))
    return result


def checked_manifest(z):
    seen=0
    for line in z.read('SHA256SUMS').decode().splitlines():
        sha,path=line.split('  ',1)
        require(hashlib.sha256(z.read(path)).hexdigest()==sha,'source SHA mismatch: '+path)
        seen+=1
    return seen


def one(z,stratum,repeat,expected_event):
    def log(arm):
        prefix=f'depth-a/R33-040/{stratum}/12/{arm}-{repeat}/'
        raw=z.read(prefix+'stderr.txt')
        result={k:records(raw,'C3X_R23_'+k) for k in ('START','CANDIDATE','END','BEST')}
        result.update({'open':records(raw,'C3X_R33_OPEN'),'close':records(raw,'C3X_R33_CLOSE')})
        require(len(result['BEST'])==1,'missing best')
        return result
    control=log('control');treated=log('both_off')
    def event(ar):
        op=[r for r in ar['open'] if r['event']==str(expected_event)]
        cl=[r for r in ar['close'] if r['event']==str(expected_event)]
        require(len(op)==len(cl)==1,'target event absent or duplicated')
        return op[0],cl[0]
    so,sc=event(control);mo,mc=event(treated)
    require(so==mo,'event identity changed before treatment')
    require(sc['skip_f']=='0' and mc['skip_f']=='1','futility target not masked')
    require(sc['value']!=mc['value'],'target direct return did not change')
    require(int(so['attempt'])<=24,'target treatment happened after shared window')
    for state in (control,treated):
        start=[r for r in state['START'] if r['attempt']=='24']
        require(len(start)==1,'no unique attempt 24')
        require({k:start[0][k] for k in ('iteration','adjusted','alpha','beta')}==
                {'iteration':'12','adjusted':'12','alpha':'367','beta':'407'},
                'attempt 24 did not preserve common 367-407 window')
    def candidates(state):
        return {int(r['count']):r for r in state['CANDIDATE'] if r['attempt']=='24'}
    s=candidates(control);m=candidates(treated)
    require(len(s)==len(m)==43,'incomplete root candidate census')
    comparable=[]
    for index in sorted(set(s)&set(m)):
        a,b=s[index],m[index]
        if all(a[k]==b[k] for k in ('move','alpha','beta','depth')):
            comparable.append({'index':index,'move':a['move'],'alpha':a['alpha'],
                               'base_value':int(a['value']),'treated_value':int(b['value']),
                               'base_update':a['update'],'treated_update':b['update']})
    require(any(row['index']==3 and row['move']=='h2h3' and row['base_value']==392
                and row['base_update']=='1' and row['treated_update']=='0'
                for row in comparable),'h3 did not lose active-leader update at matched window')
    h=next(row for row in comparable if row['index']==3)
    require((h['treated_value']==363 if stratum=='0' else h['treated_value']==367),'unknown h3 masked value')
    require(s[1]['move']==m[1]['move']=='d4b3','first root candidate identity diverged')
    last_ctrl=[x for x in control['END'] if x['attempt']=='24']
    last_treat=[x for x in treated['END'] if x['attempt']=='24']
    require(len(last_ctrl)==len(last_treat)==1,'attempt 24 did not close')
    require(last_ctrl[0]['move']=='h2h3' and last_treat[0]['move']=='d4b3','wrong end of shared window')
    retry=[x for x in treated['START'] if x['attempt']=='25']
    require(len(retry)==1 and (retry[0]['alpha'],retry[0]['beta'])==('341','387'),'wrong aspiration retry')
    t25=[x for x in treated['END'] if x['attempt']=='25']
    require(len(t25)==1 and t25[0]['move']=='a5c7','retry did not select Qxc7')
    require(control['BEST'][0]['move']=='h2h3' and treated['BEST'][0]['move']=='a5c7','final choice mismatch')
    return {
      'stratum':stratum,'repeat':repeat,'target_event':expected_event,
      'physical_read_key':so['key'],'event_root':so['root'],'event_candidate':so['candidate'],
      'event_attempt':int(so['attempt']), 'event_before':sc['value'], 'event_after':mc['value'],
      'matched_root_window':{'attempt':24,'iteration':12,'alpha':367,'beta':407},
      'first_same_window_score_change':next((x for x in comparable if x['base_value']!=x['treated_value']),None),
      'same_window_h3_competition':h,
      'base_attempt24_end':last_ctrl[0], 'treated_attempt24_end':last_treat[0],
      'treated_aspiration_retry_start':retry[0], 'treated_aspiration_retry_end':t25[0],
      'final_moves':[control['BEST'][0]['move'],treated['BEST'][0]['move']],
      'comparison_limit':'Physical upstream event -> shared-window candidate flip observed; intervening TT/history/write events not yet mapped',
    }


def audit(path):
    with ZipFile(path) as z:
        require(z.testzip() is None,'CRC failed')
        cnt=checked_manifest(z)
        results=[one(z,s,r,32 if s=='0' else 102) for s in ['0','1'] for r in [0,1]]
    for idx in (0,2):
        a,b=results[idx],results[idx+1]
        for k in a:
            if k!='repeat': require(a[k]==b[k],'replay discrepancy '+str(k))
    return {'category':'RETROSPECTIVE_R34_R33_040_SOURCE_TRANSPORT',
            'sha256_zip':hashlib.sha256(Path(path).read_bytes()).hexdigest(),
            'manifest_files_verified':cnt,'results':[results[0],results[2]],
            'observation':'Two different upstream mechanisms converge on lost h3 update in attempt 24 and Qxc7 in the new attempt 25',
            'unproven':'Exact intermediate state mediation between selected source event and h3 candidate; independent board superiority; human value'}


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('r34_zip',type=Path)
    ap.add_argument('output',type=Path)
    a=ap.parse_args()
    res=audit(a.r34_zip)
    a.output.write_text(json.dumps(res,indent=2,sort_keys=True,ensure_ascii=False)+'\n')
    print(json.dumps(res,indent=2,ensure_ascii=False)[:7000])

if __name__=='__main__':main()
