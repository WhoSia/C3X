#!/usr/bin/env node
// P14-P0 matched native-sham factorial; source qscore vs qhint physically
// distinct interventions, deterministic repetitions, no M5/Elo inference.
import {spawn} from 'node:child_process';
import {createInterface} from 'node:readline';
import {writeFileSync} from 'node:fs';
const [original,observer,dest]=process.argv.slice(2);
if(!original||!observer||!dest)throw Error('original observer receipt.json required');
async function run(bin,enabled,arm) {
 return await new Promise((resolve,reject)=>{
  const p=spawn(bin,[],{env:{...process.env,C3X025_P8_TT_FIELDS:enabled?'1':'0',C3X025_P14_ARM:arm}});
  const lines=[];let phase=0,done=false;
  const timer=setTimeout(()=>fail(Error('P14_UCI_TIMEOUT')),90000);
  function fail(e){if(done)return;done=true;clearTimeout(timer);p.kill('SIGKILL');reject(e);}
  p.on('error',fail);
  const rl=createInterface({input:p.stdout});
  rl.on('line',s=>{
   lines.push(s);
   if(s==='uciok'&&phase===0){phase=1;p.stdin.write('setoption name Threads value 1\nsetoption name Hash value 16\nsetoption name MultiPV value 1\nsetoption name Use NNUE value false\nucinewgame\nisready\n');}
   else if(s==='readyok'&&phase===1){phase=2;p.stdin.write('position startpos\ngo depth 7\n');}
   else if(s.startsWith('bestmove ')&&phase===2){phase=3;p.stdin.write('quit\n');}
  });
  p.on('close',code=>{if(done)return;done=true;clearTimeout(timer);if(code!==0){reject(Error('P14_NATIVE_EXIT_'+code));return;}
   const best=lines.filter(s=>s.startsWith('bestmove '));
   const info=lines.filter(s=>/^info depth 7 /.test(s)&&/\bnodes \d+/.test(s));
   if(best.length!==1||info.length===0){reject(Error('P14_FINAL_UCI_MISSING'));return;}
   const uci=best[0].split(' ')[1],nodes=Number(info.at(-1).match(/\bnodes (\d+)/)[1]);
   if(!/^[a-h][1-8][a-h][1-8][qrbn]?$/.test(uci)||!Number.isSafeInteger(nodes)||nodes<=0){reject(Error('INVALID_NATIVE_BESTMOVE_OR_NODES'));return;}
   const contacts=[];
   for(const s of lines.filter(s=>s.startsWith('info string c3x025_p14 '))){
    if(!enabled){reject(Error('P14_OBSERVER_OFF_EVENT'));return;}
    const f={};for(const part of s.slice('info string c3x025_p14 '.length).split(' ')){
     const i=part.indexOf('=');if(i<=0||Object.hasOwn(f,part.slice(0,i))){reject(Error('P14_DUPLICATE_TAG'));return;}
     f[part.slice(0,i)]=part.slice(i+1);
    }contacts.push(f);
   }
   resolve({uci,nodes,contacts});
  });
  p.stdin.write('uci\n');
 });
}
const arms={SHAM:0,SCORE:1,HINT:2,BOTH:3};
const originalTwo=[await run(original,false,'SHAM'),await run(original,false,'SHAM')];
const shamTwo=[await run(observer,true,'SHAM'),await run(observer,true,'SHAM')];
const off=await run(observer,false,'SHAM');
function equal(x,y){return JSON.stringify(x)===JSON.stringify(y);}
if(!equal(originalTwo[0],originalTwo[1])||!equal(shamTwo[0],shamTwo[1]))
 throw Error('P14_COLD_SHAM_REPETITION_NOT_IDENTICAL');
for(const z of [...originalTwo,...shamTwo,off])
 if(z.uci!=='b1c3'||z.nodes!==8657)throw Error('P14_UNTOUCHED_SHAM_CHANGED_ORIGINAL_SF16_SEARCH');
const results={};
for(const [arm,mask] of Object.entries(arms)){
 const twice=arm==='SHAM'?shamTwo:[await run(observer,true,arm),await run(observer,true,arm)];
 if(!equal(twice[0],twice[1]))throw Error('P14_INTERVENTION_NOT_COLD_REPRODUCIBLE_'+arm);
 const v=twice[0],byKind={};
 for(const e of v.contacts){
  if(!['Q_SCORE_RETURN_BOUND_CONTACT','Q_NONZERO_HINT_CONTACT'].includes(e.kind))throw Error('P14_UNKNOWN_OPERATOR');
  if(Number(e.arm)!==mask||![0,1].includes(Number(e.mutated))||byKind[e.kind])throw Error('P14_TAG_CLASS_OR_MODE_MISMATCH');
  byKind[e.kind]=e;
 }
 const score=byKind.Q_SCORE_RETURN_BOUND_CONTACT,hint=byKind.Q_NONZERO_HINT_CONTACT;
 const scoreMutated=score?Number(score.mutated):0,hintMutated=hint?Number(hint.mutated):0;
 if(scoreMutated && !(mask&1))throw Error('P14_SCORE_INTERVENTION_WRONG_ARM');
 if(hintMutated && !(mask&2))throw Error('P14_HINT_INTERVENTION_WRONG_ARM');
 if(score && (mask&1) && !scoreMutated)throw Error('P14_SCORE_ACTUAL_CONTACT_NOT_INTERVENED');
 if(hint && (mask&2) && !hintMutated)throw Error('P14_HINT_ACTUAL_CONTACT_NOT_INTERVENED');
 results[arm]={uci:v.uci,nodes:v.nodes,root_changed:v.uci!==originalTwo[0].uci,
   node_delta:v.nodes-originalTwo[0].nodes,
   original_q_score_cutoff_contact:Boolean(score),q_score_skipped:scoreMutated,
   original_q_hint_nonzero_contact:Boolean(hint),q_hint_masked:hintMutated,
   contact_status:((mask&1)&&!score||(mask&2)&&!hint)?'PARTIAL_CONTACT_HOLD':'ALL_REQUESTED_OPERATOR_CONTACTS'};
}
const receipt={schema:'c3x025-P14-P0-native-original-Q-TT-score-cutoff-vs-move-hint-factorial-v1',
 frozen_original_sf16:'68e1e9b3811e16cad014b590d7443b9063b3eb52',
 source_startpos_only:true,depth:7,threads:1,hash_mb:16,nnue:false,
 original_uci:originalTwo[0].uci,original_nodes:originalTwo[0].nodes,
 exact_original_observer_sham_and_optout_parity:true,
 arms:results,
 technical_result:'PHYSICAL_NATIVE_SOURCE_OPERATOR_INTERVENTIONS_IF_CONTACTED',
 causal_limit:'SOURCE_POLICY_MODIFICATION_IS_NOT_NATURAL_TT_SEE_MEDIATION',
 performance_limit:'SINGLE_STARTPOS_DEPTH7_NOT_ELO_OR_ENGINE_IMPROVEMENT',
 prospective_M5:'NOT_RUN'};
writeFileSync(dest,JSON.stringify(receipt,null,2)+'\n');
console.log('C3X025_P14_P0_ACTUAL_NATIVE_FACTORIAL',JSON.stringify(receipt));
