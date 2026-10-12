#!/usr/bin/env node
// M6-B independent 2026-07 64-game selective STABLE/ABSTAIN after HUMAN
// Git-literal pre-FIRST seal. Target: one actual original SF16 qsearch TT
// numeric bounded score return suppression; no SEE boolean manipulation.
import {readFileSync,writeFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {spawn} from 'node:child_process';
import {createInterface} from 'node:readline';
const [sourcePath,stagePath,sealPath,original,modified,out]=process.argv.slice(2);
if(!out||!modified)throw Error('usage: source stageA humanGitLiteral original SF16 modified SF16 out');
const SH='45d758947b6f224901f2674eaed4dc1dc34f4d5a439ccd62fa408393dd7c2a80';
const bytes=readFileSync(sourcePath);
if(createHash('sha256').update(bytes).digest('hex')!==SH)throw Error('M6_B_JULY64_SOURCE_SHA_CHANGED');
const src=JSON.parse(bytes),st=JSON.parse(readFileSync(stagePath)),seal=JSON.parse(readFileSync(sealPath));
if(src.schema!=='c3x025-M6-S-july2026-source-only-independent-64-v1'||src.selected?.length!==64||
 st.schema!=='c3x025-M6-A-july2026-64game-untreated-native-source-preFIRST-selective-stability-v1'||
 st.cases?.length!==64||st.actual_first_intervention_count!==0||st.treated_outcomes_seen||
 seal.schema!=='c3x025-M6-A-July2026-64game-actual-native-untreated-human-Git-literal-stability-UCI-preSCORE-v1'||
 seal.exact_all_64_model_rows?.length!==64||seal.source_game_count!==64||
 seal.covered_STABLE!==19||seal.ABSTAIN!==45||seal.treated_outcomes_seen||
 seal.Original_source_minimal_SHA256!==SH||seal.physically_mutated_first_qscore_interventions_seen!==0)
 throw Error('M6_B_INVALID_SOURCE_STAGEA_HUMAN_FORECAST_SEAL');
function checkPre(i){
 const s=src.selected[i],a=st.cases[i],p=seal.exact_all_64_model_rows[i];
 if(s.id!==i+1||a.game_id!==i+1||p.id!==i+1||
    s.source_game_sha256!==a.source_game_sha256||s.source_game_sha256!==p.source_game_sha256||
    a.physical_qscore_interventions_performed!==0||a.actual_treated_root_UCI_seen!==false||
    p.actual_physical_SCORE_target_UCI!=='UNSEEN_BEFORE_LITERAL_SEAL'||
    p.M0_exact_UCI!==a.M0||
    p.original_sham_qTT_numeric_contact!==Boolean(a.untreated_q_tt_numeric_return_contact)||
    p.M6_stable_prediction!==(p.M6_selective_label==='STABLE'))
    throw Error('M6_B_PRETREATMENT_LITERAL_IDENTITY_MISMATCH_'+i);
 const match=a.original_depth7_score.match(/^(cp|mate):(-?\d+)$/);
 if(!match)throw Error('M6_B_UNTREATED_NATIVE_SCORE_MALFORMED_'+i);
 const stable=a.untreated_q_tt_numeric_return_contact&&
  a.original_depth6_exact_UCI===a.original_depth7_exact_UCI&&
  match[1]==='cp'&&Math.abs(Number(match[2]))>=40;
 if(stable!==p.M6_stable_prediction||p.M6_selective_label!==(stable?'STABLE':'ABSTAIN'))
   throw Error('M6_B_PREARCHIVE_DECISION_RULE_SEAL_CHANGED_'+i);
}
for(let i=0;i<64;i++)checkPre(i);
function execute(bin,observe,arm,fen){
 return new Promise((resolve,reject)=>{
  const p=spawn(bin,[],{env:{...process.env,C3X025_P8_TT_FIELDS:observe?'1':'0',C3X025_P14_ARM:arm}});
  let phase=0,closed=false;const lines=[];
  const timer=setTimeout(()=>fail(Error('M6_ORIGINAL_NATIVE_TIMEOUT')),90000);
  function fail(e){if(closed)return;closed=true;clearTimeout(timer);p.kill('SIGKILL');reject(e);}
  p.on('error',fail);
  createInterface({input:p.stdout}).on('line',s=>{
   if(s.startsWith('bestmove ')||/^info depth 7 /.test(s)||s.startsWith('info string c3x025_p14 '))lines.push(s);
   if(s==='uciok'&&phase===0){phase=1;p.stdin.write('setoption name Threads value 1\nsetoption name Hash value 16\nsetoption name MultiPV value 1\nsetoption name Use NNUE value false\nucinewgame\nisready\n');}
   if(s==='readyok'&&phase===1){phase=2;p.stdin.write('position fen '+fen+'\ngo depth 7\n');}
   if(s.startsWith('bestmove ')&&phase===2){phase=3;p.stdin.write('quit\n');}
  });
  p.on('close',code=>{if(closed)return;closed=true;clearTimeout(timer);try{
   if(code!==0)throw Error('M6_NATIVE_EXIT_'+code);
   const best=lines.filter(s=>s.startsWith('bestmove '));
   const info=lines.filter(s=>/^info depth 7 /.test(s)&&/\bnodes \d+/.test(s)).at(-1);
   if(best.length!==1||!info)throw Error('M6_NATIVE_NO_COMPLETED_DEPTH7');
   const move=best[0].split(' ')[1],nodes=Number(info.match(/\bnodes (\d+)/)?.[1]);
   if(!/^[a-h][1-8][a-h][1-8][qrbn]?$/.test(move)||!Number.isSafeInteger(nodes)||nodes<=0)
    throw Error('M6_NATIVE_UCI_OR_NODES_INVALID');
   const contacts=lines.filter(s=>s.startsWith('info string c3x025_p14 '));
   const score=contacts.filter(s=>s.includes('kind=Q_SCORE_RETURN_BOUND_CONTACT'));
   const hint=contacts.filter(s=>s.includes('kind=Q_NONZERO_HINT_CONTACT'));
   if(!observe&&contacts.length)throw Error('M6_ORIGINAL_TAG_LEAK');
   if(score.length>1||hint.length>1||contacts.length!==score.length+hint.length)
    throw Error('M6_DUPLICATE_NATIVE_SOURCE_CLASS');
   if(arm==='SHAM'&&contacts.some(s=>s.includes('mutated=1')))throw Error('M6_SHAM_ACTUATION_LEAK');
   if(arm==='SCORE'&&hint.some(s=>s.includes('mutated=1')))throw Error('M6_SCORE_ARM_HINT_MUTATED');
   const mutated=score.filter(s=>s.includes('mutated=1')).length;
   resolve({move,nodes,source_qscore_contact:score.length===1,source_qscore_actuation:mutated,
     untouched_native_qhint_contact:hint.length===1});
  }catch(e){reject(e);}
  });
  p.stdin.write('uci\n');
 });
}
const rows=[];let exposed=0,stable=0,stableFailure=0,abstain=0,abstainChange=0,allFlips=0,n0=0,n1=0,nup=0,ndown=0,nequal=0;
for(let i=0;i<64;i++){
 const r=src.selected[i],a=st.cases[i],f=seal.exact_all_64_model_rows[i];
 const fen=[r.fen4,r.source_halfmove_clock,r.source_fullmove_number].join(' ');
 const orig=await execute(original,false,'SHAM',fen);
 const sham=await execute(modified,true,'SHAM',fen);
 const treated=await execute(modified,true,'SCORE',fen);
 const repeat=await execute(modified,true,'SCORE',fen);
 if(JSON.stringify(treated)!==JSON.stringify(repeat))
   throw Error('M6_PHYSICAL_SCORE_COLD_REPEAT_FAIL_'+r.id);
 if(orig.move!==a.M0||orig.move!==sham.move||orig.nodes!==sham.nodes||
    orig.nodes!==a.original_depth7_nodes||
    Boolean(a.untreated_q_tt_numeric_return_contact)!==sham.source_qscore_contact)
   throw Error('M6_ORIGINAL_UNTREATED_SHAM_GIT_IDENTITY_DRIFT_'+r.id);
 const contact=treated.source_qscore_contact && treated.source_qscore_actuation===1;
 if(treated.source_qscore_actuation && !contact)throw Error('M6_UNREGISTERED_PHYSICAL_MUTATION');
 const changed=contact?treated.move!==orig.move:null;
 exposed+=Number(contact);
 if(contact){
  allFlips+=Number(changed);n0+=orig.nodes;n1+=treated.nodes;
  nup+=Number(treated.nodes>orig.nodes);
  ndown+=Number(treated.nodes<orig.nodes);
  nequal+=Number(treated.nodes===orig.nodes);
  if(f.M6_stable_prediction){stable++;stableFailure+=Number(changed);}
  else{abstain++;abstainChange+=Number(changed);}
 }
 rows.push({id:r.id,source_game_sha256:r.source_game_sha256,
  Git_human_sealed_original_M0_UCI:f.M0_exact_UCI,
  Git_human_sealed_M6_selective_label:f.M6_selective_label,
  original_source_qscore_physically_contacted:contact,
  real_SF16_SCORE_intervention_bestmove:contact?treated.move:null,
  true_root_choice_changed:changed,
  original_nodes:orig.nodes,treated_nodes:treated.nodes,
  if_STABLE_original_source_prediction_correct:contact&&f.M6_stable_prediction?!changed:null,
  if_ABSTAIN_root_change_actual:contact&&!f.M6_stable_prediction?changed:null,
  scientific_status:contact?'NATIVE_EXPERIMENT_ORIGINAL_SCORE_OPERATOR_CONTACT':'NO_CONTACT_HOLD'});
}
const cpUpper=stable?1-Math.pow(0.05,1/stable):null;
const report={
 schema:'c3x025-P14-P3-M6-B-July64-human-preSCORE-Git-sealed-selective-root-stability-first-native-evaluation-v1',
 source_provider:'Lichess broadcast July2026 CC BY-SA 4.0',
 original_archive_SHA256:'714d0eb99f99fca8d791142038b6c59b5ca6a51b3339bd3891a92f4bdffcbf0c',
 source_minimal_64_SHA256:SH,source_count:64,
 frozen_preArchive_rule_commit:'4f1bfb787c38192b372dceee67d3f1aace90fa06',
 frozen_64_source_games_preNative_commit:'2e410199d42562798bf1a15a03a5a5003e1cc360',
 frozen_all64_literal_UCI_STABLE_ABSTAIN_prePhysical_SCORE_commit:'bba80067e9aac053a58dfb5c38e3858049c788ea',
 native_untreated_StageA_CI_run:38198429964,
 pinned_original_SF16:'68e1e9b3811e16cad014b590d7443b9063b3eb52',
 native_conditions:{threads:1,hash_mb:16,nnue:false,depth:7,first_original_qsearch_score_bounded_return_suppressed_at_most_once:true},
 physical_qscore_original_contacts:exposed,NO_CONTACT_HOLD:64-exposed,
 predeclared_STABLE_forecasts:19,predeclared_ABSTAIN:45,
 covered_physically_STABLE:stable,covered_STABLE_false_positives:stableFailure,
 physically_ABSTAIN:abstain,ABSTAIN_actual_root_flips:abstainChange,
 actually_changed_original_root_UCI:allFlips,
 M0_exact_UCI_correct_among_contacted:exposed-allFlips,
 M6_selective_prediction_error_rate:stable?stableFailure/stable:null,
 conditional_95pct_zero_error_upper_bound_if_zero_failures:
  stable&&stableFailure===0?cpUpper:null,
 risk_bound_scope:'Simple one-sided binomial bound assumes independent Bernoulli covered games, not certified here due to same-source/event/player dependence; not a mechanistic sound safety bound',
 nodes:{original:n0,score_suppressed:n1,delta:n1-n0,more:nup,less:ndown,same:nequal},
 scientific_verdict:exposed===0?'HOLD_NO_PHYSICAL_TREATMENT':
  stable===0?'HOLD_ZERO_M6_COVERAGE':
  allFlips===0?'M6_COVERAGE_ESTIMATED_BUT_ZERO_ROOT_FLIPS_NO_DISCRIMINATION_EVIDENCE':
  stableFailure?'SCIENTIFIC_NEGATIVE_M6_SELECTIVE_STABILITY_FALSE_POSITIVE':
  'M6_SELECTIVE_STABILITY_PILOT_SURVIVED_NO_SOUNDNESS_OR_ELO_CLAIM',
 cannot_claim_better_than_M0_without_gain:true,
 no_natural_TT_to_SEE_mediation:true,no_engine_strength_or_speed_Elo_evaluation:true,
 per_game:rows
};
writeFileSync(out,JSON.stringify(report,null,2)+'\n');
console.log('C3X025_M6_JULY64_ORIGINAL_NATIVE_FIRST_SCORE_SELECTIVE_VERDICT',JSON.stringify({
 contact:exposed,preselected_stable:19,preselected_abstain:45,
 covered_STABLE:stable,stable_failures:stableFailure,abstain_root_flips:abstainChange,
 root_flips:allFlips,M0_accuracy:exposed-allFlips,
 nodes:report.nodes,verdict:report.scientific_verdict,
 flipped_games:rows.filter(x=>x.true_root_choice_changed).map(x=>({id:x.id,model:x.Git_human_sealed_M6_selective_label}))}));
