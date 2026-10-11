#!/usr/bin/env node
// Strict source-native P13 UCI court. Evidence is one actual original process.
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
 const events=[];
 for(const line of lines.filter(l=>l.startsWith('info string c3x025_p13 '))){
  if(!active)throw Error('NEGATIVE_CONTROL_LEAKED_P13_EVENT');
  const f={};for(const part of line.slice('info string c3x025_p13 '.length).split(' ')){
   const z=part.split('=');if(z.length!==2||Object.hasOwn(f,z[0]))throw Error('MALFORMED_P13_EVENT');
   f[z[0]]=z[1];
  }
  events.push(f);
 }
 return {bestmove:best[0],nodes,events};
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
 writeFileSync(destination,JSON.stringify(result,null,2)+'\n');
 console.log('C3X025_P13_NATIVE_SOURCE_COURT',JSON.stringify(result));
