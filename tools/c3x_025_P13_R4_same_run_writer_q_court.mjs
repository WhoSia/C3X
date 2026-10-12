#!/usr/bin/env node
// Strict source-native P13-R4 single-run original writer UCI court. Evidence is one actual original process.
import {spawn} from 'node:child_process';
import {createInterface} from 'node:readline';
import {writeFileSync} from 'node:fs';
const [original,observed,destination]=process.argv.slice(2);
if(!original||!observed||!destination)throw Error('usage: original observed out.json');
function run(binary,active){
 return new Promise((resolve,reject)=>{
  const p=spawn(binary,[],{env:{...process.env,C3X025_P8_TT_FIELDS:active?'1':'0'}});
  const lines=[];let finished=false,phase=0;
  const timer=setTimeout(()=>rejectOnce(Error('ENGINE_TIMEOUT')),90000);
  function rejectOnce(e){if(finished)return;finished=true;clearTimeout(timer);p.kill('SIGKILL');reject(e);}
  p.on('error',rejectOnce);
  const rl=createInterface({input:p.stdout});
  rl.on('line',line=>{
   lines.push(line);
   if(line==='uciok'&&phase===0){phase=1;p.stdin.write('setoption name Threads value 1\nsetoption name Hash value 16\nsetoption name MultiPV value 1\nsetoption name Use NNUE value false\nucinewgame\nisready\n');}
   else if(line==='readyok'&&phase===1){phase=2;p.stdin.write('position startpos\ngo depth 7\n');}
   else if(line.startsWith('bestmove ')&&phase===2){phase=3;p.stdin.write('quit\n');}
  });
  p.on('close',code=>{if(finished)return;finished=true;clearTimeout(timer);if(code!==0)reject(Error('NATIVE_EXIT_'+code));else resolve(lines);});
  p.stdin.write('uci\n');
 });
}
function parse(lines,active){
 const best=lines.filter(l=>l.startsWith('bestmove ')).map(l=>l.split(' ')[1]);
 const infos=lines.filter(l=>/^info depth 7 /.test(l)&&/\bnodes \d+/.test(l));
 if(best.length!==1||infos.length===0)throw Error('UCI_TERMINAL_MISSING');
 const nodes=Number(infos.at(-1).match(/\bnodes (\d+)/)[1]);
 const events=[];const source11=[],source12=[];
 function tagged(l,prefix){const f={};for(const token of l.slice(prefix.length).split(" ")){const n=token.indexOf("=");if(n<1||n===token.length-1||Object.hasOwn(f,token.slice(0,n)))throw Error("R4_SOURCE_FIELD_MALFORMED");f[token.slice(0,n)]=token.slice(n+1);}return f;}
 for(const line of lines){if(line.startsWith("info string c3x025_p11 "))source11.push(tagged(line,"info string c3x025_p11 "));if(line.startsWith("info string c3x025_p12 "))source12.push(tagged(line,"info string c3x025_p12 "));}
 for(const line of lines.filter(l=>l.startsWith('info string c3x025_p13 '))){
  if(!active)throw Error('NEGATIVE_CONTROL_LEAKED_P13_EVENT');
  const f={};for(const part of line.slice('info string c3x025_p13 '.length).split(' ')){
   const z=part.split('=');if(z.length!==2||Object.hasOwn(f,z[0]))throw Error('MALFORMED_P13_EVENT');
   f[z[0]]=z[1];
  }
  events.push(f);
 }
 return {bestmove:best[0],nodes,events,source11,source12};
}
const a=[parse(await run(original,false),false),parse(await run(original,false),false)];
const b=[parse(await run(observed,true),true),parse(await run(observed,true),true)];
const off=parse(await run(observed,false),false);
for(const x of [...a,...b,off])if(x.bestmove!=='b1c3'||x.nodes!==8657)throw Error('P13_OBSERVER_CHANGED_ORIGINAL_NATIVE_UCI_OR_NODES');
if(JSON.stringify(b[0])!==JSON.stringify(b[1]))throw Error('P13_NONDETERMINISTIC_COLD_NATIVE_EVENTS');
const root=b[0];let direct=0,best=0;const directIds=new Set();
for(const e of root.events){
 if(e.kind==='Q_DIRECT_PARENT_ASSIGN'){
  const raw=Number(e.child_tt_score),assigned=Number(e.assigned_score);
  const parent=Number(e.parent_id),child=Number(e.child_id),rid=Number(e.root_id);
  if(assigned!==-raw||child<=parent||parent<1||rid<1)throw Error('NATIVE_ASSIGNMENT_FALSE_CERT');
  const id=String(child)+':'+String(parent);if(directIds.has(id))throw Error('SPLICED_DYNAMIC_CHILD');directIds.add(id);
  direct++;
 } else if(e.kind==='Q_BEST_VALUE_ASSIGNED'){
  if(e.final_root_mediation!=='0')throw Error('FALSE_ROOT_CAUSAL_CLAIM');best++;
 } else if(!['Q_DIRECT_CENSORED','Q_BEST_CENSORED'].includes(e.kind))throw Error('UNKNOWN_SOURCE_EVENT');
}
if(direct>24||best>24)throw Error('CLASS_QUOTA_BREACH');
const result={schema:'c3x025-P13-native-q-TT-direct-child-parent-court-v1',
 real_original_SF16:true,original_depth:7,original_UCI:root.bestmove,original_nodes:root.nodes,
 observer_cold_repeat_exact:true,original_observer_optout_parity:true,
 exact_source_site:'qsearch_native_move_recursion',direct_TT_parent_score_assignments:direct,
 candidate_best_value_updates:best,
 direct_TT_assignments_verdict:direct?'NATIVE_DIRECT_Q_ASSIGNMENT_PARTIAL_PASS':'HOLD_NO_DIRECT_TT_CONTACT_IN_Q_SITE',
 natural_TT_SEE_root_mediation_proven:false,chess_strength_or_speedup_proven:false,
 other_active_call_sites:'CENSORED_SITE'};

