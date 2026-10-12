#!/usr/bin/env node
// C3X M5-B first physical original qsearch bounded TT score-return suppression.
// Source, model, original no-intervention native Stage A, human Git-literal exact
// legal UCI predictions MUST be sealed before this script or workflow was run.
import {readFileSync,writeFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {spawn} from 'node:child_process';
import {createInterface} from 'node:readline';
const [srcFile,stageFile,predFile,original,modified,out]=process.argv.slice(2);
if(!srcFile||!stageFile||!predFile||!original||!modified||!out)throw Error('Usage: source StageA humanGitForecast original observer output');
const SHA='71ab8e4c4ddb52d8f63e6e51ea6b4cf991e135246773460c3d6f4800288521be';
const sha=b=>createHash('sha256').update(b).digest('hex');
const bytes=readFileSync(srcFile);
if(sha(bytes)!==SHA)throw Error('M5_B_SOURCE_MINIMAL_JSON_SHA_MISMATCH');
const source=JSON.parse(bytes),stage=JSON.parse(readFileSync(stageFile)),forecast=JSON.parse(readFileSync(predFile));
if(source.selected?.length!==32||
 stage.schema!=='c3x025-M5-A-june2026-32game-untreated-native-source-preFIRST-forecast-candidates-v1'||
 stage.cases?.length!==32||stage.treated_outcomes_seen!==false||stage.actual_first_intervention_count!==0||
 forecast.schema!=='c3x025-M5-A-human-Git-sealed-32-literal-uci-before-any-source-SCORE-treatment-v1'||
 forecast.exact_UCI_by_game?.length!==32||
 forecast.game_count!==32||forecast.positive_M5_trigger_games!==9||
 forecast.source_minimal_JSON_sha256!==SHA||
 forecast.M5_outcome_correctness_status!=='UNSEEN_BEFORE_TREATMENT'||
 forecast.engine_interventions_seen!==0)
 throw Error('M5_STAGE_SEAL_OR_NO_TREATMENT_PHASE_GATE');
const physicalRows=[];
function modelFromStage(stageRow){
 const b=stageRow.original_depth7_score.match(/^(cp|mate):(-?\d+)$/);
 if(!b)throw Error('M5_NATIVE_BASELINE_SCORE_MALFORMED');
 const trig=Boolean(stageRow.untreated_q_tt_numeric_return_contact)&&
  stageRow.original_depth6_exact_UCI!==stageRow.original_depth7_exact_UCI&&
  b[1]==='cp'&&Math.abs(Number(b[2]))<=30;
 return {M0:stageRow.original_depth7_exact_UCI,M5:trig?stageRow.original_depth6_exact_UCI:stageRow.original_depth7_exact_UCI,trigger:trig};
}
for(let n=0;n<32;n++){
 const s=source.selected[n],u=stage.cases[n],f=forecast.exact_UCI_by_game[n];
 if(s.id!==n+1||u.game_id!==s.id||f.game_id!==s.id||
    u.source_game_sha256!==s.source_game_sha256||f.source_game_sha256!==s.source_game_sha256||
    u.actual_treated_root_UCI_seen!==false||u.physical_qscore_interventions_performed!==0)
    throw Error('M5_SOURCE_ORIGINAL_STAGEA_LITERAL_GAME_ORDER_DRIFT_'+(n+1));
 const m=modelFromStage(u);
 if(m.M0!==f.M0_original_untreated_depth7_UCI||
    m.M5!==f.M5_frozen_source_rule_UCI||m.trigger!==f.M5_predicted_change||
    stage.M5_predicted_changed_count!==9)throw Error('M5_GIT_FORECAST_RULE_VS_UNTREATED_STAGEA_DRIFT_'+(n+1));
}
function engine(bin,envFields,arm,fen){
 return new Promise((resolve,reject)=>{
  const p=spawn(bin,[],{env:{...process.env,C3X025_P8_TT_FIELDS:envFields?'1':'0',C3X025_P14_ARM:arm}});
  const lines=[];let phase=0,closed=false;
  const timer=setTimeout(()=>stop(Error('M5_B_NATIVE_ENGINE_TIMEOUT')),90000);
  function stop(e){if(closed)return;closed=true;clearTimeout(timer);p.kill('SIGKILL');reject(e);}
  p.on('error',stop);
  createInterface({input:p.stdout}).on('line',s=>{
   if(s.startsWith('bestmove ')||/^info depth 7 /.test(s)||s.startsWith('info string c3x025_p14 '))lines.push(s);
   if(s==='uciok'&&phase===0){phase=1;p.stdin.write('setoption name Threads value 1\nsetoption name Hash value 16\nsetoption name MultiPV value 1\nsetoption name Use NNUE value false\nucinewgame\nisready\n');}
   if(s==='readyok'&&phase===1){phase=2;p.stdin.write('position fen '+fen+'\ngo depth 7\n');}
   if(s.startsWith('bestmove ')&&phase===2){phase=3;p.stdin.write('quit\n');}
  });
  p.on('close',code=>{if(closed)return;closed=true;clearTimeout(timer);try{
   if(code!==0)throw Error('M5_B_NATIVE_ENGINE_EXIT_'+code);
   const best=lines.filter(s=>s.startsWith('bestmove '));
   const terminal=lines.filter(s=>/^info depth 7 /.test(s)&&/\bnodes \d+/.test(s)).at(-1);
   if(best.length!==1||!terminal)throw Error('M5_B_NATIVE_RESULT_INCOMPLETE');
   const move=best[0].split(' ')[1],nodes=Number(terminal.match(/\bnodes (\d+)/)?.[1]);
   if(!/^[a-h][1-8][a-h][1-8][qrbn]?$/.test(move)||!Number.isSafeInteger(nodes)||nodes<=0)throw Error('M5_B_INVALID_RESULT');
   const events=lines.filter(s=>s.startsWith('info string c3x025_p14 '));
   if(!envFields&&events.length)throw Error('ORIGINAL_ENGINE_SOURCE_TAG_LEAK');
   const scoreEvents=events.filter(s=>s.includes('kind=Q_SCORE_RETURN_BOUND_CONTACT'));
   const hintEvents=events.filter(s=>s.includes('kind=Q_NONZERO_HINT_CONTACT'));
   if(scoreEvents.length>1||hintEvents.length>1||events.length!==scoreEvents.length+hintEvents.length)
     throw Error('M5_NATIVE_SOURCE_CLASSES_AMBIGUOUS');
   const manipulated=scoreEvents.filter(s=>s.includes('mutated=1')).length;
   if(manipulated>1)throw Error('SOURCE_TT_SCORE_MODIFIED_MORE_THAN_ONCE');
   if(arm==='SHAM'&&events.some(s=>s.includes('mutated=1')))throw Error('SHAM_TT_INTERVENTION_LEAK');
   if(arm==='SCORE'&&hintEvents.some(s=>s.includes('mutated=1')))throw Error('HINT_TT_INTERVENTION_UNREGISTERED');
   resolve({move,nodes,actual_score_first_contact:scoreEvents.length===1,
    actual_first_score_return_blocked:manipulated,actual_hint_first_contact:hintEvents.length===1});
  }catch(e){reject(e);}});
  p.stdin.write('uci\n');
 });
}
let scoreContact=0,model0Correct=0,model5Correct=0,wins=0,losses=0,ties=0,rootFlips=0;
for(let n=0;n<32;n++){
 const s=source.selected[n],f=forecast.exact_UCI_by_game[n],u=stage.cases[n];
 const fen=[s.fen4,s.source_halfmove_clock,s.source_fullmove_number].join(' ');
 const orig=await engine(original,false,'SHAM',fen);
 const sham=await engine(modified,true,'SHAM',fen);
 const treated=await engine(modified,true,'SCORE',fen);
 const rerun=await engine(modified,true,'SCORE',fen);
 if(JSON.stringify(treated)!==JSON.stringify(rerun))throw Error('M5_B_TREATED_NOT_COLD_DETERMINISTIC_'+s.id);
 if(orig.move!==f.M0_original_untreated_depth7_UCI||orig.nodes!==u.original_depth7_nodes||
    orig.move!==sham.move||orig.nodes!==sham.nodes)
    throw Error('M5_B_ORIGINAL_TO_HUMAN_GIT_OR_SHAM_NOT_PARITY_'+s.id);
 if(sham.actual_score_first_contact!==u.untreated_q_tt_numeric_return_contact)
    throw Error('M5_B_ACTUAL_CONTACT_PRETREATMENT_FEATURE_DRIFT_'+s.id);
 const contact=treated.actual_score_first_contact&&treated.actual_first_score_return_blocked===1;
 if(!contact && treated.actual_first_score_return_blocked!==0)
    throw Error('M5_B_UNREGISTERED_SOURCE_INTERVENTION');
 scoreContact+=Number(contact);
 const correct0=contact&&f.M0_original_untreated_depth7_UCI===treated.move;
 const correct5=contact&&f.M5_frozen_source_rule_UCI===treated.move;
 if(contact){
  model0Correct+=Number(correct0);model5Correct+=Number(correct5);
  if(correct5&&!correct0)wins++;else if(correct0&&!correct5)losses++;else ties++;
  rootFlips+=Number(treated.move!==orig.move);
 }
 physicalRows.push({
  game_id:s.id,source_game_sha256:s.source_game_sha256,
  M0_frozen_literal_UCI:f.M0_original_untreated_depth7_UCI,
  M5_frozen_literal_UCI:f.M5_frozen_source_rule_UCI,
  M5_predicted_change:f.M5_predicted_change,
  true_score_return_physical_contact:contact,
  status:contact?'SCORE_SOURCE_OPERATOR_INTERVENTION_CONTACT':'HOLD_NO_ACTUAL_OPERATOR_CONTACT',
  outcome_actual_native_physical_score_UCI:contact?treated.move:null,
  untouched_original_root_UCI:orig.move,
  untouched_original_nodes:orig.nodes,
  treated_nodes:treated.nodes,
  root_flipped:contact?treated.move!==orig.move:null,
  M0_correct_on_actual_treatment:contact?correct0:null,
  M5_correct_on_actual_treatment:contact?correct5:null
 });
}
const eligible=scoreContact;const dis=wins+losses;
function choose(n,k){let v=1;for(let i=1;i<=k;i++)v=v*(n-i+1)/i;return v;}
let tail=0;for(let i=0;i<=Math.min(wins,losses);i++)tail+=choose(dis,i);
const signP=dis?Math.min(1,2*tail/2**dis):1;
const result={
 schema:'c3x025-M5-B-June2026-32game-human-Git-sealed-exact-UCI-before-actual-qscore-intervention-v1',
 original_SF16:"68e1e9b3811e16cad014b590d7443b9063b3eb52",
 source_minimal_JSON_SHA256:SHA,
 human_preFIRST_exact_UCI_Git_commit:"9e3c50c4ecf77f87bd8f8108ef59958d3adaaa35",
 source_preStageA_identity_human_Git_commit:"5a1c58844dcf390407d361ad061a54fac09d76ee",
 preArchive_model_rule_human_Git_commit:"6046e3e03ef0a81d059f550419859f3914db993a",
 previous_native_untreated_StageA_run:38193949242,
 source_only_original_archive_SHA256:"65905d611c0d78d90ab57cd9edd3821f4119b46c22b5489fd7e265a74c6767b3",
 source_game_count:32,predeclared_M5_predicted_changed_games:9,
 physically_contacted_original_qsearch_TT_numeric_bound_return:eligible,
 NO_CONTACT_HOLD:32-eligible,
 physically_observed_root_bestmove_changes:rootFlips,
 M0_exact_UCI_correct_in_contacted_games:model0Correct,
 M5_exact_UCI_correct_in_contacted_games:model5Correct,
 paired_game_M5_win:wins,paired_game_M5_loss:losses,paired_game_tie:ties,
 game_level_two_sided_exact_sign_test_p:signP,
 technical_verdict:eligible===32?'ALL_32_ORIGINAL_QSEARCH_TT_SCORE_INTERVENTIONS_ACTUALLY_CONTACTED':'CENSORED_ORIGINAL_QSCORE_CONTACT_SOME_GAMES',
 scientific_verdict:wins>losses?'POINT_GAIN_HOLD_POWER_AND_INDEPENDENT_REPLICATION':wins===losses?'NO_PAIRED_ADVANTAGE':'SCIENTIFIC_NEGATIVE_M5_UNDERPERFORMS_M0',
 scope:'June2026 Lichess 32 new game pilot, one SF16 engine, one qsearch first bounded-score return policy vs untouched M0; exact legal UCI target not chess Elo',
 SEE_natural_indirect_effect_proven:false,
 general_chess_strength_improvement_proven:false,
 source_only_licenses:'Lichess broadcast CC BY-SA 4.0 derived positions and predictions; no original complete PGN/player names or modified GPL binaries exported',
 per_game:physicalRows
};
if(eligible===0)result.scientific_verdict='HOLD_NO_NATIVE_QSCORE_CONTACT';
writeFileSync(out,JSON.stringify(result,null,2)+'\n');
console.log('C3X025_M5_B_PRESEALED_ACTUAL_PHYSICAL_SF16_SCORE_OUTCOMES',JSON.stringify({
 original_games:result.source_game_count,contact:eligible,hold:32-eligible,
 M5_nontrivial_predictions:9,root_flips:rootFlips,
 M0_correct:model0Correct,M5_correct:model5Correct,
 wins,losses,ties,sign_p:signP,verdict:result.scientific_verdict,
 discordant_cases:physicalRows.filter(r=>r.M5_predicted_change).map(r=>({
 id:r.game_id,baseline:r.M0_frozen_literal_UCI,M5:r.M5_frozen_literal_UCI,
 actual:r.outcome_actual_native_physical_score_UCI,
 M0_correct:r.M0_correct_on_actual_treatment,M5_correct:r.M5_correct_on_actual_treatment,
 contact:r.true_score_return_physical_contact}))}));
