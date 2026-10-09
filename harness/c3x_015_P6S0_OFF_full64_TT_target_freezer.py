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
def trace(engine,hist,arm,sq,pn):
 env={**os.environ,'C3X014_PIN_ROOT_OBJECT_ARM':arm,'C3X014_PIN_ROOT_SQUARE_ID':str(sq),
      'C3X014_PIN_ROOT_PINNER_ID':str(pn)}
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
 result['p6_source_target']={k:int(v) for k,v in typed('c3x015_p6s0_target').items()}
 return result
def core(z):return {k:z[k] for k in CORE}
def main():
 p=argparse.ArgumentParser()
 for k in ('source','prior-p2','engine','out'):p.add_argument('--'+k,required=True)
 a=p.parse_args();src=load(a.source,SRC);prior=load(a.prior_p2,P2)
 worlds=src['pin_roots'];old=prior['pin_worlds'];must(len(worlds)==len(old)==64,'P6S0_ORIGINAL_COHORT_CHANGED')
 roots=[]
 for j,(w,past) in enumerate(zip(worlds,old),1):
  must(sha(w['root_sixfield_fen'].encode())==past['fen_sha256'],'P6S0_FEN_NOT_FROZEN')
  obj=w['objects'][0]
  hist=w['full_history_uci'][:w['root_ply']]
  sq=chess.parse_square(obj['pinned_square']);pn=chess.parse_square(obj['pinner_square'])
  board=chess.Board(w['initial_fen'])
  for u in hist:
   move=chess.Move.from_uci(u);must(move in board.legal_moves,'P6S0_ILLEGAL_SOURCE_HISTORY')
   board.push(move)
  must(board.fen(en_passant='fen')==w['root_sixfield_fen'],'P6S0_EXACT_BOARD_MISMATCH')
  pair=[trace(a.engine,hist,'OFF',sq,pn) for _ in range(2)]
  must(pair[0]==pair[1],'P6S0_COLD_TRACE_NOT_EXACT')
  z=pair[0]
  must(core(z)==past['native_pristine_OFF'],'P6S0_INSTRUMENTED_OFF_CHANGED_P2')
  must(z['guard']['target_fired']==0,'P6S0_OBSERVE_OFF_EXECUTED_SEE_TREATMENT')
  t=z['p6_source_target']
  if t['eligible']:
   must(t['slot_offset'] in (0,1,2),'P6S0_PHYSICAL_TT_CLUSTER_SLOT_OUT_OF_RANGE')
   must(t['writer_tag'] in (1,2,3,4,5,6),'P6S0_UNKNOWN_SOURCE_WRITER')
   must(t['writer_seq']>0 and t['key']>0,'P6S0_WRITER_IDENTITY_UNKNOWN')
   must(t['stored_bound'] in (1,2,3),'P6S0_WRITER_BOUND_UNEXPECTED')
  else:
   must(t['key']==0 and t['writer_seq']==0,'P6S0_NO_TARGET_MUST_ZERO')
  roots.append({'ordinal':j,'game_sha256':past['game_sha256'],'fen_sha256':past['fen_sha256'],
    'event':past['event'],'original_pin_law':past['law'],'prior_P2_SEE_effect_known_but_not_used_in_target_selection':past['y_changed_bestmove'],
    'original_OFF_native_UCI':core(z),'source_frozen_root_square':obj['pinned_square'],
    'source_frozen_pinner_square':obj['pinner_square'],
    'target':t,'target_deliverable_in_OFF':bool(t['eligible']),
    'first_root_see_candidate_search_ordinal':z['window']['first_search_ordinal'],
    'prior_candidate_search_prefix_fnv64':z['window']['prefix_fnv64']})
  print('C3X015_P6S0_NATIVE_ORIGINAL_OFF',j,'EXACT_TT_TARGET',t['eligible'],'FULLKEY',t['key'],
    'WRITER',t['writer_tag'],'BOUND',t['stored_bound'],'WRITESEQ',t['writer_seq'],flush=True)
 result={'schema':'c3x-015-P6S0-off-only-first-exact-physical-TT-writer-reader-preintervention-target-v1',
    'source_sha256':SRC,'prior_P2_sha256':P2,
    'engine_original_source_commit':'68e1e9b3811e16cad014b590d7443b9063b3eb52',
    'new_native_source_observer_processes':128,'exact_64_cold_pairs':'64/64',
    'OFF_native_reported_UCI_equal_original_P2':'64/64',
    'OFF_source_treatment_fired_count':0,
    'frozen_original_source_games':64,
    'target_selection_rule':'FIRST NATURALLY TAKEN main/qsearch early TT RETURN AFTER FIRST ROOT OBJECT SEE ELIGIBLE CANDIDATE, PHYSICAL TT WRITER PRESENT AND FULL64 KEY EXACT; OFF ONLY; NO P2/P5 LABEL SELECTION',
    'targets_eligible':sum(z['target']['eligible'] for z in roots),
    'writer_tag_distribution':{str(tag):sum(z['target']['eligible'] and z['target']['writer_tag']==tag for z in roots) for tag in range(1,7)},
    'negative_no_target_worlds':sum(not z['target']['eligible'] for z in roots),
    'all64_targets':roots,
    'limits':['This observer selects OFF native first exact writer-reader after original source candidate; no P6 TT return has been suppressed.',
     'Writer sequence and exact position key are valid only in fixed native run; later ON path might not encounter the same edge.',
     'Hash of this target file must be committed before any P6 block intervention.',
     'P2 response labels are included for provenance but not consulted by selection code.']}
 Path(a.out).write_text(json.dumps(result,sort_keys=True,indent=2,ensure_ascii=False)+'\n')
 print('C3X015_P6S0_EXACT_TT_TARGET_FREEZE_RESULT',json.dumps({
  'target_count':result['targets_eligible'],'negative_no_target_count':result['negative_no_target_worlds'],
  'writer_tag_distribution':result['writer_tag_distribution']},sort_keys=True),flush=True)
if __name__=='__main__':main()
