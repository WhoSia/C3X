import {test} from 'node:test';
import assert from 'node:assert/strict';
import {buildRivalPlan,chooseRestrictedMove,parseInfo} from './c3x_025_P14_P10_P2_rival_policy.mjs';
const row=(depth,rank,move,score,extra={})=>({depth,rank,move,score,scoreType:'cp',bound:false,...extra});
const history=[
 row(4,1,'e2e4',40),row(4,2,'d2d4',10),
 row(5,1,'e2e4',41),row(5,2,'d2d4',49)
]; // Must be internally consistent with rank order on each depth.
const volatile=[row(4,1,'e2e4',50),row(4,2,'d2d4',10),
 row(5,1,'e2e4',51),row(5,2,'d2d4',40)];
test('near-score volatile challenger triggers deterministic rival-heavy allocation',()=>{
 const p=buildRivalPlan(volatile);assert.equal(p.status,'RIVAL_TRIGGER');
 assert.deepEqual(p.budgets.RIVAL,{e2e4:3150,d2d4:5850});
 assert.deepEqual(p.budgets.UNIFORM,{e2e4:4500,d2d4:4500});
 assert.deepEqual(p.budgets.LEADER_HEAVY,{e2e4:5850,d2d4:3150});
 assert.equal(p.triggerEvidence.rivalVariationCp,30);
});
test('earlier-depth rank reversal is independently eligible',()=>{
 const p=buildRivalPlan([
  row(4,1,'d2d4',39),row(4,2,'e2e4',34),
  row(5,1,'e2e4',40),row(5,2,'d2d4',35)]);
 assert.equal(p.trigger,true);assert.equal(p.triggerEvidence.leaderMoved,true);
});
test('distant scores force uniform fallback with full denominator',()=>{
 const p=buildRivalPlan([row(4,1,'e2e4',170),row(4,2,'d2d4',10),
  row(5,1,'e2e4',180),row(5,2,'d2d4',50)]);
 assert.equal(p.trigger,false);assert.deepEqual(p.budgets.RIVAL,p.budgets.UNIFORM);
});
test('missing previous complete depth forces abstention from rival priority',()=>{
 const p=buildRivalPlan([row(5,1,'e2e4',50),row(5,2,'d2d4',40)]);
 assert.equal(p.trigger,false);
 assert.equal(p.status,'ABSTAIN_RIVAL_UNIFORM_FALLBACK');
});
test('incomplete final frame uses last complete frame, never one-sided optimistic update',()=>{
 const p=buildRivalPlan([...volatile,row(6,1,'a2a3',500)]);
 assert.equal(p.depth,5);assert.equal(p.candidates.leader,'e2e4');
});
test('mate or bound scores are not interpreted as comparable cp',()=>{
 for(const extra of [{scoreType:'mate'},{bound:true}]){
  const p=buildRivalPlan([...volatile.slice(0,3),row(5,2,'d2d4',40,extra)]);
  assert.equal(p.status,'ABSTAIN_INVALID_EXACT_ROOT_SCORES');
  assert.equal(p.candidates,null);
 }
});
test('duplicate or malformed candidate roots are refused',()=>{
 const p=buildRivalPlan([row(5,1,'e2e4',50),row(5,2,'e2e4',40)]);
 assert.equal(p.candidates,null);
});
test('larger restricted exact cp chooses challenger, and ties go to pilot leader',()=>{
 const p=buildRivalPlan(volatile);
 let r=chooseRestrictedMove(p,{e2e4:{move:'e2e4',scoreType:'cp',score:22,bound:false},
   d2d4:{move:'d2d4',scoreType:'cp',score:28,bound:false}});
 assert.equal(r.move,'d2d4');assert.equal(r.status,'HEURISTIC_CHOICE_NOT_CHESS_PROOF');
 r=chooseRestrictedMove(p,{e2e4:{move:'e2e4',scoreType:'cp',score:22,bound:false},
   d2d4:{move:'d2d4',scoreType:'cp',score:22,bound:false}});
 assert.equal(r.move,'e2e4');
});
test('negative root search identity and incomplete score refuse decision',()=>{
 const p=buildRivalPlan(volatile);
 const r=chooseRestrictedMove(p,{e2e4:{move:'e2e4',scoreType:'cp',score:22,bound:false},
  d2d4:{move:'d2d4',scoreType:'mate',score:1,bound:false}});
 assert.equal(r.status,'ABSTAIN_UNCOMPARABLE_NATIVE_RESULTS');
});
test('UCI parser preserves root PV, rank, mate/bound and reported nodes',()=>{
 const s='info depth 8 seldepth 12 multipv 2 score cp -17 upperbound nodes 3210 nps 20000 time 12 pv d2d4 d7d5';
 const p=parseInfo(s);assert.equal(p.move,'d2d4');assert.equal(p.score,-17);
 assert.equal(p.bound,true);assert.equal(p.rank,2);assert.equal(p.nodes,3210);
 assert.equal(parseInfo('bestmove e2e4'),null);
 assert.equal(parseInfo('info depth 8 multipv 1 score mate 2 nodes 500 pv e2e4').scoreType,'mate');
});
test('unsupported nonintegral or too-small search budget fails closed',()=>{
 assert.throws(()=>buildRivalPlan(volatile,{probeNodes:500}),/probeNodes/);
});
