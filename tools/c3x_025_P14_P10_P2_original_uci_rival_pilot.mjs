#!/usr/bin/env node
// Original-Stockfish-only external controller. Development smoke test, NOT a
// source-native mediation proof, fresh-game prospective result or Elo trial.
// Preregistered before observation: 58a4e04043b90b6452a63635d1b8cc8fd04dc7c8.
import {spawn} from 'node:child_process';
import {createInterface} from 'node:readline';
import {writeFileSync} from 'node:fs';
import {buildRivalPlan,chooseRestrictedMove,parseInfo,DEFAULTS} from './c3x_025_P14_P10_P2_rival_policy.mjs';
const [bin,out]=process.argv.slice(2);
if(!bin||!out)throw Error('Usage: node tools/c3x_025_P14_P10_P2_original_uci_rival_pilot.mjs ORIGINAL_SF16 OUT.json');
const positions=[
 {id:'ENGLISH6',uci:'position startpos moves c2c4 e7e5 b1c3 g8f6 g2g3 b8c6'},
 {id:'FRENCH8',uci:'position startpos moves e2e4 e7e6 d2d4 d7d5 b1c3 g8f6 e4e5 f6d7'},
 {id:'ITALIAN8',uci:'position startpos moves e2e4 e7e5 g1f3 b8c6 f1c4 f8c5 c2c3 g8f6'},
 {id:'CARO_KANN8',uci:'position startpos moves e2e4 c7c6 d2d4 d7d5 b1c3 d5e4 c3e4 c8f5'}
];
const same=(a,b)=>JSON.stringify(a)===JSON.stringify(b);
async function runNative(pos,nodes,{multiPV=1,searchmove=null}={}){
 return new Promise((resolve,reject)=>{
  const start=Date.now(),p=spawn(bin,[],{env:{...process.env}});
  let phase=0,closed=false,timedOut=false,bestmove=null;
  const rows=[];let reportedNodes=0;
  const timer=setTimeout(()=>{timedOut=true;p.kill('SIGKILL');},45000);
  p.on('error',e=>{if(!closed){closed=true;clearTimeout(timer);reject(e);}});
  createInterface({input:p.stdout}).on('line',line=>{
   const row=parseInfo(line);if(row){rows.push(row);if(row.nodes!==null)reportedNodes=Math.max(reportedNodes,row.nodes);}
   if(phase===0&&line==='uciok'){
    phase=1;p.stdin.write('setoption name Threads value 1\nsetoption name Hash value 16\nsetoption name Use NNUE value false\nsetoption name MultiPV value '+multiPV+'\nisready\n');
   }else if(phase===1&&line==='readyok'){
    phase=2;p.stdin.write('ucinewgame\n'+pos.uci+'\nisready\n');
   }else if(phase===2&&line==='readyok'){
    phase=3;p.stdin.write('go nodes '+nodes+(searchmove?' searchmoves '+searchmove:'')+'\n');
   }else if(phase===3&&line.startsWith('bestmove ')){
    bestmove=line.split(' ')[1];phase=4;p.stdin.write('quit\n');
   }
  });
  p.on('close',(code)=>{
   if(closed)return;closed=true;clearTimeout(timer);
   if(timedOut||code!==0||phase!==4||!bestmove)return reject(Error('native incomplete '+pos.id+' '+nodes+' '+searchmove+' code '+code));
   const last=[...rows].filter(r=>r.rank===1).sort((a,b)=>b.depth-a.depth)[0];
   resolve({bestmove,rows,latest:last??null,
     reportedNodesAtInfo:reportedNodes,requestedNodes:nodes,
     nodeCountIsExact:false,wallMsIncludingLaunch:Date.now()-start});
  });
  p.stdin.write('uci\n');
 });
}
function small(x){return {bestmove:x.bestmove,requestedNodes:x.requestedNodes,
 reportedNodesAtInfo:x.reportedNodesAtInfo,nodeCountIsExact:x.nodeCountIsExact,
 wallMsIncludingLaunch:x.wallMsIncludingLaunch,depth:x.latest?.depth??null,
 score:x.latest?{scoreType:x.latest.scoreType,score:x.latest.score,bound:x.latest.bound,move:x.latest.move}:null};}
