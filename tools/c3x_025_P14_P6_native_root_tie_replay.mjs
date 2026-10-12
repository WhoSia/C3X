#!/usr/bin/env node
// Real original RootMove stable_sort source snapshot versus executed final UCI.
// Only exposed SF16 roots; operational tie/order, not chess utility proof.
import {readFileSync,writeFileSync} from 'node:fs';
const [inp,out]=process.argv.slice(2),x=JSON.parse(readFileSync(inp));
if(!x.cases?.EXPOSED_M6_JULY2026_ROOT28||!x.cases?.EXPOSED_ORIGINAL_STARTPOS)
 throw Error('NOT_ACTUAL_ORIGINAL_EXPOSED_SF16_ROOTS');
function square(file,rank){return file.charCodeAt(0)-97+8*(Number(rank)-1);}
function encode(uci){if(!/^[a-h][1-8][a-h][1-8]$/.test(uci))throw Error('special move unmodelled, abstain');return 64*square(uci[0],uci[1])+square(uci[2],uci[3]);}
let checks=0,tieCount=0,observed=[];const arms=['sham','first_qscore_suppression','bounded_policies.LOWER','bounded_policies.UPPER'];
for(const [id,c] of Object.entries(x.cases))for(const a of arms){
 const r=a.includes('.')?c.bounded_policies[a.split('.')[1]]:c[a];
 const raw=r.final_attempt_candidate_snapshot;
 if(!Array.isArray(raw)||raw.length<2)throw Error('NO_FULL_NATIVE_ROOT_SNAPSHOT');
 const ordered=raw.map((z,i)=>({...z,sourceIndex:i}));
 ordered.sort((p,q)=>q.storedScore-p.storedScore||q.priorScore-p.priorScore||p.sourceIndex-q.sourceIndex);
 for(let i=1;i<ordered.length;i++){
  const a=ordered[i-1],b=ordered[i];
  if(a.storedScore<b.storedScore||(a.storedScore===b.storedScore&&a.priorScore<b.priorScore)||
     (a.storedScore===b.storedScore&&a.priorScore===b.priorScore&&a.sourceIndex>b.sourceIndex))
    throw Error('BAD_ORIGINAL_STABLE_SORT_COMPARATOR_CERT');
  tieCount+=Number(a.storedScore===b.storedScore);
 }
 const predicted=ordered[0].moveID,actual=encode(r.uci);
 if(predicted!==actual)throw Error('SOURCE_SORT_RESULT_NOT_NATIVE_ROOT_'+id+'_'+a+'_'+predicted+'_'+actual);
 checks++;
 observed.push({case:id,arm:a,bestmove:r.uci,source_score:ordered[0].storedScore,
  previous_score:ordered[0].priorScore,source_contenders:raw.length,
  strict_source_top_score:ordered[0].storedScore>ordered[1].storedScore,
  ties_by_source_record:raw.filter(z=>z.storedScore===ordered[0].storedScore).length});
}
if(checks!==8)throw Error('MISSING_NATIVE_CASE_ARM');
const cert={schema:'c3x025-P14-P6-original-SF16-root-source-lexicographic-operational-tie-cert-v1',
 previous_actual_source_CI:38207386206,
 source_original_struct:'RootMove::operator< uses descending (score,previousScore); original search.cpp stable_sort preserves input order when both equal',
 validation:'8 REAL ORIGINAL EXPOSED ROOT ENDPOINT SNAPSHOTS WITH LEGAL NONSPECIAL UCI',
 source_lexicographic_operational_certification:'PASS',
 genuine_chess_utility_or_full_K_proved:false,
 cross_policy_winner_invariance_proved:false,
 actual_Elo_increase_measured:false,cases:observed};
writeFileSync(out,JSON.stringify(cert,null,2)+'\n');
console.log('C3X025_P14P6_ACTUAL_ORIGINAL_ROOT_SORT_TIE_REPLAY_PASS',JSON.stringify({checks,tieCount,observed}));
