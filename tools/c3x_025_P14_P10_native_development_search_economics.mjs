#!/usr/bin/env node
// P14-P10 prospective four-opening ORIGINAL Stockfish16 search economics.
// No prediction of strength/move improvement. Instrumented SF16 C++ via P14-P6.
import {spawn} from 'node:child_process';
import {createInterface} from 'node:readline';
import {writeFileSync} from 'node:fs';
const [original,patched,out]=process.argv.slice(2);
if(!out)throw Error('Usage: node court.mjs ORIGINAL_SF16 PATCHED_SF16 OUT_JSON');
const positions=[
 {id:'ENGLISH6',uci:'position startpos moves c2c4 e7e5 b1c3 g8f6 g2g3 b8c6',fullmove:4},
 {id:'FRENCH8',uci:'position startpos moves e2e4 e7e6 d2d4 d7d5 b1c3 g8f6 e4e5 f6d7',fullmove:5},
 {id:'ITALIAN8',uci:'position startpos moves e2e4 e7e5 g1f3 b8c6 f1c4 f8c5 c2c3 g8f6',fullmove:5},
 {id:'CARO_KANN8',uci:'position startpos moves e2e4 c7c6 d2d4 d7d5 b1c3 d5e4 c3e4 c8f5',fullmove:5}
];
const policies=['SHAM','FIRST','UPPER','LOWER'];
function parseFields(line){
 const out={};for(const word of line.split(' ').slice(3)){
  const i=word.indexOf('=');if(i>0)out[word.slice(0,i)]=word.slice(i+1);
 }
 return out;
}
function execNative(bin,policy,pos,observer) {
 return new Promise((resolve,reject)=>{
  const env={...process.env,C3X025_P14P6_POLICY:policy};
  if(observer)env.C3X025_P14P4_TRACE='1';
  else delete env.C3X025_P14P4_TRACE;
  const p=spawn(bin,[],{env});let phase=0,closed=false;
  const source=[],root=[],uci=[];let fen='',key='';
  const timer=setTimeout(()=>{p.kill('SIGKILL');},35000);
  p.on('error',reject);
  createInterface({input:p.stdout}).on('line',s=>{
   if(s.startsWith('info string c3x025_p14p6 '))source.push(parseFields(s));
   if(s.startsWith('info string c3x025_p14p4 event=ROOT_ATTEMPT '))root.push(parseFields(s));
   if(s.startsWith('Fen: '))fen=s.slice(5);
   if(s.startsWith('Key: '))key=s.slice(5);
   if(s.startsWith('info depth 7 ')||s.startsWith('bestmove '))uci.push(s);
   if(s==='uciok'&&phase===0){
    phase=1;p.stdin.write('setoption name Threads value 1\nsetoption name Hash value 16\nsetoption name Use NNUE value false\nsetoption name MultiPV value 1\nucinewgame\nisready\n');
   }else if(s==='readyok'&&phase===1){
    phase=2;p.stdin.write(pos.uci+'\nd\nisready\n');
   }else if(s==='readyok'&&phase===2){
    phase=3;p.stdin.write('go depth 7\n');
   }else if(s.startsWith('bestmove ')&&phase===3){
    phase=4;p.stdin.write('quit\n');
   }
  });
  p.on('close',code=>{
   if(closed)return;closed=true;clearTimeout(timer);
   try{
    if(code!==0||phase!==4)throw Error('native engine timeout/crash/incomplete '+code);
    const last=uci.filter(x=>x.startsWith('info depth 7 ')&&/\bnodes \d+/.test(x)).at(-1);
    const moves=uci.filter(x=>x.startsWith('bestmove '));
    if(!last||moves.length!==1)throw Error('missing exact completed depth7');
    const score=last.match(/\bscore (cp|mate) (-?\d+)/);
    const nodes=last.match(/\bnodes (\d+)/);
    if(!score||!nodes||!fen||!key)throw Error('original UCI state missing');
    const fields=fen.split(' ');
    if(fields.length!==6||fields[1]!=='w'||Number(fields[5])!==pos.fullmove)
      throw Error('source-precommitted legal-move sequence not fully applied '+pos.id+': '+fen);
    const bestmove=moves[0].split(' ')[1];
    if(!/^[a-h][1-8][a-h][1-8][qrbn]?$/.test(bestmove))throw Error('illegal bestmove UCI shape');
    resolve({bestmove,score:score[1]+':'+score[2],nodes:Number(nodes[1]),
      fen,full_key:key,source,root_attempts:root.length,
      aspiration_retries:root.filter(x=>x.window_class!=='INSIDE').length});
   }catch(err){reject(err);}
  });
  p.stdin.write('uci\n');
 });
}
function core(x){return {bestmove:x.bestmove,score:x.score,nodes:x.nodes,fen:x.fen,key:x.full_key};}
function summary(x,policy,base){
 let acts=x.source.filter(y=>y.kind==='ACTUATED'&&y.mutated==='1');
 if(acts.length>1|| (policy==='SHAM'&&acts.length))
   throw Error('wrong number of actual original source interventions');
 for(const row of x.source){
  const val=Number(row.score),beta=Number(row.beta),bound=Number(row.bound);
  if(!Number.isFinite(val)||!Number.isFinite(beta)||!Number.isFinite(bound)||
     row.side!==(val>=beta?'LOWER':'UPPER')||
     !(bound&(val>=beta?2:1))||
     Number(row.stored_depth)<Number(row.required_depth))
   throw Error('unproven/incorrect original source eligible TT-bound branch');
 }
 if(acts.some(y=>y.policy!==policy ||
    (policy==='UPPER'&&y.side!=='UPPER')||
    (policy==='LOWER'&&y.side!=='LOWER')))
  throw Error('source directional operator mismatched');
 return {
  bestmove:x.bestmove,score:x.score,nodes:x.nodes,
  node_difference_vs_original:x.nodes-base.nodes,
  changed_move:x.bestmove!==base.bestmove,
  physical_operator_actuated:acts.length===1,
  actuated_bound_side:acts[0]?.side||null,
  original_source_first_seen_bound_side:x.source[0]?.side||null,
  root_attempts:x.root_attempts,
  aspiration_retry_count:x.aspiration_retries,
  no_contact:!acts.length
 };
}
const result={schema:'c3x025-P14-P10-P0-four-early-opening-source-TT-policy-development-court-v1',
 preexperiment_human_Git:'c18431c81fb8da2979eb48e9e55c8a42f00d696c',
 original_source_revision:'68e1e9b3811e16cad014b590d7443b9063b3eb52',
 depth:7,threads:1,hash_MB:16,NNUE:false,
 two_cold_repeats_every_arm:true,source_original_p6_cutoff_operator:true,
 categories:'FOUR_FROZEN_DEVELOPMENT_OPENINGS_ONLY_NOT_M7_OR_ELO_HOLDOUT',
 source_original_numeric_TT_bound_chess_minimax_proven:false,
 native_time_control_or_Elo:0,
 cases:{}};
