#!/usr/bin/env node
// P14-P1: P14-P0 arms on preregistered EXPOSED development positions, inspect
// actual native source qsearch trace and final original root contender set.
import {spawn} from 'node:child_process';
import {createInterface} from 'node:readline';
import {writeFileSync} from 'node:fs';
const [original,observer,output]=process.argv.slice(2);
if(!original||!observer||!output)throw Error('usage: original observer report.json');
const [sourceFile,outcomeFile]=process.argv.slice(5);
if(!sourceFile||!outcomeFile)throw Error('R3 source+actual M6 score evidence missing');
const {readFileSync}=await import('node:fs');
const {createHash}=await import('node:crypto');
const raw=readFileSync(sourceFile);
if(createHash('sha256').update(raw).digest('hex')!=='45d758947b6f224901f2674eaed4dc1dc34f4d5a439ccd62fa408393dd7c2a80')
 throw Error('R3_ORIGINAL_JULY_SOURCE_SHA_CHANGED');
const source=JSON.parse(raw),actual=JSON.parse(readFileSync(outcomeFile));
const root=source.selected[27],exposed=actual.per_game[27];
if(source.selected.length!==64||root.id!==28||exposed.id!==28||
 root.source_game_sha256!==exposed.source_game_sha256||
 exposed.true_root_choice_changed!==true||
 actual.physical_qscore_original_contacts!==64)
 throw Error('R3_PREDECLARED_POST_OUTCOME_ROOT28_REAL_FIRST_CONDITION_ABSENT');