// Additional R4 audit: actual original full64 field writer from P8 metadata,
// and (where P11 cap permits) same-run P11 return -> P12 source/frame -> P13.
const native11=new Map(),frames=new Map(),sources=new Map();
for(const e of root.source11)if(['TT_Q_RETURN','TT_MAIN_RETURN'].includes(e.kind)){
 const serial=Number(e.serial);if(native11.has(serial))throw Error('R4_DUPLICATE_TT_RETURN_SERIAL');native11.set(serial,e);
}
for(const e of root.source12){
 if(e.kind==='SOURCE_EVENT'){let serial=Number(e.serial);if(sources.has(serial))throw Error('R4_DUPLICATE_SOURCE_EVENT');sources.set(serial,e);}
 if(e.kind==='TT_RETURN_FRAME_EXIT'){let id=Number(e.call_id);if(frames.has(id))throw Error('R4_DUPLICATE_EXIT');frames.set(id,e);}
}
let r4Writer=0,r4Joined=0,r4Censored=0,joinedBest=0;
const assignedChildren=new Map();
for(const e of root.events.filter(e=>e.kind==='Q_DIRECT_PARENT_ASSIGN')){
 const writer=Number(e.writer_serial),returned=Number(e.return_serial);
 const child=Number(e.child_id),parent=Number(e.parent_id),raw=Number(e.child_tt_score);
 const originalScore=Number(e.assigned_score),exact=Number(e.writer_exact);
 if(![writer,returned,child,parent,raw,originalScore,exact].every(Number.isSafeInteger)||
    ![0,1].includes(exact)||returned>=Number(e.serial)||returned<=0||originalScore!==-raw)
   throw Error('R4_INVALID_REAL_TT_RETURN_METADATA');
 if(assignedChildren.has(child))throw Error('R4_DUPLICATE_ACTUAL_CHILD_VALUE');
 assignedChildren.set(child,e);
 if(exact===1){
   if(writer<=0||writer>=returned)throw Error('R4_WRITER_MISSING_OR_NONPRECEDING');
   r4Writer++;
 }
 const ret=native11.get(returned);
 if(!ret){r4Censored++;continue;}
 if(ret.kind!=='TT_Q_RETURN'||Number(ret.value)!==raw||
    Number(ret.score_writer)!==writer||Number(ret.score_writer_exact)!==exact)
    throw Error('R4_ORIGINAL_P11_SCORE_WRITER_RETURN_MISMATCH');
 const frame=sources.get(returned),exit=frames.get(child);
 if(!frame||frame.source_kind!=='TT_Q_RETURN'||
    Number(frame.call_id)!==child||Number(frame.parent_id)!==parent||
    Number(frame.root_id)!==Number(e.root_id)||
    !exit||Number(exit.call_id)!==child||Number(exit.parent_id)!==parent||
    Number(exit.value)!==raw||Number(exit.root_id)!==Number(e.root_id))
    throw Error('R4_P12_NATIVE_CALL_EXIT_OR_SOURCE_DOES_NOT_MATCH');
 if(exact===1)r4Joined++;
}
for(const e of root.events.filter(e=>e.kind==='Q_BEST_VALUE_ASSIGNED')){
 const a=assignedChildren.get(Number(e.child_id));if(!a)continue;
 if(Number(a.parent_id)!==Number(e.parent_id)||
    Number(a.assigned_score)!==Number(e.assigned_score)||
    Number(a.move_code)!==Number(e.move_code)||
    Number(a.serial)>=Number(e.serial))throw Error('R4_FALSE_BEST_JOIN');
 joinedBest++;
}
result.R4_full64_original_score_writer_exact_at_native_q_child_return=r4Writer;
result.R4_P11_P12_P13_R4_same_run_log_visible_complete_writer_return_exit_assignment_join=r4Joined;
result.R4_P11_first24_public_source_class_not_logged_at_P13_return=r4Censored;
result.R4_parent_bestValue_child_join_visible=joinedBest;
result.R4_coverage='QSEARCH_ONLY';
result.R4_same_run_writer_metadata_observed_but_not_an_exhaustive_TT_return_total=true;
result.R4_scientific_verdict=r4Joined?'SAME_RUN_EXACT_WRITER_RETURN_PARENT_Q_ASSIGNMENT_PARTIAL_PASS':
 r4Writer?'WRITER_AT_REAL_RETURN_PASS_LOG_VISIBLE_CHAIN_CENSORED':'HOLD_NO_FULL64_WRITER_EXACT';
result.R4_natural_SEE_mediation_proven=false;

 writeFileSync(destination,JSON.stringify(result,null,2)+'\n');
 console.log('C3X025_P13_NATIVE_SOURCE_COURT',JSON.stringify(result));
