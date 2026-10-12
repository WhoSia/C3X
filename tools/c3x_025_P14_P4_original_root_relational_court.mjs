#!/usr/bin/env node
// P14-P4 ORIGINAL SF16 concise source court; intentionally uses source
// operations rather than the long historical P8...P14 overlays.
import {spawn} from 'node:child_process';
import {createInterface} from 'node:readline';
import {readFileSync,writeFileSync} from 'node:fs';
const [unmodified,patched,julySource,out]=process.argv.slice(2);
if(!unmodified||!patched||!julySource||!out)throw Error('original patched July64_source output');
const src=JSON.parse(readFileSync(julySource));
if(src.selected?.length!==64||src.selected[27].id!==28)throw Error('P14P4_SOURCE_JULY64_GAME28');
const r=src.selected[27];
const cases=[
 {id:'EXPOSED_ORIGINAL_STARTPOS',uci:'position startpos',expectSham:'b1c3',expectedNodes:8657},
 {id:'EXPOSED_M6_JULY2026_ROOT28',uci:'position fen '+[r.fen4,r.source_halfmove_clock,r.source_fullmove_number].join(' '),
  expectSham:'f1d1',expectedNodes:7456,expectedScore:'a1a5',expectedScoreNodes:4380}
];
function fields(line){
 const x={};
 for(const item of line.split(/\s+/).slice(3)){
  const k=item.indexOf('=');
  if(k<1||k===item.length-1)throw Error('P14P4_BAD_FIELD');
  const key=item.slice(0,k),val=item.slice(k+1);
  if(Object.hasOwn(x,key))throw Error('P14P4_DUPLICATE_FIELD');
  x[key]=val;
 }
 return x;
}
function n(x,tag){if(!/^-?\d+$/.test(x??'')||!Number.isSafeInteger(Number(x)))throw Error('P14P4_INVALID_INT_'+tag);return Number(x);}
function run(path,trace,arm,c){
 return new Promise((resolve,reject)=>{
  const p=spawn(path,[],{env:{...process.env,C3X025_P14P4_TRACE:trace?'1':'',C3X025_P14P4_ARM:arm}});
  let phase=0,closed=false;
  const source=[],uci=[],timer=setTimeout(()=>fail(Error('P14P4_NATIVE_TIMEOUT_'+c.id)),90000);
  function fail(e){if(closed)return;closed=true;clearTimeout(timer);p.kill('SIGKILL');reject(e);}
  p.on('error',fail);
  createInterface({input:p.stdout}).on('line',line=>{
   if(line.startsWith('info string c3x025_p14p4 '))source.push(fields(line));
   if(line.startsWith('bestmove ')||/^info depth 7 /.test(line))uci.push(line);
   if(line==='uciok'&&phase===0){phase=1;p.stdin.write('setoption name Threads value 1\nsetoption name Hash value 16\nsetoption name MultiPV value 1\nsetoption name Use NNUE value false\nucinewgame\nisready\n');}
   if(line==='readyok'&&phase===1){phase=2;p.stdin.write(c.uci+'\ngo depth 7\n');}
   if(line.startsWith('bestmove ')&&phase===2){phase=3;p.stdin.write('quit\n');}
  });
  p.on('close',code=>{if(closed)return;closed=true;clearTimeout(timer);try{
   if(code!==0)throw Error('P14P4_NATIVE_NONZERO_EXIT_'+code);
   const bm=uci.filter(x=>x.startsWith('bestmove ')),info=uci.filter(x=>/^info depth 7 /.test(x)&&/\bnodes \d+/.test(x)).at(-1);
   if(bm.length!==1||!info)throw Error('P14P4_INCOMPLETE_DEPTH7');
   const bestmove=bm[0].split(/\s+/)[1],nodes=n(info.match(/\bnodes (\d+)/)?.[1],'nodes');
   if(!/^[a-h][1-8][a-h][1-8][qrbn]?$/.test(bestmove))throw Error('P14P4_NATIVE_BAD_UCI');
   resolve({bestmove,nodes,source});
  }catch(e){reject(e);}});
  p.stdin.write('uci\n');
 });
}
function analyze(x,c,arm){
 const contacts=x.source.filter(z=>z.event==='FIRST_QSCORE');
 const moves=x.source.filter(z=>z.event==='ROOT_MOVE_RESULT');
 const attempts=x.source.filter(z=>z.event==='ROOT_ATTEMPT');
 const stored=x.source.filter(z=>z.event==='ROOT_STORED_CANDIDATE');
 if(contacts.length!==1||n(contacts[0].changed,'contact_changed')!==Number(arm==='SCORE')||
    !moves.length||attempts.length<7||!stored.length||
    x.source.length!==contacts.length+moves.length+attempts.length+stored.length)
  throw Error('P14P4_ACTUAL_ORIGINAL_SOURCE_OPERATOR_MISSING_'+c.id+'_'+arm);
 const seen=new Set(),perDepth={};
 let failLow=0,failHigh=0,inside=0;
 let sentinel=0,upperFlags=0,lowerFlags=0,nonExactFromFlags=0;
 let reSearches=0;
 let totalMoveUpdates=moves.length;
 let depth7=[];
 for(const a of attempts){
  let seq=n(a.seq,'seq'),depth=n(a.root_depth,'depth'),alpha=n(a.alpha,'alpha'),
      beta=n(a.beta,'beta'),v=n(a.returned,'returned'),effective=n(a.effective_depth,'effective'),
      cls=a.window_class;
  if(seq!==seen.size+1||seen.has(seq)||depth<1||depth>7||!(alpha<beta)||effective<1)
   throw Error('P14P4_ORIGINAL_ROOT_ATTEMPT_ORDER_OR_WINDOW');
  seen.add(seq);
  if(cls!==(v<=alpha?'FAIL_LOW':v>=beta?'FAIL_HIGH':'INSIDE'))throw Error('P14P4_RESEARCH_CLASS_INCONSISTENT');
  failLow+=Number(cls==='FAIL_LOW');failHigh+=Number(cls==='FAIL_HIGH');inside+=Number(cls==='INSIDE');
  perDepth[depth]??={attempts:0,fail_low:0,fail_high:0,inside:0,root_candidate_count:n(a.count,'candidate_count')};
  perDepth[depth].attempts++;
  perDepth[depth].fail_low+=Number(cls==='FAIL_LOW');
  perDepth[depth].fail_high+=Number(cls==='FAIL_HIGH');
  perDepth[depth].inside+=Number(cls==='INSIDE');
  if(cls!=='INSIDE')reSearches++;
  if(depth===7)depth7.push({seq,alpha,beta,returned:v,class:cls,effective_depth:effective});
 }
 const grouped=new Map();
 for(const row of stored){
  const seq=n(row.seq,'candidate_seq'),move=n(row.move,'move'),
    score=n(row.score,'score'),u=n(row.uci,'uci'),
    lo=n(row.lo,'lo'),hi=n(row.hi,'hi');
  if(!seen.has(seq)||move<1||lo>1||hi>1||lo<0||hi<0|| (lo&&hi) || u>40000||u< -40000)
   throw Error('P14P4_INVALID_NATIVE_CANDIDATE_FIELD');
  const group=grouped.get(seq)??new Set();if(group.has(move))throw Error('P14P4_DUPLICATE_ROOT_MOVE_SAME_SEARCH');group.add(move);grouped.set(seq,group);
  sentinel+=Number(score===-32001);upperFlags+=hi;lowerFlags+=lo;nonExactFromFlags+=Number(lo||hi);
 }
 for(const a of attempts){
  const seq=n(a.seq,'seq');if((grouped.get(seq)?.size??0)!==n(a.count,'count'))
    throw Error('P14P4_CANDIDATE_VECTOR_NOT_EXACTLY_ALL_ORIGINAL_ROOT_MOVES');
 }
 const finalAttempt=attempts.at(-1);
 const lastStored=stored.filter(row=>row.seq===finalAttempt.seq);
 // Source flag means bounded reported value, never assert true interval!
 const finalSummary=lastStored.map(row=>({
  moveID:n(row.move,'move'),storedScore:n(row.score,'score'),
  uciScore:n(row.uci,'uci'),priorScore:n(row.prior,'prior'),
  scoreLowerbound:Boolean(n(row.lo,'lo')),scoreUpperbound:Boolean(n(row.hi,'hi')),
  PVlength:n(row.pvlen,'pvlen')
 }));
 return {uci:x.bestmove,nodes:x.nodes,source_original_first_TT_return_contact:contacts[0],
   actual_root_move_results:totalMoveUpdates,
   root_attempts:attempts.length,
   fail_low:failLow,fail_high:failHigh,inside,
   aspiration_retry_lower_bound:reSearches,
   per_depth:perDepth,
   root_stored_sentinels_across_attempts:sentinel,
   source_lowerbound_flags:lowerFlags,source_upperbound_flags:upperFlags,
   source_bound_flags_are_not_proven_true_score_intervals:true,
   final_depth7_root_attempts:depth7,
   final_attempt_candidate_snapshot:finalSummary,
   original_complete_score_interval_certificate:'HOLD'};
}
const record={schema:'c3x025-P14-P4-original-root-aspiration-original-move-source-relational-stability-observer-v1',
 pinned_original_SF16:'68e1e9b3811e16cad014b590d7443b9063b3eb52',
 actual_score_intervention:'first original qsearch TT bounded numeric return suppressed once',
 research_stage:'POSTOUTCOME_EXPOSED_DEVELOPMENT_ONLY',source_only_compact:true,
 cases:{},strict_actual_original_uci_parity:true,
 final_root_bound_labels_not_converted_into_mathematically_certified_intervals:true,
 no_Elo_improvement_proven:true,no_natural_TT_SEE_root_mediation_certified:true};
