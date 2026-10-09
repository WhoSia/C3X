#!/usr/bin/env python3
"""CSWP P3: post-outcome native first eligible SEE and search-frame window audit.
Uses frozen P2 source/results; never repurpose it as prospective prediction.
"""
import argparse,hashlib,json,os,re,subprocess
from pathlib import Path
import chess
from c3x_014_ROOT_PIN_object_guarded_SEE_40world_native_court import main_engine
SRC='1e932aa881eaef549c770211c078d930cd8d675e5688644e1bc36ab31bae4534'
P2='e930f0b489301c656690d09f4821583a28eead04e43382b545bda35b71279256'
CORE=('score_kind','value_root_stm','score_flag','nodes','pv','bestmove')
def sha(b):return hashlib.sha256(b).hexdigest()
def must(ok,msg):
 if not ok:raise RuntimeError(msg)
def load(p,expected):
 b=Path(p).read_bytes();must(sha(b)==expected,'SOURCE_SHA_FAIL_'+p);return json.loads(b)
def trace(engine,hist,arm,sq,pn,target,regime):
 env={**os.environ,'C3X014_PIN_ROOT_OBJECT_ARM':arm,'C3X014_PIN_ROOT_SQUARE_ID':str(sq),
      'C3X014_PIN_ROOT_PINNER_ID':str(pn),
      'C3X015_P6S1_MODE':regime,
      'C3X015_P6S1_TARGET_FULLKEY':str(target['key']),
      'C3X015_P6S1_TARGET_SLOT':str(target['slot_offset']),
      'C3X015_P6S1_TARGET_TAG':str(target['writer_tag']),
      'C3X015_P6S1_TARGET_BOUND':str(target['stored_bound']),
      'C3X015_P6S1_TARGET_DEPTH':str(target['stored_depth']),
      'C3X015_P6S1_TARGET_WRITESEQ':str(target['writer_seq']),
      'C3X015_P6S1_TARGET_ALPHA':str(target['alpha']),
      'C3X015_P6S1_TARGET_BETA':str(target['beta']),
      'C3X015_P6S1_TARGET_CDEPTH':str(target['consumer_depth']),
      'C3X015_P6S1_TARGET_PLY':str(target['ply']),
      'C3X015_P6S1_TARGET_KIND':str(target['node_type'])}
 lines=[]
 with subprocess.Popen([engine],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,
                       text=True,bufsize=1,env=env) as p:
  def send(*cmd):p.stdin.write('\n'.join(cmd)+'\n');p.stdin.flush()
  def read(prefix):
   for _ in range(200000):
    s=p.stdout.readline();must(s,'UCI_EOF_'+prefix)
    lines.append(s.rstrip())
    if s.startswith(prefix):return
   raise RuntimeError('UCI_LINES_BOUNDED')
  send('uci');read('uciok')
  send('setoption name Threads value 1','setoption name Hash value 16','setoption name MultiPV value 1',
       'setoption name Use NNUE value false','ucinewgame','isready');read('readyok')
  send('position startpos moves '+' '.join(hist),'go depth 12');read('bestmove ')
  send('quit');must(p.wait(timeout=30)==0,'NATIVE_EXIT_FAIL')
 depth=[]
 for line in lines:
  if not line.startswith('info depth ') or ' pv ' not in line:continue
  d=re.search(r'\bdepth (\d+)',line);sc=re.search(r'\bscore (cp|mate) (-?\d+)(?: (lowerbound|upperbound))?(?:\s|$)',line)
  nodes=re.search(r'\bnodes (\d+)',line)
  if d and int(d.group(1))==12 and sc and nodes:depth.append(dict(score_kind=sc.group(1),value_root_stm=int(sc.group(2)),
   score_flag=sc.group(3) or 'exact_reported',nodes=int(nodes.group(1)),pv=line.split(' pv ',1)[1].split()[:16]))
 must(depth,'DEPTH12_MISSING');result=depth[-1]
 b=[s.split()[1] for s in lines if s.startswith('bestmove ')]
 must(len(b)==1 and b[0]==result['pv'][0],'BESTMOVE_NOT_VALID');result['bestmove']=b[0]
 def typed(pre):
  rows=[s for s in lines if s.startswith('info string '+pre+' ')]
  must(len(rows)==1,'TRACE_MISSING_'+pre)
  return {k:v for k,v in (w.split('=',1) for w in rows[0].split()[3:])}
 result['guard']={k:int(v) for k,v in typed('c3x014_root_object_see').items()}
 win=typed('c3x015_first_site_window')
 result['window']={k:(v if k=='stream' else int(v)) for k,v in win.items()}
 result['p6s0']={k:int(v) for k,v in typed('c3x015_p6s0_target').items()}
 result['p6s1']={k:int(v) for k,v in typed('c3x015_p6s1_target_intervention').items()}
 result['p7']={k:int(v) for k,v in typed('c3x015_p7_return_score').items()}
 p8=typed('c3x015_p8_qsearch_trace')
 result['p8']={k:(v if k=='stream' else int(v)) for k,v in p8.items()}
 perdepth={}
 for line in lines:
  if not line.startswith('info depth ') or ' pv ' not in line:continue
  match=re.search(r'\bdepth (\d+)',line)
  if match:
   sc=re.search(r'\bscore (cp|mate) (-?\d+)',line)
   perdepth[int(match.group(1))]={'pv_first':line.split(' pv ',1)[1].split()[0],
      'value':int(sc.group(2)) if sc else None}
 result['root_iteration']=perdepth
 return result
