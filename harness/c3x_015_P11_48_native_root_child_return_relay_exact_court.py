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
 result['p9']={k:int(v) for k,v in typed('c3x015_p9_a1_intervention').items()}
 raw_p10=typed('c3x015_p10_root_lineage')
 result['p10']={k:(v if k=='stream' else int(v)) for k,v in raw_p10.items()}
 result['p11']={k:int(v) for k,v in typed('c3x015_p11_root_relay').items()}
 return result
def core(z):return {k:z[k] for k in CORE}
def main():
 ap=argparse.ArgumentParser()
 for name in ('source','targets','prior-p2','prior-p6','prior-p7','prior-p8','prior-p9a1','prior-p10','engine','out'):
  ap.add_argument('--'+name,required=True)
 a=ap.parse_args()
 src=load(a.source,SRC)
 frozen=load(a.targets,'0dd412cdfad82ea6b042dd3381e07182f2d4f3e52cd3e83c71004b6ecaed6ee1')
 load(a.prior_p2,P2)
 load(a.prior_p6,'c04ee3061835babb846fee54b269617da5ab809dc9efe46c1e6cbe9360fefa11')
 load(a.prior_p7,'01ea31dcb1d900925ff38ec3d6d5da4afe63bba6c87eccc2eb8563d9440d8c77')
 load(a.prior_p8,'bb2af016857dff393a6054bad2b2978d3ecb2d92c527891f578688e513452e22')
 load(a.prior_p9a1,'0a0a40d891af736491ecbfb92dee145c969b853d6e1ac43495beb202e905ec17')
 prior=load(a.prior_p10,'2d74c4edd45700b9ffcbb2763edc4dad94a5bee9f4590dc85d2295f6c38a1c45')
 result={'schema':'c3x015-P11-exact-ROOT-child-return-gate-two-case-48-native-v1',
     'status':'SOURCE_EXPOSED_TWO_WORLDS_NOT_INDEPENDENT_VALIDATION',
     'source_sha256':SRC,
     'P10_original_R2_sha256':'2d74c4edd45700b9ffcbb2763edc4dad94a5bee9f4590dc85d2295f6c38a1c45',
     'native_cold_processes':0,'sham_exact_P10_UCI_regressions':0,
     'worlds':[],'limits':['Artificial source relay at a frozen P10 root child-return contact, not TT natural-mediation necessity proof.',
         'Do not count same P6-disclosed cases as independent games or new prospective C3X016 strategy validation.']}
 for ordinal in (2,29):
  k=ordinal-1;root=src['pin_roots'][k]
  obj=root['objects'][0]
  sq=chess.parse_square(obj['pinned_square'])
  pn=chess.parse_square(obj['pinner_square'])
  prior_world=prior['cases'][0 if ordinal==2 else 1]
  fixed=frozen['all64_targets'][k]['target']
  history=root['full_history_uci'][:root['root_ply']]
  must(sha(root['root_sixfield_fen'].encode())==prior_world['source_fen_sha256'],'P11_SOURCE_FEN_DRIFT')
  row={'ordinal':ordinal,'root_FEN_sha256':prior_world['source_fen_sha256'],
       'cells':{},'effects':{}}
  for see in ('OFF','ROOT_OBJECT_SEE_UNMASK'):
   for regime in ('I','V','B'):
    old=prior_world['cells'][see+'__'+regime]
    for micro in ('SHAM','CLAMP'):
     os.environ['C3X015_P9_A1_MODE']='SHAM'
     os.environ['C3X015_P9_A1_CASE']=str(ordinal)
     os.environ['C3X015_P7_SCORE_MODE']='RETURN_ALPHA' if regime=='V' else 'IDENTITY'
     os.environ['C3X015_P11_ROOT_CLAMP']=micro
     physical='BLOCK_EXACT_ONCE' if regime=='B' else 'ALLOW'
     a1=trace(a.engine,history,see,sq,pn,fixed,physical)
     a2=trace(a.engine,history,see,sq,pn,fixed,physical)
     must(a1==a2,f'P11_COLD_NONREPRODUCIBLE_{ordinal}_{see}_{regime}_{micro}')
     result['native_cold_processes']+=2
     rel=a1['p11']
     expected=int(ordinal==2 and regime in ('V','B') and micro=='CLAMP')
     must(rel['requested']==int(micro=='CLAMP') and rel['fired']==expected,
          f'P11_SOURCE_CONTACT_EXACT_FAILURE_{ordinal}_{see}_{regime}_{micro}')
     if expected:must(rel['original']==(130 if regime=='V' else 0) and rel['replacement']==14,
                 'P11_WRONG_TARGET_NUMERIC_VALUE')
     if micro=='SHAM':
      must(core(a1)==old['UCI'],'P11_SHAM_CHANGED_PRIOR_P10_NATIVE_CORE')
      must(a1['p10']==old['root_event_trace'],'P11_SHAM_CHANGED_PRIOR_P10_TRACE')
      must(a1['p9']==old['micro_gates'],'P11_SHAM_CHANGED_PRIOR_P9_MICROCONTACT')
      result['sham_exact_P10_UCI_regressions']+=1
     old_event=old['root_event_trace']['stream'].rstrip('|').split('|')
     new_event=a1['p10']['stream'].rstrip('|').split('|')
     at=next((i for i in range(min(len(old_event),len(new_event))) if old_event[i]!=new_event[i]),None)
     if at is None and len(old_event)!=len(new_event):at=min(len(old_event),len(new_event))
     key=see+'__'+regime+'__'+micro
     row['cells'][key]={'UCI':core(a1),'root_relay_source':rel,
       'first_P10_root_trace_difference_index_from_unchanged_original':at,
       'original_P10_event':old_event[at] if at is not None and at<len(old_event) else None,
       'new_P11_event':new_event[at] if at is not None and at<len(new_event) else None,
       'root_events_seen':a1['p10']['seen'],'root_events_truncated':a1['p10']['truncated']}
     print('C3X015_P11_NATIVE',ordinal,see,regime,micro,'fired',rel['fired'],
       'move',a1['bestmove'],'score',a1['value_root_stm'],'nodes',a1['nodes'],
       'root_first_event_delta',at,flush=True)
    x=row['cells'][see+'__'+regime+'__SHAM']['UCI']
    y=row['cells'][see+'__'+regime+'__CLAMP']['UCI']
    row['effects'][see+'__'+regime]={
      'root_move_changed':x['bestmove']!=y['bestmove'],
      'reported_score_changed':(x['value_root_stm'],x['score_kind'],x['score_flag'])!=(y['value_root_stm'],y['score_kind'],y['score_flag']),
      'nodes_changed':x['nodes']!=y['nodes'],
      'first_root_PV_changed':x['pv']!=y['pv']}
  result['worlds'].append(row)
 must(result['sham_exact_P10_UCI_regressions']==12,'P11_EXPECT_12_SHAM_CONTROL_BASELINES')
 Path(a.out).write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
 print('C3X015_P11_48_NATIVE_FIXED_ROOT_VALUE_RELAY_SHAM_EXACT_GATES_PASS',flush=True)
if __name__=='__main__':main()
