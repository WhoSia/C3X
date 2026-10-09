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
 return result
def core(z):return {k:z[k] for k in CORE}
def main():
 ap=argparse.ArgumentParser()
 for field in ('source','targets','prior-p2','prior-p6','engine','out'):
  ap.add_argument('--'+field,required=True)
 args=ap.parse_args()
 src=load(args.source,SRC)
 p2=load(args.prior_p2,P2)
 targets=load(args.targets,"0dd412cdfad82ea6b042dd3381e07182f2d4f3e52cd3e83c71004b6ecaed6ee1")
 p6=load(args.prior_p6,"c04ee3061835babb846fee54b269617da5ab809dc9efe46c1e6cbe9360fefa11")
 roots=src['pin_roots']
 p2rows=p2['pin_worlds']
 refrows=p6['all_64_native_four_cell_interventions']
 targetrows=targets['all64_targets']
 assert len(roots)==len(p2rows)==len(refrows)==len(targetrows)==64
 cases=[]
 total=0
 for ordinal in (2,29):
  j=ordinal-1
  r=roots[j];old=p2rows[j];pre=refrows[j];target=targetrows[j]['target']
  must(old['fen_sha256']==pre['fen_sha256']==targetrows[j]['fen_sha256']==sha(r['root_sixfield_fen'].encode()),'P7_FEN_ORDER_NOT_FROZEN')
  must(bool(target['eligible']),'P7_PRESELECTED_TT_EDGE_INELIGIBLE')
  must(target['writer_tag']==6 and target['stored_bound']==1 and target['alpha']==130 and target['beta']==131,
       'P7_UPPER_BOUND_QSEARCH_READER_CONTEXT_NOT_AS_PRECOMMITTED')
  obj=r['objects'][0]
  sq=chess.parse_square(obj['pinned_square']);pn=chess.parse_square(obj['pinner_square'])
  hist=r['full_history_uci'][:r['root_ply']]
  board=chess.Board(r['initial_fen'])
  for m in hist:
   step=chess.Move.from_uci(m)
   must(step in board.legal_moves,'P7_ILLEGAL_SOURCE_HISTORY')
   board.push(step)
  must(board.fen(en_passant='fen')==r['root_sixfield_fen'],'P7_SOURCE_NOT_SAME')
  cells={}
  for see in ('OFF','ROOT_OBJECT_SEE_UNMASK'):
   for mode in ('IDENTITY','RETURN_ALPHA','BLOCK_EXACT_ONCE'):
    p6mode='BLOCK_EXACT_ONCE' if mode=='BLOCK_EXACT_ONCE' else 'ALLOW'
    os.environ['C3X015_P7_SCORE_MODE']='RETURN_ALPHA' if mode=='RETURN_ALPHA' else 'IDENTITY'
    runs=[trace(args.engine,hist,see,sq,pn,target,p6mode) for _ in range(2)]
    total+=2
    must(runs[0]==runs[1],'P7_COLD_TRACE_MISMATCH_'+str(ordinal)+'_'+see+'_'+mode)
    z=runs[0]
    must(z['p6s1']['target_valid']==1,'P7_TARGET_DISABLED')
    must(z['p6s1']['suppressed']<=1,'P7_MORE_THAN_ONE_TT_RETURN_BLOCKED')
    if mode=='RETURN_ALPHA':
     must(z['p6s1']['suppressed']==0,'P7_ALPHA_MODE_IS_NOT_BLOCKED')
     must(z['p7']['mode']==1 and z['p7']['matched_score_deliveries']==1,
         'P7_EXACT_ONCE_RETURN_ALPHA_NOT_DELIVERED')
     must(z['p7']['alpha']==130 and z['p7']['beta']==131,
         'P7_READER_WINDOW_CHANGED')
     must(z['p7']['delivered_value']==130,'P7_SCORE_NOT_REPLACED_BY_ALPHA')
    else:
     must(z['p7']['mode']==0 and z['p7']['matched_score_deliveries']==0,'P7_OBSERVER_PERTURBED_CONTROL')
    label=see+'__'+mode
    if mode in ('IDENTITY','BLOCK_EXACT_ONCE'):
     oldlabel=see+'__'+('ALLOW' if mode=='IDENTITY' else 'BLOCK_EXACT_ONCE')
     prior=pre['four_native_cold_conditions'][oldlabel]
     must(core(z)==prior['UCI'],'P7_CONTROL_ARM_DIVERGED_FROM_PREVIOUS_P6_NATIVE')
     must(z['p6s1']==prior['target'],'P7_P6_TARGET_DELIVERY_DRIFT')
    cells[label]={'UCI':core(z),'p6s1':z['p6s1'],'p7_value':z['p7'],
      'first_search_prefix_hash':z['window']['prefix_fnv64']}
    print('C3X015_P7_NATIVE',ordinal,see,mode,'bestmove',z['bestmove'],
          'delivered',z['p7']['matched_score_deliveries'],
          'numeric_diff',z['p7']['numeric_changes'],flush=True)
  off=lambda mode:cells['OFF__'+mode]['UCI']['bestmove']
  on=lambda mode:cells['ROOT_OBJECT_SEE_UNMASK__'+mode]['UCI']['bestmove']
  outcomes={mode:int(off(mode)!=on(mode)) for mode in ('IDENTITY','RETURN_ALPHA','BLOCK_EXACT_ONCE')}
  comparisons={'OFF_value_only_changed':off('RETURN_ALPHA')!=off('IDENTITY'),
               'SEE_value_only_changed':on('RETURN_ALPHA')!=on('IDENTITY'),
               'OFF_search_continuation_changed':off('BLOCK_EXACT_ONCE')!=off('IDENTITY'),
               'SEE_search_continuation_changed':on('BLOCK_EXACT_ONCE')!=on('IDENTITY')}
  cases.append({'ordinal':ordinal,'root_fen_sha256':old['fen_sha256'],
      'frozen_target':target,'source_law':old['law'],'cells':cells,
      'SEE_response_by_TT_return_regime':outcomes,
      'root_choice_contrasts':comparisons})
 result={'schema':'c3x015-P7-2-world-TT-return-value-vs-continue-24-native-v1',
   'classification':'P7_POST_P6_DISCLOSURE_MECHANISM_SCOPED',
   'source_r2_sha256':SRC,'P2_sha256':P2,
   'P6S0_target_sha256':'0dd412cdfad82ea6b042dd3381e07182f2d4f3e52cd3e83c71004b6ecaed6ee1',
   'P6S1_original_sha256':'c04ee3061835babb846fee54b269617da5ab809dc9efe46c1e6cbe9360fefa11',
   'original_SF16_commit':'68e1e9b3811e16cad014b590d7443b9063b3eb52',
   'native_search_processes':total,'cold_pairs':12,
   'source_worlds':2,'arms_per_source_world':6,
   'limits':['P7 is post-P6-targeted analysis, not out-of-source blind validation',
     'RETURN_ALPHA changes only one matched fail-low TT return value while preserving immediate return',
     'BLOCK_EXACT_ONCE continues qsearch and is a different executed control-flow intervention',
     'No complete TT natural indirect effect or tactical concept generalization proven'],
   'cases':cases}
 Path(args.out).write_text(json.dumps(result,sort_keys=True,indent=2,ensure_ascii=False)+'\n')
 print('C3X015_P7_QSEARCH_SCORE_VS_CONTINUATION_FINAL',json.dumps(
  [{'ordinal':z['ordinal'],'responses':z['SEE_response_by_TT_return_regime'],
    'contrasts':z['root_choice_contrasts']} for z in cases],sort_keys=True),flush=True)
if __name__=='__main__':main()