for(const pos of positions){
 const a=await execNative(original,'SHAM',pos,false);
 const b=await execNative(original,'SHAM',pos,false);
 const o=await execNative(patched,'SHAM',pos,false);
 if(JSON.stringify(core(a))!==JSON.stringify(core(b))||
    JSON.stringify(core(a))!==JSON.stringify(core(o)))
  throw Error('original cold repeat/observer off parity fail '+pos.id);
 const cases={};
 for(const policy of policies){
  const first=await execNative(patched,policy,pos,true);
  const repeat=await execNative(patched,policy,pos,true);
  if(JSON.stringify(first)!==JSON.stringify(repeat))throw Error('cold source trace instability '+pos.id+' '+policy);
  cases[policy]=summary(first,policy,a);
  if(policy==='SHAM'&&JSON.stringify(core(first))!==JSON.stringify(core(a)))
    throw Error('original vs sham parity fail '+pos.id);
 }
 result.cases[pos.id]={position:pos.uci,original:core(a),policies:cases};
 console.log('C3X025_P14P10_DEVELOPMENT_SEARCH_ECONOMICS',JSON.stringify({position:pos.id,
   baseline:{move:a.bestmove,nodes:a.nodes,score:a.score},
   arms:Object.fromEntries(Object.entries(cases).map(([arm,x])=>[arm,{
     move:x.bestmove,nodes:x.nodes,delta:x.node_difference_vs_original,
     actuated:x.physical_operator_actuated,side:x.actuated_bound_side,
     retries:x.aspiration_retry_count
   }]))}));
}
writeFileSync(out,JSON.stringify(result,null,2)+'\n');
console.log('C3X025_P14P10_SOURCE_DISJOINT_OPENING_POLICY_CONTRAST_NATIVE_PASS');
