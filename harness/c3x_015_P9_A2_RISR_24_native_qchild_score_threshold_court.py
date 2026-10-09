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
 result['p9a2']={k:int(v) for k,v in typed('c3x015_p9_a2_child_boundary').items()}
 return result
def core(z):return {k:z[k] for k in CORE}
def main():
 ap=argparse.ArgumentParser()
 for name in ('source','targets','prior-p2','prior-p6','prior-p7','prior-p8','prior-p9a1','engine','out'):
  ap.add_argument('--'+name,required=True)
 a=ap.parse_args()
 src=load(a.source,SRC)
 frozen=load(a.targets,'0dd412cdfad82ea6b042dd3381e07182f2d4f3e52cd3e83c71004b6ecaed6ee1')
 prior=load(a.prior_p9a1,'0a0a40d891af736491ecbfb92dee145c969b853d6e1ac43495beb202e905ec17')
 load(a.prior_p2,P2)
 load(a.prior_p6,'c04ee3061835babb846fee54b269617da5ab809dc9efe46c1e6cbe9360fefa11')
 load(a.prior_p7,'01ea31dcb1d900925ff38ec3d6d5da4afe63bba6c87eccc2eb8563d9440d8c77')
 load(a.prior_p8,'bb2af016857dff393a6054bad2b2978d3ecb2d92c527891f578688e513452e22')
 assert len(prior['cases'])==2 and len(src['pin_roots'])==64
 outputs=[];n=0
 for ordinal in (2,29):
  idx=ordinal-1;r=src['pin_roots'][idx]
  target=frozen['all64_targets'][idx]['target']
  hist=r['full_history_uci'][:r['root_ply']]
  obj=r['objects'][0]
  sq=chess.parse_square(obj['pinned_square'])
  pn=chess.parse_square(obj['pinner_square'])
  previous=prior['cases'][0 if ordinal==2 else 1]['cells']
  world={'ordinal':ordinal,'source_fen_sha256':sha(r['root_sixfield_fen'].encode()),
         'original_exact_TT_target':target,'cells':{}}
  for see in ('OFF','ROOT_OBJECT_SEE_UNMASK'):
   base=previous[see+'__B']['UCI']
   for score in (129,130,131):
    os.environ['C3X015_P9_A1_MODE']='SHAM'
    os.environ['C3X015_P9_A1_CASE']=str(ordinal)
    os.environ['C3X015_P9_A2_CHILD_VALUE']=str(score)
    os.environ['C3X015_P7_SCORE_MODE']='IDENTITY'
    z1=trace(a.engine,hist,see,sq,pn,target,'BLOCK_EXACT_ONCE')
    z2=trace(a.engine,hist,see,sq,pn,target,'BLOCK_EXACT_ONCE')
    n+=2
    must(z1==z2,f'P9A2_COLD_NOT_EXACT_{ordinal}_{see}_{score}')
    t=z1['p9a2']
    must(z1['p6s1']['suppressed']==1,'P9A2_EXACT_TT_RETURN_NOT_SUPPRESSED_ONCE')
    must(sum(z1['p9'][key] for key in ('suppressed_beta_break','suppressed_TT_write','clamped_local_return'))==0,
         'P9A2_OTHER_MICRO_INTERVENTION_OCCURRED')
    must(t['targetscore']==score and t['caseid']==ordinal,'P9A2_WRONG_ARM_CONTEXT')
    if ordinal==29:
     must(t['delivered']==1 and t['matched']>=1 and t['previous_score']==-59
        and t['substituted_score']==score and t['native_move']==729,
        f'P9A2_FIRST_CHILD_TARGET_DID_NOT_DELIVER_{ordinal}_{see}_{score}')
    else:
     must(t['delivered']==0 and t['matched']==0,'P9A2_WORLD2_MUST_BE_NO_CONTACT')
     must(core(z1)==base,'P9A2_WORLD2_NONCONTACT_CHANGED_PREVIOUS_B_OUTPUT')
    rootfirst=next((d for d in range(1,13) if
       z1['root_iteration'].get(d,{}).get('pv_first')!=
       previous[see+'__B']['root_iteration'].get(str(d),{}).get('pv_first')),None)
    world['cells'][see+'__'+str(score)]={'UCI':core(z1),
        'source_targeted_child_return':t,'root_first_PV_divergence_depth_from_B':rootfirst,
        'P8_source_event_count':z1['p8']['seen'],
        'alpha_beta_window_at_original_target':[130,131],
        'categorical_root_changed_from_B':core(z1)['bestmove']!=base['bestmove']}
    print('C3X015_P9A2',ordinal,see,'score',score,'bm',core(z1)['bestmove'],
         'firstPV',rootfirst,'delivered',t['delivered'],flush=True)
  world['threshold_outcomes']={}
  for score in (129,130,131):
   o=world['cells']['OFF__'+str(score)]['UCI']['bestmove']
   on=world['cells']['ROOT_OBJECT_SEE_UNMASK__'+str(score)]['UCI']['bestmove']
   world['threshold_outcomes'][str(score)]={'OFF':o,'SEE_ON':on,'SEE_flip':int(o!=on)}
  outputs.append(world)
 result={'schema':'c3x015-P9-A2-original-case2-case29-first-qchild-alpha-beta-boundary-24-native-v1',
  'research_generation':'C3X0.15','source_R2_sha256':SRC,
  'prior_P9_A1_48native_sha256':'0a0a40d891af736491ecbfb92dee145c969b853d6e1ac43495beb202e905ec17',
  'native_searches':n,'distinct_source_worlds':2,'scopes':['P9_A2_POST_P6_DISCLOSURE_MECHANISM','CASE2_NO_CONTACT_NEGATIVE','CASE29_EXACT_CHILD_SCORE_BOUNDARY_ARTIFICIAL','P1_C1_ORIGINAL_ACCURACY_FAIL_UNCHANGED'],
  'worlds':outputs}
 Path(a.out).write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
 print('C3X015_P9_A2_24_NATIVE_FIRST_CHILD_THRESHOLD_COURT_SCOPED_PASS',flush=True)
if __name__=='__main__':main()