def core(z):return {k:z[k] for k in CORE}
def main():
 ap=argparse.ArgumentParser()
 for k in ('source','targets','prior-p2','prior-p6','prior-p7','engine','out'):
  ap.add_argument('--'+k,required=True)
 a=ap.parse_args()
 raw=load(a.source,SRC)
 p2=load(a.prior_p2,P2)
 p6=load(a.prior_p6,'c04ee3061835babb846fee54b269617da5ab809dc9efe46c1e6cbe9360fefa11')
 p7=load(a.prior_p7,'01ea31dcb1d900925ff38ec3d6d5da4afe63bba6c87eccc2eb8563d9440d8c77')
 frozen=load(a.targets,'0dd412cdfad82ea6b042dd3381e07182f2d4f3e52cd3e83c71004b6ecaed6ee1')
 cases=[]
 for ordinal in (2,29):
  j=ordinal-1
  root=raw['pin_roots'][j]; prior=p7['cases'][0 if ordinal==2 else 1]
  obj=root['objects'][0];t=frozen['all64_targets'][j]['target']
  sq=chess.parse_square(obj['pinned_square']);pn=chess.parse_square(obj['pinner_square'])
  hist=root['full_history_uci'][:root['root_ply']]
  must(sha(root['root_sixfield_fen'].encode())==prior['root_fen_sha256'],'FROZEN_ROOT_DRIFT')
  row={'ordinal':ordinal,'root_fen_sha256':prior['root_fen_sha256'],
       'frozen_TT_target':t,'cells':{}}
  for see in ('OFF','ROOT_OBJECT_SEE_UNMASK'):
   for mode in ('IDENTITY','RETURN_ALPHA','BLOCK_EXACT_ONCE'):
    os.environ['C3X015_P7_SCORE_MODE']='RETURN_ALPHA' if mode=='RETURN_ALPHA' else 'IDENTITY'
    p6mode='BLOCK_EXACT_ONCE' if mode=='BLOCK_EXACT_ONCE' else 'ALLOW'
    cold=[trace(a.engine,hist,see,sq,pn,t,p6mode) for _ in range(2)]
    must(cold[0]==cold[1],f'P8_COLD_TRACE_REPLAY_FAILED_{ordinal}_{see}_{mode}')
    z=cold[0]
    key=see+'__'+mode
    oldcell=prior['cells'][key]
    must(core(z)==oldcell['UCI'],f'P8_OBSERVER_ALTERED_P7_CORE_{ordinal}_{key}')
    must(z['p6s1']==oldcell['p6s1'],f'P8_OBSERVER_ALTERED_SOURCE_TARGET_{ordinal}_{key}')
    must(z['p7']==oldcell['p7_value'],f'P8_OBSERVER_ALTERED_VALUE_DELIVERY_{ordinal}_{key}')
    p8=z['p8']
    must(p8['marks']>0 and p8['target_key']==int(t['key']) and p8['target_ply']==int(t['ply']),
         f'P8_PHYSICAL_TT_TARGET_NOT_FOUND_{ordinal}_{key}')
    stream=p8['stream'].rstrip('|').split('|') if p8['stream'] else []
    parsed=[]
    for e in stream:
     cells=e.split(':');must(len(cells)==7,'P8_INVALID_EVENT_ENCODING')
     parsed.append({'key_hex':cells[0], 'ply':int(cells[1]),
       'kind':int(cells[2]),'alpha':int(cells[3]),'beta':int(cells[4]),
       'score':int(cells[5]),'move_id':int(cells[6])})
    must(p8['listed']==len(parsed),'P8_EVENT_COUNT_MISMATCH')
    same_target=[e for e in parsed if int(e['key_hex'],16)==int(t['key']) and e['ply']==int(t['ply'])]
    continued=any(e['kind']==3 for e in same_target)
    must(continued==(mode=='BLOCK_EXACT_ONCE'),f'P8_TARGET_QSEARCH_CONTINUATION_MISMATCH_{ordinal}_{key}')
    tags={}
    for e in parsed:tags[str(e['kind'])]=tags.get(str(e['kind']),0)+1
    row['cells'][key]={'UCI':core(z),'root_depth':z['root_iteration'],
      'target_microevents':same_target,
      'microevent_type_counts':tags,
      'first_100_post_match_microevents':parsed[:100],
      'trace_limits':{'recorded':p8['listed'],'observed':p8['seen'],'truncated':p8['truncated']},
      'target_qsearch_continued':continued,
      'TT_value_delivery':z['p7']}
    print('C3X015_P8_NATIVE',ordinal,key,'bestmove',z['bestmove'],
      'target_qsearch_continued',int(continued),
      'q_events',p8['listed'],'truncated',p8['truncated'],flush=True)
  r={}
  for see in ('OFF','ROOT_OBJECT_SEE_UNMASK'):
   a0=row['cells'][see+'__IDENTITY']['root_depth']
   for mode in ('RETURN_ALPHA','BLOCK_EXACT_ONCE'):
    a1=row['cells'][see+'__'+mode]['root_depth']
    at=next((d for d in range(1,13) if a0.get(d,{}).get('pv_first')!=a1.get(d,{}).get('pv_first')),None)
    r[see+'__'+mode]={'first_root_pv_choice_difference_depth':at,
      'baseline_depth12_bestmove':row['cells'][see+'__IDENTITY']['UCI']['bestmove'],
      'treatment_depth12_bestmove':row['cells'][see+'__'+mode]['UCI']['bestmove']}
  row['root_pv_lineage_first_differences']=r
  cases.append(row)
 result={'schema':'c3x015-P8-SF16-qsearch-microevent-plus-root-depth-PV-2cases-24native-v1',
   'original_P7_sha256':'01ea31dcb1d900925ff38ec3d6d5da4afe63bba6c87eccc2eb8563d9440d8c77',
   'original_P6_SHA256':'c04ee3061835babb846fee54b269617da5ab809dc9efe46c1e6cbe9360fefa11',
   'P7_source_rights':'TWIC raw PGN not redistributed',
   'scope':'POST_OUTCOME_TWO_CASE_CHRONOLOGICAL_OBSERVER_NOT_CAUSAL_MEDIATION_PROOF',
   'new_native_processes':24,'cold_conditions_exact':12,'P7_behavioural_regression_exact':12,
   'cases':cases,'notes':['qsearch microevents logged only after exact full64 TT target first encounter',
    'target-event match and continuation checked for every SEE arm and mode',
    'only first 100 event rows per condition retained in compact JSON plus complete count summary',
    'ROOT PV depth changes show chronology, not necessary causal edge',
    'original published TWIC PGN ZIP is not present in this Actions artifact']}
 Path(a.out).write_text(json.dumps(result,sort_keys=True,indent=2,ensure_ascii=False)+'\n')
 print('C3X015_P8_QSEARCH_MICROEVENT_PLUS_ROOT_PV_NATIVE_SCOPED_PASS',flush=True)
if __name__=='__main__':main()
