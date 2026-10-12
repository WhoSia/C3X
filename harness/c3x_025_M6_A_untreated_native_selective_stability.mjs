#!/usr/bin/env node
// M6-A: actual native Stockfish16 untreated depth6/depth7, native source
// observer SHAM only. Absolutely NO TT-score/hint intervention in this phase.
// Output candidate exact-UCI forecasts to be human-Git sealed BEFORE M6-B.
import {readFileSync,writeFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {spawn} from 'node:child_process';
import {createInterface} from 'node:readline';
const [sourcePath,regPath,original,observer,out]=process.argv.slice(2);
if(!sourcePath||!regPath||!original||!observer||!out)throw Error('usage: source reg native-original sham-observer out.json');
const sha=buf=>createHash('sha256').update(buf).digest('hex');
const bytes=readFileSync(sourcePath);
const expected='45d758947b6f224901f2674eaed4dc1dc34f4d5a439ccd62fa408393dd7c2a80';
if(sha(bytes)!==expected)throw Error('M6_SOURCE_SHA_NOT_SEALED');
const source=JSON.parse(bytes),reg=JSON.parse(readFileSync(regPath,'utf8'));
if(source.selected?.length!==64||reg.selected_game_SHA256?.length!==64||
 reg.minimal_source_SHA256!==expected||
 source.schema!=='c3x025-M6-S-july2026-source-only-independent-64-v1'||
 !source.source_only_no_stockfish_used||source.treatment_outcomes_seen||
 reg.native_or_treated_outcomes_seen||Object.keys(source.historical_source_receipts).length!==15)
 throw Error('M6_PHASE_CROSS_CONTAMINATION_OR_HISTORY_DRIFT');
for(let i=0;i<64;i++)if(source.selected[i].source_game_sha256!==reg.selected_game_SHA256[i]||
 source.selected[i].engine_outcomes_seen!==false)throw Error('M6_HUMAN_GIT_LITERAL_SOURCE_GAME_SHA_DRIFT');
async function execute(bin,observe,fen,depth){
 return new Promise((resolve,reject)=>{
  const env={...process.env,C3X025_P8_TT_FIELDS:observe?'1':'0',C3X025_P14_ARM:'SHAM'};
  const p=spawn(bin,[],{env});const lines=[];let phase=0,closed=false;
  const timer=setTimeout(()=>fail(Error('M6_STAGEA_NATIVE_TIMEOUT')),90000);
  function fail(e){if(closed)return;closed=true;clearTimeout(timer);p.kill('SIGKILL');reject(e);}
  p.on('error',fail);
  createInterface({input:p.stdout}).on('line',s=>{
   if(s.startsWith('bestmove ')||/^info depth \d+ /.test(s)||s.startsWith('info string c3x025_p14 '))lines.push(s);
   if(s==='uciok'&&phase===0){phase=1;p.stdin.write('setoption name Threads value 1\nsetoption name Hash value 16\nsetoption name MultiPV value 1\nsetoption name Use NNUE value false\nucinewgame\nisready\n');}
   if(s==='readyok'&&phase===1){phase=2;p.stdin.write('position fen '+fen+'\ngo depth '+depth+'\n');}
   if(s.startsWith('bestmove ')&&phase===2){phase=3;p.stdin.write('quit\n');}
  });
  p.on('close',code=>{
   if(closed)return;closed=true;clearTimeout(timer);
   if(code!==0){reject(Error('M6_STAGEA_NATIVE_EXIT_'+code));return;}
   try{
    const best=lines.filter(s=>s.startsWith('bestmove '));
    const info=lines.filter(s=>new RegExp('^info depth '+depth+' ').test(s)&&/\bnodes \d+/.test(s)).at(-1);
    if(best.length!==1||!info)throw Error('M6_NATIVE_DEPTH_OR_UCI_MISSING');
    const move=best[0].split(' ')[1],nodes=Number(info.match(/\bnodes (\d+)/)?.[1]);
    const score=info.match(/\bscore (cp|mate) (-?\d+)/),pv=info.match(/\bpv ([a-h][1-8][a-h][1-8][qrbn]?(?: [a-h][1-8][a-h][1-8][qrbn]?)*)/);
    if(!/^[a-h][1-8][a-h][1-8][qrbn]?$/.test(move)||!Number.isSafeInteger(nodes)||!score)
       throw Error('M6_INVALID_ORIGINAL_UNTREATED_ENGINE_TERMINAL');
    const contacts=lines.filter(s=>s.startsWith('info string c3x025_p14 '));
    if(!observe&&contacts.length)throw Error('M6_UNMODIFIED_NATIVE_EMITTED_OBSERVER_TAGS');
    if(observe&&contacts.some(s=>/\bmutated=1\b/.test(s)))throw Error('M6_STAGEA_ACTUAL_PHYSICAL_TT_INTERVENTION_BLOCK');
    return resolve({move,nodes,score_type:score[1],score_value:Number(score[2]),pv:pv?.[1]||'',q_score_contact:contacts.some(s=>s.includes('kind=Q_SCORE_RETURN_BOUND_CONTACT')),q_hint_contact:contacts.some(s=>s.includes('kind=Q_NONZERO_HINT_CONTACT'))});
   }catch(e){reject(e);}
  });
  p.stdin.write('uci\n');
 });
}
let cases=[];let triggers=0;
for(const r of source.selected){
 const fen=[r.fen4,r.source_halfmove_clock,r.source_fullmove_number].join(' ');
 const depth6=await execute(original,false,fen,6);
 const depth7=await execute(original,false,fen,7);
 const nativeRepeat=await execute(original,false,fen,7);
 if(JSON.stringify(depth7)!==JSON.stringify(nativeRepeat))throw Error('M6_COLD_ORIGINAL_NOT_REPEATABLE_'+r.id);
 const sham=await execute(observer,true,fen,7);
 if(depth7.move!==sham.move||depth7.nodes!==sham.nodes||depth7.score_type!==sham.score_type||
    depth7.score_value!==sham.score_value||depth7.pv!==sham.pv)
   throw Error('M6_NATIVE_SHAM_PARITY_FAIL_'+r.id);
 const trigger=sham.q_score_contact&&depth6.move===depth7.move&&depth7.score_type==='cp'&&Math.abs(depth7.score_value)>=40;
 const target=trigger?'STABLE':'ABSTAIN';
 triggers+=Number(trigger);
 cases.push({game_id:r.id,source_game_sha256:r.source_game_sha256,
  original_depth6_exact_UCI:depth6.move,original_depth7_exact_UCI:depth7.move,
  original_depth7_score:depth7.score_type+':'+depth7.score_value,
  original_depth7_nodes:depth7.nodes,untreated_q_tt_numeric_return_contact:sham.q_score_contact,
  original_sham_exact_parity:true,M0:depth7.move,M6_selective_label:target,M6_covered:trigger,
  physical_qscore_interventions_performed:0,physical_hint_interventions_performed:0,
  actual_treated_root_UCI_seen:false});
}
const result={schema:'c3x025-M6-A-july2026-64game-untreated-native-source-preFIRST-selective-stability-v1',
 frozen_original_SF16:'68e1e9b3811e16cad014b590d7443b9063beb52'.replace('3beb52','3eb52'),
 prior_source_git_identity_seal:regPath,source_bytes_sha256:expected,source_games:64,
 original_depths:[6,7],threads:1,hash_mb:16,nnue:false,contact:'SHAM_ONLY',
 native_depth7_cold_repeat_and_sham_parity:true,actual_first_intervention_count:0,
 M6_rule:'STABLE iff SHAM original q TT bounded return physical source contact, exact UCI depth6 equals depth7 and original depth7 abs(cp)>=40; otherwise ABSTAIN. M0 original depth7 retained for all cases',
 models:['M0','M6_selective_STABLE_ABSTAIN'],M6_covered_count:triggers,
 scientific_status:triggers?'SELECTIVE_STABLE_CANDIDATES_REQUIRE_HUMAN_LITERAL_GIT_SEAL_BEFORE_FIRST':'ZERO_COVERAGE_HOLD',
 treated_outcomes_seen:false,observer_treatment_arms_seen:[],
 cases};
writeFileSync(out,JSON.stringify(result,null,2)+'\n');
console.log('M6_A_UNTREATED_SOURCE_NATIVE_PRE_FIRST',JSON.stringify({source_games:64,covered:triggers,
 candidates:cases.map(c=>[c.game_id,c.source_game_sha256,c.M0,c.M6_selective_label,Number(c.M6_covered),c.original_depth7_score,Number(c.untreated_q_tt_numeric_return_contact)])}));
