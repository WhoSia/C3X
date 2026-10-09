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
 tt=typed('c3x015_tt_provenance')
 result['tt']={k:(v if k=='stream' else int(v)) for k,v in tt.items()}
 return result
def core(z):return {k:z[k] for k in CORE}
def main():
 p=argparse.ArgumentParser()
 for k in ('source','prior-p2','engine','out'):p.add_argument('--'+k,required=True)
 a=p.parse_args();source=load(a.source,SRC);prior=load(a.prior_p2,P2)
 rows=[];orig=prior['pin_worlds'];must(len(source['pin_roots'])==len(orig)==64,'COHORT_NOT64')
 for j,(r,base) in enumerate(zip(source['pin_roots'],orig),1):
  hist=r['full_history_uci'][:r['root_ply']];ob=r['objects'][0]
  must(sha(r['root_sixfield_fen'].encode())==base['fen_sha256'],'P2_SOURCE_CASE_MISMATCH')
  sq=chess.parse_square(ob['pinned_square']);pn=chess.parse_square(ob['pinner_square'])
  world={'source_game_history_uci':hist,'pinned_square':ob['pinned_square'],'pinning_square':ob['pinner_square']}
  arms={}
  for mode in ('OFF','ROOT_OBJECT_SEE_UNMASK'):
   native=main_engine(a.engine,world,mode)
   obs=trace(a.engine,hist,mode,sq,pn)
   must(core(native)==core(obs),'WINDOW_OBSERVER_NOT_COLD_DETERMINISTIC')
   must(native['object_guard']==obs['guard'],'WINDOW_OBSERVER_GUARD_DRIFT')
   arms[mode]=obs
  off=arms['OFF'];on=arms['ROOT_OBJECT_SEE_UNMASK']
  must(core(off)==base['native_pristine_OFF'],'WINDOW_OBSERVER_ALTERS_P2_ORIGINAL')
  must(core(on)==base['native_ROOT_SEE_UNMASK'],'WINDOW_OBSERVER_ALTERS_P2_TREATMENT')
  fire=on['guard']['target_fired'];wo=off['window'];wt=on['window']
  eqprefix=(wo['first_key']==wt['first_key'] and wo['first_search_ordinal']==wt['first_search_ordinal'] and
            wo['prefix_fnv64']==wt['prefix_fnv64'] and wo['entry_alpha']==wt['entry_alpha'] and
            wo['entry_beta']==wt['entry_beta'] and wo['entry_depth']==wt['entry_depth'])
  if fire:must(eqprefix,'FIRST_SOURCE_ELIGIBLE_SITE_PREPREFIX_DIFFERENCE')
  if fire:must(wo['first_candidate']==wt['first_candidate']==1,'SOURCE_POTENTIAL_NOT_MATCHED')
  if not fire:must(core(off)==core(on),'UNFIRED_DIVERGENCE_IN_P3')
  before=wo['stream'].rstrip('|').split('|') if wo['stream'] else []
  after=wt['stream'].rstrip('|').split('|') if wt['stream'] else []
  idx=next((i for i,(x,y) in enumerate(zip(before,after),1) if x!=y),None)
  kind='NO_WINDOWED_SEARCH_ENTRY_DIFFERENCE_IN_RECORDED_SUFFIX'
  detail=None
  if idx is not None:
   aa=before[idx-1].split(':');bb=after[idx-1].split(':')
   kind=('WINDOW_OR_DEPTH_DIFFERENCE_SAME_POSITION' if aa[0]==bb[0] else 'SEARCH_POSITION_PATH_DIFFERENCE')
   detail={'off_event':before[idx-1],'treated_event':after[idx-1]}
  elif len(before)!=len(after):kind='SEARCH_SUFFIX_LENGTH_DIFFERENCE'
  ttbefore=wo_t=off['tt']['stream'].rstrip('|').split('|') if off['tt']['stream'] else []
  ttafter=wt_t=on['tt']['stream'].rstrip('|').split('|') if on['tt']['stream'] else []
  ttidx=next((k for k,(q,t) in enumerate(zip(ttbefore,ttafter),1) if q!=t),None)
  if ttidx is None and len(ttbefore)!=len(ttafter):ttidx=min(len(ttbefore),len(ttafter))+1
  rows.append({'first_TT_recorded_difference_index':ttidx,
    'first_TT_records':{'OFF':ttbefore[ttidx-1] if ttidx and ttidx<=len(ttbefore) else None,
                         'TREAT':ttafter[ttidx-1] if ttidx and ttidx<=len(ttafter) else None},
    'TT_observed_OFF':{k:v for k,v in off['tt'].items() if k!='stream'},
    'TT_observed_TREAT':{k:v for k,v in on['tt'].items() if k!='stream'},
    'TT_first_recorded_stream_OFF':ttbefore[:10],
    'TT_first_recorded_stream_TREAT':ttafter[:10],
    'ordinal':j,'fen_sha256':base['fen_sha256'],'y_changed_bestmove':base['y_changed_bestmove'],
    'actual_site_fires':fire,'first_site_aligned_prefix':eqprefix,'first_candidate_OFF':wo,
    'first_candidate_TREATED':{k:v for k,v in wt.items() if k!='stream'},
    'first_recorded_search_suffix_difference_index':idx,'first_suffix_divergence_kind':kind,
    'first_suffix_differing_event':detail})
  print('C3X015_CSWP_P3',j,'FIRE',fire,'SAME_BEFORE_SITE',eqprefix,
        'AFTER_SITE_FIRST_WINDOW_EVENT',idx,kind,flush=True)
 out={'schema':'c3x-015-CSWP-P4-physical-TT-writer-reader-bound-window-after-SEE-v1',
   'scope':'POST_OUTCOME_MECHANISM_RECONSTRUCTION_AFTER_P2','source_sha256':SRC,'P2_sha256':P2,
   'native_new_processes':256,'cold_pair_exact_128':True,'pristine_P2_UCI_equivalence_128':True,
   'fired_worlds':sum(r['actual_site_fires']>0 for r in rows),
   'first_prefix_aligned_fired_worlds':sum(r['actual_site_fires']>0 and r['first_site_aligned_prefix'] for r in rows),
   'observed_post_candidate_search_entry_divergence_worlds':sum(r['first_recorded_search_suffix_difference_index'] is not None for r in rows),
   'first_TT_record_mismatch_worlds':sum(r['first_TT_recorded_difference_index'] is not None for r in rows),
   'TT_cutoff_witness_worlds':sum(r['TT_observed_TREAT']['taken_cutoffs']>0 for r in rows),
   'TT_fullkey_exact_read_total_observed':sum(r['TT_observed_TREAT']['key_exact'] for r in rows),
   'limits':['Active alpha/beta is the search frame ENTRY window, not necessarily updated current window at SEE invocation.',
    'First source candidate is not necessarily first alpha-beta divergence.',
    '4096 post-candidate search entries and 2048 TT events are bounded.',
    'Physical writer→reader is observed not necessarily a but-for causal mediator.',
    'TT read/cutoff observation is not a source intervention on TT, thus no causal necessity proof.',
    'No new treatment outcomes used to refit frozen predictor.'], 'rows':rows}
 Path(a.out).write_text(json.dumps(out,sort_keys=True,indent=2,ensure_ascii=False)+'\n')
 print('C3X015_CSWP_P3_SUMMARY',json.dumps({k:out[k] for k in ('fired_worlds','first_prefix_aligned_fired_worlds',
   'observed_post_candidate_search_entry_divergence_worlds','first_TT_record_mismatch_worlds','TT_cutoff_witness_worlds')}),flush=True)
if __name__=='__main__':main()
