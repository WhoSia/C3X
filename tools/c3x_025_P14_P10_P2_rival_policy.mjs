// C3X 0.25-P14-P10-P2. Deterministic, source-blind policy kernel.
// Preregistered before native observation: 58a4e04043b90b6452a63635d1b8cc8fd04dc7c8.
// A Stockfish cp score is a procedural heuristic, never a verified chess bound.
export const DEFAULTS=Object.freeze({pilotNodes:3000,probeNodes:9000,gapMaxCp:60,volatilityMarginCp:20});
const validMove=m=>typeof m==='string'&&/^[a-h][1-8][a-h][1-8][qrbn]?$/.test(m);
const exact=r=>r&&r.scoreType==='cp'&&Number.isInteger(r.score)&&!r.bound&&validMove(r.move);
function completeFrames(rows){
  const by=new Map();
  for(const r of rows){
    if(!Number.isInteger(r.depth)||r.depth<1||![1,2].includes(r.rank))continue;
    if(!by.has(r.depth))by.set(r.depth,new Map());
    by.get(r.depth).set(r.rank,r);
  }
  return [...by.entries()].filter(([d,m])=>m.has(1)&&m.has(2))
    .sort((a,b)=>a[0]-b[0]).map(([depth,m])=>({depth,first:m.get(1),second:m.get(2)}));
}
export function buildRivalPlan(rows, cfg=DEFAULTS){
  const n=cfg.probeNodes??DEFAULTS.probeNodes;
  if(!Number.isInteger(n)||n<1000)throw Error('probeNodes must be integer >=1000');
  const frames=completeFrames(rows),last=frames.at(-1);
  if(!last)return {status:'ABSTAIN_INCOMPLETE_PILOT',trigger:false,candidates:null,budgets:null};
  const L=last.first,R=last.second;
  if(!exact(L)||!exact(R)||L.move===R.move)
    return {status:'ABSTAIN_INVALID_EXACT_ROOT_SCORES',trigger:false,candidates:null,budgets:null,depth:last.depth};
  const previous=frames.filter(f=>f.depth<last.depth).at(-1);
  const prevRows=previous?[previous.first,previous.second]:[];
  const pastL=prevRows.find(x=>x.move===L.move);
  const pastR=prevRows.find(x=>x.move===R.move);
  const sameMoveHistory=exact(pastL)&&exact(pastR);
  const gap=L.score-R.score;
  const close=gap>=0&&gap<=(cfg.gapMaxCp??DEFAULTS.gapMaxCp);
  const leaderMoved=!!(sameMoveHistory&&previous.first.move!==L.move);
  const leaderVariation=sameMoveHistory?Math.abs(L.score-pastL.score):null;
  const rivalVariation=sameMoveHistory?Math.abs(R.score-pastR.score):null;
  const moreVolatile=!!(sameMoveHistory&&rivalVariation>=leaderVariation+(cfg.volatilityMarginCp??DEFAULTS.volatilityMarginCp));
  const trigger=Boolean(close&&sameMoveHistory&&(leaderMoved||moreVolatile));
  const leaderUniform=Math.floor(n/2),rivalUniform=n-leaderUniform;
  const leaderRival=trigger?Math.floor(n*0.35):leaderUniform;
  const rivalRival=n-leaderRival;
  const leaderHeavy=trigger?Math.floor(n*0.65):leaderUniform;
  const rivalHeavy=n-leaderHeavy;
  return {
    status:trigger?'RIVAL_TRIGGER':'ABSTAIN_RIVAL_UNIFORM_FALLBACK',
    trigger,depth:last.depth,previousDepth:previous?.depth??null,
    candidates:{leader:L.move,challenger:R.move},pilotScores:{leader:L.score,challenger:R.score},
    triggerEvidence:{gapCp:gap,close,sameMoveHistory:Boolean(sameMoveHistory),leaderMoved,
      leaderVariationCp:leaderVariation,rivalVariationCp:rivalVariation,moreVolatile},
    budgets:{
      UNIFORM:{[L.move]:leaderUniform,[R.move]:rivalUniform},
      RIVAL:{[L.move]:leaderRival,[R.move]:rivalRival},
      LEADER_HEAVY:{[L.move]:leaderHeavy,[R.move]:rivalHeavy}
    }
  };
}
export function chooseRestrictedMove(plan,results){
  if(!plan?.candidates)return {status:'ABSTAIN_PILOT',move:null};
  const {leader,challenger}=plan.candidates;
  const a=results?.[leader],b=results?.[challenger];
  // Root-restricted trials must actually evaluate the intended root UCI move.
  if(!exact(a)||!exact(b)||a.move!==leader||b.move!==challenger)
    return {status:'ABSTAIN_UNCOMPARABLE_NATIVE_RESULTS',move:null};
  return {status:'HEURISTIC_CHOICE_NOT_CHESS_PROOF',
    move:b.score>a.score?challenger:leader,rootCp:{[leader]:a.score,[challenger]:b.score}};
}
export function parseInfo(line){
  if(!line.startsWith('info ')||!line.includes(' pv '))return null;
  const d=line.match(/\bdepth (\d+)\b/),rank=line.match(/\bmultipv (\d+)\b/);
  const cp=line.match(/\bscore (cp|mate) (-?\d+)\b/);
  const node=line.match(/\bnodes (\d+)\b/);
  const pv=line.match(/\bpv ([a-h][1-8][a-h][1-8][qrbn]?)(?:\s|$)/);
  if(!d||!cp||!pv)return null;
  return {depth:Number(d[1]),rank:rank?Number(rank[1]):1,
    scoreType:cp[1],score:Number(cp[2]),move:pv[1],
    bound:/\b(?:lowerbound|upperbound)\b/.test(line),
    nodes:node?Number(node[1]):null};
}