const positions=[{
 id:'POSTOUTCOME_EXPOSED_JULY2026_M6_REAL_ROOT_FLIP_GAME28',
 command:'position fen '+root.fen4+' '+root.source_halfmove_clock+' '+root.source_fullmove_number
}];
const arms={SHAM:0,SCORE:1,HINT:2,BOTH:3,GUARD:0};
function parseTags(line,prefix){
 const o={};for(const part of line.slice(prefix.length).trim().split(/\s+/)){
  const i=part.indexOf('=');if(i<1||i===part.length-1||Object.hasOwn(o,part.slice(0,i)))throw Error('INVALID_NATIVE_FIELD');
  o[part.slice(0,i)]=part.slice(i+1);
 }return o;
}
function number(x,label){if(!/^\d+$/.test(String(x))||!Number.isSafeInteger(Number(x)))throw Error('NATIVE_INTEGER_INVALID_'+label);return Number(x);}
function execute(bin,enabled,arm,position){
 return new Promise((resolve,reject)=>{
  const p=spawn(bin,[],{env:{...process.env,C3X025_P8_TT_FIELDS:enabled?'1':'0',C3X025_P14_ARM:arm==='GUARD'?'SHAM':arm,C3X025_P14P3_POLICY:arm==='GUARD'?'GUARD':'SHAM'}});
  const lines=[];let phase=0,done=false;
  const timer=setTimeout(()=>fail(Error('NATIVE_UCI_TIMEOUT_'+position.id+'_'+arm)),120000);
  function fail(e){if(done)return;done=true;clearTimeout(timer);p.kill('SIGKILL');reject(e);}
  p.on('error',fail);
  createInterface({input:p.stdout}).on('line',s=>{
   lines.push(s);
   if(s==='uciok'&&phase===0){phase=1;p.stdin.write('setoption name Threads value 1\nsetoption name Hash value 16\nsetoption name MultiPV value 1\nsetoption name Use NNUE value false\nucinewgame\nisready\n');}
   else if(s==='readyok'&&phase===1){phase=2;p.stdin.write(position.command+'\ngo depth 7\n');}
   else if(s.startsWith('bestmove ')&&phase===2){phase=3;p.stdin.write('quit\n');}
  });
  p.on('close',code=>{
   if(done)return;done=true;clearTimeout(timer);
   if(code!==0){reject(Error('NATIVE_EXIT_'+code));return;}
   try{
    const b=lines.filter(x=>x.startsWith('bestmove '));
    const last=lines.filter(x=>/^info depth 7 /.test(x)&&/\bnodes \d+/.test(x)).at(-1);
    if(b.length!==1||!last)throw Error('MISSING_DEPTH7_UCI');
    const bestmove=b[0].split(/\s+/)[1],nodes=number(last.match(/\bnodes (\d+)/)?.[1],'nodes');
    if(!/^[a-h][1-8][a-h][1-8][qrbn]?$/.test(bestmove))throw Error('ILLEGAL_UCI_FORMAT');
    const pv=last.match(/(?:^| )pv ([a-h][1-8][a-h][1-8][qrbn]?(?: [a-h][1-8][a-h][1-8][qrbn]?)*)/);
    const score=last.match(/(?:^| )score (cp|mate) (-?\d+)/);
    const contacts=[],frames=[],rootSets=[],p14p2Q=[],p14p2Root=[],p14p3Guard=[];
    for(const s of lines){
     if(s.startsWith('info string c3x025_p14 ')) contacts.push(parseTags(s,'info string c3x025_p14 '));
     if(s.startsWith('info string c3x025_p14p3 ')) p14p3Guard.push(parseTags(s,'info string c3x025_p14p3 '));
     if(s.startsWith('info string c3x025_p14p2 ')){
      const x=parseTags(s,'info string c3x025_p14p2 ');
      if(x.kind==='Q_EVENT')p14p2Q.push(x);
      else if(x.kind==='ROOT_CANDIDATE')p14p2Root.push(x);
      else throw Error('P14P2_UNKNOWN_NATIVE_EVENT');
     }
     if(s.startsWith('info string c3x025_p14p1 ')){
      const x=parseTags(s,'info string c3x025_p14p1 ');
      if(x.kind==='ROOT_FRAME')frames.push(x);
      else if(x.kind==='ROOT_CONTENDER_SET')rootSets.push(x);
      else throw Error('UNKNOWN_SOURCE_EVENT_CLASS');
     }
    }
    if(!enabled&&(contacts.length||frames.length||rootSets.length||p14p3Guard.length))throw Error('OBSERVER_OFF_SOURCE_TAG_LEAK');
    if(enabled&&rootSets.length!==1)throw Error('ROOT_SET_NOT_FROM_ACTUAL_NATIVE_FINAL_SOURCE_ONCE');
    resolve({bestmove,nodes,score:score?score[1]+':'+score[2]:'NOT_IN_UCI',pv:pv?pv[1]:'NOT_IN_UCI',
      contacts,p14p2Q,p14p2Root,p14p3Guard,frames:frames.map(f=>({root_id:f.root_id,qhash:f.qhash,qevents:f.qevents,qreturns:f.qreturns,qbest:f.qbest})),
      root:rootSets.length?rootSets[0]:null});
   }catch(e){reject(e);}
  });
  p.stdin.write('uci\n');
 });
}
const comparisons={};
const compact=x=>({bestmove:x.bestmove,nodes:x.nodes,score:x.score,pv:x.pv,
  qframe_hashes:x.frames.map(f=>f.qhash),qframe_counts:x.frames.map(f=>f.qevents),
  candidate_digest:x.root?.digest??null,candidate_viable:x.root?number(x.root.viable,'viable'):null,
  candidate_count:x.root?number(x.root.count,'count'):null,root_score:x.root?.first_score??null});
