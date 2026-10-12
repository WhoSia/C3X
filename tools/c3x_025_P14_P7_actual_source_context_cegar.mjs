#!/usr/bin/env node
// Real original Stockfish CEGAR counterexample to factorization through key.
// This is a two-state *exposed* fiber, not a globally certified abstraction.
import {readFileSync,writeFileSync} from 'node:fs';
const [input,output]=process.argv.slice(2);
if(!input||!output)throw Error('usage: original small source receipt, derived output');
const raw=JSON.parse(readFileSync(input));
if(raw.schema!=='c3x025-P14-P7-original-SF16-context-identity-v1'||
 !raw.same_full_adjusted_position_key||raw.cases?.length!==2)
 throw Error('DOES_NOT_MATCH_ACTUAL_PINNED_ORIGINAL_STOCKFISH');
const [a,b]=raw.cases;
const board=s=>s.fen.split(' ').slice(0,4).join(' ');
if(board(a)!==board(b)||a.board_key_64!==b.board_key_64||
 a.halfmove_clock!==94||b.halfmove_clock!==100||
 a.bestmove===b.bestmove||a.score===b.score)
 throw Error('REAL_SOURCE_TWO_STATE_ACTION_NONFACTORING_COUNTERMODEL_LOST');
const observations=[a,b];
const keyOnly=new Map();
for(const s of observations){
 const set=keyOnly.get(s.board_key_64)||new Set();
 set.add(s.bestmove);keyOnly.set(s.board_key_64,set);
}
if(keyOnly.size!==1||[...keyOnly.values()][0].size!==2)
 throw Error('KEY_OBSERVATION_FIBER_NOT_CONFLICTED');
const refined=new Map();
for(const s of observations){
 // Exactly one additional source-recognized boolean distinguishes THIS pair.
 const observation=s.board_key_64+':'+Number(s.halfmove_clock>99);
 const set=refined.get(observation)||new Set();
 set.add(s.bestmove);refined.set(observation,set);
}
if(refined.size!==2||[...refined.values()].some(x=>x.size!==1))
 throw Error('SOURCE_GUARD_REFINEMENT_FAILED_ON_TWO_OBSERVED_STATES');
const receipt={
 schema:'c3x025-P14-P7-actual-original-context-fiber-CEGAR-exposed-v1',
 native_original_run:38209111244,
 original_source_revision:'68e1e9b3811e16cad014b590d7443b9063b3eb52',
 original_full_position_key:a.board_key_64,
 same_position_key_different_full_source_context:true,
 original_native_moves:[a.bestmove,b.bestmove],
 original_native_scores:[a.score,b.score],
 exact_rule50_counts:[94,100],
 claim:'No total f(key) can reproduce both original selected moves on this two-element actually observed fiber',
 local_refinement:'(Position.key(), rule50 > 99) splits BOTH observed worlds',
 observed_fiber_min_extra_binary_observation_bits:1,
 full_historical_repetition_information_recovered:false,
 globally_sound_refined_Stockfish_search_state:false,
 TT_entry_illegal_or_corrupt:false,
 engine_strength_or_Elo_gain_proved:false,
 prospective_generalization_claim:false
};
writeFileSync(output,JSON.stringify(receipt,null,2)+'\n');
console.log('C3X025_P14P7_ACTUAL_SOURCE_CEGAR_CONTEXT_FIBER_PASS',JSON.stringify(receipt));
