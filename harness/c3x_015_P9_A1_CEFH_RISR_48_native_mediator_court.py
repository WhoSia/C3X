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
 return result
def core(z):return {k:z[k] for k in CORE}
def main():
 ap=argparse.ArgumentParser()
 for n in ('source','targets','prior-p2','prior-p6','prior-p7','prior-p8','engine','out'):
  ap.add_argument('--'+n,required=True)
 a=ap.parse_args()
 src=load(a.source,SRC)
 p2=load(a.prior_p2,P2)
 p6=load(a.prior_p6,'c04ee3061835babb846fee54b269617da5ab809dc9efe46c1e6cbe9360fefa11')
 p7=load(a.prior_p7,'01ea31dcb1d900925ff38ec3d6d5da4afe63bba6c87eccc2eb8563d9440d8c77')
 p8=load(a.prior_p8,'bb2af016857dff393a6054bad2b2978d3ecb2d92c527891f578688e513452e22')
 t=load(a.targets,'0dd412cdfad82ea6b042dd3381e07182f2d4f3e52cd3e83c71004b6ecaed6ee1')
 cases=[];observed=0;original_regression=0
 for ordinal in (2,29):
  j=ordinal-1;root=src['pin_roots'][j]
  fixed=t['all64_targets'][j]['target']
  prior=p8['cases'][0 if ordinal==2 else 1]
  obj=root['objects'][0]
  sq=chess.parse_square(obj['pinned_square'])
  pn=chess.parse_square(obj['pinner_square'])
  hist=root['full_history_uci'][:root['root_ply']]
  must(sha(root['root_sixfield_fen'].encode())==prior['root_fen_sha256'],'P9_PRE_FROZEN_WORLD_FEN_DRIFT')
  rows={'ordinal':ordinal,'source_fen_sha256':prior['root_fen_sha256'],
        'frozen_physical_TT_target':fixed,'cells':{},'root_categorical_effect':{}}
  for see in ('OFF','ROOT_OBJECT_SEE_UNMASK'):
   for mode in ('I','V','B','G','W','L'):
    oldmode={'I':'IDENTITY','V':'RETURN_ALPHA','B':'BLOCK_EXACT_ONCE'}.get(mode)
    os.environ['C3X015_P7_SCORE_MODE']='RETURN_ALPHA' if mode=='V' else 'IDENTITY'
    os.environ['C3X015_P9_A1_MODE']={'I':'SHAM','V':'SHAM','B':'SHAM','G':'G_BREAK','W':'W_SAVE','L':'L_CLAMP'}[mode]
    os.environ['C3X015_P9_A1_CASE']=str(ordinal)
    p6mode='ALLOW' if mode in ('I','V') else 'BLOCK_EXACT_ONCE'
    cold=[trace(a.engine,hist,see,sq,pn,fixed,p6mode) for _ in range(2)]
    observed+=2
    must(cold[0]==cold[1],f'P9_NONDETERMINISTIC_NATIVE_COLD_{ordinal}_{see}_{mode}')
    z=cold[0]
    must(z['p9']['caseid']==ordinal,'P9_CASEID_MISMATCH')
    must(z['p9']['suppressed_beta_break']<=1
      and z['p9']['suppressed_TT_write']<=1
      and z['p9']['clamped_local_return']<=1,
      'P9_MORE_THAN_ONE_MICRO_EVENT_INTERVENTION')
    counts={k:z['p9'][k] for k in ('suppressed_beta_break','suppressed_TT_write','clamped_local_return')}
    gates=sum(counts.values())
    must(gates<=1,'P9_MULTIPLE_GATES_IN_SINGLE_RUN')
    if oldmode is not None:
      previous=prior['cells'][see+'__'+oldmode]
      must(core(z)==previous['UCI'],f'P9_SHAM_CORE_CHANGED_{ordinal}_{see}_{mode}')
      must(z['p6s1']==previous['p6s1'],f'P9_SHAM_TT_SOURCE_CHANGED_{ordinal}_{see}_{mode}')
      must(z['p7']==previous['TT_value_delivery'],f'P9_SHAM_SCORE_SOURCE_CHANGED_{ordinal}_{see}_{mode}')
      must(gates==0,'P9_INACTIVE_ARM_CAUSED_MICRO_GATES')
      original_regression+=1
    else:
      expected=(ordinal==2) if mode=='G' else True
      tag={'G':'suppressed_beta_break','W':'suppressed_TT_write','L':'clamped_local_return'}[mode]
      must(bool(counts[tag])==expected,
        f'P9_EXPECTED_EXACT_TARGET_EVENT_NOT_MATCHED_{ordinal}_{see}_{mode}')
      if mode=='L':
       must(z['p9']['new_qreturn']==(14 if ordinal==2 else 29),
            'P9_RELAY_NOT_ORIGINAL_TT_RETURN')
       must(z['p9']['changed_return_value']==int(ordinal==2),
            'P9_RELAY_NUMERIC_DIFF_NOT_EXPECTED')
    state={'UCI':core(z),'micro_gates':z['p9'],
      'root_iteration':z['root_iteration'],
      'trace_event_counts':{k:z['p8'][k] for k in ('marks','seen','listed','truncated')},
      'target_context':{'key':z['p8']['target_key'],'ply':z['p8']['target_ply']},
      'P6_exact_target':z['p6s1'],
      'P7_exact_value':z['p7']}
    rows['cells'][see+'__'+mode]=state
    print('C3X015_P9_A1',ordinal,see,mode,
        'bm',z['bestmove'],'beta_supp',counts['suppressed_beta_break'],
        'TTwrite_supp',counts['suppressed_TT_write'],
        'return_clamp',counts['clamped_local_return'],flush=True)
  for mode in ('I','V','B','G','W','L'):
   off=rows['cells']['OFF__'+mode]['UCI']['bestmove']
   on=rows['cells']['ROOT_OBJECT_SEE_UNMASK__'+mode]['UCI']['bestmove']
   rows['root_categorical_effect'][mode]={'off':off,'on':on,'binary_see_flip':int(off!=on)}
  cases.append(rows)
 out={'schema':'c3x015-P9-A1-CEFH-RISR-exact-qsearch-48-native-v1',
 'status':'POST_P6_OUTCOME_TWO_WORLD_MECHANISM_ONLY',
 'original_source_r2_sha256':SRC,
 'original_P8_result_sha256':'bb2af016857dff393a6054bad2b2978d3ecb2d92c527891f578688e513452e22',
 'native_cold_processes':observed,'exact_P8_baseline_cell_regression':original_regression,
 'expected_beta_gate_negative_control_world29':True,
 'P9_A2_D129_130_131_status':'PRECOMMITTED_NOT_EXECUTED',
 'cases':cases,
 'limits':['No new independent game worlds, no claim of prospective generalization',
   'Single P9 beta/TT save/return gate is an artificial source intervention, not identified natural indirect mediator',
   'P9 G case29 no-contact control is a positive RISR mechanism context, not evidence case29 unimportant',
   'Full search, motif, NNUE and other-engine transport claims HOLD']}
 Path(a.out).write_text(json.dumps(out,sort_keys=True,indent=2,ensure_ascii=False)+'\n')
 print('C3X015_P9_A1_NATIVE_48_SUMMARY',json.dumps([{'case':z['ordinal'],
  'root_effects':z['root_categorical_effect']} for z in cases],sort_keys=True),flush=True)
if __name__=='__main__':main()
