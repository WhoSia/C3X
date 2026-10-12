#!/usr/bin/env node
// Post hoc exact-source verification of a PRECOMMITTED original SF16 native run.
// Proof is bounded to printed first-four qsearch returns per two source states.
import {readFileSync,writeFileSync} from 'node:fs';
const [baselineFile,observerFile,out]=process.argv.slice(2);
if(!out)throw Error('usage original.json observer.json derived.json');
const a=JSON.parse(readFileSync(baselineFile)),b=JSON.parse(readFileSync(observerFile));
if(a.schema!=='c3x025-P14-P8-native-original-history-pair-v1'||
 b.schema!==a.schema||a.cases.length!==2||b.cases.length!==2)
 throw Error('source-schema-mismatch');
function tokens(line,prefix){
 if(!line.startsWith(prefix))throw Error('unsupported original source event');
 return Object.fromEntries(line.slice(prefix.length).trim().split(' ').map(t=>{
  const j=t.indexOf('=');if(j<1)throw Error('invalid original label');
  return [t.slice(0,j),t.slice(j+1)];
 }));
}
let n=0,low=0,upper=0,serials=[],actors=[];
for(let i=0;i<2;i++){
 const x=a.cases[i],y=b.cases[i];
 for(const k of ['fen','key','move','score','score_type','nodes'])
  if(x[k]!==y[k])throw Error('observer changed original source behavior:'+k);
 if(x.tt_writer_qreturn_events.length||x.history.length)
   throw Error('baseline unexpectedly instrumented');
 if(y.history.length!==1||y.tt_writer_qreturn_events.length!==4)
   throw Error('actual originally capped source events missing');
 const ctx=tokens(y.history[0],'info string c3xp8_history ');
 if(ctx.rule50!=='24'||(i===0&&(ctx.repetition!=='0'||ctx.draw0!=='0'||ctx.repeated!=='0'))||
  (i===1&&(ctx.repetition!=='-4'||ctx.draw0!=='1'||ctx.repeated!=='1')))
  throw Error('actual source repetition predicate discrepancy');
 for(const line of y.tt_writer_qreturn_events){
  const t=tokens(line,'info string c3xp8_tt_return ');
  if(t.known!=='1'||t.same_fullkey!=='1'||t.same_raw!=='1'||
    Number(t.serial)<=0||t.writer_bound!==t.reader_bound||
    t.writer_depth!==t.reader_depth)throw Error('source writer and reader provenance falsified');
  const value=Number(t.value),beta=Number(t.beta),bound=Number(t.reader_bound);
  const side=value>=beta?'LOWER':'UPPER';
  if(side!==t.side||!(bound&(side==='LOWER'?2:1)))
    throw Error('source branch comparison / TT bound incompatibility');
  if(side==='LOWER')low++;else upper++;
  serials.push(t.serial);n++;
 }
 actors.push({source_history_repetition:ctx.repetition,draw_at_ply0:ctx.draw0,
  search_nodes:y.nodes,root_choice:y.move,first_observed_TT_numeric_returns:y.tt_writer_qreturn_events.length});
}
if(n!==8||actors[0].root_choice!==actors[1].root_choice||
 actors[0].search_nodes===actors[1].search_nodes)throw Error('key-is-not-cost-history-contrast-missing');
const conclusion={
 schema:'c3x025-P14-P8-same-execution-original-TT-writer-qsearch-reader-and-history-court-v1',
 original_native_execution_run:38211438198,
 evidence_scope:'first four executed qsearch TT numeric returns per each of two real original source histories',
 same_exact_final_FEN_and_adjusted_position_key:true,
 same_exact_rule50:true,
 source_actual_history_query_diff:true,
 same_root_move_despite_diff_draw_and_search_cost:true,
 distinct_original_TT_numeric_return_events_checked:n,
 original_writer_full64_match_and_raw_value_match:n,
 bound_numeric_return_source_side_compatible:n,
 lower_side:low,upper_side:upper,
 writer_serials:serials,
 true_semantic_chess_value_bound_certified:false,
 source_to_proven_root_gap_certified:false,
 automatic_safe_TT_mutation_approved:false,
 real_Elo_measured:false,
 explanation_support:'actual source physical provenance, differential legal history, and observed search resource use',
 proof_limit:'the full true candidate-value K and source TT writer legitimacy are NOT established',
 cases:actors
};
writeFileSync(out,JSON.stringify(conclusion,null,2)+'\n');
console.log('C3X025_P14P8_ORIGINAL_TT_WRITER_QSEARCH_READER_INDEPENDENT_SOURCE_COURT_PASS',JSON.stringify({n,low,upper,actors}));
