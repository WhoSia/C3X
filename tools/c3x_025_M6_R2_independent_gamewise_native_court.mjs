#!/usr/bin/env node
// Independently rescore all 64 literal HUMAN Git-sealed M6 selective predictions.
import {readFileSync,writeFileSync} from 'node:fs';
const [src,fore,treatment,out]=process.argv.slice(2);
if(!src||!fore||!treatment||!out)throw Error('usage: source seal physical report');
const s=JSON.parse(readFileSync(src)),f=JSON.parse(readFileSync(fore)),r=JSON.parse(readFileSync(treatment));
if(s.selected?.length!==64||f.exact_all_64_model_rows?.length!==64||r.per_game?.length!==64||
 r.schema!=='c3x025-P14-P3-M6-B-July64-human-preSCORE-Git-sealed-selective-root-stability-first-native-evaluation-v1')
 throw Error('M6_INDEPENDENT_INPUTS_NOT_ORIGINAL');
let contact=0,cover=0,abstain=0,fail=0,aflip=0,flips=0,n0=0,n1=0,inc=0,dec=0,same=0;
for(let i=0;i<64;i++){
 const a=s.selected[i],b=f.exact_all_64_model_rows[i],c=r.per_game[i];
 if(a.id!==i+1||b.id!==i+1||c.id!==i+1||a.source_game_sha256!==b.source_game_sha256||
  a.source_game_sha256!==c.source_game_sha256||b.M0_exact_UCI!==c.Git_human_sealed_original_M0_UCI||
  b.M6_selective_label!==c.Git_human_sealed_M6_selective_label||
  c.true_root_choice_changed!==(c.real_SF16_SCORE_intervention_bestmove!==b.M0_exact_UCI))
  throw Error('M6_INDEPENDENT_GAMEWISE_HUMAN_GIT_SOURCE_GUARD_'+(i+1));
 if(!c.original_source_qscore_physically_contacted)throw Error('M6_NO_PHYSICAL_SOURCE_RETURN_'+(i+1));
 contact++;let changed=c.true_root_choice_changed;
 flips+=Number(changed);cover+=Number(b.M6_stable_prediction);
 abstain+=Number(!b.M6_stable_prediction);
 fail+=Number(b.M6_stable_prediction&&changed);
 aflip+=Number(!b.M6_stable_prediction&&changed);
 n0+=c.original_nodes;n1+=c.treated_nodes;
 inc+=Number(c.treated_nodes>c.original_nodes);
 dec+=Number(c.treated_nodes<c.original_nodes);
 same+=Number(c.treated_nodes===c.original_nodes);
}
if(contact!==64||cover!==19||abstain!==45||fail!==0||aflip!==1||flips!==1||
 n0!==221349||n1!==217674||inc!==17||dec!==3||same!==44||
 r.covered_physically_STABLE!==cover||r.ABSTAIN_actual_root_flips!==aflip)
 throw Error('M6_INDEPENDENT_FIRST_SCORE_OUTCOMES_RECHECK_FAILED');
const result={schema:'c3x025-M6-R2-independent-human-literal-gamewise-native-court-v1',
source_games:64,source_operator_contacts:contact,STABLE:cover,ABSTAIN:abstain,
STABLE_wrong:fail,ABSTAIN_real_root_flips:aflip,
actual_root_flips:flips,M0_correct:contact-flips,first_real_flip_game_id:28,
nodes_original:n0,nodes_first_score_suppression:n1,node_delta:n1-n0,
nodes_increase_cases:inc,nodes_decrease_cases:dec,nodes_same_cases:same,
sound_semantics_winner_interval_certificate:false,
mechanism_mediation_or_engine_Elo_certified:false,
independent_July_source_prediction_from_human_literal:true};
writeFileSync(out,JSON.stringify(result,null,2)+'\n');
console.log('C3X025_M6_R2_INDEPENDENT_HUMAN_GIT_PRESEALED_SCORE_COURT_PASS',JSON.stringify(result));