function stable(x){return {bestmove:x.bestmove,reportedNodesAtInfo:x.reportedNodesAtInfo,
 frames:x.rows.map(({depth,rank,scoreType,score,bound,move,nodes})=>({depth,rank,scoreType,score,bound,move,nodes}))};}
function nativeChoice(plan,perMove){const scores={};
 for(const move of Object.values(plan.candidates??{})){
  const result=perMove[move];scores[move]={move:result.bestmove,
   scoreType:result.latest?.scoreType,score:result.latest?.score,
   bound:result.latest?.bound};
 }
 return chooseRestrictedMove(plan,scores);
}
const artifact={schema:'c3x025-P14-P10-P2-original-uci-rival-controller-development-v1',
 preregistered:'58a4e04043b90b6452a63635d1b8cc8fd04dc7c8',
 source:'OFFICIAL_STOCKFISH16_PINNED_BY_READ_ONLY_WORKFLOW',
 sourceRevision:'68e1e9b3811e16cad014b590d7443b9063b3eb52',
 population:'FOUR_EXPOSED_DEVELOPMENT_OPENINGS_NOT_FRESH_GAME_COHORT',
 budget:'REQUESTED_NODES_NOT_CERTIFIED_REALIZED_TOTAL',
 searchMechanism:'EXTERNAL_UCI_SEARCHMOVES_NOT_CPP_TT_SOURCE_INTERVENTION',
 referenceOrElo:'NONE',claim:'ENGINEERING_SMOKE_ONLY',cases:{}};
for(const pos of positions){
 const first=await runNative(pos,DEFAULTS.pilotNodes,{multiPV:2});
 const repeat=await runNative(pos,DEFAULTS.pilotNodes,{multiPV:2});
 const direct=await runNative(pos,12000,{multiPV:1});
 const directRepeat=await runNative(pos,12000,{multiPV:1});
 if(!same(stable(first),stable(repeat))||!same(stable(direct),stable(directRepeat)))
  throw Error('COLD_REPLAY_FAIL '+pos.id);
 const plan=buildRivalPlan(first.rows);
 const caseResult={position:pos.uci,pilot:small(first),direct:small(direct),
  plan,arms:{},outcomeVerdict:'NO_REFERENCE_NO_QUALITY_OR_COST_CLAIM'};
 if(!plan.candidates){caseResult.outcomeVerdict='ABSTAIN_INVALID_PILOT';artifact.cases[pos.id]=caseResult;continue;}
 if(first.bestmove!==plan.candidates.leader)throw Error('PILOT_ROOT_ID_MISMATCH '+pos.id);
 for(const [arm,allocation]of Object.entries(plan.budgets)){
  const restricted={};
  for(const [move,n]of Object.entries(allocation))
   restricted[move]=await runNative(pos,n,{multiPV:1,searchmove:move});
  const choice=nativeChoice(plan,restricted);
  // Searchmoves must actually constrain the original engine to its declared root.
  for(const [move,r]of Object.entries(restricted))
   if(r.bestmove!==move)throw Error('SOURCE_ROOT_RESTRICTION_BROKEN '+pos.id+' '+move);
  caseResult.arms[arm]={choice,restricted:Object.fromEntries(Object.entries(restricted).map(([m,x])=>[m,small(x)])),
   sumReportedNodeLowerBounds:Object.values(restricted).reduce((s,x)=>s+x.reportedNodesAtInfo,0),
   sumRequestedNodes:Object.values(allocation).reduce((s,n)=>s+n,0)};
 }
 artifact.cases[pos.id]=caseResult;
 console.log('C3X025_P14P10_P2_DEV',JSON.stringify({id:pos.id,status:plan.status,
   pilot:plan.candidates,trigger:plan.trigger,choices:Object.fromEntries(Object.entries(caseResult.arms).map(([a,b])=>[a,b.choice.move])),
   direct:direct.bestmove}));
}
writeFileSync(out,JSON.stringify(artifact,null,2)+'\n');
console.log('C3X025_P14P10_P2_DEVELOPMENT_EXECUTED_NO_REFERENCE_NO_STRENGTH_CLAIM');