for(const pos of positions){
 const orig1=await execute(original,false,'SHAM',pos);
 const orig2=await execute(original,false,'SHAM',pos);
 if(JSON.stringify(orig1)!==JSON.stringify(orig2))throw Error('NONDETERMINISTIC_ORIGINAL_'+pos.id);
 const sham1=await execute(observer,true,'SHAM',pos);
 const sham2=await execute(observer,true,'SHAM',pos);
 if(JSON.stringify(sham1)!==JSON.stringify(sham2))throw Error('NONDETERMINISTIC_SHAM_'+pos.id);
 const off=await execute(observer,false,'SHAM',pos);
 if(JSON.stringify({bestmove:sham1.bestmove,nodes:sham1.nodes,score:sham1.score,pv:sham1.pv})!==
    JSON.stringify({bestmove:orig1.bestmove,nodes:orig1.nodes,score:orig1.score,pv:orig1.pv})||
    JSON.stringify({bestmove:off.bestmove,nodes:off.nodes,score:off.score,pv:off.pv})!==
    JSON.stringify({bestmove:orig1.bestmove,nodes:orig1.nodes,score:orig1.score,pv:orig1.pv}))
     throw Error('SHAM_OR_OBSERVER_OFF_DIVERGED_FROM_ORIGINAL_'+pos.id);
 const results={};let rootChanged=0,traceChanged=0,scoreChanged=0;
 for(const [arm,mask] of Object.entries(arms)){
  const a=arm==='SHAM'?sham1:await execute(observer,true,arm,pos);
  const b=arm==='SHAM'?sham2:await execute(observer,true,arm,pos);
  if(JSON.stringify(a)!==JSON.stringify(b))throw Error('NONDETERMINISTIC_ARM_'+pos.id+'_'+arm);
  const kinds=new Set();
  const guardedEvents=a.p14p3Guard.filter(x=>x.kind==='GUARD_ACTUATED');
  const firstGuard=a.p14p3Guard.filter(x=>x.kind==='FIRST_ORIGINAL_QSCORE_CONTACT');
  if(firstGuard.length>1||guardedEvents.length>1 ||
     guardedEvents.some(x=>x.mutated!=='1'||x.eligible!=='1'||x.policy!=='1')||
     (arm!=='GUARD'&&guardedEvents.length!==0) ||
     (arm==='GUARD'&&a.p14p3Guard.some(x=>x.policy!=='1')))
     throw Error('P14P3_ORIGINAL_GUARD_SOURCE_CONTRACT_FAIL');
  for(const e of a.contacts){
   if(!['Q_SCORE_RETURN_BOUND_CONTACT','Q_NONZERO_HINT_CONTACT'].includes(e.kind)||
       kinds.has(e.kind)||number(e.arm,'arm')!==mask)throw Error('INVALID_OPERATOR_CONTACT');
   kinds.add(e.kind);
   if(number(e.mutated,'mutated')!==((e.kind==='Q_SCORE_RETURN_BOUND_CONTACT'?(mask&1):(mask&2))?1:0))
     throw Error('INTERVENTION_NOT_EXECUTED_AS_REGISTERED');
  }
  const scoreContact=kinds.has('Q_SCORE_RETURN_BOUND_CONTACT');
  const hintContact=kinds.has('Q_NONZERO_HINT_CONTACT');
  
  const baseQ=sham1.p14p2Q,curQ=a.p14p2Q;
  let first=0;while(first<Math.min(baseQ.length,curQ.length)&&
    JSON.stringify(baseQ[first])===JSON.stringify(curQ[first]))first++;
  const mismatch=first<Math.min(baseQ.length,curQ.length)||baseQ.length!==curQ.length;
  const rootVectorChanged=JSON.stringify(a.p14p2Root)!==JSON.stringify(sham1.p14p2Root);
  if(a.p14p2Root.length===0)throw Error('P14P2_NATIVE_INDIVIDUAL_ROOT_SET_MISSING');
  const firstMismatch=mismatch?{index:first,baseline:baseQ[first]??null,intervention:curQ[first]??null,
    preceding:baseQ.slice(Math.max(0,first-2),first)}:null;

  const state=compact(a),base=compact(sham1);
  results[arm]={...state,
   first_observed_qsource_difference:firstMismatch,full_q_source_count:curQ.length,
   root_candidate_fields_differ:rootVectorChanged,root_candidates:a.p14p2Root,
   native_guard:firstGuard[0]??null,native_guard_actual_actuation:guardedEvents.length,
   guard_actuation_event:guardedEvents[0]??null,
   source_operator_contact:{score:scoreContact,hint:hintContact},
   required_operator_contact:arm==='GUARD'?(guardedEvents.length===1?'PASS_GUARDED_PHYSICAL_ACTUATION':'HOLD_NO_ELIGIBLE_QSCORE_GUARD'):
      (!((mask&1)&&!scoreContact)&&!((mask&2)&&!hintContact))?'PASS':'HOLD',
   root_changed:a.bestmove!==sham1.bestmove,
   root_score_changed:a.score!==sham1.score,
   root_contender_set_digest_changed:a.root?.digest!==sham1.root?.digest,
   q_source_sequence_digest_changed:JSON.stringify(state.qframe_hashes)!==JSON.stringify(base.qframe_hashes),
   node_delta:a.nodes-sham1.nodes};
  if(arm!=='SHAM'){rootChanged+=Number(results[arm].root_changed);
   traceChanged+=Number(results[arm].q_source_sequence_digest_changed||results[arm].root_contender_set_digest_changed);
   scoreChanged+=Number(results[arm].root_score_changed);}
 }
 comparisons[pos.id]={position_command:pos.command,development_only:true,original:compact(orig1),
  arms:results,root_changed_arms:rootChanged,
  downstream_trace_changed_arms:traceChanged,root_score_changed_arms:scoreChanged};
}
const c=comparisons.POSTOUTCOME_EXPOSED_JULY2026_M6_REAL_ROOT_FLIP_GAME28;
if(!c||c.original.bestmove!==exposed.untouched_original_root_UCI||
 c.original.nodes!==exposed.original_nodes||
 c.arms.SCORE.bestmove!==exposed.real_SF16_SCORE_intervention_bestmove||
 c.arms.SCORE.nodes!==exposed.treated_nodes||
 c.arms.SCORE.root_changed!==true)
 throw Error('R3_POSTOUTCOME_DIAGNOSIS_MUST_REPRODUCE_FIRST_M6_NATIVE_FLIP');
