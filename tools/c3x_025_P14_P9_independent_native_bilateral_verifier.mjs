#!/usr/bin/env node
// P14-P9 independent verifier for actual native bilateral terminal proofs.
// NO evaluation/TT labels are allowed as premises for immediate checkmate.
import {readFileSync,writeFileSync} from 'node:fs';
const [input,output]=process.argv.slice(2);
if(!output)throw Error('native original evidence, independent proof output required');
const source=JSON.parse(readFileSync(input));
const RE=/^[a-h][1-8][a-h][1-8][qrbn]?$/;
function check(v){
 if(v.schema!=='c3x025-P14-P9-source-native-bilateral-terminal-mate1-v1'||
 v.revision!=='68e1e9b3811e16cad014b590d7443b9063b3eb52'||
 v.native?.fen!=='7k/8/5KQ1/8/8/8/8/8 w - - 0 1'||
 v.two_independent_cold_source_sessions_agree!==true||
 v.eligibility?.raw_TT_bound_is_accepted_as_chess_truth!==false||
 !Array.isArray(v.native.root_legal_moves)||
 !Array.isArray(v.native.fully_classified_root_moves))
 throw Error('INVALID_TT_OR_ROOT_SOURCE_PREMISE');
 const root=v.native.root_legal_moves,rows=v.native.fully_classified_root_moves;
 if(root.length!==23||rows.length!==root.length||v.native.root_legal_move_count!==root.length||
 new Set(root).size!==root.length||root.some(s=>!RE.test(s)))
 throw Error('ORIGINAL_ROOT_LEGAL_COVERAGE_BROKEN');
 const lookup=new Map(rows.map(z=>[z.root_legal_move,z]));
 if(lookup.size!==root.length||root.some(s=>!lookup.has(s)))
 throw Error('ORIGINAL_SOURCE_MOVE_UNIVERSE_NOT_EXHAUSTIVE');
 const mats=[],rivals=[];
 for(const [name,r] of lookup){
  const n=r.opponent_legal_reply_count;
  if(!Array.isArray(r.child_checkers)||r.child_checkers.some(s=>!/^[a-h][1-8]$/.test(s))||
     !Number.isInteger(n)||n<0||
     r.mate_in_one!==(n===0&&r.child_checkers.length>0)||
     r.stalemate_in_one!==(n===0&&r.child_checkers.length===0))
   throw Error('TERMINAL_PROOF_SOURCE_PREMISE_INVALID_'+name);
  if(r.mate_in_one){
    if(r.nonmate_counterwitness!==null)throw Error('MATE_HAS_ESCAPING_REPLY');
    mats.push(name);
  }else{
    if(n>0&&!RE.test(r.nonmate_counterwitness))throw Error('NONMATE_NO_CONCRETE_REPLY');
    if(n===0&&r.nonmate_counterwitness!=='STALEMATE_NOT_MATE')
      throw Error('STALEMATE_WRONGLY_CERTIFIED_AS_MATE');
    rivals.push(name);
  }
 }
 if(mats.length!==1||mats[0]!=='g6g7'||rivals.length!==22||
    JSON.stringify(mats)!==JSON.stringify(v.native.certified_mate_in_one_moves)||
    v.native.nonmate_alternatives!==22||
    v.native.original_depth4_bestmove!=='g6g7'||
    v.native.original_depth4_bestmove_is_certified_mate!==true||
    v.global_Stockfish_K_proven!==false||v.elo_games!==0)
  throw Error('INCORRECT_EXACT_ORIGINAL_BILATERAL_QUANTIFIERS');
 return {mate:mats[0],counterexamples:rivals};
}
const c=check(source);
function reject(mutator){
 const corrupted=JSON.parse(JSON.stringify(source));mutator(corrupted);
 let rejected=false;
 try{check(corrupted);}catch{rejected=true;}
 if(!rejected)throw Error('FALSE_PROOF_WAS_ADMITTED');
}
reject(x=>{x.native.fully_classified_root_moves.find(z=>z.mate_in_one).mate_in_one=false;});
reject(x=>{x.native.fully_classified_root_moves.find(z=>!z.mate_in_one).mate_in_one=true;});
reject(x=>{x.native.fully_classified_root_moves.pop();});
reject(x=>{x.native.fully_classified_root_moves.find(z=>!z.mate_in_one).nonmate_counterwitness=null;});
reject(x=>{x.eligibility.raw_TT_bound_is_accepted_as_chess_truth=true;});
reject(x=>{x.native.original_depth4_bestmove='a1a1';});
const theorem={
 schema:'c3x025-P14-P9-verified-original-source-typed-bilateral-root-certificate-v1',
 original_native_run:38219064407,
 provenance:'unmodified actual SF16 MoveList<LEGAL> perft1 and Position.checkers; fresh cold duplicates',
 exact_legal_root_universe_count:source.native.root_legal_move_count,
 proven_witness:{move:c.mate,claim:'there exists an original legal move that immediately checkmates',
   checkers_nonempty:true,legal_opponent_replies:0},
 proven_negative_alternatives:{count:c.counterexamples.length,moves:c.counterexamples,
   claim:'for each other original legal root move, source proves no immediate checkmate'},
 actual_engine_choice:source.native.original_depth4_bestmove,
 actual_choice_has_terminal_source_proof:true,
 independent_packet_corruptions_rejected:6,
 source_to_game_bound_eligibility:'CHECKMATE_TERMINAL_ONLY',
 original_TT_BOUNDED_NUMERIC_MINIMAX_PROVEN:false,
 all_depth_search_winner_proven:false,
 chess_engine_Elo_change_measured:false,
 frontier_0_26:'RESEARCH_GATE_CONDITIONAL_NOT_AUTOMATIC'
};
writeFileSync(output,JSON.stringify(theorem,null,2)+'\n');
console.log('C3X025_P14P9_INDEPENDENT_BILATERAL_SOURCE_PROOF_COURT_PASS',
 JSON.stringify({root_moves:23,mate_witness:c.mate,excluded_mate1_alternatives:22,
   tamper_rejections:6,original_TT_bound_semantic_validity:'HOLD'}));
