#!/usr/bin/env node
// P14-P5: explanation extraction from ALREADY OBSERVED genuine original SF16
// P14-P4 root search artifact. No new engine or giant traces, no invented K.
import {readFileSync,writeFileSync} from 'node:fs';
const [inp,out]=process.argv.slice(2);
if(!inp||!out)throw Error('usage: P14P4-native-source-observed JSON output JSON');
const raw=JSON.parse(readFileSync(inp));
if(raw.schema!=='c3x025-P14-P4-original-root-aspiration-original-move-source-relational-stability-observer-v1'||
 raw.strict_actual_original_uci_parity!==true||raw.research_stage!=='POSTOUTCOME_EXPOSED_DEVELOPMENT_ONLY')
 throw Error('P14P5_ONLY_REAL_HISTORIC_NATIVE_SOURCE_WITH_TRUE_PARITY_ACCEPTED');
function compare(x){
 const a=x.sham,b=x.first_qscore_suppression;
 const am=new Map(a.final_attempt_candidate_snapshot.map(r=>[r.moveID,r]));
 const bm=new Map(b.final_attempt_candidate_snapshot.map(r=>[r.moveID,r]));
 if(!am.size||am.size!==bm.size||
  [...am.keys()].some(k=>!bm.has(k)))throw Error('P14P5_CHANGED_ROOT_CANDIDATE_SET_HOLD');
 const keys=['storedScore','uciScore','priorScore','scoreLowerbound','scoreUpperbound','PVlength'];
 let differences=[];
 for(const [move,old] of am){
   const next=bm.get(move),changed=keys.filter(k=>old[k]!==next[k]);
   if(changed.length)differences.push({native_move_encoding:move,changed_fields:changed,
     original:{stored:old.storedScore,uci:old.uciScore,lower:old.scoreLowerbound,upper:old.scoreUpperbound},
     policy:{stored:next.storedScore,uci:next.uciScore,lower:next.scoreLowerbound,upper:next.scoreUpperbound}});
 }
 const firstAttempt=()=>{
   const u=a.final_depth7_root_attempts,v=b.final_depth7_root_attempts;
   for(let i=0;i<Math.max(u.length,v.length);i++){
     const s=u[i],t=v[i];
     if(!s||!t||s.alpha!==t.alpha||s.beta!==t.beta||s.class!==t.class||
        s.returned!==t.returned||s.effective_depth!==t.effective_depth)
       return {same_depth7_attempt_ordinal:i+1,baseline:s??null,intervention:t??null,
         caution:'ordinal agreement does not prove same dynamic source call'};
   }
   return null;
 };
 const totalRetries=z=>z.fail_low+z.fail_high;
 return {
  original:{bestmove:x.original.uci,nodes:x.original.nodes,depth7_aspiration_attempts:a.final_depth7_root_attempts.length,
    all_depth_retry_count:totalRetries(a),source_root_move_returns:a.actual_root_move_results},
  intervention:{bestmove:b.uci,nodes:b.nodes,depth7_aspiration_attempts:b.final_depth7_root_attempts.length,
    all_depth_retry_count:totalRetries(b),source_root_move_returns:b.actual_root_move_results},
  root_choice_changed:a.uci!==b.uci,
  final_root_candidate_identifiers_compared:am.size,
  final_candidates_with_changed_original_source_fields:differences.length,
  changed_original_candidate_field_examples:differences.slice(0,5),
  first_different_recorded_depth7_aspiration_attempt:firstAttempt(),
  observed_mechanistic_contrast:'one original TT qscore return suppression led to this actual result; ordered source event and final candidate record differences are observable',
  winner_margin_from_source_fields_proven:false,
  sound_reachable_candidate_K_from_native_log:'HOLD',
  proved_semantic_difference_constraints:[],
  explainable_source_level_status:'DESCRIPTIVE_COUNTERFACTUAL_WITNESS',
  proof_carrying_root_winner_certificate:'ABSTAIN',
  if_no_certificate:'fall back to source engine behavior, do not claim a safe TT adaptation',
  selected_after_native_M6_results:true
 };
}
if(!raw.cases.EXPOSED_ORIGINAL_STARTPOS||!raw.cases.EXPOSED_M6_JULY2026_ROOT28)
 throw Error('P14P5_MISSING_REAL_SOURCE_NEGATIVE_AND_POSITIVE_CONTROL');
const start=compare(raw.cases.EXPOSED_ORIGINAL_STARTPOS);
const pivot=compare(raw.cases.EXPOSED_M6_JULY2026_ROOT28);
if(start.root_choice_changed||start.final_candidates_with_changed_original_source_fields||
 !pivot.root_choice_changed||pivot.final_candidates_with_changed_original_source_fields<=0||
 start.original.nodes!==start.intervention.nodes||
 pivot.original.bestmove!=='f1d1'||pivot.intervention.bestmove!=='a1a5'||
 pivot.original.nodes!==7456||pivot.intervention.nodes!==4380)
 throw Error('P14P5_ACTUAL_SOURCE_PIVOT_AND_CONTROL_FALSIFIED');
const result={schema:'c3x025-P14-P5-original-source-contrastive-why-not-with-soundness-abstention-v1',
 prior_original_source_success_run:38200812256,
 original_Stockfish_git:'68e1e9b3811e16cad014b590d7443b9063b3eb52',
 source_experiment_reused_without_recompilation:true,
 is_first_observed_difference_global:false,
 two_real_exposed_cases:{
  EXPOSED_ORIGINAL_STARTPOS:start,
  EXPOSED_M6_JULY2026_ROOT28:pivot
 },
 mathematical_model_proof:'independent C++17 DBM finite theorem; no bridge to actual SF16 score meanings yet',
 technical_correctness:'observed action and source-path differences verified; missing semantic proof remains explicit',
 actual_safe_TT_policy_invented:false,
 Elo_gain_proven:false
};
writeFileSync(out,JSON.stringify(result,null,2)+'\n');
console.log('C3X025_P14P5_REAL_STOCKFISH_EXPLAINABLE_ROOT_CONTRAST_PASS',
 JSON.stringify({negative_control:start.original.bestmove,
 pivot_baseline:pivot.original.bestmove,pivot_intervention:pivot.intervention.bestmove,
 root_competitors_changed:pivot.final_candidates_with_changed_original_source_fields,
 source_to_sound_K:'HOLD',proof_carrying_explanation:'ABSTAIN'}));