const receipt={schema:'c3x025-P14-P3-R3-postoutcome-original-native-root28-tt-qsource-contender-first-mismatch-v1',
 source:'original Stockfish16 git 68e1e9b3811e16cad014b590d7443b9063b3eb52',
 precommitted_positions:positions.map(p=>p.id),development_exposed_only:true,game28_selected_after_prospective_M6_root_flip_seen:true,
 original_prospective_M6_B_run:38198653228,
 original_vs_sham_vs_observer_off_exact:true,cold_repeats_per_arm:2,depth:7,
 positions:comparisons,
 verdict:'P14P3_REAL_ORIGINAL_TT_CONTEXT_GUARD_SOURCE_ACTUATION_AND_ROOT_COMPETITION_DIAGNOSTIC_NOT_SAFETY_PROOF',
 scientific_limit:'A source intervention and changed digest are not a natural TT-to-SEE effect; no counterfactual root causation except the scoped source-policy intervention.',
 M5_prospective_prediction:'SEPARATE_SOURCE_ONLY_PRIOR_SEAL',P15_speed_Elo:'NOT_MEASURED'};
writeFileSync(output,JSON.stringify(receipt,null,2)+'\n');
console.log('C3X025_P14_P1_ACTUAL_NATIVE_SOURCE_DIVERGENCE',JSON.stringify({
 positions:Object.fromEntries(Object.entries(comparisons).map(([k,v])=>[k,{
 baseline:v.original,
 summary:Object.fromEntries(Object.entries(v.arms).map(([arm,x])=>[arm,{
  uci:x.bestmove,nodes:x.nodes,score:x.score,root_changed:x.root_changed,
  root_set_changed:x.root_contender_set_digest_changed,qhash_changed:x.q_source_sequence_digest_changed,
  contact:x.required_operator_contact,guard_actuations:x.native_guard_actual_actuation,first_original_guard_contact:x.native_guard}] ))}]))}));
