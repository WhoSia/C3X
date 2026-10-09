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
 return result
def core(z):return {k:z[k] for k in CORE}
def main():
 p=argparse.ArgumentParser()
 for k in ('source','targets','prior-p2','engine','out'):p.add_argument('--'+k,required=True)
 a=p.parse_args()
 src=load(a.source,SRC);prior=load(a.prior_p2,P2)
 TARGET_SHA="0dd412cdfad82ea6b042dd3381e07182f2d4f3e52cd3e83c71004b6ecaed6ee1"
 tg=load(a.targets,TARGET_SHA)
 roots=src['pin_roots'];olds=prior['pin_worlds'];targets=tg['all64_targets']
 must(len(roots)==len(olds)==len(targets)==64,'P6S1_ORIGINAL_COHORT_WRONG')
 cases=[]
 for j,(root,old,targetrec) in enumerate(zip(roots,olds,targets),1):
  must(j==targetrec['ordinal'],'P6S1_SOURCE_ORDINAL_CHANGED')
  must(sha(root['root_sixfield_fen'].encode())==old['fen_sha256']==targetrec['fen_sha256'],
       'P6S1_TARGET_ROOT_FEN_SHA_DIFFERENT')
  obj=root['objects'][0];t=targetrec['target']
  sq=chess.parse_square(obj['pinned_square']);pn=chess.parse_square(obj['pinner_square'])
  history=root['full_history_uci'][:root['root_ply']]
  board=chess.Board(root['initial_fen'])
  for u in history:
   m=chess.Move.from_uci(u);must(m in board.legal_moves,'P6S1_ILLEGAL_FROZEN_MOVES')
   board.push(m)
  must(board.fen(en_passant='fen')==root['root_sixfield_fen'],'P6S1_BOARD_ROOT_CHANGED')
  arms={}
  for see in ('OFF','ROOT_OBJECT_SEE_UNMASK'):
   for policy in ('ALLOW','BLOCK_EXACT_ONCE'):
    cold=[trace(a.engine,history,see,sq,pn,t,policy) for _ in range(2)]
    must(cold[0]==cold[1],'P6S1_COLD_REPEAT_NOT_EQUAL_'+str(j)+'_'+see+'_'+policy)
    z=cold[0];q=z['p6s1']
    must(q['mode']==int(policy=='BLOCK_EXACT_ONCE'),'P6S1_SOURCE_MODE_WRONG')
    must(q['target_valid']==int(bool(t['eligible'])),'P6S1_TARGET_VALID_WRONG')
    must(q['suppressed']<=1,'P6S1_BLOCKED_MORE_THAN_ONE_TT_RETURN')
    if policy=='ALLOW':must(q['suppressed']==0,'P6S1_ALLOW_MUST_NOT_BLOCK')
    if not t['eligible']:must(q['exact_hits']==q['suppressed']==0,'P6S1_NO_TARGET_INTERVENTION')
    arms[(see,policy)]=z
  offallow=arms[('OFF','ALLOW')];onallow=arms[('ROOT_OBJECT_SEE_UNMASK','ALLOW')]
  must(core(offallow)==old['native_pristine_OFF'],'P6S1_OFF_ALLOWS_ORIGINAL_P2_CHANGED')
  must(core(onallow)==old['native_ROOT_SEE_UNMASK'],'P6S1_TARGET_ALLOWS_ORIGINAL_P2_CHANGED')
  must(onallow['guard']['target_fired']==old['source_site_fires'],'P6S1_SOURCE_OBJECT_FIRES_CHANGED')
  if t['eligible']:must(offallow['p6s1']['exact_hits']>0,'P6S1_PRESEALED_OFF_TARGET_NOT_OBSERVED')
  for see in ('OFF','ROOT_OBJECT_SEE_UNMASK'):
   allowed=arms[(see,'ALLOW')];blocked=arms[(see,'BLOCK_EXACT_ONCE')]
   if blocked['p6s1']['suppressed']==0:
    must(core(allowed)==core(blocked),'P6S1_NO_TT_RETURN_BLOCK_YET_OUTPUT_CHANGED')
   must(allowed['window']['prefix_fnv64']==blocked['window']['prefix_fnv64'] and
        allowed['window']['first_search_ordinal']==blocked['window']['first_search_ordinal'],
        'P6S1_TT_INTERVENTION_ALTERED_PRE_SITES')
  signals={}
  for see in ('OFF','ROOT_OBJECT_SEE_UNMASK'):
   for policy in ('ALLOW','BLOCK_EXACT_ONCE'):
    z=arms[(see,policy)]
    signals[see+'__'+policy]={'UCI':core(z),'target':z['p6s1'],
     'first_candidate_seen':z['window']['first_candidate'],
     'pre_source_first_key':z['window']['first_key'],
     'search_suffix_sha256':sha(z['window']['stream'].encode())}
  see_no_tt=int(offallow['bestmove']!=onallow['bestmove'])
  block_off=arms[('OFF','BLOCK_EXACT_ONCE')];block_on=arms[('ROOT_OBJECT_SEE_UNMASK','BLOCK_EXACT_ONCE')]
  see_under_block=int(block_off['bestmove']!=block_on['bestmove'])
  must(see_no_tt==old['y_changed_bestmove'],'P6S1_ORIGINAL_SEE_RESPONSE_NOT_P2')
  cases.append({'ordinal':j,'source_game_sha256':old['game_sha256'],'fen_sha256':old['fen_sha256'],
   'event':old['event'],'law':old['law'],'presealed_tt_target':t,
   'OFF_delivered':int(bool(block_off['p6s1']['suppressed'])),
   'SEE_delivered':int(bool(block_on['p6s1']['suppressed'])),
   'original_p2_SEE_root_flip':see_no_tt,'SEEsensitivity_under_one_edge_block':see_under_block,
   'regime_OFF_rootflip':int(offallow['bestmove']!=block_off['bestmove']),
   'regime_SEE_rootflip':int(onallow['bestmove']!=block_on['bestmove']),
   'four_native_cold_conditions':signals})
  print('C3X015_P6S1_NATIVE_EXACT_RETURN',j,'SOURCE_TARGET',int(bool(t['eligible'])),
        'OFF_BLOCK_DELIVERED',block_off['p6s1']['suppressed'],
        'SEE_BLOCK_DELIVERED',block_on['p6s1']['suppressed'],
        'OFF_ORIGINAL_SEE_FLIP',see_no_tt,'BLOCKED_SEE_FLIP',see_under_block,flush=True)
 eligible=[z for z in cases if z['presealed_tt_target']['eligible']]
 delivered=[z for z in cases if z['OFF_delivered'] and z['SEE_delivered']]
 output={'schema':'c3x-015-P6S1-post-outcome-targeted-exact-full64-physical-writer-TT-return-intervention-64x4x2-v1',
 'scientific_scope':'SINGLE_DECLARED_SF16_TT_RETURN_SURGERY_NOT_COMPLETE_CAUSAL_MEDIATION_PROOF',
 'source_r2_sha256':SRC,'P2_prior_SHA256':P2,'P6S0_target_sha256':TARGET_SHA,
 'original_native_processes':512,'all_256_cold_conditions_exact':'256/256',
 'all_P2_allow_conditions_identical':'64/64','all_original_worlds':64,
 'presealed_target_eligible':len(eligible),
 'exact_matching_OFF_suppressed_worlds':sum(z['OFF_delivered'] for z in cases),
 'exact_matching_SEE_suppressed_worlds':sum(z['SEE_delivered'] for z in cases),
 'same_presealed_edge_suppressed_in_both_worlds':len(delivered),
 'original_SEE_root_change_count':sum(z['original_p2_SEE_root_flip'] for z in cases),
 'exact_edge_block_SEE_root_change_count':sum(z['SEEsensitivity_under_one_edge_block'] for z in cases),
 'one_edge_changes_OFF_root_move':sum(z['regime_OFF_rootflip'] for z in cases),
 'one_edge_changes_SEE_root_move':sum(z['regime_SEE_rootflip'] for z in cases),
 'joint_delivered_cases':len(delivered),
 'limits':['Source target is first original OFF executed full64 writer-matched postsource TT cutoff, selected independently of P2 outcome but after disclosure.',
 'Writer sequence and alpha/beta consumed frame must match: a treatment may never encounter the same event, and that is an ABSTAIN/UNDELIVERED result.',
 'Block at most one TT early return; other TT behavior and move legality are original. This is not full natural indirect-effect identification.',
 'P1 C1 prior primary accuracy FAIL remains unmodified.',
 'Worlds share tournament-event clusters; cold-process repeats are not independent games.'],
 'all_64_native_four_cell_interventions':cases}
 Path(a.out).write_text(json.dumps(output,sort_keys=True,indent=2,ensure_ascii=False)+'\n')
 print('C3X015_P6S1_EXACT_TT_RETURN_INTERVENTION_FINAL',
  json.dumps({k:output[k] for k in ('presealed_target_eligible','exact_matching_OFF_suppressed_worlds',
   'exact_matching_SEE_suppressed_worlds','same_presealed_edge_suppressed_in_both_worlds',
   'one_edge_changes_OFF_root_move','one_edge_changes_SEE_root_move',
   'original_SEE_root_change_count','exact_edge_block_SEE_root_change_count')},sort_keys=True),flush=True)
if __name__=='__main__':main()