for(const c of cases){
 const orig=await run(unmodified,false,'SHAM',c),off=await run(patched,false,'SHAM',c);
 const sham1=await run(patched,true,'SHAM',c),sham2=await run(patched,true,'SHAM',c);
 const score1=await run(patched,true,'SCORE',c),score2=await run(patched,true,'SCORE',c);
 if(JSON.stringify(orig)!==JSON.stringify(off)||JSON.stringify(sham1)!==JSON.stringify(sham2)||
    JSON.stringify(score1)!==JSON.stringify(score2)||orig.bestmove!==sham1.bestmove||
    orig.nodes!==sham1.nodes||orig.bestmove!==c.expectSham||orig.nodes!==c.expectedNodes)
  throw Error('P14P4_UNMODIFIED_SHAM_COLDCALL_IDENTITY_FAIL_'+c.id);
 if(c.expectedScore&&(score1.bestmove!==c.expectedScore||score1.nodes!==c.expectedScoreNodes))
  throw Error('P14P4_ACTUAL_ORIGINAL_PRIOR_ROOT_PIVOT_NOT_REPRODUCED');
 const s=analyze(sham1,c,'SHAM'),t=analyze(score1,c,'SCORE');
 record.cases[c.id]={original:{uci:orig.bestmove,nodes:orig.nodes},
    sham:s,first_qscore_suppression:t,
    selected_root_changed:s.uci!==t.uci,
    all_search_stored_candidate_state_equal:JSON.stringify(s.final_attempt_candidate_snapshot)===JSON.stringify(t.final_attempt_candidate_snapshot),
    root_aspiration_retry_count_changed:s.aspiration_retry_lower_bound!==t.aspiration_retry_lower_bound};
}
writeFileSync(out,JSON.stringify(record,null,2)+'\n');
console.log('C3X025_P14P4_REAL_ORIGINAL_ROOT_ATTEMPT_RESEARCH_COURT_PASS',
 JSON.stringify(Object.fromEntries(Object.entries(record.cases).map(([k,c])=>[k,{
 original_uci:c.original.uci,original_nodes:c.original.nodes,
 qscore_uci:c.first_qscore_suppression.uci,qscore_nodes:c.first_qscore_suppression.nodes,
 root_flipped:c.selected_root_changed,
 root_candidate_fields_differ:!c.all_search_stored_candidate_state_equal,
 untreated_aspiration_rounds:c.sham.root_attempts,
 treated_aspiration_rounds:c.first_qscore_suppression.root_attempts,
 untreated_retries:c.sham.aspiration_retry_lower_bound,
 treated_retries:c.first_qscore_suppression.aspiration_retry_lower_bound,
 bounds_sham:{lower:c.sham.source_lowerbound_flags,upper:c.sham.source_upperbound_flags,
  masked:c.sham.root_stored_sentinels_across_attempts},
 bounds_score:{lower:c.first_qscore_suppression.source_lowerbound_flags,upper:c.first_qscore_suppression.source_upperbound_flags,
  masked:c.first_qscore_suppression.root_stored_sentinels_across_attempts}
 }]))));
