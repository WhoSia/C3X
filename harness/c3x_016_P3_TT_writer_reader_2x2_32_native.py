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
 result['c3x016_writer']={k:int(v) for k,v in typed('c3x016_writer_factor').items()}
 return result
def core(z):return {k:z[k] for k in CORE}
def main():
 ap=argparse.ArgumentParser()
 for n in ('source','targets','prior-p2','prior-p6','prior-p7','prior-p8','prior-p9a1','prior-p10','prior-p11','engine','out'):
  ap.add_argument('--'+n,required=True)
 a=ap.parse_args()
 src=load(a.source,SRC)
 targets=load(a.targets,'0dd412cdfad82ea6b042dd3381e07182f2d4f3e52cd3e83c71004b6ecaed6ee1')
 load(a.prior_p2,P2)
 load(a.prior_p6,'c04ee3061835babb846fee54b269617da5ab809dc9efe46c1e6cbe9360fefa11')
 load(a.prior_p7,'01ea31dcb1d900925ff38ec3d6d5da4afe63bba6c87eccc2eb8563d9440d8c77')
 load(a.prior_p8,'bb2af016857dff393a6054bad2b2978d3ecb2d92c527891f578688e513452e22')
 load(a.prior_p9a1,'0a0a40d891af736491ecbfb92dee145c969b853d6e1ac43495beb202e905ec17')
 load(a.prior_p10,'2d74c4edd45700b9ffcbb2763edc4dad94a5bee9f4590dc85d2295f6c38a1c45')
 p11=load(a.prior_p11,'0a296860a26db3b8b5530a23eb7935f6f71f8fd9e809299ea39486133022a2f8')
 must([w['ordinal'] for w in p11['worlds']]==[2,29],'P11_PREVIOUS_WORLD_IDS_CHANGED')
 outputs=[]
 for ordinal in (2,29):
  index=ordinal-1
  world=src['pin_roots'][index]
  target=targets['all64_targets'][index]['target']
  obj=world['objects'][0]
  square=chess.parse_square(obj['pinned_square'])
  pinner=chess.parse_square(obj['pinner_square'])
  history=world['full_history_uci'][:world['root_ply']]
  prior=p11['worlds'][0 if ordinal==2 else 1]
  must(sha(world['root_sixfield_fen'].encode())==prior['root_FEN_sha256'],
        'C3X016_WRITER_READER_SOURCE_FEN_CHANGED')
  result={'ordinal':ordinal,'source_fen_sha256':prior['root_FEN_sha256'],
          'frozen_target':target,'cells':{},'pre_assigned_2x2_arms':['W1R1','W1R0','W0R1','W0R0']}
  for see in ('OFF','ROOT_OBJECT_SEE_UNMASK'):
   for wmode in ('W1','W0'):
    for rmode in ('R1','R0'):
     os.environ['C3X016_TT_WRITER_MODE']=wmode
     os.environ['C3X015_P9_A1_MODE']='SHAM'
     os.environ['C3X015_P9_A1_CASE']=str(ordinal)
     os.environ['C3X015_P7_SCORE_MODE']='IDENTITY'
     os.environ['C3X015_P11_ROOT_CLAMP']='SHAM'
     native_reader='ALLOW' if rmode=='R1' else 'BLOCK_EXACT_ONCE'
     first=trace(a.engine,history,see,square,pinner,target,native_reader)
     second=trace(a.engine,history,see,square,pinner,target,native_reader)
     must(first==second,f'C3X016_2X2_COLD_MISMATCH_{ordinal}_{see}_{wmode}_{rmode}')
     actual=first['c3x016_writer']
     must(actual['W']==int(wmode=='W1'),'C3X016_WRITER_ARM_NOT_MATCHED')
     must(actual['suppressed']==int(wmode=='W0'),'C3X016_WRITER_SINGLE_EXACT_SAVE_NOT_CONTACTED')
     must(actual['contact']>=1,'C3X016_ORIGINAL_WRITER_NOT_SEEN')
     must(actual['suppressed']<=1 and first['p6s1']['suppressed']<=1,
          'C3X016_MORE_THAN_ONE_WRITE_OR_READ_SUPPRESSED')
     must(first['p11']['fired']==0 and first['p9']['suppressed_TT_write']==0
          and first['p9']['suppressed_beta_break']==0
          and first['p9']['clamped_local_return']==0,
          'C3X016_OTHER_ARTIFICIAL_GATE_FIRED')
     if wmode=='W1':
      old_regime='I' if rmode=='R1' else 'B'
      old=prior['cells'][see+'__'+old_regime+'__SHAM']
      must(core(first)==old['UCI'],
          f'C3X016_W1_NATIVE_ORIGINAL_P11_CORE_MISMATCH_{ordinal}_{see}_{rmode}')
      must(first['p11']==old['root_relay_source'],
          f'C3X016_W1_P11_SOURCE_CONTACT_MISMATCH_{ordinal}_{see}_{rmode}')
     elif first['p6s1']['suppressed']==0:
      # Writer absence can make the preselected original consumer disappear.
      # Treat missing consumer as a real result, never dynamically substitute it.
      pass
     key=f'{see}__{wmode}{rmode}'
     result['cells'][key]={
      'UCI':core(first),
      'writer_assignment':wmode,'reader_assignment':rmode,
      'writer_source':actual,
      'reader_source':first['p6s1'],
      'preexisting_P6_target':first['p6s0'],
      'P10_root_events_seen':first['p10']['seen'],
      'P10_root_events_retained':first['p10']['retained'],
      'P10_root_events_truncated':first['p10']['truncated'],
      'root_iteration':first['root_iteration'],
      'reader_selected_generation_contact':first['p6s1']['exact_hits']>0,
      'reader_source_return_blocked':first['p6s1']['suppressed']>0
     }
     print('C3X016_P3_NATIVE',ordinal,see,wmode+rmode,
           'writer=',actual['contact'],'suppressed=',actual['suppressed'],
           'reader_matches=',first['p6s1']['exact_hits'],
           'reader_blocks=',first['p6s1']['suppressed'],
           'move=',first['bestmove'],'cp=',first['value_root_stm'],
           'nodes=',first['nodes'],flush=True)
  result['contrasts']={}
  for see in ('OFF','ROOT_OBJECT_SEE_UNMASK'):
   for dim in ('W','R'):
    a0,a1=(('W0R1','W1R1') if dim=='W' else ('W1R0','W1R1'))
    o0=result['cells'][see+'__'+a0]['UCI']
    o1=result['cells'][see+'__'+a1]['UCI']
    result['contrasts'][see+'__'+dim]={
      'categorical_root_move_changed':o0['bestmove']!=o1['bestmove'],
      'root_score_changed':(o0['value_root_stm'],o0['score_flag'],o0['score_kind'])!=
                            (o1['value_root_stm'],o1['score_flag'],o1['score_kind']),
      'search_nodes_changed':o0['nodes']!=o1['nodes'],
      'PV_changed':o0['pv']!=o1['pv']
    }
  outputs.append(result)
 out={'schema':'c3x016-P3-frozen-physical-TT-writer-reader-2x2-32-native-v1',
      'status':'POST_OUTCOME_TWO_WORLD_MECHANISM_DEVELOPMENT_ONLY',
      'source_original_R2_sha256':SRC,
      'prior_P11_raw_SHA256':'0a296860a26db3b8b5530a23eb7935f6f71f8fd9e809299ea39486133022a2f8',
      'new_native_processes':32,'unique_original_worlds':2,
      'factors':['W1R1','W0R1','W1R0','W0R0'],
      'cold_repeats_per_arm':2,'worlds':outputs,
      'inference_limits':[
       'Source-specific controlled 2x2 effects, not cross-world natural indirect TT effects.',
       'Preselected writer and reader cannot be dynamically retargeted after W0 changes search.',
       'Writer ghost ordinal counts are not physical TT writes.',
       'Reader no-contact stays as measured result, not discarded.',
       'Two worlds chosen after predecessor P6 result; not external motif validation.',
       'Prior context-prediction accuracy failure C1 42/64 vs B0 53/64 remains FAIL.'
      ]}
 Path(a.out).write_text(json.dumps(out,sort_keys=True,indent=2)+'\n')
 print('C3X016_P3_TT_WRITER_READER_2X2_NATIVE_32_COURT_SCOPED_PASS',flush=True)
if __name__=='__main__':main()
