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
 result['p9_a2']={k:int(v) for k,v in typed('c3x015_p9_a2_threshold').items()}
 return result
def core(z):return {k:z[k] for k in CORE}
def main():
 ap=argparse.ArgumentParser()
 for field in ('source','targets','prior-p9a1','engine','out'):
  ap.add_argument('--'+field,required=True)
 a=ap.parse_args()
 source=load(a.source,SRC)
 frozen=load(a.targets,'0dd412cdfad82ea6b042dd3381e07182f2d4f3e52cd3e83c71004b6ecaed6ee1')
 earlier=load(a.prior_p9a1,'0a0a40d891af736491ecbfb92dee145c969b853d6e1ac43495beb202e905ec17')
 assert len(earlier['cases'])==2
 cases=[];n=0;neg=0;pos=0
 for ordinal in (2,29):
  root=source['pin_roots'][ordinal-1]
  target=frozen['all64_targets'][ordinal-1]['target']
  obj=root['objects'][0]
  sq=chess.parse_square(obj['pinned_square'])
  pn=chess.parse_square(obj['pinner_square'])
  history=root['full_history_uci'][:root['root_ply']]
  oldcase=earlier['cases'][0 if ordinal==2 else 1]
  must(sha(root['root_sixfield_fen'].encode())==oldcase['source_fen_sha256'],
       'P9_A2_PRECOMMITTED_CHESS_WORLD_DRIFT')
  row={'ordinal':ordinal,'source_fen_sha256':oldcase['source_fen_sha256'],'cells':{}}
  for see in ('OFF','ROOT_OBJECT_SEE_UNMASK'):
   ref=oldcase['cells'][see+'__B']
   for threshold in (129,130,131):
    os.environ['C3X015_P7_SCORE_MODE']='IDENTITY'
    os.environ['C3X015_P9_A1_MODE']='SHAM'
    os.environ['C3X015_P9_A1_CASE']=str(ordinal)
    os.environ['C3X015_P9_A2_CHILD_VALUE']=str(threshold)
    os.environ['C3X015_P9_A2_CASE']=str(ordinal)
    cold=[trace(a.engine,history,see,sq,pn,target,'BLOCK_EXACT_ONCE') for _ in range(2)]
    n+=2
    must(cold[0]==cold[1],f'P9_A2_COLD_REPLAY_FAIL_{ordinal}_{see}_{threshold}')
    x=cold[0];b=x['p9_a2'];armkey=see+'__D'+str(threshold)
    must(x['p9']['mode']==0 and x['p9']['suppressed_beta_break']==0
      and x['p9']['suppressed_TT_write']==0 and x['p9']['clamped_local_return']==0,
      'P9_A1_UNRELATED_GATE_FIRED')
    must(x['p6s1']['suppressed']==1,'P9_A2_ORIGINAL_EXACT_TT_RETURN_NOT_BLOCKED')
    must(b['requested']==threshold and b['caseid']==ordinal,
      'P9_A2_EXPOSURE_REQUEST_NOT_COHERENT')
    must(b['contacts']<=1,'P9_A2_DOUBLE_EXPOSURE')
    if ordinal==2:
      must(b['contacts']==0,'P9_A2_WORLD2_SHAM_NOT_NULL')
      must(core(x)==ref['UCI'],'P9_A2_WORLD2_SHAM_ALTERED_BASELINE_UCI')
      neg+=1
    else:
      must(b['contacts']==1 and b['changes']==1 and b['first_original']==-59
        and b['substituted']==threshold and b['ply']==4 and b['move']==729,
        f'P9_A2_WORLD29_FIRST_CHILD_NOT_EXACT_{see}_{threshold}')
      pos+=1
    row['cells'][armkey]={'UCI':core(x),'target_source':x['p6s1'],
      'first_qchild_threshold':b,
      'root_depth':x['root_iteration'],
      'baseline_B_bestmove':ref['UCI']['bestmove'],
      'different_root_move_than_B':x['bestmove']!=ref['UCI']['bestmove'],
      'delta_nodes_vs_B':x['nodes']-ref['UCI']['nodes'],
      'last_beta_window':{'alpha':130,'beta':131}}
    print('C3X015_P9_A2_NATIVE',ordinal,see,threshold,
      'event',b['contacts'],'bm',x['bestmove'],'score',x['value_root_stm'],
      'nodes',x['nodes'],'original_B',ref['UCI']['bestmove'],flush=True)
  cases.append(row)
 result={'schema':'c3x015-P9-A2-RISR-first-qchild-alpha-beta-24native-v1',
    'status':'P9_A2_POST_P6_OUTCOME_ARTIFICIAL_SOURCE_BRANCH_THRESHOLD_ONLY',
    'P9_A1_original_sha256':'0a0a40d891af736491ecbfb92dee145c969b853d6e1ac43495beb202e905ec17',
    'original_source_r2_sha256':SRC,
    'native_processes':n,'cold_repeats_pairs':12,
    'target_world29_6_unique_arm_exposures':pos,
    'negative_world2_6_unique_null_arms':neg,
    'original_preselected_qsearch_child_return':-59,
    'artificial_test_values':[129,130,131],
    'cases':cases,
    'limits':['Artificial first-child score does not represent true chess evaluation',
      'Two outcome-disclosed chess source worlds, not new independent observations',
      'A threshold step may alter root choice without identifying original natural mediator',
      'P1 C1 overall accuracy 42/64 < trivial B0 53/64 remains FAIL',
      'TT/NNUE/strategy cross-provider transport remains unestablished']}
 Path(a.out).write_text(json.dumps(result,sort_keys=True,indent=2,ensure_ascii=False)+'\n')
 print('C3X015_P9_A2_SCORE_BOUNDARY_COURT_PASS',json.dumps(
  [{'ordinal':c['ordinal'],
   'selected':{k:{'bestmove':v['UCI']['bestmove'],'different_root':v['different_root_move_than_B']} for k,v in c['cells'].items()}}
   for c in cases],sort_keys=True),flush=True)
if __name__=='__main__':main()
