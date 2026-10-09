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
def trace(engine,hist,arm,sq,pn,regime):
 env={**os.environ,'C3X014_PIN_ROOT_OBJECT_ARM':arm,'C3X014_PIN_ROOT_SQUARE_ID':str(sq),
      'C3X014_PIN_ROOT_PINNER_ID':str(pn),'C3X015_POST_SEE_TT_RETURN_MODE':regime}
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
 result['tt_regime']={k:int(v) for k,v in typed('c3x015_tt_return_factorial').items()}
 return result
def core(z):return {k:z[k] for k in CORE}
def main():
 p=argparse.ArgumentParser()
 for k in ('source','prior-p2','engine','out'):p.add_argument('--'+k,required=True)
 a=p.parse_args()
 source=load(a.source,SRC);prior=load(a.prior_p2,P2)
 pins=source['pin_roots'];priorrows=prior['pin_worlds']
 must(len(pins)==len(priorrows)==64,'P5_FROZEN_COHORT_INCORRECT')
 results=[]
 for index,(original,old) in enumerate(zip(pins,priorrows),1):
  must(sha(original['root_sixfield_fen'].encode())==old['fen_sha256'],'P5_COHORT_ROOT_SHA_CHANGED')
  ob=original['objects'][0]
  sq=chess.parse_square(ob['pinned_square']);pn=chess.parse_square(ob['pinner_square'])
  hist=original['full_history_uci'][:original['root_ply']]
  board=chess.Board(original['initial_fen'])
  for u in hist:
   m=chess.Move.from_uci(u);must(m in board.legal_moves,'P5_ILLEGAL_HISTORY')
   board.push(m)
  must(board.fen(en_passant='fen')==original['root_sixfield_fen'],'P5_ROOT_FEN_CHANGED')
  arms={}
  for see in ('OFF','ROOT_OBJECT_SEE_UNMASK'):
   for regime in ('ALLOW','BLOCK_AFTER_CANDIDATE'):
    repeats=[trace(a.engine,hist,see,sq,pn,regime) for _ in range(2)]
    must(repeats[0]==repeats[1],'P5_COLD_INSTRUMENTED_UCI_REPLAY_FAIL_'+str(index)+'_'+see+'_'+regime)
    z=repeats[0];cnt=z['tt_regime']
    must(cnt['mode']==int(regime=='BLOCK_AFTER_CANDIDATE'),'P5_TT_FACTORIAL_MODE_MISMATCH')
    must(cnt['eligible_returns']==cnt['before_candidate']+cnt['after_candidate_allowed']+
         cnt['after_candidate_blocked'],'P5_TT_RETURN_COUNTER_INCONSISTENT')
    if regime=='ALLOW':must(cnt['after_candidate_blocked']==0,'P5_TT_CONTROL_EVER_BLOCKED')
    else:must(cnt['after_candidate_allowed']==0,'P5_TT_BLOCKED_MODE_PERMITTED_POST_CANDIDATE_RETURN')
    if not z['window']['first_candidate']:must(cnt['after_candidate_blocked']==0,
                                                 'P5_POST_ONLY_SUPPRESSION_BEFORE_SOURCE_ELIGIBILITY')
    arms[(see,regime)]=z
  normal_off=arms[('OFF','ALLOW')]
  normal_see=arms[('ROOT_OBJECT_SEE_UNMASK','ALLOW')]
  must(core(normal_off)==old['native_pristine_OFF'],
       'P5_ALLOWS_REGIME_CHANGED_FROZEN_P2_ORIGINAL_UCI')
  must(core(normal_see)==old['native_ROOT_SEE_UNMASK'],
       'P5_ALLOWS_REGIME_CHANGED_FROZEN_P2_TARGET_UCI')
  must(normal_see['guard']['target_fired']==old['source_site_fires'],
       'P5_TARGET_FIRE_COUNTS_CHANGED_FROM_P2')
  block_off=arms[('OFF','BLOCK_AFTER_CANDIDATE')]
  block_see=arms[('ROOT_OBJECT_SEE_UNMASK','BLOCK_AFTER_CANDIDATE')]
  if not normal_see['guard']['target_fired']:
   must(core(normal_off)==core(normal_see),
        'P5_ROOT_OBJECT_NONFIRE_CHANGED_PREVIOUS_CAUSAL_COMPARISON')
   must(core(block_off)==core(block_see),
        'P5_ROOT_OBJECT_NONFIRE_YET_COUNTERFACTUAL_DIFFERENT')
  deltas={
   'd_normal':int(normal_off['bestmove']!=normal_see['bestmove']),
   'd_tt_blocked':int(block_off['bestmove']!=block_see['bestmove']),
   'TT_regime_affects_OFF':int(normal_off['bestmove']!=block_off['bestmove']),
   'TT_regime_affects_SEE':int(normal_see['bestmove']!=block_see['bestmove'])}
  must(deltas['d_normal']==old['y_changed_bestmove'],'P5_NORMAL_TREATMENT_OUTCOME_NOT_PREVIOUS_P2')
  summary={}
  for see in ('OFF','ROOT_OBJECT_SEE_UNMASK'):
   for regime in ('ALLOW','BLOCK_AFTER_CANDIDATE'):
    z=arms[(see,regime)];w=z['window']
    summary[see+'__'+regime]={'uci':core(z),'source_fire':z['guard']['target_fired'],
      'tt_event_counts':z['tt_regime'],
      'first_eligible_search_ordinal':w['first_search_ordinal'],
      'first_eligible_position_key':w['first_pos_key'],
      'pre_source_hash':w['prefix_fnv64'],
      'post_4096_search_entry_stream_sha256':sha(w['stream'].encode()),
      'post_4096_search_entries':w['post_search_entries']}
  before=summary['OFF__ALLOW'];other=summary['OFF__BLOCK_AFTER_CANDIDATE']
  must(before['pre_source_hash']==other['pre_source_hash'] and
       before['first_eligible_position_key']==other['first_eligible_position_key'],
       'P5_TT_REGIME_ALTERED_PRE_SOURCE_SEARCH')
  results.append({'ordinal':index,'source_game_sha256':old['game_sha256'],
    'FEN_sha256':old['fen_sha256'],'event':old['event'],'law':old['law'],
    'P2_C1_sealed_prediction':old['pred']['C1'],'P2_source_site_fires':old['source_site_fires'],
    'outcomes':deltas,'arms':summary})
  print('C3X015_P5_FACTORIAL',index,'P2_SEE_FLIP',deltas['d_normal'],
        'TT_BLOCK_SEE_FLIP',deltas['d_tt_blocked'],
        'BLOCKED_TT_RETURNS',block_see['tt_regime']['after_candidate_blocked'],
        flush=True)
 sums={k:sum(y['outcomes'][k] for y in results) for k in
      ('d_normal','d_tt_blocked','TT_regime_affects_OFF','TT_regime_affects_SEE')}
 interaction={'normal_only':sum(z['outcomes']['d_normal']==1 and z['outcomes']['d_tt_blocked']==0 for z in results),
  'suppressed_only':sum(z['outcomes']['d_normal']==0 and z['outcomes']['d_tt_blocked']==1 for z in results),
  'both_flip':sum(z['outcomes']['d_normal']==1 and z['outcomes']['d_tt_blocked']==1 for z in results),
  'neither_flip':sum(z['outcomes']['d_normal']==0 and z['outcomes']['d_tt_blocked']==0 for z in results)}
 summary={'schema':'c3x-015-P5-TWIC-SEE-X-conditional-TT-return-factorial-64world-512native-v1',
   'research_status':'RETROSPECTIVE_FACTORIAL_INTERACTION_NOT_SINGLE_TT_CAUSAL_MEDIATION',
   'source_sha256':SRC,'P2_native_sha256':P2,'actual_native_search_processes':512,
   'cold_pairs':256,'all_normal_OFF_AND_SEE_equal_P2':64,
   'P2_normal_flip_count':11,'factorial_counts':sums,'responder_contingency':interaction,
   'block_regime_exposure_OFF_worlds':sum(z['arms']['OFF__BLOCK_AFTER_CANDIDATE']['tt_event_counts']['after_candidate_blocked']>0 for z in results),
   'block_regime_exposure_SEE_worlds':sum(z['arms']['ROOT_OBJECT_SEE_UNMASK__BLOCK_AFTER_CANDIDATE']['tt_event_counts']['after_candidate_blocked']>0 for z in results),
   'total_blocked_TT_early_returns_SEE':sum(z['arms']['ROOT_OBJECT_SEE_UNMASK__BLOCK_AFTER_CANDIDATE']['tt_event_counts']['after_candidate_blocked'] for z in results),
   'limits':['Broad suppression of eligible TT returns after source exposure only; cannot isolate any single TT reader.',
    'Original P1 C1 predictor remains 42/64 accuracy and is not retrained.',
    'Stockfish classical SF16 depth12 only; post-outcome exploration with 64 rooted game units.',
    'Forced full search can change ordering and history; not purely an isolated path-mediator natural direct effect.',
    'A zero difference does not imply no TT causal role due to compensating search paths.'],
   'all_original_pin_roots':results}
 Path(a.out).write_text(json.dumps(summary,sort_keys=True,indent=2,ensure_ascii=False)+'\n')
 print('C3X015_P5_FACTORIAL_FINAL',json.dumps({k:summary[k] for k in
      ('factorial_counts','responder_contingency','total_blocked_TT_early_returns_SEE')},sort_keys=True),flush=True)
if __name__=='__main__':main()
